#!/usr/bin/env python3
"""Generate mutants that each violate exactly ONE contract clause.

A harness that cannot fail is not evidence. Each mutant below has a DECLARED
contract it must break; if the harness passes it, the harness is broken.
"""
import os, re, sys

def load(p): return open(p).readlines()
def save(p, l):
    open(p, "w").writelines(l); os.chmod(p, 0o755)

def find(lines, rx, start=0):
    r = re.compile(rx)
    for i in range(start, len(lines)):
        if r.match(lines[i]): return i
    return None

def main():
    src, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    os.makedirs(out, exist_ok=True)
    base = load(src)
    trap_i   = find(base, r"^\s*(builtin\s+)?trap\s+'.*exit 0'.*\bHUP\b")
    exec_i   = find(base, r"^exec\s+>/dev/null")
    lastexit = max(i for i, l in enumerate(base) if re.match(r"^\s*(builtin\s+)?exit 0\s*$", l))
    made = []

    def emit(name, lines, breaks):
        p = os.path.join(out, name + ".sh"); save(p, lines); made.append((name, breaks))

    # C2: a byte on real stdout, emitted BEFORE the redirect to /dev/null
    m = list(base); m.insert(exec_i, "builtin printf 'LEAK'\n")
    emit("M1_stdout_leak", m, "C2")
    # C1: nonzero final exit
    m = list(base); m[lastexit] = "builtin exit 3\n"
    emit("M2_nonzero_exit", m, "C1")
    # C3: unbounded spin before exiting
    m = list(base); m.insert(lastexit, "while builtin :; do builtin :; done\n")
    emit("M3_infinite_hang", m, "C3")
    # C4: destroys a pre-existing file
    m = list(base); m.insert(lastexit, '/bin/rm -rf "${HOME}/precious" 2>/dev/null\n')
    emit("M4_destroys_file", m, "C4")
    # C1 under signals: no signal traps at all
    m = [l for l in base if not re.match(r"^\s*(builtin\s+)?trap\s+", l)]
    emit("M5_no_traps", m, "C1-signal")
    # C1/C3 under stop signals: the round 19 regression, reintroduced
    m = [re.sub(r"\s+TSTP TTIN TTOU", "", l) if re.match(r"^\s*(builtin\s+)?trap\s+", l) else l
         for l in base]
    m = [l for l in m if not re.match(r"^\s*(builtin\s+)?trap\s+''\s*$", l)]
    emit("M6_no_stop_traps", m, "C1/C3-stop")
    # C2: stdout leak from the worker path (post-redirect fd 1 restored)
    m = list(base); m.insert(exec_i + 1, "builtin exec 1>&2 2>/dev/null\nbuiltin printf 'LEAK2' >&2\n")
    emit("M7_fd_shuffle_leak", m, "C2-or-none")
    for n, b in made:
        print(f"{n:<22} breaks={b}")
    print(f"anchors: trap@{trap_i+1} exec@{exec_i+1} lastexit@{lastexit+1}")

main()
