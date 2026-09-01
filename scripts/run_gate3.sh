#!/bin/bash
cd "/private/tmp/claude-501/-Users-yauch-Documents-claude-code-technique/d8a69179-c2ab-4c5b-927b-3b9417b15cb6/scratchpad/round23/harness-frozen3"
for v in v27 v22-installed v26; do
  lbl=$(echo "$v" | sed 's/-installed//')
  wd="/private/tmp/claude-501/-Users-yauch-Documents-claude-code-technique/d8a69179-c2ab-4c5b-927b-3b9417b15cb6/scratchpad/round23/gate3wd_$lbl"
  chmod -R u+rwx "$wd" 2>/dev/null; rm -rf "$wd"; mkdir -p "$wd"
  /usr/bin/python3 contract.py "/private/tmp/claude-501/-Users-yauch-Documents-claude-code-technique/d8a69179-c2ab-4c5b-927b-3b9417b15cb6/scratchpad/round23/candidate/$v.sh" "$lbl" "$wd" > "/private/tmp/claude-501/-Users-yauch-Documents-claude-code-technique/d8a69179-c2ab-4c5b-927b-3b9417b15cb6/scratchpad/round23/out/GATE_$lbl.log" 2>&1
  echo "$lbl exit=$? $(date +%H:%M:%S)" >> "/private/tmp/claude-501/-Users-yauch-Documents-claude-code-technique/d8a69179-c2ab-4c5b-927b-3b9417b15cb6/scratchpad/round23/out/GATE3_progress.txt"
done
echo "ALL-DONE $(date +%H:%M:%S)" >> "/private/tmp/claude-501/-Users-yauch-Documents-claude-code-technique/d8a69179-c2ab-4c5b-927b-3b9417b15cb6/scratchpad/round23/out/GATE3_progress.txt"
