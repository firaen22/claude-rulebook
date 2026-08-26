#!/usr/bin/env bash
# Project gate — ONE command runs every gate. Copy into your project's checks/
# and rewire the three paths below to your real module/data. All gates run even
# if an early one fails, so a single run reports everything.
set -uo pipefail
cd "$(dirname "$0")"
fail=0

# 1. typecheck / lint (optional): export TYPECHECK_CMD="npx tsc --noEmit" etc.
if [ -n "${TYPECHECK_CMD:-}" ]; then
  echo "== typecheck: $TYPECHECK_CMD"
  eval "$TYPECHECK_CMD" || fail=1
fi

echo "== golden gate"
node golden-gate.mjs --module ./example/classifier.mjs --cases ./example/cases.jsonl || fail=1

echo "== replay gate"
node replay-gate.mjs --module ./example/redact.mjs --corpus ./example/corpus.jsonl --baseline ./example/baseline.json || fail=1

if [ "$fail" -eq 0 ]; then echo "ALL GATES PASS"; else echo "GATE FAILURE"; fi
exit "$fail"
