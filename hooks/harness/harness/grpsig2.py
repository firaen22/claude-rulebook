#!/usr/bin/env python3
"""Reliable group-directed KILL / STOP-CONT instrument (closes sol 2026-09-01 F4).

WHY THIS REPLACES grpsig.py
  grpsig.py delivered the group signal after a blind time.sleep(0.35). On v27 the
  parent-level probe deadline is phase-dependent -- bash SECONDS is whole-second,
  so the 1s probe budget resolves anywhere in 0..1s. When it fires before 0.35s
  the hook has ALREADY cleaned up its own probe and exited 0 (event lost = cheap,
  contract-legal); the blind killpg then hits a dead/reused group -> EPERM, which
  grpsig.py scored as a FAIL. That was a harness artifact, not a hook defect.

THIS VERSION
  * READY-HANDSHAKE: after spawn, poll `ps` until the hung interpreter probe is
    observed ALIVE and in the hook's process group, and only THEN deliver the
    group signal -- so the signal provably lands mid-self-test. If the hook exits
    before the probe is caught (probe window too short this run), the trial is
    VOID and retried, exactly as pidhang.py retries until its pid-directed signal
    lands on a live target.
  * DOUBLE-SAMPLED survivors: a pid counts as a real survivor only if present and
    non-zombie in TWO ps samples >=SURV_GAP apart, so a process mid-teardown is
    not a false positive.
  * A version that cannot reach MIN_LANDED landed trials in MAXTRIES is reported
    INCONCLUSIVE (never a silent pass).

Cases per target:
  I01 group KILL mid-probe : killpg(SIGKILL); zero real survivors.
  I02 group STOP mid-probe : killpg(SIGSTOP); while stopped NO member may be in
    state R (the v24 "burns CPU while its watchdog is stopped" regression);
    SIGCONT; hook must exit rc 0, zero stdout, zero real survivors.

Usage: grpsig2.py OUTDIR TARGET [TARGET...]
Exit 0 iff every target passes both cases with >=MIN_LANDED landed trials.
"""
import os, sys, time, signal, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contract  # reuse make_interp_variant + build_home + _rmtree

MAXTRIES   = 60
MIN_LANDED = 5
CATCH_WIN  = 3.0     # seconds to wait for the probe to appear alive in-group
SURV_GAP   = 0.45    # gap between the two survivor samples
PAYLOAD    = b'{"session_id":"grpsig2","transcript_path":"/dev/null","hook_event_name":"PreCompact","trigger":"manual"}'


def ps_rows():
    """-E appends the environment to command= so members() can also attribute a
    descendant that left the group by its inherited HOME (sol 2026-09-02 F2).
    None on any ps failure, including rc!=0 with empty stdout (sol F7)."""
    try:
        r = subprocess.run(["/bin/ps", "-axwwEo", "pid=,pgid=,state=,command="],
                           capture_output=True, text=True, timeout=10)
        if r.returncode != 0 or not r.stdout.strip():
            return None
        out = r.stdout
    except Exception:
        return None
    rows = []
    for ln in out.splitlines():
        f = ln.split(None, 3)
        if len(f) == 4 and f[0].isdigit() and f[1].isdigit():
            rows.append((int(f[0]), int(f[1]), f[2], f[3]))
    return rows

HOMEMARK = {}      # stubmark -> " HOME=<home> " token, set by run_target
HOME_BEFORE = {}   # home -> pre-run canary snapshot, set by run_target

def members(rows, pgid, stubmark):
    """Non-zombie processes in the hook's group, any stub of this run, or any
    process still carrying this run's HOME (left the group)."""
    hm = HOMEMARK.get(stubmark)
    return [r for r in rows
            if (r[1] == pgid or stubmark in r[3] or (hm and hm in (" " + r[3] + " ")))
            and not r[2].startswith("Z")]

def probe_alive(rows, pgid, stubmark):
    """The hung interpreter probe, alive AND in the hook's process group."""
    return [r for r in rows if r[1] == pgid and stubmark in r[3] and not r[2].startswith("Z")]

