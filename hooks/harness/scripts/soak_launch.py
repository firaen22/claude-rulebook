#!/usr/bin/env python3
"""soak_launch.py <hook.sh> [N] [workdir] -- N launches in contract.py's sig_pid
LAUNCH shape (not its stdin/signal shape): own pgid, isolated $HOME with observed/
pre-created, stdin on a pipe held open 0.35s then closed, argv ["manual"],
/bin/bash --noprofile --norc -p, stdout tapped to a file. No signal is delivered.
It asks how often the hook takes a pre-worker exit-0 path and what breadcrumb it
left. A launch is CLEAN only if: rc 0, exactly one *.complete.json that parses
with saw_eof true and truncated false, no .dropped/.error/.partial file, zero
stdout bytes, and no process left in the hook's pgid. Anything else is an ANOMALY
and its HOME is kept as evidence. Exit status: 1 if any anomaly, 2 on usage.
KNOWN LIMITS (cross-model review 2026-09-06, recorded not fixed): the survivor
check is killpg(pgid,0) on the hook's own group, so a descendant that setsid()s
away is invisible (contract.py's lsof-cwd sweep would see it; v29/v28 never
change pgid). Re-running into a workdir that still holds kept anomaly HOMEs
raises FileExistsError (exit 1, fail-loud) — use a fresh workdir. Requires a
healthy LOCAL $TMPDIR."""
import json, os, shutil, subprocess, sys, time

INVOC = ["/bin/bash", "--noprofile", "--norc", "-p"]
HOLD = 0.35
STDIN_B = b'{"hook_event_name":"PreCompact","session_id":"soak","cwd":"/tmp"}'

MAX_EVIDENCE = 1 << 20   # a hook record is a few KB; anything bigger is itself an anomaly

def read_small(path):
    """Read a REGULAR file of bounded size without following symlinks or blocking on
    a FIFO. None = not a small regular file (caller grades that as an anomaly)."""
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    except OSError:
        return None
    try:
        import stat
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_size > MAX_EVIDENCE: return None
        return os.read(fd, MAX_EVIDENCE).decode("utf-8", "replace").strip()
    except OSError:
        return None
    finally:
        os.close(fd)

def survivors(pgid):
    try: os.killpg(pgid, 0); return True
    except ProcessLookupError: return False
    except PermissionError: return True

def one(hook, work, i):
    home = os.path.join(work, "h%06d" % i)
    obs = os.path.join(home, ".claude", "session-state", "observed")
    os.makedirs(obs)
    env = {"HOME": home, "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
           "SHELL": "/bin/zsh", "LANG": "en_US.UTF-8", "TERM": "dumb"}
    outf = os.path.join(home, "stdout.bin")
    rfd, wfd = os.pipe()
    why = []
    with open(outf, "wb") as fo, open(os.devnull, "wb") as fe:
        t0 = time.monotonic()
        p = subprocess.Popen(INVOC + [hook, "manual"], stdin=rfd, stdout=fo,
                             stderr=fe, env=env, cwd=work, close_fds=True,
                             preexec_fn=lambda: os.setpgid(0, 0))
        os.close(rfd)
        try:
            try: os.write(wfd, STDIN_B)
            except OSError: pass
            early = False
            while time.monotonic() - t0 < HOLD:
                if p.poll() is not None:
                    early = True; break
                time.sleep(0.01)
        finally:
            try: os.close(wfd)
            except OSError: pass
        try:
            rc = p.wait(timeout=12)
        except subprocess.TimeoutExpired:
            try: os.killpg(p.pid, 9)
            except OSError: pass
            rc = p.wait(); why.append("TIMEOUT-killed")
        elapsed = time.monotonic() - t0
    time.sleep(0.05)                       # let a just-exited worker reap
    if survivors(p.pid):
        why.append("pgid-survivor")
        try: os.killpg(p.pid, 9)
        except OSError: pass
    names = sorted(n for n in os.listdir(obs))
    drops = []
    for n in names:
        if n.endswith(".dropped.txt"):
            body = read_small(os.path.join(obs, n))
            if body is None: why.append("dropped-file-not-regular %s" % n)
            drops.append((n, body if body is not None else "<unreadable>"))
    complete = [n for n in names if n.endswith(".complete.json")]
    if rc != 0: why.append("rc=%s" % rc)
    if early: why.append("exit-before-hold")
    if drops: why.append("dropped")
    if len(complete) != 1 or len(names) != 1:
        why.append("files=%s" % names)
    else:
        body = read_small(os.path.join(obs, complete[0]))
        if body is None:
            why.append("record not a small regular file")
        else:
            UNPARSED = object()          # JSON `null` decodes to None, so None cannot be the sentinel
            try: rec = json.loads(body)
            except ValueError as e: rec = UNPARSED; why.append("record unreadable %s" % e)
            if rec is not UNPARSED:
                if not isinstance(rec, dict):
                    why.append("record not an object: %s" % type(rec).__name__)
                elif (rec.get("saw_eof") is not True or rec.get("truncated") is not False
                      or rec.get("raw") != STDIN_B.decode("utf-8")
                      or rec.get("registered_matcher") != "manual"):
                    why.append("record saw_eof=%r truncated=%r raw_ok=%r matcher=%r" % (
                        rec.get("saw_eof"), rec.get("truncated"),
                        rec.get("raw") == STDIN_B.decode("utf-8"), rec.get("registered_matcher")))
    if os.path.getsize(outf) > 0: why.append("stdout=%dB" % os.path.getsize(outf))
    keep = bool(why)
    if not keep: shutil.rmtree(home, ignore_errors=True)
    return {"i": i, "rc": rc, "early": early, "elapsed": elapsed, "names": names,
            "drops": drops, "why": why, "home": home if keep else None}

def main():
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    hook = os.path.abspath(sys.argv[1])
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    if n <= 0 or not os.path.isfile(hook): print("usage: N>0 and hook must exist"); sys.exit(2)
    work = sys.argv[3] if len(sys.argv) > 3 else \
        os.path.join(os.environ.get("TMPDIR", "/tmp"), "soak-%d" % os.getpid())
    os.makedirs(work, exist_ok=True)
    print("hook=%s N=%d work=%s" % (hook, n, work), flush=True)
    anomalies = 0; alldrops = []
    for i in range(n):
        r = one(hook, work, i)
        alldrops += [(i, nm, body) for nm, body in r["drops"]]
        if r["why"]:
            anomalies += 1
            print("ANOMALY i=%d rc=%s elapsed=%.3f why=%s names=%s drops=%s home=%s"
                  % (i, r["rc"], r["elapsed"], r["why"], r["names"], r["drops"], r["home"]), flush=True)
        if i % 100 == 99:
            print("... %d/%d anomalies=%d drops=%d" % (i + 1, n, anomalies, len(alldrops)), flush=True)
    print("SOAK launches=%d anomalies=%d dropped_files=%d" % (n, anomalies, len(alldrops)), flush=True)
    for i, nm, body in alldrops: print("DROPPED i=%d %s :: %s" % (i, nm, body), flush=True)
    sys.exit(1 if anomalies else 0)

main()
