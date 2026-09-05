#!/usr/bin/env python3
"""Deterministic contract harness for the compaction observer hook.

CONTRACT (must hold on EVERY path):
  C1 exit status is 0
  C2 zero bytes on stdout
  C3 completes within WALL_CEIL seconds (never blocks indefinitely)
  C4 no pre-existing file is deleted or replaced (path set, inode, size, mtime, md5)

Method: EXPECTED for every case is written to disk BEFORE any subprocess runs (R0).
Grading compares ACTUAL against that frozen file; the grader never re-derives expected.
"""
import hashlib, json, os, select, shutil, signal, stat, subprocess, sys, threading, time
import re

WALL_CEIL = 12.0          # C3 ceiling, seconds
SIGDELAY  = 0.35          # when to deliver a signal after spawn
SETTLE    = 1.5           # how long to keep watching stdout AFTER the parent exits
# Bound on the GRADER's deadline-loop segment (first stdin pump .. bounded reap):
# ceiling + kill/reap bound (5s) + scheduling margin. Diagnostics (ps/lsof, 10s
# timeouts each), snapshots, settle and tap finalize are bounded on their own and
# are NOT in this clock (codex sol 2026-09-06 GRADER-BOUND). A segment that runs
# longer is a harness stall (M19 pre-fix: 40s), graded as such independent of rc.
GRADER_STALL = WALL_CEIL + 5.0 + 3.0
INVOC     = ["/bin/bash", "--noprofile", "--norc", "-p"]   # the installed form

LSOF = "/usr/sbin/lsof"

def cwd_pids(workdir, under=False):
    """PIDs of this user's live processes whose cwd is `workdir` (or, with
    under=True, is `workdir` or anywhere beneath it), or None when lsof is
    unusable (never an empty set -- unknown is not clean).

    Why cwd: out-of-group survivors used to be attributed by the inherited
    `HOME=` in `ps -axwwEo command=`. macOS emits NO environment for platform
    binaries -- a `/bin/sleep` row is 18 chars with no HOME= where a
    CommandLineTools python3 row is 5000+ chars with it -- so a setsid'd
    descendant that execs /bin/sleep, /bin/sh or /bin/bash was invisible and
    scored orph=0 while alive with ppid 1 (mutant M18; measured 2026-09-05).
    cwd survives execve and fd-closing, every graded instrument spawns the hook
    with cwd=workdir, and the workdir is unique to the run -- so a live process
    whose cwd is the workdir and was NOT there before Popen is the hook's.
    Defeated only by a hook that chdir()s away, the same residual class as the
    environment scrub. lsof reports realpath (/private/var/...), so compare that."""
    want = os.path.realpath(workdir)
    try:
        # cwd="/" so lsof's OWN row can never match the workdir: launched from
        # inside the workdir, the harness's lsof child inherited that cwd, showed
        # up in `now` but not `pre`, and scored v28 orph=1 (false red, measured).
        r = subprocess.run([LSOF, "-a", "-d", "cwd", "-u", str(os.getuid()), "-Fpn"],
                           capture_output=True, text=True, timeout=10, cwd="/")
    except (OSError, subprocess.TimeoutExpired):
        return None
    # Unknown is never an empty set. lsof exits 0 here in normal operation --
    # measured 30/30 under concurrent process churn -- and 1 means "some file
    # could not be inspected", i.e. the listing may be PARTIAL: seeing our own
    # row proves one row exists, not that the target descendant was listed
    # (codex 2026-09-05 r2). Any nonzero status is unknown, as is a listing that
    # does not contain THIS process (which always has a cwd).
    if r.returncode != 0 or not r.stdout.strip():
        return None
    allpids, match, cur = set(), set(), None
    for ln in r.stdout.splitlines():
        if ln.startswith("p"):
            cur = int(ln[1:]) if ln[1:].isdigit() else None
            if cur is not None: allpids.add(cur)
        elif ln.startswith("n") and cur is not None \
             and (ln[1:] == want or (under and ln[1:].startswith(want + "/"))):
            match.add(cur)
    if os.getpid() not in allpids:
        return None            # completeness sentinel failed: partial/malformed output
    match.discard(os.getpid())
    return match

def _ancestors():
    """This process and its parent chain up to pid 1 (bounded), via ps -o ppid=."""
    out, pid = set(), os.getpid()
    # Walk to pid 1 with a visited set; a failed/malformed ps reply stops the walk
    # and an older ancestor in the workdir would then read as foreign -- that is
    # a loud refusal (fail-closed), never a false green (codex 2026-09-05 r2, low).
    while pid > 1 and pid not in out and len(out) < 4096:
        out.add(pid)
        try:
            r = subprocess.run(["/bin/ps", "-o", "ppid=", "-p", str(pid)],
                               capture_output=True, text=True, timeout=5)
            nxt = int(r.stdout.strip() or 0)
        except (OSError, ValueError, subprocess.TimeoutExpired):
            break
        if nxt <= 0: break
        pid = nxt
    out.add(1)
    return out

_LOCKS = []

def _lock_path(workdir):
    return os.path.join(os.environ.get("TMPDIR", "/tmp"),
                        "hook-harness-%s.lock" % hashlib.sha1(
                            os.path.realpath(workdir).encode()).hexdigest()[:16])

