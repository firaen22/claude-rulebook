"""pid-directed SIGTERM delivered while the hook's interpreter self-test is hung (H1).

grok 2026-09-02 F5/F6 (CONFIRMED by reading): the old instrument fired SIGTERM at a
fixed delay from spawn and counted the trial "landed" whenever the hook was merely
alive -- not when the hung probe was. Trials that hit the hook before or after
its probe phase inflated `landed`, and a hook that ignored SIGTERM ran into the
6s cap, where killpg(SIGKILL) destroyed the in-group evidence BEFORE the survivor
scan, so the trial still scored clean. Now: the same ready-handshake grpsig2 uses
(deliver only once the probe is observed alive in-group, else VOID and retry), a
small phase offset after that, kill failures never count as landed, and a hook
still running at the cap is a BLOCKED trial that is scanned before it is killed.
Run from the repo root: python3 harness/pidhang.py
"""
import sys, os, time, subprocess, signal, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contract, grpsig2
GOOD=b'{"session_id":"abc","transcript_path":"/tmp/x.jsonl","hook_event_name":"PreCompact","trigger":"manual"}'
CAP=6.0; MAXTRIES=40

def scan(pgid, workdir, home):
    """Survivors, or None when ps is unusable (sol F7: rc!=0 + empty stdout is not an empty table)."""
    r=subprocess.run(["/bin/ps","-axwwEo","pid=,pgid=,state=,command="],capture_output=True,text=True,timeout=10)
    if r.returncode!=0 or not r.stdout.strip(): return None
    ps=r.stdout
    surv=[]; seen=set(); homemark=" HOME="+home+" "
    for ln in ps.splitlines():
        f=ln.split(None,3)
        if len(f)>=3 and f[1].isdigit() and int(f[1])==pgid and int(f[0])!=pgid and not f[2].startswith("Z"):
            surv.append((int(f[0]),f[2])); seen.add(int(f[0]))
    for ln in ps.splitlines():
        f=ln.split(None,3)
        if len(f)==4 and f[0].isdigit() and int(f[0]) not in seen and int(f[0])!=pgid and not f[2].startswith("Z") \
           and ((workdir+"/interp_") in f[3] or homemark in (" "+f[3]+" ")):   # grok F2: out-of-group descendants
            surv.append((int(f[0]),f[2])); seen.add(int(f[0]))
    return surv

def one(hook, sig, offset, workdir):
    """Returns (alive, orphans): alive True = signal landed on a live hook mid-probe;
    None = VOID (probe never observed / gone before delivery); "BLOCKED" = hook
    still running at CAP after the signal; False = kill failed."""
    home=os.path.join(workdir,"home")
    contract._rmtree(home)                                   # sol F9: survives mode-500 leftovers
    os.makedirs(home); contract.build_home(home,"")
    target=contract.make_interp_variant(hook, workdir, "hang")
    stubmark=os.path.join(workdir,"interp_hang")
    env={"HOME":home,"PATH":"/usr/bin:/bin:/usr/sbin:/sbin","SHELL":"/bin/zsh","LANG":"en_US.UTF-8","TERM":"dumb"}
    before=contract.snapshot(home)
    outf=os.path.join(workdir,"ph.out"); fo=open(outf,"wb")
    rfd,wfd=os.pipe()
    p=subprocess.Popen(contract.INVOC+[target,"manual"],stdin=rfd,stdout=fo,stderr=subprocess.DEVNULL,env=env,cwd=workdir,preexec_fn=lambda:os.setpgid(0,0))
    os.close(rfd)
    try: os.write(wfd,GOOD[:20])
    except OSError: pass
    alive=None
    if grpsig2.wait_probe_landed(p, stubmark, grpsig2.CATCH_WIN):
        time.sleep(offset)                                   # vary the phase inside the probe window
        rows=grpsig2.ps_rows()
        if rows is not None and grpsig2.probe_alive(rows, p.pid, stubmark) and p.poll() is None:
            try: os.kill(p.pid, sig); alive=True
            except OSError: alive=False
    try: os.close(wfd); wfd=None
    except OSError: pass
    t1=time.time()
    while p.poll() is None and time.time()-t1<CAP:
        time.sleep(0.02)
    if p.poll() is None and alive is True:
        alive="BLOCKED"                                      # grok F6: scan BEFORE destroying the group
    time.sleep(0.35)
    surv=scan(p.pid, workdir, home)
    for pid,_ in (surv or []):
        try: os.kill(pid,9)
        except OSError: pass
    try: os.killpg(p.pid,signal.SIGKILL)
    except OSError: pass
    try: p.wait(timeout=3)
    except Exception: pass
    fo.close()
    if surv is None:
        return (None if alive is True else alive), -1     # ps unusable: never "clean" (sol F7)
    # sol 2026-09-02 F3 (CONFIRMED by reading): a landed trial only checked survivors;
    # rc, stdout bytes and the canary tree were discarded. All three are contract.
    dirty=[]
    if alive is True and p.returncode!=0: dirty.append("rc=%r"%p.returncode)
    ob=os.path.getsize(outf)
    if ob: dirty.append("%dB stdout"%ob)
    dirty+=contract.diff_snapshots(before, contract.snapshot(home))
    if alive is True and dirty: alive=("DIRTY", dirty)
    return alive, len(surv)

