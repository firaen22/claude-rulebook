import sys, os, time, subprocess, signal, shutil, re
HF=os.path.join(os.path.dirname(os.path.abspath(__file__)),"harness-frozen3")
sys.path.insert(0,HF); import contract
GOOD=b'{"session_id":"abc","transcript_path":"/tmp/x.jsonl","hook_event_name":"PreCompact","trigger":"manual"}'

# a setsid-then-spin stub masquerading as the pinned interpreter
STUB_BODY = ("#!/usr/bin/env python3\n"
             "import os,sys,time\n"
             "try: os.setsid()\n"
             "except OSError: pass\n"
             "open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'READY'),'w').close()\n"
             "while True: time.sleep(1)\n")

def make_setsid_variant(hook, workdir):
    bindir=os.path.join(workdir,"interp_setsid"); os.makedirs(bindir,exist_ok=True)
    stub=os.path.join(bindir,"python3")
    open(stub,"w").write(STUB_BODY); os.chmod(stub,0o755)
    src=open(hook).read()
    m=re.search(r'^([ \t]*)for _p in /Library/Developer/CommandLineTools/usr/bin/python3 \\\n[ \t]*/usr/bin/python3; do',src,re.M)
    assert m,"anchor"
    ind=m.group(1)
    new="%sfor _p in %s \\\n%s          /usr/bin/python3; do"%(ind,stub,ind)
    out=os.path.join(workdir,"hook_setsid.sh"); open(out,"w").write(src[:m.start()]+new+src[m.end():]); os.chmod(out,0o755)
    return out, bindir

def scan(hook_pgid, bindir):
    ps=subprocess.run(["/bin/ps","-axo","pid=,pgid=,state=,command="],capture_output=True,text=True,timeout=10).stdout
    surv=[]
    for ln in ps.splitlines():
        f=ln.split(None,3)
        if len(f)==4 and f[0].isdigit() and int(f[0])!=hook_pgid and not f[2].startswith("Z") and bindir in f[3]:
            surv.append((int(f[0]),int(f[1]),f[2]))
    return surv

def run(hook,tag):
    wd=os.path.join(os.path.dirname(os.path.abspath(__file__)),"f2wd_"+tag)
    if os.path.exists(wd): shutil.rmtree(wd,ignore_errors=True)
    os.makedirs(wd)
    home=os.path.join(wd,"home"); os.makedirs(home); contract.build_home(home,"")
    target,bindir=make_setsid_variant(hook,wd)
    ready=os.path.join(bindir,"READY")
    env={"HOME":home,"PATH":"/usr/bin:/bin:/usr/sbin:/sbin","SHELL":"/bin/zsh","LANG":"en_US.UTF-8","TERM":"dumb"}
    rfd,wfd=os.pipe(); t0=time.time()
    p=subprocess.Popen(contract.INVOC+[target,"manual"],stdin=rfd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                       env=env,cwd=wd,preexec_fn=lambda: os.setpgid(0,0))
    os.close(rfd)
    try: os.write(wfd,GOOD[:20])
    except OSError: pass
    delivered=False; alive=None
    while True:
        try: wpid,st=os.waitpid(p.pid,os.WNOHANG)
        except ChildProcessError: break
        if wpid==p.pid: break
        now=time.time()
        fire = os.path.lexists(ready) or (now-t0>=1.5)
        if not delivered and fire:
            try: os.kill(p.pid,0); alive=True
            except OSError: alive=False
            try: os.killpg(p.pid,signal.SIGKILL)   # GROUP-directed KILL from the "caller"
            except OSError: pass
            delivered=True
            try: os.close(wfd); wfd=None
            except OSError: pass
        if now-t0>8:
            try: os.killpg(p.pid,signal.SIGKILL)
            except OSError: pass
            break
        time.sleep(0.02)
    time.sleep(0.4)
    surv=scan(p.pid,bindir)
    for pid,_,_ in surv:
        try: os.kill(pid,9)
        except OSError: pass
    if wfd is not None:
        try: os.close(wfd)
        except OSError: pass
    print("%-6s ready_gated=%s alive_at_signal=%s  detached_survivors=%d %s"%(
        tag, os.path.lexists(ready), alive, len(surv), [(s[0],'pgid=%d'%s[1],s[2]) for s in surv]))
    return len(surv)

if __name__=="__main__":
    r={}
    for h,t in [("v22-installed","v22"),("v26","v26"),("v27","v27")]:
        r[t]=run(os.path.join("candidate",h+".sh"),t)
    print()
    print("F2 (setsid-detached probe + caller group-KILL):")
    for t in ["v22","v26","v27"]:
        print("  %s: %d survivor(s) -> %s"%(t,r[t],"LEAKS (topology limit)" if r[t]>0 else "clean"))
    print("\nCONCLUSION:", "F2 is PRE-EXISTING in the approved live v22 (not a v27 regression)" if r["v22"]>0 else "v22 clean (F2 would be new)")
