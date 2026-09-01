#!/bin/bash
# Token-lean full verification of one hook candidate.
#   scripts/run_all.sh [candidate.sh] [label] [--pidhang]
# Prints ONE line per instrument (PASS/FAIL + summary); every instrument's full
# output goes to $WORK/<instrument>.log. Exit 1 if any instrument fails.
# --pidhang adds the slow 4-version H1 differential (v22/v26/v27/v28, several min).
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CAND="${1:-$ROOT/candidate/v28.sh}"; LABEL="${2:-$(basename "${CAND%.sh}")}"
WORK="${WORK:-${TMPDIR:-/tmp}/hook-harness-$LABEL}"
chmod -R u+rwx "$WORK" 2>/dev/null; rm -rf "$WORK"; mkdir -p "$WORK"
bad=0
run() {  # name, command...
  local name="$1"; shift
  "$@" > "$WORK/$name.log" 2>&1; local rc=$?
  local last; last="$(grep -E '^(FAIL|PASS|\[|DISCRIMINATED|INCONCLUSIVE)' "$WORK/$name.log" | tail -1)"
  printf '%-8s %s %s\n' "$name" "$([ $rc -eq 0 ] && echo PASS || echo FAIL)" "${last:-<no summary line; see $WORK/$name.log>}"
  [ $rc -eq 0 ] || bad=1
}
cd "$ROOT"
run contract python3 harness/contract.py "$CAND" "$LABEL" "$WORK/contract"
run gap      python3 harness/gap.py "$WORK/gap" "$CAND"
run grpsig2  python3 harness/grpsig2.py "$WORK/grpsig2" "$CAND"
if [ "${3:-}" = "--pidhang" ]; then run pidhang python3 harness/pidhang.py; fi
echo "logs: $WORK"
exit $bad