def require_exclusive_workdir(workdir, who, lock=True):
    """Refuse to grade in a workdir another run occupies or holds.

    Survivors are attributed by cwd under workdir and then SIGKILLed, so the
    workdir must be ours alone. Measured 2026-09-05: two concurrent runs sharing
    one dir -> run A counted AND killed run B's leaked descendant (orph=5), so
    run B then scored 1/1 pass on a leaking hook -- a false green.

    Two checks, because an occupancy snapshot alone is racy (codex r2): (1) an
    ATOMIC lock file keyed by the workdir's realpath, O_CREAT|O_EXCL, held for
    the life of this process (stale lock from a dead pid is reclaimed); (2) no
    live process other than our own ancestors may have its cwd AT OR UNDER the
    workdir -- under, because gap's probes run in child dirs. Exit 2, printed in
    the FAIL shape run_all.sh greps for. lsof unusable also refuses: every cwd
    clause downstream would be blind. lock=False is for run_all.sh's pre-rm-rf
    check on an explicit WORK, which must not hold the lock its instruments need."""
    if lock:
        lp = _lock_path(workdir)
        # Write the pid to a private temp file first, then link() it into place:
        # link() is atomic and fails if the lock exists, so the lock file can never
        # be observed EMPTY. With open(O_EXCL)+write, a second run reading the file
        # between those two calls saw holder=0, judged it stale, unlinked it and
        # acquired -- both runs then graded the same workdir (hit once under load).
        tmp = "%s.%d" % (lp, os.getpid())
        with open(tmp, "w") as f: f.write(str(os.getpid()))
        for attempt in (1, 2):
            try:
                os.link(tmp, lp)
                os.unlink(tmp)
                _LOCKS.append(lp)
                import atexit
                atexit.register(lambda p=lp: (os.path.exists(p) and os.unlink(p)))
                break
            except FileExistsError:
                try: holder = int(open(lp).read().strip() or 0)
                except (OSError, ValueError): holder = 0
                alive = False
                if holder > 0:
                    try: os.kill(holder, 0); alive = True
                    except ProcessLookupError: alive = False
                    except PermissionError: alive = True
                if alive or attempt == 2:
                    try: os.unlink(tmp)
                    except OSError: pass
                    print("FAIL %s: workdir %s is LOCKED by live pid %s (%s) -- another run in "
                          "progress; use a fresh directory" % (who, workdir, holder, lp)); sys.exit(2)
                try: os.unlink(lp)          # stale: holder is dead
                except OSError: pass
    occ = cwd_pids(workdir, under=True)
    if occ is None:
        print("FAIL %s: lsof unusable (%s) -- cwd survivor attribution impossible; not grading"
              % (who, LSOF)); sys.exit(2)
    # The harness's own ancestors (the shell it was launched from) may legitimately
    # sit in the workdir; they predate every Popen so the per-case diff already
    # excludes them, and they cannot be a hook descendant. Anything else is foreign.
    occ -= _ancestors()
    if occ:
        print("FAIL %s: workdir %s is occupied by pid(s) %s -- another run? use a fresh "
              "directory (run_all.sh now defaults to a unique one)"
              % (who, workdir, ",".join(map(str, sorted(occ))))); sys.exit(2)

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(65536), b""):
            h.update(c)
    return h.hexdigest()

def snapshot(root, exclude=()):
    """Every regular file + symlink under root: identity that a delete/replace changes.
    exclude: absolute paths (files or directory subtrees) the harness itself mutates
    during the run; they are skipped, never graded."""
    out = {}
    ex = tuple(os.path.abspath(e) for e in exclude)
    for dp, dns, fns in os.walk(root, followlinks=False):
        dns[:] = [d for d in dns if not os.path.abspath(os.path.join(dp, d)).startswith(ex)]
        for n in fns + dns:
            p = os.path.join(dp, n)
            if ex and os.path.abspath(p).startswith(ex):
                continue
            try:
                st = os.lstat(p)
            except OSError:
                continue
            rec = {"ino": st.st_ino, "size": st.st_size, "mtime": st.st_mtime_ns,
                   "mode": stat.S_IMODE(st.st_mode), "type": "l" if stat.S_ISLNK(st.st_mode)
                   else ("d" if stat.S_ISDIR(st.st_mode) else "f")}
            if rec["type"] == "f":
                try: rec["md5"] = md5(p)
                except OSError: rec["md5"] = "UNREADABLE"
            elif rec["type"] == "l":
                rec["target"] = os.readlink(p)
            out[os.path.relpath(p, root)] = rec
    return out

def diff_snapshots(before, after):
    """Only DESTRUCTION counts. New files are expected (the hook writes records)."""
    bad = []
    for p, b in before.items():
        a = after.get(p)
        if a is None:
            bad.append(f"DELETED {p}"); continue
        if a["type"] != b["type"]:
            bad.append(f"TYPE-CHANGED {p} {b['type']}->{a['type']}"); continue
        if a["ino"] != b["ino"]:
            bad.append(f"REPLACED(inode) {p} {b['ino']}->{a['ino']}"); continue
        if b["type"] == "f":
            if a.get("md5") != b.get("md5"):
                bad.append(f"CONTENT-CHANGED {p}")
            elif a["size"] != b["size"]:
                bad.append(f"SIZE-CHANGED {p}")
            elif a["mtime"] != b["mtime"]:
                bad.append(f"MTIME-CHANGED {p}")
        if b["type"] == "l" and a.get("target") != b.get("target"):
            bad.append(f"SYMLINK-REPOINTED {p}")
        if a["mode"] != b["mode"]:
            bad.append(f"MODE-CHANGED {p} {oct(b['mode'])}->{oct(a['mode'])}")
    return bad

def cwd_snapshot(workdir, home, ext_root, outf, errf):
    """The cwd the hook runs in, recursively, minus what the harness itself writes
    during this case (this case's home and canary tree are graded separately;
    the capture files and the run-level TABLE/RESULT files are harness-owned).
    sol 2026-09-02 F4 (CONFIRMED by probe): the earlier top-level-only listing
    left every nested pre-existing file (hostilebin/python3, other cases' homes)
    ungraded -- a hook deleting one scored destroyed=[]."""
    ex = [home, ext_root, outf, errf]
    ex += [os.path.join(workdir, n) for n in os.listdir(workdir)
           if n.startswith(("TABLE-", "RESULT-"))]
    snap = snapshot(workdir, exclude=ex)
    # top-level directories: identity only -- their mtime moves whenever a file
    # is legitimately created inside (the hook writes its own records there).
    for rel, rec in snap.items():
        if rec["type"] == "d":
            rec["mtime"] = 0; rec["size"] = 0
    return snap

# ---------------------------------------------------------------- canary tree
CANARY_TEXT = b"CANARY-DO-NOT-TOUCH\n" * 8

def _rmtree(path):
    """rmtree that survives mode-500 dirs / read-only trees (test fixtures
    leave observed/ at 0o500; a plain rmtree then dies on PermissionError)."""
    def _onerr(func, pth, exc):
        try: os.chmod(os.path.dirname(pth), 0o700)
        except OSError: pass
        try: os.chmod(pth, 0o700)
        except OSError: pass
        try: func(pth)
        except OSError: pass
    if os.path.lexists(path):
        shutil.rmtree(path, onerror=_onerr)

def build_home(home, variant=""):
    """Isolated HOME with a canary set the hook must never destroy."""
    obs = os.path.join(home, ".claude", "session-state", "observed")
    os.makedirs(obs, exist_ok=True)
    os.makedirs(os.path.join(home, "precious"), exist_ok=True)
    files = {
        os.path.join(obs, "0000000000000000-1.complete.json"): b'{"pre":"existing"}\n',
        os.path.join(obs, "0000000000000000-2.partial.json"):  b'{"pre":"partial"}\n',
        os.path.join(obs, "zzz-not-ours.txt"):                 CANARY_TEXT,
        os.path.join(home, "precious", "keep.txt"):            CANARY_TEXT,
        os.path.join(home, ".claude", "settings.json"):        b'{"hooks":{}}\n',
    }
    for p, b in files.items():
        with open(p, "wb") as f: f.write(b)
    os.chmod(os.path.join(home, "precious", "keep.txt"), 0o444)   # read-only canary
    ln = os.path.join(obs, "link-to-precious")
    if not os.path.lexists(ln):
        os.symlink(os.path.join(home, "precious", "keep.txt"), ln)
    if variant == "obs_is_file":
        _rmtree(obs); open(obs, "wb").write(b"i am a file, not a dir\n")
    if variant == "obs_unwritable":
        os.chmod(obs, 0o500)
    return home

