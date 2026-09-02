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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contract   # build_home / snapshot / diff_snapshots: C3+C4 graded here too (sol F5)

def survivors(pgid, home):
    """Live non-zombie processes in the hook's group or carrying its HOME (see
    contract.py's orphan scan). None = ps unusable (never 'no survivors')."""
    r = subprocess.run(["/bin/ps", "-axwwEo", "pid=,pgid=,state=,command="],
                       capture_output=True, text=True, timeout=10)
    if r.returncode != 0 or not r.stdout.strip():
        return None
    mark = " HOME=" + home + " "; out = []
    for ln in r.stdout.splitlines():
        f = ln.split(None, 3)
        if len(f) == 4 and f[0].isdigit() and f[1].isdigit() and int(f[0]) != pgid \
           and not f[2].startswith("Z") and (int(f[1]) == pgid or mark in (" " + f[3] + " ")):
            out.append(int(f[0]))
    return out

# grok 2026-09-02 F11 (CONFIRMED by reading): delivery was a blind sleep(1.0) after
# spawn; an oversleep past the ~2-3s window would land the signal AFTER the ignore
# line and grade a gap-vulnerable hook exit0. The busy-wait now announces itself
# (a redirection on a builtin: no fork) and the prober delivers only after seeing
# the marker, recording how long after; too late or never = VOID, not a pass.
READY = ".gap_ready"
READY_MAX = 1.5      # seconds after the marker within which delivery still provably hits the window
BUSY = ('builtin : > "$HOME/' + READY + '"; _gapwait=$(( SECONDS + 3 )); '
        'while builtin [ "$SECONDS" -lt "$_gapwait" ]; do builtin :; done\n')
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
    contract._rmtree(home); os.makedirs(home)
    contract.build_home(home, "")
    devnull = open(os.devnull, "wb")
    # sol 2026-09-01 (CONFIRMED): stdout went to /dev/null and grading looked only
    # at exit status, so a mutant leaking bytes in the stop-signal window PASSED.
    # C2 is graded here now; the leak is folded into the verdict string so every
    # existing consumer of (verdict, elapsed) keeps working unchanged.
    outf = os.path.join(home, "gap_stdout.bin")
    fo = open(outf, "wb")
    rfd, wfd = os.pipe()
    ready = os.path.join(home, READY)
    try: os.unlink(ready)
    except OSError: pass
    before = contract.snapshot(home, exclude=[ready, outf])
    t0 = time.time()
    p = subprocess.Popen(["/bin/bash", "--noprofile", "--norc", "-p", path, "manual"],
                         stdin=rfd, stdout=fo, stderr=devnull, env=env,
                         preexec_fn=lambda: os.setpgid(0, 0))
    os.close(rfd)
    # wait for the busy-wait's own marker instead of sleeping blind (grok F11)
    verdict, state = None, None
    while time.time() - t0 < 4.0 and not os.path.exists(ready):
        if p.poll() is not None:
            verdict = "VOID-exited-before-signal"; break
        time.sleep(0.005)
    late = None
    if verdict is None:
        if not os.path.exists(ready):
            verdict = "VOID-no-ready-marker"
        else:
            try:
                late = time.time() - os.stat(ready).st_mtime
            except OSError:            # sol F10: marker vanished between exists() and stat()
                late = None; verdict = "VOID-ready-marker-vanished"
            if late is not None and late > READY_MAX:
                verdict = "VOID-late%.2fs" % late
    s = getattr(signal, "SIG" + sig)
    # codex 2026-09-01 F7 (CONFIRMED by reading): a target already gone before
    # delivery, or a failed kill, fell through to the exit-status read and could
    # grade "exit0" == PASS without the signal ever landing in the window. Both
    # are now VOID verdicts, which never equal "exit0" -> loud FAIL, never a pass.
    if verdict is not None:
        pass
    elif p.poll() is not None:
        verdict = "VOID-exited-before-signal"
    else:
        try:
            if mode == "pid": os.kill(p.pid, s)
            else:             os.killpg(p.pid, s)
        except OSError as e:
            verdict = "VOID-kill-%s" % e.__class__.__name__
    end = time.time() + 10
    while verdict is None and time.time() < end:
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
    if verdict is None:
        verdict = "BLOCKED"
    el = round(time.time() - t0, 2)
    # sol 2026-09-02 F5 (CONFIRMED by reading): killpg below destroyed any survivor
    # before it could be counted, and no canary was graded. Scan first, grade C4.
    surv = survivors(p.pid, home)
    if surv is None:      verdict += "+SURV?"                      # unknown, never clean
    elif surv:            verdict += "+SURV%d" % len(surv)
    try:
        os.killpg(p.pid, signal.SIGCONT); os.killpg(p.pid, signal.SIGKILL)
        os.waitpid(p.pid, 0)
    except (OSError, ChildProcessError):
        pass
    for spid in (surv or []):
        try: os.kill(spid, 9)
        except OSError: pass
    destroyed = contract.diff_snapshots(before, contract.snapshot(home, exclude=[ready, outf]))
    if destroyed:         verdict += "+C4:" + ";".join(destroyed[:3])
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
