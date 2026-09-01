#!/usr/bin/env python3
"""Self-consistency check: every `line NNN` reference in the comments must
point at a line that still says what the reference implies.

Rule: a documentation reference to "line N" is stale unless line N is an
EXECUTABLE line (not blank, not a comment). Comments describing code by line
number rot silently every time a line is inserted above them; nothing else in
the review pipeline catches it, because it never changes behaviour.
"""
import re, sys, json

REF = re.compile(r"\bline\s+(\d+)", re.I)

def classify(l, n=None):
    if n == 1 and l.startswith("#!"): return "exec"   # shebang IS executable config
    s = l.strip()
    if not s: return "blank"
    if s.startswith("#"): return "comment"
    return "exec"

def main():
    path = sys.argv[1]
    lines = open(path).read().split("\n")
    bad, ok = [], []
    for i, l in enumerate(lines, 1):
        if classify(l, i) != "comment": continue
        for m in REF.finditer(l):
            n = int(m.group(1))
            if n < 1 or n > len(lines):
                bad.append((i, n, "OUT-OF-RANGE", "")); continue
            tgt = lines[n-1]
            k = classify(tgt, n)
            rec = (i, n, k, tgt.strip()[:78])
            (ok if k == "exec" else bad).append(rec)
    print(f"{path}\n  references: {len(ok)+len(bad)}   STALE: {len(bad)}")
    for i, n, k, t in bad:
        print(f"  STALE  comment L{i} -> 'line {n}' is {k}: {t!r}")
    for i, n, k, t in ok:
        print(f"  ok     comment L{i} -> 'line {n}' = {t!r}")
    json.dump({"file": path, "stale": bad, "ok": ok},
              open(sys.argv[2], "w") if len(sys.argv) > 2 else sys.stdout, indent=1)
    sys.exit(1 if bad else 0)

main()
