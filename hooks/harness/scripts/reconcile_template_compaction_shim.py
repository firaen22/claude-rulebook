#!/usr/bin/env python3
"""Shim: drive reconcile_template.py's CompactionAdapter through the compaction
fixture suite (test_reconcile_pairs.sh), which asserts SUMMARY tokens in the
compaction vocabulary (PC=/SSC=).

It runs the template's REAL CLI as a subprocess -- so argparse, exit codes, and
every finding line are the template's own, untouched -- and rewrites ONLY the two
SUMMARY field names `BEFORE=`->`PC=` and `AFTER=`->`SSC=`. That rename is the one
intended, documented divergence between the generic engine and the original; the
ANOMALY/VOID/ORPHAN lines already match because they use the adapter's labels
(PreCompact / SessionStart/compact). `BEFORE=`/`AFTER=` appear only in the SUMMARY
line, never in a finding line, so the rewrite cannot touch anything else.

A GREEN suite through this shim regression-locks the extracted engine against all
65 fixtures, not just the live directory.
"""
import os
import re
import subprocess
import sys

TMPL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "harness", "reconcile_template.py")
p = subprocess.run([sys.executable, TMPL] + sys.argv[1:],
                   capture_output=True, text=True)
out = re.sub(r"\bBEFORE=", "PC=", p.stdout)
out = re.sub(r"\bAFTER=", "SSC=", out)
sys.stdout.write(out)
sys.stderr.write(p.stderr)
sys.exit(p.returncode)
