#!/usr/bin/env bash
# Upload spec → Inkling on Colab VM → download reply (one in flight per session).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SESSION="${INKLING_COLAB_SESSION:-inkling-25mini}"
SPEC=""
OUT=""

usage() {
  echo "Usage: $0 -f SPEC.md [-s SESSION] [-o OUT.md]" >&2
}

while getopts "s:f:o:h" opt; do
  case "$opt" in
    s) SESSION="$OPTARG" ;;
    f) SPEC="$OPTARG" ;;
    o) OUT="$OPTARG" ;;
    h) usage; exit 0 ;;
    *) usage; exit 2 ;;
  esac
done

if [[ -z "$SPEC" || ! -f "$SPEC" ]]; then
  usage
  exit 2
fi

if [[ -z "$OUT" ]]; then
  _dir="$(mktemp -d "${TMPDIR:-/tmp}/inkling-out.XXXXXX")"
  OUT="$_dir/out.md"
fi
COLAB="${COLAB_BIN:-$(command -v colab || true)}"
if [[ -z "$COLAB" ]]; then
  echo "colab not on PATH" >&2
  exit 2
fi

LOCK="/tmp/inkling-packet-${SESSION}.lock"
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "another inkling packet is in flight for session $SESSION" >&2
  exit 9
fi

if [[ ! -f "$ROOT/lib/dispatch.py" ]]; then
  echo "refusing upload: missing $ROOT/lib/dispatch.py (scan_secrets required)" >&2
  exit 3
fi

SNAPSHOT="$(mktemp "${TMPDIR:-/tmp}/inkling-spec.XXXXXX.md")"
REMOTE_SPEC=""
REMOTE_OUT=""
cleanup_remote() {
  local status=$1
  [[ $status -eq 0 ]] && return 0
  [[ -n "$REMOTE_SPEC" ]] || return 0
  "$COLAB" exec -s "$SESSION" --timeout 120 \
    --env "INKLING_RM_PATHS=${REMOTE_SPEC},${REMOTE_OUT}" \
    -f "$ROOT/scripts/colab_vm_inkling_cleanup.py" 2>/dev/null || true
}
trap 'status=$?; rm -f "$SNAPSHOT"; cleanup_remote "$status"' EXIT
cp "$SPEC" "$SNAPSHOT"
if ! python3 - "$SNAPSHOT" "$ROOT/lib/dispatch.py" <<'PY'
import sys
from pathlib import Path
spec = Path(sys.argv[1]).read_text()
sys.path.insert(0, str(Path(sys.argv[2]).parent))
from dispatch import scan_secrets
hits = scan_secrets([spec])
if hits:
    print("refusing upload: dispatch scan_secrets:", ", ".join(hits), file=sys.stderr)
    raise SystemExit(3)
PY
then
  exit 3
fi

REQ_ID="$(python3 -c 'import secrets; print(secrets.token_hex(8))')"
REMOTE_SPEC="/content/inkling_spec_${REQ_ID}.md"
REMOTE_OUT="/content/inkling_out_${REQ_ID}.md"
SENTINEL="INKLING_CODE_HELP_OK:${REQ_ID}"

"$COLAB" upload -s "$SESSION" "$SNAPSHOT" "$REMOTE_SPEC"
EXEC_LOG="$(mktemp "${TMPDIR:-/tmp}/inkling-exec.XXXXXX")"
if ! "$COLAB" exec -s "$SESSION" --timeout 900 \
  --env "INKLING_SPEC_PATH=${REMOTE_SPEC}" \
  --env "INKLING_OUT_PATH=${REMOTE_OUT}" \
  --env "INKLING_REQUEST_ID=${REQ_ID}" \
  -f "$ROOT/scripts/colab_vm_inkling_code_help.py" | tee "$EXEC_LOG"; then
  echo "colab exec failed (timeout/connection)" >&2
  rm -f "$EXEC_LOG"
  exit 1
fi
if ! grep -qx "$SENTINEL" "$EXEC_LOG"; then
  echo "code_help missing sentinel $SENTINEL" >&2
  rm -f "$EXEC_LOG"
  exit 1
fi
rm -f "$EXEC_LOG"
"$COLAB" download -s "$SESSION" "$REMOTE_OUT" "$OUT"
[[ -s "$OUT" ]] || { echo "downloaded output empty" >&2; exit 1; }
"$COLAB" exec -s "$SESSION" --timeout 120 \
  --env "INKLING_RM_PATHS=${REMOTE_SPEC},${REMOTE_OUT}" \
  -f "$ROOT/scripts/colab_vm_inkling_cleanup.py" 2>/dev/null || true
trap - EXIT
rm -f "$SNAPSHOT"
echo "$OUT"