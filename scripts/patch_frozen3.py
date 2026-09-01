import os, re
R = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(R,"harness-frozen3","contract.py")
s = open(p).read()

# (1) make_interp_variant: indentation-agnostic anchor
old_anchor = '''    src = open(target).read()
    old = ("  for _p in /Library/Developer/CommandLineTools/usr/bin/python3 \\\\\\n"
           "            /usr/bin/python3; do")
    assert old in src, "interpreter candidate list anchor not found"
    new = "  for _p in %s \\\\\\n            /usr/bin/python3; do" % stub
    out = os.path.join(workdir, "hook_interp_%s.sh" % mode)
    with open(out, "w") as f: f.write(src.replace(old, new))'''
new_anchor = '''    src = open(target).read()
    # ROUND 27: match the candidate-list `for` regardless of indentation, so the
    # same harness drives v26 (probe nested in the worker, 2-space indent) and
    # v27 (probe hoisted to the parent, column-0 indent).
    m = re.search(r'^([ \\t]*)for _p in /Library/Developer/CommandLineTools/usr/bin/python3 \\\\\\n[ \\t]*/usr/bin/python3; do',
                  src, re.M)
    assert m, "interpreter candidate list anchor not found"
    indent = m.group(1)
    new_block = "%sfor _p in %s \\\\\\n%s          /usr/bin/python3; do" % (indent, stub, indent)
    src2 = src[:m.start()] + new_block + src[m.end():]
    out = os.path.join(workdir, "hook_interp_%s.sh" % mode)
    with open(out, "w") as f: f.write(src2)'''
assert old_anchor in s, "make_interp_variant block not found verbatim"
s = s.replace(old_anchor, new_anchor)

# ensure `import re` present
if "\nimport re\n" not in s and not s.startswith("import re"):
    s = s.replace("import os", "import os, re", 1)

# (2) cases(): add H05 combined cases after the H04 line
h04 = 'A(("H04_interp_stdout",     "interp",   ["manual"], good, {"__V": "noisy"}, "noisy", "candidate passes probe then floods stdout"))'
assert h04 in s
h05 = (h04 +
'\n    # --- ROUND 27: interpreter hang COMBINED with a PID-directed parent signal.\n'
'    # This is the blind spot grok named on v26: contract had H01 (hang) and\n'
'    # D_pid_* (pid signal) but never one case with BOTH. A terminating signal to\n'
'    # the hook while a probe hangs fires the top-of-file trap; if the hung probe\n'
'    # is not a direct child of the parent, the trap misses it and it spins on as\n'
'    # an orphan (v26 H1). Expect: v22 FAIL, v26 FAIL, v27 PASS.\n'
'    for s in ["TERM", "INT", "HUP"]:\n'
'        A((f"H05_interp_hang_pid_{s}", "interp_pidsig", ["manual"], good, {}, "hang",\n'
'           f"first interpreter hangs AND {s} to hook pid mid-probe"))')
s = s.replace(h04, h05)

# fix L2 note wording
s = s.replace('"fail", "every candidate fails the 1337 probe"', '"fail", "first candidate fails the exit-37 probe (second is the real python3)"')

# (3) run_case: variant rewrite for interp_pidsig
s = s.replace('    if kind == "interp":\n        target = make_interp_variant(target, workdir, variant)',
              '    if kind in ("interp", "interp_pidsig"):\n        target = make_interp_variant(target, workdir, variant)')
assert 'kind in ("interp", "interp_pidsig")' in s, "variant rewrite patch failed"

# signal delivery condition
s = s.replace('if not delivered and kind in ("sig_pid", "sig_grp") and now - t0 >= SIGDELAY:',
              'if not delivered and kind in ("sig_pid", "sig_grp", "interp_pidsig") and now - t0 >= SIGDELAY:')
assert 'kind in ("sig_pid", "sig_grp", "interp_pidsig") and now - t0' in s, "delivery cond patch failed"

# delivery branch (pid vs grp)
s = s.replace('if kind == "sig_pid": os.kill(p.pid, sig_sent)',
              'if kind in ("sig_pid", "interp_pidsig"): os.kill(p.pid, sig_sent)')
assert 'if kind in ("sig_pid", "interp_pidsig"): os.kill' in s, "delivery branch patch failed"

# (4) grade VOID-check includes interp_pidsig
s = s.replace('if act.get("kind") in ("sig_pid", "sig_grp") and act.get("alive_at_signal") is not True:',
              'if act.get("kind") in ("sig_pid", "sig_grp", "interp_pidsig") and act.get("alive_at_signal") is not True:')
assert 'in ("sig_pid", "sig_grp", "interp_pidsig") and act.get("alive_at_signal")' in s, "grade VOID patch failed"

open(p,"w").write(s)
print("patched frozen3 contract.py OK")