def trials(hook, tag, n=10):
    wd=os.path.join(os.path.dirname(os.path.abspath(__file__)),"mrepwd_"+tag)
    contract._rmtree(wd)
    os.makedirs(wd)
    landed=0; maxorph=0; orphaned_runs=0; blocked=0; void=0; dirty=0; tries=0; offsets=[0.0,0.1,0.2]; why=[]
    while landed<n and tries<MAXTRIES:
        alive,orph=one(hook, signal.SIGTERM, offsets[tries%3], wd); tries+=1
        if alive is True or (isinstance(alive,tuple) and alive[0]=="DIRTY"):
            landed+=1
            if orph>0: orphaned_runs+=1
            maxorph=max(maxorph,orph)
            if alive is not True: dirty+=1; why.append(alive[1])
        elif alive=="BLOCKED": blocked+=1
        else: void+=1
    print("%-5s tries=%d landed=%d void=%d blocked=%d dirty=%d runs_with_orphan=%d max_orphans=%d%s"
          %(tag,tries,landed,void,blocked,dirty,orphaned_runs,maxorph,("  "+repr(why[:2])) if why else ""))
    return orphaned_runs, landed, blocked+dirty

if __name__=="__main__":
    cand="candidate"
    # The target under test comes from argv, as contract/gap/grpsig2 already do.
    # It used to be a hardcoded v22/v26/v27/v28 list, so `run_all.sh other.sh
    # --pidhang` graded v27+v28 and never touched the candidate it was asked
    # about -- a clean DISCRIMINATED for a hook the run never executed.
    CONTROL = os.path.join(cand, "v26.sh")   # known leaker: the positive control
    target  = sys.argv[1] if len(sys.argv) > 1 else os.path.join(cand, "v28.sh")
    tlabel  = os.path.basename(target)
    if tlabel.endswith(".sh"): tlabel = tlabel[:-3]
    print("H1 multi-trial (H01 hang + pid-directed SIGTERM landed mid-probe):")
    print("target=%s  control=%s" % (target, CONTROL))
    if os.path.realpath(target) == os.path.realpath(CONTROL):
        # Control and target are the same file; "must leak" and "must be clean"
        # cannot both hold, so this is a harness misuse, not a hook verdict.
        print("INCONCLUSIVE: target is the positive control (%s); pick another candidate" % CONTROL)
        sys.exit(1)
    # The control must still LEAK. If it stops leaking, the probe itself is broken
    # and a clean target proves nothing -- that is the whole point of running it.
    o26,l26,b26 = trials(CONTROL, "v26")
    ot, lt, bt  = trials(target, tlabel)
    # The control must leak on MOST landed trials, not merely once. `o26>0` alone
    # let a badly degraded probe certify itself off a single observation, which
    # says nothing about its sensitivity on THIS machine. v26 measured 10 leaks
    # over 10 landed trials on two consecutive baseline runs (2026-09-05), so a
    # floor at MIN_LANDED leaves roughly 2x margin over observed behaviour.
    ctl_ok = (l26 >= grpsig2.MIN_LANDED and o26 >= grpsig2.MIN_LANDED)
    ok = (ctl_ok and ot == 0 and bt == 0 and lt >= grpsig2.MIN_LANDED)
    print("%s" % ("DISCRIMINATED: control v26 leaks (orph=%d over %d landed trials), "
                  "%s clean and unblocked across %d landed trials"%(o26,l26,tlabel,lt) if ok
                  else "INCONCLUSIVE: control v26 orph=%d landed=%d blk=%d (need orph>=%d and landed>=%d); "
                       "%s orph=%d blk=%d landed=%d (need orph=0, blk=0, landed>=%d)"
                       %(o26,l26,b26,grpsig2.MIN_LANDED,grpsig2.MIN_LANDED,tlabel,ot,bt,lt,grpsig2.MIN_LANDED)))
    sys.exit(0 if ok else 1)
