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
    ps=subprocess.run(["/bin/ps","-axwwEo","pid=,pgid=,state=,command="],capture_output=True,text=True,timeout=10).stdout
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
    if os.path.exists(home): shutil.rmtree(home, ignore_errors=True)
    os.makedirs(home); contract.build_home(home,"")
    target=contract.make_interp_variant(hook, workdir, "hang")
    stubmark=os.path.join(workdir,"interp_hang")
    env={"HOME":home,"PATH":"/usr/bin:/bin:/usr/sbin:/sbin","SHELL":"/bin/zsh","LANG":"en_US.UTF-8","TERM":"dumb"}
    rfd,wfd=os.pipe()
    p=subprocess.Popen(contract.INVOC+[target,"manual"],stdin=rfd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env,cwd=workdir,preexec_fn=lambda:os.setpgid(0,0))
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
    for pid,_ in surv:
        try: os.kill(pid,9)
        except OSError: pass
    try: os.killpg(p.pid,signal.SIGKILL)
    except OSError: pass
    try: p.wait(timeout=3)
    except Exception: pass
    return alive, len(surv)

def trials(hook, tag, n=10):
    wd=os.path.join(os.path.dirname(os.path.abspath(__file__)),"mrepwd_"+tag)
    if os.path.exists(wd): shutil.rmtree(wd, ignore_errors=True)
    os.makedirs(wd)
    landed=0; maxorph=0; orphaned_runs=0; blocked=0; void=0; tries=0; offsets=[0.0,0.1,0.2]
    while landed<n and tries<MAXTRIES:
        alive,orph=one(hook, signal.SIGTERM, offsets[tries%3], wd); tries+=1
        if alive is True:
            landed+=1
            if orph>0: orphaned_runs+=1
            maxorph=max(maxorph,orph)
        elif alive=="BLOCKED": blocked+=1
        else: void+=1
    print("%-5s tries=%d landed=%d void=%d blocked=%d runs_with_orphan=%d max_orphans=%d"%(tag,tries,landed,void,blocked,orphaned_runs,maxorph))
    return orphaned_runs, landed, blocked

if __name__=="__main__":
    cand="candidate"
    print("H1 multi-trial (H01 hang + pid-directed SIGTERM landed mid-probe):")
    o22,l22,b22=trials(os.path.join(cand,"v22-installed.sh"),"v22")
    o26,l26,b26=trials(os.path.join(cand,"v26.sh"),"v26")
    o27,l27,b27=trials(os.path.join(cand,"v27.sh"),"v27")
    o28,l28,b28=trials(os.path.join(cand,"v28.sh"),"v28")
    ok = (o26>0 and o27==0 and o28==0 and b27==0 and b28==0 and min(l27,l28)>=grpsig2.MIN_LANDED)
    print("%s"%("DISCRIMINATED: v26 leaks (%d), v27+v28 clean and unblocked across >=%d landed trials"%(o26,min(l27,l28)) if ok
                 else "INCONCLUSIVE: v26 orph=%d v27 orph=%d/blk=%d v28 orph=%d/blk=%d landed=%d/%d"%(o26,o27,b27,o28,b28,l27,l28)))
    sys.exit(0 if ok else 1)
