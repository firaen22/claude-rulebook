#!/bin/bash
R=/private/tmp/claude-501/-Users-yauch-Documents-claude-code-technique/d8a69179-c2ab-4c5b-927b-3b9417b15cb6/scratchpad/round23
F="$R/harness-frozen2"; L="$R/out/GATE3.log"; : > "$L"
{
echo "FROZEN2 $(cd $F && md5 -q contract.py gap.py grpsig.py | tr '\n' ' ')"
echo "== contract v22 (expect 1 FAIL: H01) =="
CONTRACT_LABEL=v22 /usr/bin/python3 "$F/contract.py" "$R/candidate/v22-installed.sh" v22b "$R/out/g3_v22" 2>&1 | grep -E '^FAIL|pass|FAIL$|/56|/5[0-9]' | tail -5
echo "== contract v26 (expect 0 FAIL) =="
CONTRACT_LABEL=v26 /usr/bin/python3 "$F/contract.py" "$R/candidate/v26.sh" v26 "$R/out/g3_v26" 2>&1 | grep -E '^FAIL|/5[0-9]' | tail -5
echo "== gap v26 (expect PASS 6/6) =="
/usr/bin/python3 "$F/gap.py" "$R/out/g3_gap" "$R/candidate/v26.sh" 2>&1 | tail -3
echo "== grpsig v26 (expect PASS) =="
/usr/bin/python3 "$F/grpsig.py" "$R/out/g3_sig" "$R/candidate/v26.sh" 2>&1
echo "== refcheck v26 =="
/usr/bin/python3 "$F/refcheck.py" "$R/candidate/v26.sh" 2>&1 | tail -3
echo "== exectext: v22 vs v26 executable-line diff size =="
/usr/bin/python3 "$F/exectext.py" "$R/candidate/v22-installed.sh" 2>&1 | tail -1
/usr/bin/python3 "$F/exectext.py" "$R/candidate/v26.sh" 2>&1 | tail -1
echo "=== GATE3 COMPLETE ==="
} >> "$L" 2>&1
echo END
