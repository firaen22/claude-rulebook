#!/usr/bin/env bash
# Provision Colab T4 + Inkling 2 Mini Q3 GGUF as OpenAI API on loopback :8092.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SESSION="${INKLING_COLAB_SESSION:-inkling-25mini}"
GPU="${INKLING_COLAB_GPU:-T4}"
COLAB="${COLAB_BIN:-$(command -v colab || true)}"

cleanup_hint() {
  echo "On failure, stop CU burn: colab stop -s $SESSION" >&2
}

if [[ -z "$COLAB" ]]; then
  echo "colab not on PATH (uv tool install google-colab-cli)" >&2
  exit 2
fi

SESSION_LIST="$("$COLAB" sessions)" || {
  echo "colab sessions failed (auth/network?); fix auth or connection before provisioning" >&2
  exit 3
}
if printf '%s\n' "$SESSION_LIST" | grep -Eq "^\\[${SESSION//./\\.}\\]"; then
  echo "[1/3] session $SESSION already listed" >&2
elif [[ "${INKLING_ALLOW_NEW:-}" == "1" ]]; then
  echo "[1/3] colab new -s $SESSION --gpu $GPU (INKLING_ALLOW_NEW=1)" >&2
  "$COLAB" new -s "$SESSION" --gpu "$GPU"
else
  echo "[1/3] session $SESSION not listed; refusing colab new (spends CU). Run:" >&2
  echo "  INKLING_ALLOW_NEW=1 $0" >&2
  exit 4
fi

LOCK="/tmp/inkling-packet-${SESSION}.lock"
exec 8>"$LOCK"
if ! flock -w 1200 8; then
  echo "timed out waiting for inkling session lock (packet or provision in progress)" >&2
  exit 7
fi

trap cleanup_hint ERR

START_LOG="$(mktemp "${TMPDIR:-/tmp}/inkling-start.XXXXXX")"
PING_LOG="$(mktemp "${TMPDIR:-/tmp}/inkling-ping.XXXXXX")"

echo "[2/3] start inkling (no exec timeout)" >&2
if ! "$COLAB" exec -s "$SESSION" --timeout 0 -f "$ROOT/scripts/colab_vm_start_inkling_25_mini.py" | tee "$START_LOG"; then
  echo "colab exec failed during start (timeout/connection)" >&2
  cleanup_hint
  exit 5
fi
if ! grep -q '^READY ' "$START_LOG"; then
  echo "start script did not print READY sentinel (colab exec exit code is not reliable)" >&2
  cleanup_hint
  exit 5
fi

echo "[3/3] ping" >&2
if ! "$COLAB" exec -s "$SESSION" --timeout 300 -f "$ROOT/scripts/colab_vm_ping_inkling.py" | tee "$PING_LOG"; then
  echo "colab exec failed during ping (timeout/connection)" >&2
  cleanup_hint
  exit 6
fi
if ! grep -qx 'INKLING_PING_OK' "$PING_LOG" || ! grep -qx 'inkling-ok' "$PING_LOG"; then
  echo "ping missing inkling-ok and/or INKLING_PING_OK (colab exec exit code is not reliable)" >&2
  cleanup_hint
  exit 6
fi

rm -f "$START_LOG" "$PING_LOG"
trap - ERR