# ------------------------------------------------------------------ case table
def cases():
    """(name, kind, argv_extra, stdin_bytes, env_overrides, home_variant, note)"""
    good = b'{"session_id":"abc","transcript_path":"/tmp/x.jsonl","hook_event_name":"PreCompact","trigger":"manual"}'
    C = []
    A = C.append
    # --- input shapes
    A(("A01_happy_manual",      "run", ["manual"],  good,        {}, "", "normal payload"))
    A(("A02_happy_auto",        "run", ["auto"],    good,        {}, "", "other matcher"))
    A(("A03_empty_stdin",       "run", ["manual"],  b"",         {}, "", "zero-byte stdin"))
    A(("A04_no_argv",           "run", [],          good,        {}, "", "no matcher argument"))
    A(("A05_many_argv",         "run", ["a"]*40,    good,        {}, "", "argv flood"))
    A(("A06_oversize",          "run", ["manual"],  b'{"k":"' + b"Z"*300000 + b'"}', {}, "", ">MAX_INPUT"))
    A(("A07_binary_stdin",      "run", ["manual"],  bytes(range(256))*64, {}, "", "invalid utf-8"))
    A(("A08_nul_bytes",         "run", ["manual"],  b'{"a":"b"}\x00\x00trailing', {}, "", "NUL in stream"))
    A(("A09_not_json",          "run", ["manual"],  b"<<<not json at all>>>", {}, "", "unparseable"))
    A(("A10_argv_metachars",    "run", ["$(touch /tmp/PWNED_ARGV);`id`;|;&"], good, {}, "", "shell metachars in matcher"))
    A(("A11_deep_json",         "run", ["manual"],  b"[" * 4000 + b"]" * 4000, {}, "", "recursion bait"))
    # --- environment hostility
    A(("B01_bash_env",          "run", ["manual"],  good, {"BASH_ENV": "@PAYLOAD@"}, "", "BASH_ENV code exec"))
    A(("B02_env_file",          "run", ["manual"],  good, {"ENV": "@PAYLOAD@"}, "", "ENV code exec"))
    A(("B03_shellopts_xtrace",  "run", ["manual"],  good, {"SHELLOPTS": "xtrace", "BASH_XTRACEFD": "1"}, "", "trace onto stdout"))
    A(("B04_ps4_payload",       "run", ["manual"],  good, {"PS4": "$(echo PWNED_PS4)"}, "", "PS4 command sub"))
    A(("B05_empty_path",        "run", ["manual"],  good, {"PATH": ""}, "", "no PATH"))
    A(("B06_path_hostile",      "run", ["manual"],  good, {"PATH": "@HOSTILE@"}, "", "DEAD CASE: hook hardcodes absolute interpreter paths, ignores PATH (hook.sh:627-628) -- kept only to prove PATH is irrelevant"))
    A(("B07_no_home",           "run", ["manual"],  good, {"HOME": None}, "", "HOME unset"))
    A(("B08_home_missing",      "run", ["manual"],  good, {"HOME": "/nonexistent/nope"}, "", "HOME points nowhere"))
    A(("B09_ifs_mangled",       "run", ["manual"],  good, {"IFS": "0123456789abcdef "}, "", "IFS poisoning"))
    A(("B10_locale_junk",       "run", ["manual"],  good, {"LC_ALL": "xx_YY.INVALID", "LANG": "xx_YY.INVALID"}, "", "bad locale"))
    A(("B11_cdpath_glob",       "run", ["manual"],  good, {"CDPATH": "/", "GLOBIGNORE": "*"}, "", "cd/glob poisoning"))
    A(("B12_pythonpath",        "run", ["manual"],  good, {"PYTHONPATH": "@PAYLOAD_DIR@", "PYTHONSTARTUP": "@PAYLOAD@"}, "", "python import hijack"))
    A(("B13_obs_is_file",       "run", ["manual"],  good, {}, "obs_is_file", "observed/ is a regular file"))
    A(("B14_obs_unwritable",    "run", ["manual"],  good, {}, "obs_unwritable", "observed/ mode 500"))
    A(("B15_tmpdir_missing",    "run", ["manual"],  good, {"TMPDIR": "/nonexistent/tmp"}, "", "bad TMPDIR"))
    # --- stdin liveness (C3 pressure)
    A(("C01_stdin_never_eof",   "hang_stdin", ["manual"], good, {}, "", "writer holds pipe open"))
    A(("C02_stdin_slow_drip",   "drip_stdin", ["manual"], good, {}, "", "1 byte/0.5s, never EOF"))
    A(("C03_stdin_from_dev_zero","zero_stdin", ["manual"], b"", {}, "", "infinite stdin"))
    # --- inherited file descriptors (harness previously stripped all fd>=3)
    A(("G01_inherited_fd_pipe", "fd_pipe",  ["manual"], good, {}, "", "open fd 3 pipe, reader held by harness"))
    A(("G02_inherited_fd_many", "fd_many",  ["manual"], good, {}, "", "fds 3..12 all open pipes"))
    # --- interpreter-path failures (only reachable by rewriting the candidate list)
    A(("H01_interp_hangs",      "interp",   ["manual"], good, {}, "hang",  "first interpreter candidate hangs forever"))
    A(("H02_interp_first_fail", "interp",   ["manual"], good, {"__V": "fail"}, "fail", "first candidate fails the exit-37 probe (second is the real python3, which works)"))
    A(("H03_interp_zero_byte",  "interp",   ["manual"], good, {"__V": "zero"}, "zero", "first candidate is a zero-byte file"))
    A(("H04_interp_stdout",     "interp",   ["manual"], good, {"__V": "noisy"}, "noisy", "candidate passes probe then floods stdout"))
    A(("H05_interp_every_fail", "interp",   ["manual"], good, {"__V": "allfail"}, "allfail", "sol 2026-09-01: EVERY candidate fails the probe -> _chosen empty -> watchdog skipped -> exit 0 (the no-interpreter path, previously untested)"))
    # --- signals, PID-directed
    for s in ["TERM", "INT", "HUP", "QUIT", "USR1", "USR2", "ALRM", "PIPE", "XCPU", "VTALRM", "PROF"]:
        A((f"D_pid_{s}", "sig_pid", ["manual"], good, {}, "", f"{s} to pid"))
    # --- signals, group-directed
    for s in ["TERM", "INT", "HUP", "USR1"]:
        A((f"E_grp_{s}", "sig_grp", ["manual"], good, {}, "", f"{s} to process group"))
    # --- stop signals (the round 19-22 class), both delivery shapes
    for s in ["TSTP", "TTIN", "TTOU"]:
        A((f"F_pid_{s}", "sig_pid", ["manual"], good, {}, "", f"{s} to pid (suspend class)"))
        A((f"F_grp_{s}", "sig_grp", ["manual"], good, {}, "", f"{s} to group (suspend class)"))
    return C

