#!/usr/bin/env python3
"""Signal-window differential: the 174->175 gap the plain suite is blind to.

The window between the early exit-0 trap and the `trap '' TSTP TTIN TTOU` is
microseconds wide, so a plain run cannot land a signal in it. This instrument
WIDENS the window identically in every variant (a pure-builtin, SECONDS-bounded
busy-wait -- NOT /bin/sleep, which is itself a killable foreground child and
produces a false BLOCKED) and then delivers the stop signal inside it.

Non-orphaned process group is mandatory: in an orphaned group the kernel
DISCARDS stop signals and every variant would falsely pass.
"""
import os, re, signal, subprocess, sys, time, json

BUSY = ('_gapwait=$(( SECONDS + 3 )); while builtin [ "$SECONDS" -lt "$_gapwait" ]; '
        'do builtin :; done\n')
TRAP_RE   = re.compile(r"^\s*(builtin\s+)?trap\s+'.*exit 0'.*\bHUP\b")
IGNORE_RE = re.compile(r"^\s*(builtin\s+)?trap\s+''\s+TSTP")

def instrument(src, dst):
    lines = open(src).readlines()
    ti = ii = None
    for i, l in enumerate(lines):
        if ti is None and TRAP_RE.match(l): ti = i
        if ti is not None and ii is None and i > ti and IGNORE_RE.match(l): ii = i
    if ti is None:
        return None, "NO-EARLY-TRAP-ANCHOR"
    ins = (ii if ii is not None else ti + 1)
    out = lines[:ins] + [BUSY] + lines[ins:]
    open(dst, "w").writelines(out)
    os.chmod(dst, 0o755)
    return (ti + 1, ins + 1), ("has-ignore" if ii is not None else "NO-IGNORE-LINE")

def probe(path, sig, mode, home):
    env = {"HOME": home, "PATH": "/usr/bin:/bin", "TERM": "dumb"}
    os.makedirs(os.path.join(home, ".claude", "session-state", "observed"), exist_ok=True)
    devnull = open(os.devnull, "wb")
    # sol 2026-09-01 (CONFIRMED): stdout went to /dev/null and grading looked only
    # at exit status, so a mutant leaking bytes in the stop-signal window PASSED.
    # C2 is graded here now; the leak is folded into the verdict string so every
    # existing consumer of (verdict, elapsed) keeps working unchanged.
    outf = os.path.join(home, "gap_stdout.bin")
    fo = open(outf, "wb")
    rfd, wfd = os.pipe()
    t0 = time.time()
    p = subprocess.Popen(["/bin/bash", "--noprofile", "--norc", "-p", path, "manual"],
                         stdin=rfd, stdout=fo, stderr=devnull, env=env,
                         preexec_fn=lambda: os.setpgid(0, 0))
    os.close(rfd)
    time.sleep(1.0)                      # land inside the widened window
    s = getattr(signal, "SIG" + sig)
    try:
        if mode == "pid": os.kill(p.pid, s)
        else:             os.killpg(p.pid, s)
    except OSError:
        pass
    verdict, state = None, None
    end = time.time() + 10
    while time.time() < end:
        try:
            wpid, st = os.waitpid(p.pid, os.WNOHANG | os.WUNTRACED)
        except ChildProcessError:
            verdict = "GONE"; break
        if wpid == p.pid:
            if os.WIFSTOPPED(st): verdict = "STOPPED"
            elif os.WIFSIGNALED(st): verdict = f"KILLED-sig{os.WTERMSIG(st)}"
            else: verdict = f"exit{os.WEXITSTATUS(st)}"
            break
        time.sleep(0.02)
    else:
        verdict = "BLOCKED"
    el = round(time.time() - t0, 2)
    try:
        os.killpg(p.pid, signal.SIGCONT); os.killpg(p.pid, signal.SIGKILL)
        os.waitpid(p.pid, 0)
    except (OSError, ChildProcessError):
        pass
    try: os.close(wfd)
    except OSError: pass
    devnull.close()
    try:
        fo.flush(); fo.close()
    except OSError:
        pass
    try:
        nb = os.path.getsize(outf)
    except OSError:
        nb = -1
    if nb != 0:
        verdict = "%s+C2LEAK%dB" % (verdict, nb)   # never equals "exit0" -> FAIL
    return verdict, el

def main():
    work = os.path.abspath(sys.argv[1]); targets = sys.argv[2:]
    os.makedirs(work, exist_ok=True)
    rows = []
    for t in targets:
        label = os.path.basename(t)
        inst = os.path.join(work, "inst_" + label)
        anchors, note = instrument(os.path.abspath(t), inst)
        if anchors is None:
            rows.append({"target": label, "verdicts": {}, "note": note, "pass": False}); continue
        v = {}
        for sig in ("TSTP", "TTIN", "TTOU"):
            for mode in ("pid", "grp"):
                h = os.path.join(work, f"h_{label}_{sig}_{mode}")
                os.makedirs(h, exist_ok=True)
                v[f"{sig}/{mode}"] = probe(inst, sig, mode, h)
        ok = all(r[0] == "exit0" for r in v.values())
        rows.append({"target": label, "anchor_lines": anchors, "note": note,
                     "verdicts": {k: f"{a} @{b}s" for k, (a, b) in v.items()}, "pass": ok})
        print(f"{'PASS' if ok else 'FAIL'} {label:<14} " +
              "  ".join(f"{k}={a}" for k, (a, b) in v.items()))
    json.dump(rows, open(os.path.join(work, "GAP-RESULT.json"), "w"), indent=1)

main()
