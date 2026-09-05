#!/bin/bash
R="/private/tmp/claude-501/-Users-yauch-Documents-claude-code-technique/d8a69179-c2ab-4c5b-927b-3b9417b15cb6/scratchpad/round23"
cd "$R/harness-frozen3"
: > "$R/out/GRPSIG2c.log"
for f in v27 v26 v22-installed; do
  python3 grpsig2.py "$R/g2wd" "$R/candidate/$f.sh" >> "$R/out/GRPSIG2c.log" 2>&1
done
echo "GRPSIG2c-DONE" >> "$R/out/GRPSIG2c.log"
