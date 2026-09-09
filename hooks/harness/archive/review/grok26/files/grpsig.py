#!/usr/bin/env python3
"""Group-directed KILL/STOP instrument (sol 2026-09-01 finding 1/4).

Two cases, both against the interp-hang variant so a probe child is alive when
the signal lands:
  I01_grp_KILL_midhang: killpg(SIGKILL) at the whole hook group mid-hang.
    Contract: nothing survives (rc is the caller's own kill -- not graded).
  I02_grp_STOP_midhang: killpg(SIGSTOP) mid-hang; while stopped, NO member of
    the tree may be running (state R = burning CPU while its watchdog is
    stopped, the v24 regression); then SIGCONT, hook must finish rc 0, zero
    stdout, zero survivors.
Usage: grpsig.py OUTDIR TARGET [TARGET...]
Exit 0 iff every target passes both cases (per-target lines on stdout).
"""
import os, sys, time, signal, subprocess, tempfile, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contract  # reuse make_interp_variant + build_home + INVOC


def ps_rows():
    try:
        out = subprocess.run(["/bin/ps", "-axo", "pid=,pgid=,state=,command="],
                             capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return None
    rows = []
    for ln in out.splitlines():
        f = ln.split(None, 3)
        if len(f) == 4 and f[0].isdigit() and f[1].isdigit():
            rows.append((int(f[0]), int(f[1]), f[2], f[3]))
    return rows

def tree_members(rows, pgid, stubmark):
    return [r for r in rows if (r[1] == pgid or stubmark in r[3]) and not r[2].startswith("Z")]

def sweep(rows, pgid, stubmark):
    for r in tree_members(rows, pgid, stubmark):
        try: os.kill(r[0], 9)
        except OSError: pass

def spawn(hook, workdir, home):
    env = {"HOME": home, "PATH": "/usr/bin:/bin", "LANG": "C"}
    payload = b'{"session_id":"grpsig","transcript_path":"/dev/null","hook_event_name":"PreCompact","trigger":"manual"}'
    outf = open(os.path.join(workdir, "grp.out"), "wb")
    errf = open(os.path.join(workdir, "grp.err"), "wb")
    rfd, wfd = os.pipe()
    p = subprocess.Popen(["/bin/bash", "--noprofile", "--norc", "-p", hook, "manual"],
                         stdin=rfd, stdout=outf, stderr=errf, env=env, cwd=workdir,
                         preexec_fn=lambda: os.setpgid(0, 0))
    os.close(rfd)
    try: os.write(wfd, payload)
    except OSError: pass
    return p, wfd, outf

def run_target(target, outroot):
    label = os.path.basename(target)
    workdir = os.path.join(outroot, "grpsig_" + label)
    if os.path.exists(workdir): shutil.rmtree(workdir)
    os.makedirs(workdir)
    home = os.path.join(workdir, "home")
    contract.build_home(home, "")
    hook = contract.make_interp_variant(target, workdir, "hang")
    stubmark = os.path.join(workdir, "interp_hang")
    fails = []

    # ---- I01 group KILL mid-hang
    p, wfd, outf = spawn(hook, workdir, home)
    time.sleep(0.35)                     # worker is inside the hung probe
    try: os.killpg(p.pid, signal.SIGKILL)
    except OSError as e: fails.append("I01 killpg failed: %r" % e)
    try: os.close(wfd)
    except OSError: pass
    try: p.wait(timeout=5)
    except Exception: fails.append("I01 hook did not die")
    time.sleep(0.5)
    rows = ps_rows()
    if rows is None:
        fails.append("I01 ps unavailable -- survivors UNKNOWN")
    else:
        surv = tree_members(rows, p.pid, stubmark)
        if surv: fails.append("I01 %d survivor(s) after group KILL: %s" %
                              (len(surv), [(r[0], r[2]) for r in surv]))
        sweep(rows, p.pid, stubmark)

    # ---- I02 group STOP mid-hang, then CONT
    p, wfd, outf = spawn(hook, workdir, home)
    time.sleep(0.35)
    try: os.killpg(p.pid, signal.SIGSTOP)
    except OSError as e: fails.append("I02 killpg STOP failed: %r" % e)
    time.sleep(0.6)
    rows = ps_rows()
    if rows is None:
        fails.append("I02 ps unavailable -- stop-state UNKNOWN")
    else:
        running = [r for r in tree_members(rows, p.pid, stubmark) if r[2].startswith("R")]
        if running: fails.append("I02 running while group STOPPED: %s" %
                                 [(r[0], r[2], r[3][:60]) for r in running])
    try: os.killpg(p.pid, signal.SIGCONT)
    except OSError: pass
    try: os.close(wfd)
    except OSError: pass
    rc = None
    try: rc = p.wait(timeout=10)
    except Exception:
        fails.append("I02 hook did not exit after CONT")
        try: os.killpg(p.pid, signal.SIGKILL)
        except OSError: pass
    if rc is not None and rc != 0: fails.append("I02 rc=%r after CONT (want 0)" % rc)
    outf.close()
    ob = os.path.getsize(os.path.join(workdir, "grp.out"))
    if ob: fails.append("I02 %dB on stdout" % ob)
    time.sleep(0.5)
    rows = ps_rows()
    if rows is None:
        fails.append("I02 ps unavailable -- survivors UNKNOWN")
    else:
        surv = tree_members(rows, p.pid, stubmark)
        if surv: fails.append("I02 %d survivor(s) after CONT+exit: %s" %
                              (len(surv), [(r[0], r[2]) for r in surv]))
        sweep(rows, p.pid, stubmark)
    return fails

def main():
    outroot = os.path.abspath(sys.argv[1])
    targets = [os.path.abspath(t) for t in sys.argv[2:]]
    os.makedirs(outroot, exist_ok=True)
    bad = 0
    for t in targets:
        fails = run_target(t, outroot)
        if fails:
            bad += 1
            print("FAIL %-20s %s" % (os.path.basename(t), " | ".join(fails)))
        else:
            print("PASS %-20s I01_grp_KILL + I02_grp_STOP clean" % os.path.basename(t))
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