EXPECT = {"rc": 0, "stdout_bytes": 0, "within_ceiling": True, "destroyed": [],
          "orphans": 0}

# ------------------------------------------------------------------ execution
def write_payload(d):
    p = os.path.join(d, "payload.sh")
    with open(p, "w") as f:
        f.write("echo PWNED_BASH_ENV\nprintf 'PWNED_STDOUT'\n")
    os.chmod(p, 0o755)
    sp = os.path.join(d, "sitecustomize.py")
    with open(sp, "w") as f:
        f.write("import sys; sys.stdout.write('PWNED_PYTHONPATH')\n")
    hostile = os.path.join(d, "hostilebin")
    os.makedirs(hostile, exist_ok=True)
    stub = os.path.join(hostile, "python3")
    with open(stub, "w") as f:
        f.write("#!/bin/sh\nprintf 'PWNED_PYSTUB'\nexit 0\n")
    os.chmod(stub, 0o755)
    return p, d, hostile

def make_interp_variant(target, workdir, mode):
    """Rewrite the hook's hardcoded interpreter candidate list to point at stubs.
    The hook ignores $PATH (hook.sh:627-628), so this is the only way to reach
    its interpreter-failure paths at all."""
    bindir = os.path.join(workdir, "interp_" + mode)
    os.makedirs(bindir, exist_ok=True)
    stub = os.path.join(bindir, "python3")
    bodies = {
      "hang":  "#!/bin/sh\nwhile :; do :; done\n",
      "fail":  "#!/bin/sh\necho NOT1337\nexit 0\n",
      "zero":  "",
      "noisy": "#!/bin/sh\nfor a in \"$@\"; do :; done\nprintf 1337\nexit 37\n",
      # sol 2026-09-01: a fixture where EVERY candidate fails the exit-37 probe.
      # "fail"/"zero" leave the real /usr/bin/python3 as candidate 2, so they
      # never reach the no-interpreter path (empty _chosen -> watchdog skipped
      # -> exit 0). "allfail" drops that fallback (see new_block below).
      "allfail": "#!/bin/sh\necho NOT1337\nexit 0\n",
    }
    with open(stub, "w") as f: f.write(bodies[mode])
    os.chmod(stub, 0o755 if bodies[mode] else 0o755)
    src = open(target).read()
    # ROUND 27: match the candidate-list `for` regardless of indentation, so the
    # same harness drives v26 (probe nested in the worker, 2-space indent) and
    # v27 (probe hoisted to the parent, column-0 indent).
    m = re.search(r'^([ \t]*)for _p in /Library/Developer/CommandLineTools/usr/bin/python3 \\\n[ \t]*/usr/bin/python3; do',
                  src, re.M)
    if not m:   # grok 2026-09-02 F9: an explicit raise, not an assert (-O strips asserts)
        raise RuntimeError("interpreter candidate list anchor not found in %s" % target)
    indent = m.group(1)
    # The stub path goes into generated bash as ONE shell word. Unquoted, a workdir
    # containing a space word-split the candidate list into nonexistent fragments,
    # the loop fell through to the real /usr/bin/python3, and H01-H05 then measured
    # a healthy interpreter instead of the hang/fail fixture -- scoring ok, so the
    # run still printed "57/57 pass, 0 FAIL" with five cases silently not exercised.
    if "'" in stub:
        raise RuntimeError("stub path contains a single quote, cannot be safely "
                           "quoted into the generated candidate list: %s" % stub)
    q = "'%s'" % stub
    if mode == "allfail":
        # every candidate is the SAME failing stub -> the loop exhausts without a
        # working interpreter, exercising the empty-_chosen path. No real fallback.
        new_block = "%sfor _p in %s \\\n%s          %s; do" % (indent, q, indent, q)
    else:
        new_block = "%sfor _p in %s \\\n%s          /usr/bin/python3; do" % (indent, q, indent)
    src2 = src[:m.start()] + new_block + src[m.end():]
    out = os.path.join(workdir, "hook_interp_%s.sh" % mode)
    with open(out, "w") as f: f.write(src2)
    os.chmod(out, 0o755)
    return out

def _proc_state(pid):
    """Single-letter ps state for pid, or None if it cannot be read.
    'Z' means zombie: present enough for kill() to succeed, dead enough that no
    signal can affect it."""
    try:
        r = subprocess.run(["/bin/ps", "-o", "state=", "-p", str(pid)],
                           capture_output=True, text=True, timeout=5)
        s = r.stdout.strip()
        return s[0] if s else None
    except Exception:
        return None

