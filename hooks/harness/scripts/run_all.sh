#!/bin/bash
# Token-lean full verification of one hook candidate.
#   scripts/run_all.sh [candidate.sh] [label] [--pidhang]
# Prints ONE line per instrument (PASS/FAIL + summary); every instrument's full
# output goes to $WORK/<instrument>.log. Exit 1 if any instrument fails.
# --pidhang adds the slow H1 differential (several min): the v26 positive control,
# which must still leak, versus the candidate under test, which must not.
#
# BLIND SPOT (re-run policy): this grades SYNTHETIC state, so it can only see a
# VOID where a file was expected and none appeared. The live D_pid_INT-class VOID
# is SILENT (exit 0, no file at all) and invisible here by construction. A green
# run is necessary, not sufficient -- pair it with harness/reconcile_pairs.py
# --since <recent> against the live observed/ dir. See README "re-run policy" and
# the passive-VOID-detection section.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# --pidhang is a FLAG, accepted in any position. It used to be read only at $3,
# so the natural 2-arg form `run_all.sh cand.sh --pidhang` bound it to LABEL and
# silently skipped the instrument -- an all-green report with H1 never run.
usage() { echo "usage: run_all.sh [candidate.sh] [label] [--pidhang]" >&2; exit 2; }
PIDHANG=0; POS=()
for _a in "$@"; do
  case "$_a" in
    --pidhang) PIDHANG=1 ;;
    # A mistyped flag must never be absorbed as a positional and ignored:
    # `run_all.sh cand.sh label --pidhnag` silently skipped the instrument and
    # still finished green. Unknown options and extra positionals are errors.
    --*)       echo "run_all.sh: unknown option '$_a'" >&2; usage ;;
    *)         POS+=("$_a") ;;
  esac
done
[ "${#POS[@]}" -le 2 ] || { echo "run_all.sh: too many arguments (${#POS[@]})" >&2; usage; }
CAND="${POS[0]:-$ROOT/candidate/v28.sh}"
# Resolve the candidate BEFORE the `cd "$ROOT"` below. Every instrument opens
# "$CAND" from ROOT, so a relative path was checked against the caller's cwd and
# then GRADED from ROOT: running `run_all.sh candidate/v28.sh` from a directory
# holding your own broken candidate/v28.sh certified ROOT's good file instead --
# 57/57 pass, exit 0, with only the md5 in the report to give it away.
case "$CAND" in /*) ;; *) CAND="$PWD/$CAND" ;; esac
LABEL="${POS[1]:-$(basename "${CAND%.sh}")}"
[ -f "$CAND" ] || { echo "run_all.sh: candidate not found: $CAND" >&2; exit 2; }
# The default WORK is UNIQUE per run. It used to be $TMPDIR/hook-harness-$LABEL, so
# two concurrent runs with the same label shared one directory: each rm -rf'd the
# other's files, and -- since survivors are attributed by cwd == workdir -- run A
# counted and SIGKILLed run B's leaked descendant before B scanned, and B then
# reported 1/1 pass on a leaking hook (measured 2026-09-05: a FALSE GREEN). An
# explicit WORK=... is honoured as before; never point two live runs at one dir.
if [ -z "${WORK:-}" ]; then
  # LABEL is grading metadata; only a slash-free form goes into the pathname
  # (`run_all.sh v28.sh release/28` made mktemp look for a nonexistent parent).
  _safe="$(printf '%s' "$LABEL" | tr -c 'A-Za-z0-9._-' '_')"
  WORK="$(mktemp -d "${TMPDIR:-/tmp}/hook-harness-$_safe.XXXXXX")" || { echo "run_all.sh: mktemp failed" >&2; exit 2; }
else
  # An explicit WORK is about to be rm -rf'd: refuse if any live process still
  # has its cwd under it (another run), instead of deleting that run's files.
  python3 -c 'import sys; sys.path.insert(0, sys.argv[2]); import contract; contract.require_exclusive_workdir(sys.argv[1], "run_all", lock=False)' "$WORK" "$ROOT/harness" || exit 2
  chmod -R u+rwx "$WORK" 2>/dev/null; rm -rf "$WORK"; mkdir -p "$WORK"
fi
bad=0
run() {  # name, command...
  local name="$1"; shift
  "$@" > "$WORK/$name.log" 2>&1; local rc=$?
  local last; last="$(grep -E '^(FAIL|PASS|\[|DISCRIMINATED|INCONCLUSIVE)' "$WORK/$name.log" | tail -1)"
  # An instrument that exits 0 without emitting a recognised summary line has not
  # been shown to have RUN. Grading on rc alone reported PASS for a silent no-op
  # (gap.py's no-anchor path did exactly this), so absence of a verdict is a FAIL.
  local verdict=PASS
  [ $rc -eq 0 ] || verdict=FAIL
  if [ -z "$last" ]; then verdict=FAIL; last="<NO SUMMARY LINE -- instrument produced no verdict; see $WORK/$name.log>"; fi
  # An instrument that PRINTS a failure and still exits 0 must not be graded on
  # its rc: that exact shape (gap.py's "FAIL ... " with rc 0) is what made this
  # runner report "gap PASS FAIL M6_no_stop_traps.sh ...". The printed verdict
  # loses to nothing -- if it says FAIL or INCONCLUSIVE, the instrument failed.
  #
  # Scan the WHOLE log, not just the last matching line: `tail -1` let a later
  # "PASS cleanup" mask an earlier "FAIL", and a contract summary reading
  # "[v28] 56/57 pass, 1 FAIL" starts with '[' so it never matched FAIL* at all.
  if grep -qE '^(FAIL|INCONCLUSIVE)' "$WORK/$name.log" \
     || grep -qE '[,[:space:]][1-9][0-9]* FAIL' "$WORK/$name.log"; then
    verdict=FAIL
  fi
  printf '%-8s %s %s\n' "$name" "$verdict" "$last"
  [ "$verdict" = PASS ] || bad=1
}
cd "$ROOT"
run contract python3 harness/contract.py "$CAND" "$LABEL" "$WORK/contract"
run gap      python3 harness/gap.py "$WORK/gap" "$CAND"
run grpsig2  python3 harness/grpsig2.py "$WORK/grpsig2" "$CAND"
if [ "$PIDHANG" = 1 ]; then run pidhang python3 harness/pidhang.py "$CAND"; fi
echo "logs: $WORK"
exit $bad
