#!/usr/bin/env python3
"""Prove a change is comment-only: executable text must be byte-identical.

This is what lets a documentation fix inherit an existing approval instead of
forcing a full re-review — but only if it is PROVEN, not asserted.
Executable text = every line that is neither blank nor a `#` comment, plus the
shebang (line 1), joined with \n. Comment/blank lines are erased, not skipped,
so a comment that hides an executable line cannot pass.
"""
import hashlib, sys

def exectext(path):
    out = []
    for i, l in enumerate(open(path).read().split("\n"), 1):
        s = l.strip()
        if i == 1 and l.startswith("#!"):
            out.append(l); continue
        if not s or s.startswith("#"): continue
        out.append(l)
    return "\n".join(out)

def main():
    a, b = sys.argv[1], sys.argv[2]
    ta, tb = exectext(a), exectext(b)
    ha = hashlib.sha256(ta.encode()).hexdigest()
    hb = hashlib.sha256(tb.encode()).hexdigest()
    print(f"A {a}\n  exec lines={ta.count(chr(10))+1} sha256={ha}")
    print(f"B {b}\n  exec lines={tb.count(chr(10))+1} sha256={hb}")
    if ha == hb:
        print("EXEC-TEXT IDENTICAL -> change is comment-only")
        sys.exit(0)
    print("EXEC-TEXT DIFFERS -> NOT a comment-only change")
    la, lb = ta.split("\n"), tb.split("\n")
    import difflib
    for d in list(difflib.unified_diff(la, lb, "A", "B", lineterm="", n=1))[:40]:
        print("  " + d)
    sys.exit(1)

main()