class StdoutTap:
    """The hook's fd 1 is a PIPE the harness drains on its own thread, and C2 is
    graded on the bytes DRAINED -- a count the hook cannot shrink.

    Every instrument used to hand the hook a regular capture file and grade
    os.path.getsize() point-samples of it. The hook holds that file as fd 1, so
    `ftruncate(1, 0)` before exit made every sample read 0: mutant M20 writes 5
    bytes to stdout, truncates, and graded CLEAN in contract, grpsig2 and gap
    (measured 2026-09-06). Sampling twice (at exit and after the settle) closed
    only the settle-window case, not this one. The drained bytes are also teed
    to `path` -- opened by the harness, never handed to the hook -- for the
    stdout sample and post-mortem. A pipe is also what Claude Code itself gives
    a hook's fd 1, so this is the more faithful stdout, not a less faithful one.

    Use: tap = StdoutTap(path); Popen(stdout=tap.w, ...); tap.attach() right
    after Popen (closes the parent's write end -- or EOF never arrives -- and
    starts the drain thread). count() at the sample points; error at grading.

    Threads and fork: preexec_fn runs Python in the child, and a fork taken while
    another thread may hold an allocator or I/O lock can deadlock that child
    (agy 2026-09-06, CONFIRMED by reading: the previous case's thread outlives
    its case whenever a leaked descendant still holds that pipe). So every
    construction first quiesce()s all live taps -- stop flag + join -- and the
    thread is started only after the Popen it serves: at fork time no drain
    thread exists. A quiesced tap belongs to a case that has already graded."""
    CHUNK = 65536
    _LIVE = set()

    def __init__(self, path):
        if not StdoutTap.quiesce():   # single-threaded at the next fork (see above)
            raise RuntimeError("StdoutTap: a previous drain thread would not stop; refusing to fork")
        self.path = path
        self.n = 0                    # bytes drained; only ever grows
        self.eof = False
        self.stop = False
        self.error = None             # graded: a tap that lost bytes is never "0B"
        self.r, self.w = os.pipe()
        self._f = open(path, "wb")
        self._lk = threading.Lock()   # held around read+count so count() is exact
        self._t = None

    @classmethod
    def quiesce(cls, timeout=1.0):
        """Stop and join every live drain thread (bounded). Returns True when none
        is left. A thread is still alive here only if a descendant of an ALREADY
        GRADED case holds its pipe -- its count was taken; nothing is lost that
        the harness would still grade."""
        for t in list(cls._LIVE):
            t.stop = True
        deadline = time.monotonic() + timeout
        for t in list(cls._LIVE):
            th = t._t
            if th is not None:
                th.join(max(0.0, deadline - time.monotonic()))
        return not cls._LIVE

    def attach(self):
        if self.w is not None:
            try: os.close(self.w)
            except OSError: pass
            self.w = None
        if self._t is None:
            StdoutTap._LIVE.add(self)
            self._t = threading.Thread(target=self._drain, name="stdout-tap", daemon=True)
            self._t.start()

    def _drain(self):
        try:
            while not self.stop:
                rr, _, _ = select.select([self.r], [], [], 0.05)
                if not rr:
                    continue
                with self._lk:
                    b = os.read(self.r, self.CHUNK)
                    if not b:
                        break
                    self.n += len(b)          # counted BEFORE the tee, so a tee
                try:                          # failure never hides bytes
                    self._f.write(b); self._f.flush()
                except (OSError, ValueError) as e:
                    self.error = self.error or ("tee:" + e.__class__.__name__)
        except Exception as e:                # ANY thread death: the count is a floor, graded
            self.error = "read:" + e.__class__.__name__
        finally:
            self.eof = True
            try: os.close(self.r)
            except OSError: pass
            try: self._f.close()
            except OSError: pass
            StdoutTap._LIVE.discard(self)

    def count(self, wait=2.0):
        """Bytes drained. Exact, not a heuristic: while data is still readable in
        the pipe, wait (bounded) for the thread to take it; then take the lock, so
        a read in flight has finished counting before we return. Exact at EOF; a
        floor while a descendant is still writing (then it is >0 -- a violation
        either way). The old join(0.05) could return before bytes already in the
        pipe were counted (agy 2026-09-06)."""
        deadline = time.monotonic() + wait
        while not self.eof and time.monotonic() < deadline:
            try:
                rr, _, _ = select.select([self.r], [], [], 0)
            except (OSError, ValueError):
                break                         # r closed under us: thread is at EOF
            if not rr:
                break
            time.sleep(0.005)
        with self._lk:
            return self.n

    def finalize(self, timeout=1.0):
        """Call AFTER every attributed descendant has been killed. Waits (bounded)
        for clean EOF -- every write end closed -- and returns True on EOF. False
        means some process the survivor clauses did NOT find still holds the hook's
        fd 1 (a chdir-away daemon, an other-cwd spawn): graders treat that as a
        failure in its own right, never as "0 bytes". Also stops the thread, so
        the next case forks single-threaded regardless. (codex sol 2026-09-06
        TAP-FINALIZE, CONFIRMED by reading: a settle is a wait, not completeness.)"""
        deadline = time.monotonic() + timeout
        while not self.eof and time.monotonic() < deadline:
            time.sleep(0.01)
        eof = self.eof
        self.stop = True
        if self._t is not None:
            self._t.join(0.5)
        return eof

    def sample(self, n=200):
        try:
            with open(self.path, "rb") as f:
                return f.read(n)
        except OSError:
            return b""


