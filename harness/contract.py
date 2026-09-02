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
import hashlib, json, os, shutil, signal, stat, subprocess, sys, time
import re

WALL_CEIL = 12.0          # C3 ceiling, seconds
SIGDELAY  = 0.35          # when to deliver a signal after spawn
SETTLE    = 1.5           # how long to keep watching stdout AFTER the parent exits
INVOC     = ["/bin/bash", "--noprofile", "--norc", "-p"]   # the installed form

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
    if mode == "allfail":
        # every candidate is the SAME failing stub -> the loop exhausts without a
        # working interpreter, exercising the empty-_chosen path. No real fallback.
        new_block = "%sfor _p in %s \\\n%s          %s; do" % (indent, stub, indent, stub)
    else:
        new_block = "%sfor _p in %s \\\n%s          /usr/bin/python3; do" % (indent, stub, indent)
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
    fo, fe = open(outf, "wb"), open(errf, "wb")

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

    t0 = time.time()
    p = subprocess.Popen(INVOC + [target] + argv, stdin=stdin_arg, stdout=fo, stderr=fe,
                         env=env, cwd=workdir,
                         close_fds=not fd_writers,   # fd cases close their own in _preexec
                         preexec_fn=_preexec)
    for w in fd_writers:          # the child holds its copies; ours would defeat the EOF check
        os.close(w); fd_keep.remove(w)
    if stdin_arg == subprocess.PIPE:
        try:
            p.stdin.write(stdin_b); p.stdin.close()
        except (BrokenPipeError, OSError):
            pass
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
        if now > deadline:
            try: os.killpg(p.pid, signal.SIGKILL)
            except OSError: pass
            try: os.waitpid(p.pid, 0)
            except ChildProcessError: pass
            status = None
            break
        time.sleep(0.02)
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
    elapsed = time.time() - t0
    if pipe is not None:
        try: os.close(pipe)
        except OSError: pass
    for _fd in fd_keep:
        try: os.close(_fd)
        except OSError: pass
    if fin: fin.close()
    fo.close(); fe.close()

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

    so_at_exit = os.path.getsize(outf)
    time.sleep(SETTLE)                 # a late writer on the inherited fd 1
    so = os.path.getsize(outf); se = os.path.getsize(errf)
    late = so - so_at_exit
    sample = open(outf, "rb").read(200)
    return {"name": name, "note": note, "rc": rc, "stdout_bytes": so, "stderr_bytes": se,
            "stdout_sample": repr(sample), "elapsed": round(elapsed, 3),
            "within_ceiling": elapsed < WALL_CEIL - 0.5 and rc not in ("TIMEOUT", "VANISHED"),
            "kind": kind, "alive_at_signal": alive_at_signal, "orphans": orphans,
            "stdout_at_exit": so_at_exit, "stdout_late_bytes": late,
            "fd_held": fd_held, "destroyed": destroyed}

def grade(exp, act):
    f = []
    if act["rc"] != exp["rc"]:                        f.append(f"C1 rc={act['rc']} want 0")
    if act["stdout_bytes"] != exp["stdout_bytes"]:    f.append(f"C2 stdout={act['stdout_bytes']}B {act['stdout_sample']}")
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
    cs = [c for c in cases() if (only is None or only in c[0])]
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
