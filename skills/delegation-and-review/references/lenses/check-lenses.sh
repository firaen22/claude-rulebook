#!/bin/bash
# Gate for the lens library. Run after ANY edit to a lens or to ROUTER.md.
#   bash ~/.claude/skills/delegation-and-review/references/lenses/check-lenses.sh
# Exit 0 = pass, 1 = a lens violates the contract, 2 = the gate could not run.
#
# WHY THIS EXISTS: the first version of this library carried a "<=30 lines" rule
# as prose. It was violated by 5 of 6 files on the day it was written, and the
# fixes for the review findings pushed it further out. A number nobody checks is
# not a constraint. Written 2026-08-29 after a cross-model review said so.

set -u
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || exit 2
ROUTER="$DIR/ROUTER.md"
MAX_LINES=40          # per lens file, physical lines incl. headings and blanks
MAX_WPL=13            # prose words per line (harness §4 density twin)
fail=0

[ -f "$ROUTER" ] || { echo "GATE ERROR: no ROUTER.md in $DIR" >&2; exit 2; }

# 1. Every lens obeys the length cap.
for f in "$DIR"/*.md; do
  b="$(basename "$f")"
  [ "$b" = "ROUTER.md" ] && continue
  n=$(wc -l < "$f" | tr -d ' ')
  if [ "$n" -gt "$MAX_LINES" ]; then
    echo "FAIL length: $b is $n lines (max $MAX_LINES)"
    fail=1
  fi
done

# 2. Every lens obeys the prose density twin.
for f in "$DIR"/*.md; do
  b="$(basename "$f")"
  w=$(awk '!/^[[:space:]]*\|/ && !/^[[:space:]]*`/ && NF {t+=NF; l++} END {if(l) printf "%.1f", t/l; else print "0"}' "$f")
  over=$(awk -v w="$w" -v m="$MAX_WPL" 'BEGIN {print (w>m) ? 1 : 0}')
  if [ "$over" = "1" ]; then
    echo "FAIL density: $b is $w words/line (max $MAX_WPL)"
    fail=1
  fi
done

# 3. Every lens named in the ROUTER table exists on disk.
grep -o '`[a-z-]*\.md`' "$ROUTER" | tr -d '`' | sort -u | while read -r lens; do
  [ "$lens" = "ROUTER.md" ] && continue
  [ -f "$DIR/$lens" ] || echo "FAIL missing: ROUTER.md points at $lens which does not exist"
done > /tmp/lens-missing.$$ 2>/dev/null
if [ -s /tmp/lens-missing.$$ ]; then cat /tmp/lens-missing.$$; fail=1; fi
rm -f /tmp/lens-missing.$$

# 4. Every lens on disk is reachable from the ROUTER table.
for f in "$DIR"/*.md; do
  b="$(basename "$f")"
  [ "$b" = "ROUTER.md" ] && continue
  grep -q "\`$b\`" "$ROUTER" || { echo "FAIL orphan: $b is not named in ROUTER.md"; fail=1; }
done

if [ "$fail" -eq 0 ]; then echo "lens gate PASS"; fi
exit "$fail"
