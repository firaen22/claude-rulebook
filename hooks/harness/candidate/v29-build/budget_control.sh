#!/bin/bash -p
# Positive control for the v30 probe-budget fix (finding_harness_rerun_void_2026-09-06).
# Replicates the hook's probe budget EXACTLY (whole-second SECONDS, kill-at-tick,
# /bin/sleep 0.05 poll) around a background "probe" that needs STARTUP seconds to
# reach its exit-37. Runs many trials at UNCONTROLLED sub-second phases for a given
# +N budget and reports how many were KILLED before the probe finished (= a dropped
# event). Expectation: +1 drops a few %, +2 drops 0. This is the control the finding
# says the first "REJECTED" verdict lacked.
#   usage: budget_control.sh <N_add> <trials> <startup_secs>
N_ADD="${1:?N_add}"; TRIALS="${2:?trials}"; STARTUP="${3:?startup_secs}"
killed=0; done_ok=0
for _t in $(seq 1 "$TRIALS"); do
  # de-synchronise from the second boundary so phases spread across (0,1]
  /bin/sleep 0.0$((RANDOM % 100)) 2>/dev/null || true
  _pend=$(( SECONDS + N_ADD ))
  ( /bin/sleep "$STARTUP"; exit 37 ) </dev/null >/dev/null 2>&1 &
  _pp=$!
  _pkilled=no
  while :; do
    _prun=$(jobs -pr)
    case "
$_prun
" in
      *"
$_pp
"*) : ;;
      *) break ;;
    esac
    if [ "$SECONDS" -ge "$_pend" ]; then
      kill -KILL "$_pp" 2>/dev/null || true
      _pkilled=yes
      break
    fi
    /bin/sleep 0.05 </dev/null >/dev/null 2>&1 || true
  done
  if [ "$_pkilled" = yes ]; then
    killed=$((killed+1))
  else
    if wait "$_pp" 2>/dev/null; then :; else [ $? -eq 37 ] && done_ok=$((done_ok+1)); fi
  fi
done
printf 'N_ADD=+%s trials=%s startup=%ss  KILLED(dropped)=%s  reached-37=%s\n' \
  "$N_ADD" "$TRIALS" "$STARTUP" "$killed" "$done_ok"
