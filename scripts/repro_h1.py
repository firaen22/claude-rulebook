import sys, os, time, subprocess, signal, shutil
HF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "harness-frozen2")
sys.path.insert(0, HF)
import contract

GOOD = b'{"session_id":"abc","transcript_path":"/tmp/x.jsonl","hook_event_name":"PreCompact","trigger":"manual"}'

def scan(pgid, workdir):
    ps = subprocess.run(["/bin/ps","-axo","pid=,pgid=,state=,command="],
                        capture_output=True, text=True, timeout=10).stdout
    surv=[]; seen=set()
    for ln in ps.splitlines():
        f=ln.split(None,3)
        if len(f)>=3 and f[1].isdigit() and int(f[1])==pgid and int(f[0])!=pgid and not f[2].startswith("Z"):
            surv.append((int(f[0]),f[2],f[3] if len(f)==4 else "")); seen.add(int(f[0]))
    for ln in ps.splitlines():
        f=ln.split(None,3)
        if len(f)==4 and f[0].isdigit() and int(f[0]) not in seen and int(f[0])!=pgid \
           and not f[2].startswith("Z") and (workdir+"/interp_") in f[3]:
            surv.append((int(f[0]),f[2],f[3])); seen.add(int(f[0]))
    return surv

def run(hook, tag):
    workdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reprowd_"+tag)
    if os.path.exists(workdir): shutil.rmtree(workdir)
    os.makedirs(workdir)
    home = os.path.join(workdir,"home"); os.makedirs(home)
    contract.build_home(home, "")
    target = contract.make_interp_variant(hook, workdir, "hang")
    env={"HOME":home,"PATH":"/usr/bin:/bin:/usr/sbin:/sbin","SHELL":"/bin/zsh","LANG":"en_US.UTF-8","TERM":"dumb"}
    rfd,wfd=os.pipe()
    t0=time.time()
    p=subprocess.Popen(contract.INVOC+[target,"manual"], stdin=rfd,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       env=env, cwd=workdir, preexec_fn=lambda: os.setpgid(0,0))
    os.close(rfd)
    try: os.write(wfd, GOOD[:20])
    except OSError: pass
    delivered=False; sig_ok=None
    while True:
        try: wpid,st=os.waitpid(p.pid, os.WNOHANG)
        except ChildProcessError: break
        if wpid==p.pid: break
        now=time.time()
        if not delivered and now-t0>=0.35:
            try: os.kill(p.pid,0); sig_ok=True
            except OSError: sig_ok=False
            try: os.kill(p.pid, signal.SIGTERM)
            except OSError: pass
            delivered=True
            try: os.close(wfd); wfd=None
            except OSError: pass
        if now-t0>12:
            try: os.killpg(p.pid, signal.SIGKILL)
            except OSError: pass
            break
        time.sleep(0.02)
    pexit=time.time()-t0
    time.sleep(0.4)                      # let any orphan be visibly spinning
    surv=scan(p.pid, workdir)
    for pid,_,_ in surv:
        try: os.kill(pid,9)
        except OSError: pass
    try: os.killpg(p.pid, signal.SIGKILL)
    except OSError: pass
    if wfd is not None:
        try: os.close(wfd)
        except OSError: pass
    print("%-22s parent_exit=%5.2fs  alive_at_signal=%s  survivors=%d" % (tag, pexit, sig_ok, len(surv)))
    for pid,stt,cmd in surv:
        print("      pid=%-7d state=%-4s cmd=%s" % (pid, stt, cmd[:100]))
    return len(surv)

if __name__=="__main__":
    cand=os.path.join(os.path.dirname(os.path.abspath(__file__)),"candidate")
    n22=run(os.path.join(cand,"v22-installed.sh"), "v22_H01+pidTERM")
    n26=run(os.path.join(cand,"v26.sh"),           "v26_H01+pidTERM")
    print("\nH1 CONFIRMED on v26" if n26>0 else "\nH1 NOT reproduced on v26")
    print("pre-existing on v22" if n22>0 else "v22 clean (so v26 would be a regression)")
