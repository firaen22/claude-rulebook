import sys, os, time, subprocess, signal, shutil
HF=os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness-frozen3")
sys.path.insert(0,HF); import contract
GOOD=b'{"session_id":"abc","transcript_path":"/tmp/x.jsonl","hook_event_name":"PreCompact","trigger":"manual"}'

def scan(pgid, workdir):
    ps=subprocess.run(["/bin/ps","-axo","pid=,pgid=,state=,command="],capture_output=True,text=True,timeout=10).stdout
    surv=[]; seen=set()
    for ln in ps.splitlines():
        f=ln.split(None,3)
        if len(f)>=3 and f[1].isdigit() and int(f[1])==pgid and int(f[0])!=pgid and not f[2].startswith("Z"):
            surv.append((int(f[0]),f[2])); seen.add(int(f[0]))
    for ln in ps.splitlines():
        f=ln.split(None,3)
        if len(f)==4 and f[0].isdigit() and int(f[0]) not in seen and int(f[0])!=pgid and not f[2].startswith("Z") and (workdir+"/interp_") in f[3]:
            surv.append((int(f[0]),f[2])); seen.add(int(f[0]))
    return surv

def one(hook, sig, delay, workdir):
    home=os.path.join(workdir,"home")
    if os.path.exists(home): shutil.rmtree(home, ignore_errors=True)
    os.makedirs(home); contract.build_home(home,"")
    target=contract.make_interp_variant(hook, workdir, "hang")
    env={"HOME":home,"PATH":"/usr/bin:/bin:/usr/sbin:/sbin","SHELL":"/bin/zsh","LANG":"en_US.UTF-8","TERM":"dumb"}
    rfd,wfd=os.pipe(); t0=time.time()
    p=subprocess.Popen(contract.INVOC+[target,"manual"],stdin=rfd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env,cwd=workdir,preexec_fn=lambda:os.setpgid(0,0))
    os.close(rfd)
    try: os.write(wfd,GOOD[:20])
    except OSError: pass
    delivered=False; alive=None
    while True:
        try: wpid,st=os.waitpid(p.pid,os.WNOHANG)
        except ChildProcessError: break
        if wpid==p.pid: break
        now=time.time()
        if not delivered and now-t0>=delay:
            try:
                os.kill(p.pid,0); alive = (contract._proc_state(p.pid)!="Z")
            except OSError: alive=False
            try: os.kill(p.pid, sig)
            except OSError: pass
            delivered=True
            try: os.close(wfd); wfd=None
            except OSError: pass
        if now-t0>6:
            try: os.killpg(p.pid,signal.SIGKILL)
            except OSError: pass
            break
        time.sleep(0.02)
    time.sleep(0.35)
    surv=scan(p.pid, workdir)
    for pid,_ in surv:
        try: os.kill(pid,9)
        except OSError: pass
    try: os.killpg(p.pid,signal.SIGKILL)
    except OSError: pass
    if wfd is not None:
        try: os.close(wfd)
        except OSError: pass
    return alive, len(surv)

def trials(hook, tag, n=10):
    wd=os.path.join(os.path.dirname(os.path.abspath(__file__)),"mrepwd_"+tag)
    if os.path.exists(wd): shutil.rmtree(wd, ignore_errors=True)
    os.makedirs(wd)
    landed=0; maxorph=0; orphaned_runs=0; delays=[0.15,0.25,0.35]
    for i in range(n):
        alive,orph=one(hook, signal.SIGTERM, delays[i%3], wd)
        if alive is True:
            landed+=1
            if orph>0: orphaned_runs+=1
            maxorph=max(maxorph,orph)
    print("%-5s trials=%d  signal_landed=%d  runs_with_orphan=%d  max_orphans=%d"%(tag,n,landed,orphaned_runs,maxorph))
    return orphaned_runs, landed

if __name__=="__main__":
    cand="candidate"
    print("H1 multi-trial (H01 hang + pid-directed SIGTERM during hang):")
    o22,l22=trials(os.path.join(cand,"v22-installed.sh"),"v22")
    o26,l26=trials(os.path.join(cand,"v26.sh"),"v26")
    o27,l27=trials(os.path.join(cand,"v27.sh"),"v27")
    print()
    print("v22: orphaned in %d landed runs -> %s"%(o22,"LEAKS (H1 present)" if o22>0 else "clean"))
    print("v26: orphaned in %d landed runs -> %s"%(o26,"LEAKS (H1 present)" if o26>0 else "clean"))
    print("v27: orphaned in %d landed runs -> %s"%(o27,"LEAKS" if o27>0 else "CLEAN (H1 fixed)"))
    ok = (o26>0 and o27==0 and l27>0)
    print("\n%s"%("*** DISCRIMINATED: v26 leaks, v27 clean across %d landed trials ***"%l27 if ok else "INCONCLUSIVE (need more landed trials or unexpected)"))
