#!/bin/bash
hook="$1"; tag="$2"
# Was hardcoded to one session's scratchpad, so it could not run anywhere else.
wd="${TMPDIR:-/tmp}/functwd_$tag"
rm -rf "$wd"; mkdir -p "$wd/home"
export HOME="$wd/home"
evt='{"session_id":"funct-'"$tag"'","transcript_path":"/tmp/x.jsonl","hook_event_name":"PreCompact","trigger":"manual"}'
# C2 is measured from a FILE, never through a shell variable: command
# substitution strips ALL trailing newlines, so `out=$(...)` + ${#out} reported
# a newline-only stdout as 0 bytes -- a clean C2 reading on a real C2 violation
# (contract.py flags the same hook as "C2 stdout=1B b'\n'"). A bare `echo` in a
# trap is exactly that shape. contract.py captures to an fd and stats it; so does this now.
printf '%s' "$evt" | /bin/bash --noprofile --norc -p "$hook" manual >"$wd/stdout" 2>"$wd/stderr"
rc=$?
s_at_exit=$(wc -c < "$wd/stdout" | tr -d ' ')
# Settle before the second sample. A file redirect returns as soon as the direct
# child exits, so a detached descendant writing on the inherited fd 1 lands after
# the first read -- the old `out=$(...)` form blocked until every fd holder closed
# and did catch it. 1.5s matches contract.py's SETTLE / stdout_late_bytes.
sleep 1.5
obs="$HOME/.claude/session-state/observed"
nfiles=$(find "$obs" -type f 2>/dev/null | wc -l | tr -d ' ')
s_late=$(wc -c < "$wd/stdout" | tr -d ' ')
sbytes=$s_at_exit; [ "$s_late" -gt "$sbytes" ] && sbytes=$s_late
echo "[$tag] rc=$rc stdout_bytes=$sbytes record_files=$nfiles$([ "$s_late" != "$s_at_exit" ] && echo "  (${s_at_exit}B at exit -> ${s_late}B after settle)")"
if [ "$nfiles" -gt 0 ]; then
  f=$(find "$obs" -type f | head -1)
  echo "   record: $(basename "$f")"
  echo "   saw_eof: $(grep -o '"saw_eof"[: ]*[a-z]*' "$f" 2>/dev/null | head -1)"
  echo "   trigger: $(grep -o '"registered_matcher"[: ]*"[^"]*"' "$f" 2>/dev/null | head -1)"
fi