def sweep(pgid, stubmark):
    rows = ps_rows()
    if rows is None:
        return
    for r in members(rows, pgid, stubmark):
        try: os.kill(r[0], 9)
        except OSError: pass

def spawn(hook, workdir, home):
    env = {"HOME": home, "PATH": "/usr/bin:/bin", "LANG": "C"}
    outf = open(os.path.join(workdir, "grp.out"), "wb")
    errf = open(os.path.join(workdir, "grp.err"), "wb")
    rfd, wfd = os.pipe()
    p = subprocess.Popen(["/bin/bash", "--noprofile", "--norc", "-p", hook, "manual"],
                         stdin=rfd, stdout=outf, stderr=errf, env=env, cwd=workdir,
                         preexec_fn=lambda: os.setpgid(0, 0))
    os.close(rfd)
    try: os.write(wfd, PAYLOAD)
    except OSError: pass
    return p, wfd, outf

def wait_probe_landed(p, stubmark, budget):
    """Poll until the hung probe is alive in-group -> return True.
    Return False if the hook exits first (probe window too short: VOID trial)."""
    t = time.time()
    while time.time() - t < budget:
        rows = ps_rows()
        if rows is not None and probe_alive(rows, p.pid, stubmark):
            return True
        if p.poll() is not None:      # hook already exited -> nothing to signal
            return False
        time.sleep(0.01)
    return False

def real_survivors(pgid, stubmark):
    """Double-sampled: survivor iff present & non-zombie in TWO samples SURV_GAP apart."""
    r1 = ps_rows()
    if r1 is None: return None
    s1 = {r[0] for r in members(r1, pgid, stubmark)}
    if not s1:
        return []
    time.sleep(SURV_GAP)
    r2 = ps_rows()
    if r2 is None: return None
    m2 = {r[0]: r for r in members(r2, pgid, stubmark)}
    return [(pid, m2[pid][2], m2[pid][3][:70]) for pid in (s1 & set(m2))]

def _drain_void(p, wfd, outf, stubmark):
    try: os.close(wfd)
    except OSError: pass
    try: p.wait(timeout=3)
    except Exception:
        try: os.killpg(p.pid, signal.SIGKILL)
        except OSError: pass
    outf.close()
    sweep(p.pid, stubmark)

def one_trial_I01(hook, workdir, home, stubmark):
    p, wfd, outf = spawn(hook, workdir, home)
    if not wait_probe_landed(p, stubmark, CATCH_WIN):
        _drain_void(p, wfd, outf, stubmark)
        return None                                   # VOID -> retry
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except OSError as e:
        _drain_void(p, wfd, outf, stubmark)
        return ("ERR", "I01 killpg after landed probe: %r" % e)
    try: os.close(wfd)
    except OSError: pass
    try: p.wait(timeout=5)
    except Exception: pass
    outf.close()
    surv = real_survivors(p.pid, stubmark)
    sweep(p.pid, stubmark)
    if surv is None: return ("VOID", None)            # ps vanished -> retry
    fails = list(surv)
    # sol 2026-09-02 F6 (CONFIRMED by reading): I01 never looked at its stdout
    # capture or the canary tree. Bytes written before the KILL are C2 bytes.
    ob = os.path.getsize(os.path.join(workdir, "grp.out"))
    if ob: fails.append("%dB stdout" % ob)
    fails += ["C4 " + d for d in contract.diff_snapshots(HOME_BEFORE[home], contract.snapshot(home))]
    return ("OK", fails)

