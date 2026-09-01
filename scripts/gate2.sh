#!/bin/bash
R=/private/tmp/claude-501/-Users-yauch-Documents-claude-code-technique/d8a69179-c2ab-4c5b-927b-3b9417b15cb6/scratchpad/round23
F="$R/harness-frozen"; L="$R/out/GATE2.log"; : > "$L"
run(){ /usr/bin/python3 "$F/contract.py" "$1" "$2" "$R/out/g2_$2" 2>&1 | tail -25; }
{
echo "FROZEN contract.py=$(md5 -q $F/contract.py) gap.py=$(md5 -q $F/gap.py)"
echo "########## CANDIDATES (expect: only H01_interp_hangs fails) ##########"
run "$R/candidate/v22-installed.sh" v22
run "$R/candidate/v23.sh"           v23
echo "########## MUTANT MATRIX (expect: EVERY mutant caught) ##########"
} >> "$L"
for m in "$R"/mutants/M*.sh; do
  b=$(basename "$m" .sh)
  o=$(run "$m" "$b")
  n=$(printf '%s\n' "$o" | grep -c '^FAIL')
  if [ "$n" -gt 0 ]; then
    printf '%-28s CAUGHT   %3d cases fail | %s\n' "$b" "$n" \
      "$(printf '%s\n' "$o" | grep '^FAIL' | awk '{print $2}' | tr '\n' ',' | cut -c1-70)" >> "$L"
  else
    printf '%-28s *** ESCAPED *** 0 cases fail  <-- HARNESS BLIND SPOT\n' "$b" >> "$L"
  fi
done
{ echo "########## GAP (stop-signal window, now stdout-graded) ##########"
  /usr/bin/python3 "$F/gap.py" "$R/out/g2_gap" "$R/candidate/v22-installed.sh" "$R/candidate/v23.sh" "$R/mutants/M14_gap_window_stdout_leak.sh" 2>&1 | tail -6
  echo "=== GATE2 COMPLETE ==="; } >> "$L"