def run_case(target, case, workdir):
    name, kind, argv, stdin_b, envov, variant, note = case
    home = os.path.join(workdir, "h_" + name)
    _rmtree(home)
    os.makedirs(home)
    build_home(home, variant)
    payload, payload_dir, hostile = write_payload(workdir)

    env = {"HOME": home, "PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "SHELL": "/bin/zsh",
           "LANG": "en_US.UTF-8", "TERM": "dumb"}
    for k, v in envov.items():
        if v is None:
            env.pop(k, None); continue
        v = (v.replace("@PAYLOAD@", payload)
              .replace("@PAYLOAD_DIR@", payload_dir)
              .replace("@HOSTILE@", hostile + ":/usr/bin:/bin"))
        env[k] = v

    if kind == "interp":
        target = make_interp_variant(target, workdir, variant)
    snap_root = home
    before = snapshot(snap_root)
    # sol 2026-09-01 (CONFIRMED): the target runs with cwd=workdir (Popen below)
    # while ONLY $HOME was snapshotted -- so destruction anywhere else, including
    # this harness's own EXPECTED-*.json sitting in that cwd, graded destroyed=[].
    # Plant canaries in the cwd and grade them too. Arbitrary absolute paths stay
    # out of reach without OS-level fs isolation; that limit is stated in README.
    ext_root = os.path.join(workdir, "canary_ext")
    _rmtree(ext_root)
    os.makedirs(os.path.join(ext_root, "subdir"))
    for nm, mode in (("plain.txt", 0o644), ("readonly.txt", 0o444), ("exec.sh", 0o755),
                     (os.path.join("subdir", "nested.txt"), 0o644)):
        fp = os.path.join(ext_root, nm)
        with open(fp, "w") as f: f.write("canary %s\n" % nm)
        os.chmod(fp, mode)
    before_ext = snapshot(ext_root)
    _expf = os.path.join(workdir, "EXPECTED-%s.json" % os.environ.get("CONTRACT_LABEL", ""))
    _exp_before = md5(_expf) if os.path.exists(_expf) else None

    outf = os.path.join(workdir, f"o_{name}.out")
    errf = os.path.join(workdir, f"o_{name}.err")
    # codex 2026-09-01 F1 (CONFIRMED by reading): only the planted canaries and
    # EXPECTED-*.json were graded, so a hook deleting/replacing any REAL cwd file
    # (payload.sh, a prior case's capture) scored destroyed=[]. Snapshot the
    # cwd's own top-level entries too; this case's capture files are excluded
    # because the harness itself truncates them just below.
    before_cwd = cwd_snapshot(workdir, home, ext_root, outf, errf)
    tap, fe = StdoutTap(outf), open(errf, "wb")

    hold_open = kind in ("sig_pid", "sig_grp")   # keep target alive until the signal lands
    fd_keep, fd_readers, fd_writers = [], [], []
    if kind in ("fd_pipe", "fd_many"):
        n = 1 if kind == "fd_pipe" else 10
        for _ in range(n):
            r, w = os.pipe()
            fd_keep += [r, w]; fd_readers.append(r); fd_writers.append(w)

    def _preexec(ws=tuple(fd_writers)):
        os.setpgid(0, 0)                          # own group, NOT orphaned
        # grok 2026-09-02 F4 (CONFIRMED by reading): pass_fds handed the pipes over
        # at whatever numbers the parent held them, so "fd 3" / "fds 3..12" in the
        # case labels was never true in the child. Land the WRITE ends on exactly
        # 3..3+n-1 (via temps so a source at a target number is not clobbered),
        # then close everything else; the harness keeps the read ends and checks
        # them for EOF after the run (a held write end = a leaked descendant).
        if ws:
            # sol 2026-09-02 F8 (CONFIRMED: launchctl maxfiles soft=256 on this Mac,
            # so a Terminal-launched run has fds <256 only): temps sit just above
            # every source and target instead of at a fixed high number.
            base = max(max(ws), 3 + len(ws)) + 1
            for i, w in enumerate(ws): os.dup2(w, base + i)
            for i in range(len(ws)): os.dup2(base + i, 3 + i); os.close(base + i)
            os.closerange(3 + len(ws), 4096)
    if kind == "zero_stdin":
        fin = open("/dev/zero", "rb"); stdin_arg = fin; pipe = None
    elif kind in ("hang_stdin", "drip_stdin") or hold_open:
        rfd, wfd = os.pipe(); stdin_arg = rfd; pipe = wfd; fin = None
    else:
        stdin_arg = subprocess.PIPE; pipe = None; fin = None

    _cwd_pre = cwd_pids(workdir)     # pre-spawn baseline for the cwd survivor clause
    t0 = time.time()
    p = subprocess.Popen(INVOC + [target] + argv, stdin=stdin_arg, stdout=tap.w, stderr=fe,
                         env=env, cwd=workdir,
                         close_fds=not fd_writers,   # fd cases close their own in _preexec
                         preexec_fn=_preexec)
    tap.attach()                  # our write end closed, drain thread started (post-fork)
    for w in fd_writers:          # the child holds its copies; ours would defeat the EOF check
        os.close(w); fd_keep.remove(w)
    # Feed stdin NON-BLOCKING, from inside the deadline loop. One blocking
    # p.stdin.write of the whole payload used to sit here, BEFORE the loop, against
    # a 64KB pipe buffer -- so a hook that stopped draining stdin while alive held
    # the grader for as long as it lived and C3 was never enforced: A06_oversize on
    # mutant M19 (sleep 40 before the read) measured 40.13s against the 12.0s
    # ceiling, and a never-exiting variant hung the grader with no verdict at all
    # (2026-09-05/06). Now the pump runs one non-blocking burst per tick and the
    # deadline below owns the entire wait.
    stdin_mv = memoryview(stdin_b); stdin_off = 0
    stdin_err = None              # graded: a feed the harness could not complete is not "fed"
    if p.stdin is not None:
        try:
            os.set_blocking(p.stdin.fileno(), False)
        except OSError as e:
            # codex sol 2026-09-06 STDBLOCK-FALLTHROUGH (CONFIRMED by reading): the
            # error was recorded but p.stdin stayed set, so the pump below would
            # os.write A06's 300KB on a BLOCKING fd -- the M19 hang, back. Fail
            # closed: close it so the pump never writes; stdin_feed_error is graded.
            stdin_err = "set_blocking:" + e.__class__.__name__
            try: p.stdin.close()
            except OSError: pass
            p.stdin = None
    def _pump_stdin():
        nonlocal stdin_off, stdin_err
        if p.stdin is None:
            return
        try:
            while stdin_off < len(stdin_mv):
                stdin_off += os.write(p.stdin.fileno(), stdin_mv[stdin_off:stdin_off + 65536])
        except (BlockingIOError, InterruptedError):
            return                # pipe full (hook not draining) or EINTR: retry next tick
        except BrokenPipeError:
            pass                  # EPIPE: the hook closed its end -- the one normal early stop
        except OSError as e:      # anything else is a HARNESS fault, not a hook behaviour
            stdin_err = stdin_err or ("write:%s@%d/%d" % (e.__class__.__name__, stdin_off, len(stdin_mv)))
        try: p.stdin.close()      # all fed (or unfeedable): EOF for the hook
        except OSError as e:
            stdin_err = stdin_err or ("close:" + e.__class__.__name__)
        p.stdin = None
    # codex sol 2026-09-06 GRADER-BOUND (CONFIRMED by reading): the stall clock used
    # to start at run_case entry and stop after the final count, so it also charged
    # build_home, snapshots and three ps/lsof calls (10s timeouts each) -- a slow
    # but successful lsof could push a conforming case over the bound. Time ONLY
    # the segment the oracle is about: first stdin pump through the bounded reap.
    _case_t0 = time.monotonic()
    _pump_stdin()
    if kind in ("hang_stdin", "drip_stdin") or hold_open:
        os.close(rfd)
        try:
            os.write(pipe, stdin_b[:20] if kind != "drip_stdin" else b"{")
        except OSError:
            pass

    stopped = False; sig_sent = None; alive_at_signal = None
    deadline = t0 + WALL_CEIL
    delivered = False
    while True:
        try:
            wpid, status = os.waitpid(p.pid, os.WNOHANG | os.WUNTRACED)
        except ChildProcessError:
            # child vanished without this loop observing its exit -- never
            # a pass, the exit status is simply unknown
            status = "VANISHED"; wpid = p.pid; break
        if wpid == p.pid:
            if os.WIFSTOPPED(status):
                stopped = True
                try: os.killpg(p.pid, signal.SIGCONT)
                except OSError: pass
                try: os.killpg(p.pid, signal.SIGKILL)
                except OSError: pass
                break
            break
        now = time.time()
        if not delivered and kind in ("sig_pid", "sig_grp") and now - t0 >= SIGDELAY:
            signame = name.split("_")[-1]
            sig_sent = getattr(signal, "SIG" + signame)
            try:
                os.kill(p.pid, 0)          # liveness probe BEFORE delivery
                # sol 2026-09-01 (CONFIRMED by execution): kill(pid,0) AND
                # kill(pid,TERM) both succeed against a ZOMBIE, which then reaps
                # as exit 0 -> a signal case PASSes without ever reaching a live
                # target. os.waitid(WNOWAIT) is the textbook fix but does not
                # exist on macOS CPython, so state comes from ps.
                _st = _proc_state(p.pid)
                if _st == "Z":
                    alive_at_signal = "ZOMBIE"
                elif _st is None:
                    # grok 2026-09-02 F1 (CONFIRMED by reading): no ps reading was
                    # graded as "live". Unobserved is not alive -> VOID.
                    alive_at_signal = "STATE-UNREADABLE"
                else:
                    alive_at_signal = True
            except OSError:
                alive_at_signal = False
            try:
                if kind == "sig_pid": os.kill(p.pid, sig_sent)
                else: os.killpg(p.pid, sig_sent)
            except OSError as e:
                alive_at_signal = "KILL-" + e.__class__.__name__   # grok F1: never a pass
            delivered = True
            if pipe is not None:
                try: os.close(pipe); pipe = None
                except OSError: pass
        if kind == "drip_stdin" and pipe is not None and now - t0 < 8:
            try: os.write(pipe, b" ")
            except OSError: pass
        _pump_stdin()
        if now > deadline:
            try: os.killpg(p.pid, signal.SIGKILL)
            except OSError: pass
            # A hook that moved ITSELF out of the group makes the killpg above a
            # no-op on the parent, and the blocking waitpid that used to sit here
            # then hung the grader forever instead of reporting a timeout. Kill
            # the pid directly as well, and reap with a bounded WNOHANG poll.
            try: os.kill(p.pid, signal.SIGKILL)
            except OSError: pass
            # monotonic, not time(): a wall-clock step backwards would stretch
            # this "5 second" bound arbitrarily, which is the hang it replaced.
            _reap_deadline = time.monotonic() + 5
            while time.monotonic() < _reap_deadline:
                try:
                    if os.waitpid(p.pid, os.WNOHANG)[0] == p.pid: break
                except ChildProcessError: break
                time.sleep(0.02)
            status = None
            break
        time.sleep(0.02)
    # C3 is graded on the HOOK's wall time. Everything below (ps, lsof, fd drain)
    # is harness overhead; charging it to the hook pushed a conforming hook that
    # finishes just under the ceiling over it by the ~0.15s lsof call.
    t_done = time.time()
    grader_wall = time.monotonic() - _case_t0   # pump..reap only; graded vs GRADER_STALL
    # count survivors in the target's process group BEFORE we clean up
    orphans = 0
    fd_held = []
    try:
        # -E appends each process's environment to its command field (same-uid
        # processes only, which is all the hook can spawn).
        _psr = subprocess.run(["/bin/ps", "-axwwEo", "pid=,pgid=,state=,command="],
                              capture_output=True, text=True, timeout=10)
        if _psr.returncode != 0 or not _psr.stdout.strip():
            # sol 2026-09-02 F7 (CONFIRMED: ps exits 1 with empty stdout on error):
            # an empty listing is not an empty process table -> orphans=-1 below
            raise RuntimeError("ps failed rc=%d" % _psr.returncode)
        ps = _psr.stdout
        seen = set()
        for ln in ps.splitlines():
            f = ln.split(None, 3)
            if len(f) >= 3 and f[1].isdigit() and int(f[1]) == p.pid \
               and int(f[0]) != p.pid and not f[2].startswith("Z"):
                orphans += 1; seen.add(int(f[0]))
        # sol 2026-09-01 F4: a candidate that moves its worker to another pgid
        # (v24's set -m) makes the pgid scan blind. Belt: any non-zombie whose
        # command references THIS case's workdir stubs is a survivor too.
        for ln in ps.splitlines():
            f = ln.split(None, 3)
            if len(f) == 4 and f[0].isdigit() and int(f[0]) not in seen \
               and int(f[0]) != p.pid and not f[2].startswith("Z") \
               and (workdir + "/interp_") in f[3]:
                orphans += 1; seen.add(int(f[0]))
        # grok 2026-09-02 F2+F3 (CONFIRMED by mutant M17): a descendant that left
        # the group (setsid / double fork / set -m) and is not a stub was invisible
        # to both clauses above, and could still write to the inherited stdout
        # after SETTLE (M17 leaked 4 bytes after the case graded 0). This case's
        # HOME is unique, and every descendant inherits it unless the hook
        # scrubs its environment -- so any live process carrying it is ours.
        _homemark = " HOME=" + home + " "
        for ln in ps.splitlines():
            f = ln.split(None, 3)
            if len(f) == 4 and f[0].isdigit() and int(f[0]) not in seen \
               and int(f[0]) != p.pid and not f[2].startswith("Z") \
               and _homemark in (" " + f[3] + " "):
                orphans += 1; seen.add(int(f[0]))
        # 2026-09-05 (CONFIRMED by mutant M18): the HOME= clause above is INERT
        # for a descendant that is, or execs, a macOS platform binary -- ps -E
        # emits no environment for /bin/sleep, /bin/sh, /bin/bash -- so a
        # setsid'd /bin/sleep scored orph=0 while alive with ppid 1. Attribute by
        # cwd instead (see cwd_pids): survives execve, unique to this run.
        _cwd_now = cwd_pids(workdir)
        if _cwd_now is None or _cwd_pre is None:
            raise RuntimeError("lsof unusable: cwd survivor scan unknown")
        for cpid in sorted(_cwd_now - _cwd_pre):
            if cpid not in seen and cpid != p.pid:
                orphans += 1; seen.add(cpid)
        # grok F4 follow-through: a write end still held after the hook exited
        # means some descendant (found or not) kept the inherited fd.
        for i, r in enumerate(fd_readers):
            # sol 2026-09-02 F1 (CONFIRMED by probe): a single read returned a byte
            # some descendant had written and the fd was scored clean while still
            # held. Drain: clean only on EOF (b""), held on EAGAIN, unknown on error.
            try:
                os.set_blocking(r, False)
                while os.read(r, 65536):
                    pass
            except BlockingIOError:
                fd_held.append(3 + i)
            except OSError as e:
                fd_held.append("%d?%s" % (3 + i, e.__class__.__name__))
        for spid in seen:
            try: os.kill(spid, 9)
            except OSError: pass
    except Exception:
        orphans = -1          # unknown, never silently 0
    if orphans:
        try: os.killpg(p.pid, signal.SIGKILL)
        except OSError: pass
    elapsed = t_done - t0
    if pipe is not None:
        try: os.close(pipe)
        except OSError: pass
    if p.stdin is not None:       # payload never fully fed (hook died or stalled)
        try: p.stdin.close()
        except OSError: pass
        p.stdin = None
    for _fd in fd_keep:
        try: os.close(_fd)
        except OSError: pass
    if fin: fin.close()
    fe.close()

    if status == "VANISHED":
        rc = "VANISHED"
    elif status is None:
        rc = "TIMEOUT"
    elif stopped:
        rc = "STOPPED"
    elif os.WIFSIGNALED(status):
        rc = -os.WTERMSIG(status)
    else:
        rc = os.WEXITSTATUS(status)

    # Reopen the observed dir far enough to snapshot it, but restore EXACTLY the
    # mode the "before" snapshot recorded -- a hardcoded 0o755 here is the
    # harness mutating the tree and then reporting its own chmod as a C4
    # violation (B13/B14 did exactly that once mode comparison was added).
    _obs = os.path.join(home, ".claude", "session-state", "observed")
    _rel = os.path.relpath(_obs, home)
    _orig = before.get(_rel, {}).get("mode")
    try:                                  # the REAL post-run mode, read before we touch it
        _true_mode = stat.S_IMODE(os.lstat(_obs).st_mode)
    except OSError:
        _true_mode = None
    try:
        if os.path.isdir(_obs):
            os.chmod(_obs, 0o755)
            after = snapshot(snap_root)
            if _orig is not None:
                os.chmod(_obs, _orig)
        else:
            after = snapshot(snap_root)
    except OSError:
        after = snapshot(snap_root)
    if _rel in after and _true_mode is not None:
        after[_rel]["mode"] = _true_mode   # the hook's mode, not the harness's reopen
    _skip_after = True
    destroyed = diff_snapshots(before, after)
    destroyed += ["CWD/" + x for x in diff_snapshots(before_ext, snapshot(ext_root))]
    destroyed += ["CWDFILE/" + x for x in
                  diff_snapshots(before_cwd, cwd_snapshot(workdir, home, ext_root, outf, errf))]
    if _exp_before is not None:
        _now = md5(_expf) if os.path.exists(_expf) else None
        if _now != _exp_before:
            destroyed.append("FROZEN-EXPECTATIONS-TOUCHED %s -> %s" % (_exp_before, _now))

    so_at_exit = tap.count()           # drained bytes, not a file size the hook can shrink
    time.sleep(SETTLE)                 # a late writer on the inherited fd 1
    # Every attributed survivor is dead by now, so fd 1 must reach EOF: a pipe still
    # held means a process no clause found -- graded as its own failure below.
    so_eof = tap.finalize(1.0)
    so = tap.count(); se = os.path.getsize(errf)
    late = so - so_at_exit
    sample = tap.sample(200)
    return {"name": name, "note": note, "rc": rc, "stdout_bytes": so, "stderr_bytes": se,
            "stdout_sample": repr(sample), "elapsed": round(elapsed, 3),
            "within_ceiling": elapsed < WALL_CEIL - 0.5 and rc not in ("TIMEOUT", "VANISHED"),
            "kind": kind, "alive_at_signal": alive_at_signal, "orphans": orphans,
            "stdout_at_exit": so_at_exit, "stdout_late_bytes": late,
            "stdout_tap_error": tap.error, "stdout_eof": so_eof,
            "stdin_feed_error": stdin_err, "stdin_fed": stdin_off,
            "grader_wall": round(grader_wall, 3),
            "fd_held": fd_held, "destroyed": destroyed}