def one_trial_I02(hook, workdir, home, stubmark):
    p, wfd, outf = spawn(hook, workdir, home)
    if not wait_probe_landed(p, stubmark, CATCH_WIN):
        _drain_void(p, wfd, outf, stubmark)
        return None                                   # VOID -> retry
    fails = []
    try:
        os.killpg(p.pid, signal.SIGSTOP)
    except OSError as e:
        _drain_void(p, wfd, outf, stubmark)
        return ("ERR", "I02 killpg STOP after landed probe: %r" % e)
    time.sleep(0.4)
    rr = ps_rows()
    if rr is None:
        # codex 2026-09-01 F8 (CONFIRMED by reading): a missing ps sample here used
        # to skip the R-state check and the trial still counted as landed-clean.
        # No observation is not a clean observation -> VOID, retried.
        try: os.killpg(p.pid, signal.SIGCONT)
        except OSError: pass
        _drain_void(p, wfd, outf, stubmark)
        return ("VOID", None)
    running = [r for r in members(rr, p.pid, stubmark) if r[2].startswith("R")]
    if running:
        fails.append("running while STOPPED: %s" % [(r[0], r[2], r[3][:40]) for r in running])
    try: os.killpg(p.pid, signal.SIGCONT)
    except OSError: pass
    try: os.close(wfd)
    except OSError: pass
    rc = None
    try: rc = p.wait(timeout=10)
    except Exception:
        fails.append("hook did not exit after CONT")
        try: os.killpg(p.pid, signal.SIGKILL)
        except OSError: pass
    if rc is not None and rc != 0: fails.append("rc=%r after CONT" % rc)
    outf.close()
    ob = os.path.getsize(os.path.join(workdir, "grp.out"))
    if ob: fails.append("%dB stdout" % ob)
    surv = real_survivors(p.pid, stubmark)
    sweep(p.pid, stubmark)
    if surv is None: return ("VOID", None)            # ps vanished -> retry
    if surv: fails.append("%d survivor(s): %s" % (len(surv), surv))
    fails += ["C4 " + d for d in contract.diff_snapshots(HOME_BEFORE[home], contract.snapshot(home))]
    return ("OK", fails)

def run_case(trial_fn, hook, workdir, home, stubmark):
    landed = 0; tries = 0; fails = []
    while landed < MIN_LANDED and tries < MAXTRIES:
        tries += 1
        res = trial_fn(hook, workdir, home, stubmark)
        if res is None:
            continue
        tag, payload = res
        if tag == "ERR":
            fails.append(payload); continue
        if tag == "VOID":
            continue
        landed += 1
        if payload:
            fails.append("trial%d %s" % (landed, payload))
    return landed, tries, fails

def run_target(target, outroot):
    label = os.path.basename(target)
    workdir = os.path.join(outroot, "grpsig2_" + label)
    contract._rmtree(workdir)
    os.makedirs(workdir)
    home = os.path.join(workdir, "home")
    contract.build_home(home, "")
    hook = contract.make_interp_variant(target, workdir, "hang")
    stubmark = os.path.join(workdir, "interp_hang")
    HOMEMARK[stubmark] = " HOME=" + home + " "
    HOME_BEFORE[home] = contract.snapshot(home)      # C4 baseline for every trial (sol F6)
    l1, t1, f1 = run_case(one_trial_I01, hook, workdir, home, stubmark)
    l2, t2, f2 = run_case(one_trial_I02, hook, workdir, home, stubmark)
    return [("I01_grp_KILL", l1, t1, f1), ("I02_grp_STOP", l2, t2, f2)]

def main():
    outroot = os.path.abspath(sys.argv[1])
    targets = [os.path.abspath(t) for t in sys.argv[2:]]
    os.makedirs(outroot, exist_ok=True)
    bad = 0
    for t in targets:
        rep = run_target(t, outroot)
        lab = os.path.basename(t)
        tfail = False; lines = []
        for case, landed, tries, fails in rep:
            if landed < MIN_LANDED:
                tfail = True
                lines.append("%s: only %d landed in %d tries -- INCONCLUSIVE" % (case, landed, tries))
            elif fails:
                tfail = True
                lines.append("%s: %d landed, FAILS: %s" % (case, landed, " | ".join(fails)))
            else:
                lines.append("%s: %d/%d landed clean" % (case, landed, tries))
        if tfail: bad += 1
        print(("FAIL " if tfail else "PASS ") + "%-20s %s" % (lab, " || ".join(lines)))
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
