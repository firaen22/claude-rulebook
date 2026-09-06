#!/bin/bash
# test_reconcile_template.sh -- regression-lock the reusable pairing engine.
#
# Drives the FULL reconcile_pairs fixture suite (65 cases + 2 self-controls)
# against reconcile_template.py's CompactionAdapter, via a shim that relabels
# only the two SUMMARY field names (BEFORE/AFTER -> PC/SSC, the one intended
# divergence). A GREEN run proves the extracted generic engine reproduces the
# original's behavior on every fixture -- dup identity, inversion, --since
# straddle, lone surrogate, unreadable file, bad args -- not merely on the live
# directory. The suite's own two positive controls (always-CLEAN stub; corrupted
# -count wrapper) still certify the checker can fail.
#
# Usage: test_reconcile_template.sh
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
exec "$HERE/test_reconcile_pairs.sh" "$HERE/reconcile_template_compaction_shim.py"