def grade(exp, act):
    f = []
    if act["rc"] != exp["rc"]:                        f.append(f"C1 rc={act['rc']} want 0")
    if act["stdout_bytes"] != exp["stdout_bytes"]:    f.append(f"C2 stdout={act['stdout_bytes']}B {act['stdout_sample']}")
    # A drain thread that died or could not tee has an UNKNOWN count: never "0B".
    if act.get("stdout_tap_error"):                   f.append(f"C2 stdout tap error {act['stdout_tap_error']}")
    # fd 1 still open after every found survivor was killed = an unfound holder.
    if act.get("stdout_eof") is False:                f.append("C3 stdout pipe still held after sweep (unattributed descendant)")
    # The harness could not deliver the case's stdin: the case did not run as specified.
    if act.get("stdin_feed_error"):                   f.append(f"HARNESS stdin feed {act['stdin_feed_error']}")
    # The GRADER's own wall time: a stall here (blocking stdin write, M19 before the
    # non-blocking pump) is a harness defect that no hook-side grade would show.
    if act.get("grader_wall", 0) > GRADER_STALL:      f.append(f"HARNESS grader stalled {act['grader_wall']}s > {GRADER_STALL}s")
    if act["within_ceiling"] != exp["within_ceiling"]:f.append(f"C3 elapsed={act['elapsed']}s rc={act['rc']}")
    if act["destroyed"] != exp["destroyed"]:          f.append("C4 " + "; ".join(act["destroyed"][:4]))
    if act.get("orphans", 0) != exp.get("orphans", 0):
        f.append(f"C3 {act.get('orphans')} process(es) abandoned in the target process group")
    if act.get("fd_held"):
        f.append(f"C3 inherited fd(s) {act['fd_held']} still held after exit")
    if act.get("kind") in ("sig_pid", "sig_grp") and act.get("alive_at_signal") is not True:
        f.append(f"VOID signal never landed on a live target (alive={act.get('alive_at_signal')})")
    return f

