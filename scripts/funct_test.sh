#!/bin/bash
hook="$1"; tag="$2"
wd="/private/tmp/claude-501/-Users-yauch-Documents-claude-code-technique/d8a69179-c2ab-4c5b-927b-3b9417b15cb6/scratchpad/round23/functwd_$tag"
rm -rf "$wd"; mkdir -p "$wd/home"
export HOME="$wd/home"
evt='{"session_id":"funct-'"$tag"'","transcript_path":"/tmp/x.jsonl","hook_event_name":"PreCompact","trigger":"manual"}'
out=$(printf '%s' "$evt" | /bin/bash --noprofile --norc -p "$hook" manual 2>"$wd/stderr")
rc=$?
sleep 0.5
obs="$HOME/.claude/session-state/observed"
nfiles=$(find "$obs" -type f 2>/dev/null | wc -l | tr -d ' ')
echo "[$tag] rc=$rc stdout_bytes=${#out} record_files=$nfiles"
if [ "$nfiles" -gt 0 ]; then
  f=$(find "$obs" -type f | head -1)
  echo "   record: $(basename "$f")"
  echo "   saw_eof: $(grep -o '"saw_eof"[: ]*[a-z]*' "$f" 2>/dev/null | head -1)"
  echo "   trigger: $(grep -o '"registered_matcher"[: ]*"[^"]*"' "$f" 2>/dev/null | head -1)"
fi
