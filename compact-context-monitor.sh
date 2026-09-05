#!/bin/bash
# compact-context-monitor.sh
# Fires on Stop events. Estimates context window usage from transcript file size.
# When ~50% full, exits with code 2 (asyncRewake) so Claude gets a system reminder
# and proactively runs the compact-context skill.
#
# Two corrections over the naive "raw size > threshold" version:
#   1. The JSONL transcript is append-only ACROSS compactions, so raw size keeps
#      growing even after /compact frees context. We measure only bytes appended
#      after the last compact_boundary marker (EFFECTIVE_SIZE).
#   2. The Stop hook fires on EVERY turn end, so a naive check re-nags on every
#      completed task once you're over threshold. We debounce: warn once per
#      crossing, then stay silent until either a compact resets EFFECTIVE_SIZE or
#      it grows another REWARN_STEP beyond the last warning.
#
# Threshold tuning: JSON overhead makes bytes a proxy, not an exact count.
#   1MB ≈ ~50% of 200K context. Lower to trigger earlier; raise to trigger later.

THRESHOLD=1000000    # bytes since last compact before the first warning
REWARN_STEP=500000   # additional growth before re-warning without a compact

# Read transcript_path from Stop event JSON on stdin
TRANSCRIPT_PATH=$(python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('transcript_path', ''))
except Exception:
    print('')
" 2>/dev/null)

[ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ] && exit 0

TRANSCRIPT_SIZE=$(wc -c < "$TRANSCRIPT_PATH" 2>/dev/null | tr -d ' ')
TRANSCRIPT_SIZE=${TRANSCRIPT_SIZE:-0}

# Bytes appended after the last compact boundary. (Copies of the marker inside
# message content are JSON-escaped in the JSONL, so only real events match.)
LAST_BOUNDARY=$(grep -b -o '"subtype":"compact_boundary"' "$TRANSCRIPT_PATH" 2>/dev/null | tail -1 | cut -d: -f1)
LAST_BOUNDARY=${LAST_BOUNDARY:-0}
EFFECTIVE_SIZE=$((TRANSCRIPT_SIZE - LAST_BOUNDARY))

# Per-transcript debounce state: the EFFECTIVE_SIZE at the last warning we emitted.
STATE_DIR="$HOME/.claude/.context-monitor-state"
mkdir -p "$STATE_DIR" 2>/dev/null
STATE_KEY=$(printf '%s' "$TRANSCRIPT_PATH" | shasum | cut -d' ' -f1)
STATE_FILE="$STATE_DIR/$STATE_KEY"
LAST_WARNED=$(cat "$STATE_FILE" 2>/dev/null | tr -d ' ')
LAST_WARNED=${LAST_WARNED:-0}

# A compact shrinks EFFECTIVE_SIZE below the last warned mark — clear the debounce
# so the next real crossing warns again.
if [ "$EFFECTIVE_SIZE" -lt "$LAST_WARNED" ]; then
  LAST_WARNED=0
  echo 0 > "$STATE_FILE" 2>/dev/null
fi

if [ "$EFFECTIVE_SIZE" -gt "$THRESHOLD" ] && [ "$EFFECTIVE_SIZE" -ge "$((LAST_WARNED + REWARN_STEP))" ]; then
  echo "$EFFECTIVE_SIZE" > "$STATE_FILE" 2>/dev/null
  echo "Context window is approximately 50%+ full (${EFFECTIVE_SIZE} bytes since last compact). Use the compact-context skill now: generate a CONTEXT HANDOFF block capturing completed work, current state, key decisions, critical file paths, and next steps — then offer to run /compact."
  exit 2
fi

exit 0