def main():
    target = os.path.abspath(sys.argv[1]); label = sys.argv[2]
    os.environ["CONTRACT_LABEL"] = label   # read by run_case for the frozen-expectations check
    workdir = os.path.abspath(sys.argv[3])
    only = sys.argv[4] if len(sys.argv) > 4 else None
    os.makedirs(workdir, exist_ok=True)
    require_exclusive_workdir(workdir, "contract")
    cs = [c for c in cases() if (only is None or only in c[0])]
    # A filter that matches nothing used to run zero cases and print "0/0 pass,
    # 0 FAIL  md5=..." with exit 0 -- a typo'd 4th argument was indistinguishable
    # from a clean sweep, md5 line and all. An empty case set is a usage error.
    if not cs:
        print("FAIL: case filter %r matched none of the %d cases; nothing was run"
              % (only, len(cases())))
        sys.exit(2)
    # R0: freeze EXPECTED to disk BEFORE the first subprocess runs
    expf = os.path.join(workdir, f"EXPECTED-{label}.json")
    with open(expf, "w") as f:
        json.dump({c[0]: EXPECT for c in cs}, f, indent=1)
    frozen = json.load(open(expf))

    # Output budget: the caller is usually an LLM session reading stdout. Default
    # prints FAIL rows and one summary line; the full per-case table always goes
    # to TABLE-<label>.txt, and CONTRACT_VERBOSE=1 echoes it to stdout too.
    verbose = os.environ.get("CONTRACT_VERBOSE", "") not in ("", "0")
    tablef = os.path.join(workdir, f"TABLE-{label}.txt")
    results, fails = [], 0
    with open(tablef, "w") as tf:
        for c in cs:
            r = run_case(target, c, workdir)
            r["fails"] = grade(frozen[c[0]], r)
            if r["fails"]: fails += 1
            results.append(r)
            row = (f"{'FAIL' if r['fails'] else 'ok  '} {r['name']:<24} rc={str(r['rc']):>7} "
                   f"out={r['stdout_bytes']:<6} orph={r.get('orphans',0):<3} {r['elapsed']:>6.2f}s  {'; '.join(r['fails'])}")
            tf.write(row + "\n"); tf.flush()
            if verbose or r["fails"]:
                print(row, flush=True)
    with open(os.path.join(workdir, f"RESULT-{label}.json"), "w") as f:
        json.dump({"target": target, "md5": md5(target), "label": label,
                   "cases": len(cs), "fails": fails, "results": results}, f, indent=1)
    print(f"[{label}] {len(cs)-fails}/{len(cs)} pass, {fails} FAIL   md5={md5(target)}   table={tablef}")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":   # so the module can be imported for unit checks
    main()
