#!/usr/bin/env bash
# Regression tests for gate-opencode-stdin.py — block path and allow path.
set -eu

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
hook="$root/hooks/gate-opencode-stdin.py"

json_for() {
  COMMAND_TEXT="$1" python3 -c 'import json,os;print(json.dumps({"tool_input":{"command":os.environ["COMMAND_TEXT"]}}))'
}

fails=0
assert_exit() {
  expected="$1"; name="$2"; command_text="$3"
  set +e
  out=$(json_for "$command_text" | python3 "$hook" 2>&1)
  code=$?
  set -e
  if [ "$code" -ne "$expected" ]; then
    echo "FAIL $name: expected exit $expected, got $code" >&2
    printf '%s\n' "$out" >&2
    fails=$((fails + 1))
  else
    echo "PASS $name"
  fi
}

# --- block: opencode run with the Bash tool's open stdin ---
assert_exit 2 bare            'opencode run -m nvidia/z-ai/glm-5.3-flash "hi"'
assert_exit 2 timeout-wrap    'timeout 90 opencode run --standalone -m x "hi"'
assert_exit 2 abs-path        '/Users/yauch/.opencode/bin/opencode run "hi"'
assert_exit 2 env-prefix      'FOO=1 opencode run "hi"'
assert_exit 2 after-cd        'cd /tmp && opencode run "hi" > out 2>&1'
assert_exit 2 second-line     $'echo start\nopencode run "hi"'
assert_exit 2 redirect-before 'cat </dev/null; opencode run "hi"'
assert_exit 2 bg-ampersand    'opencode run "hi" &'

# --- allow: stdin closed or supplied ---
assert_exit 0 devnull         'opencode run "hi" </dev/null'
assert_exit 0 devnull-spaced  'timeout 90 opencode run "hi" < /dev/null > out'
assert_exit 0 fd0-devnull     'opencode run "hi" 0</dev/null'
assert_exit 0 piped-in        'echo "prompt" | opencode run'
assert_exit 0 herestring      'opencode run <<< "prompt"'
assert_exit 0 heredoc         $'opencode run <<EOF\nprompt\nEOF'
assert_exit 0 group-redirect  '(cd /tmp && opencode run "hi") </dev/null'
assert_exit 0 override        'OPENCODE_STDIN_OK=1 opencode run "hi"'

# --- allow: not an opencode run invocation ---
assert_exit 0 other-sub       'opencode --version'
assert_exit 0 serve           'opencode serve --service'
assert_exit 0 quoted-mention  'git commit -m "opencode run reads stdin"'
assert_exit 0 grep-mention    'grep -n "opencode run" notes.md'
assert_exit 0 echo-words      'echo opencode run'
assert_exit 0 python-dispatch 'python3 ~/.claude/lib/dispatch.py nim --model x'
assert_exit 0 unbalanced      'echo "unterminated'
assert_exit 0 empty           ''

# --- malformed envelope fails open ---
set +e
printf 'not json' | python3 "$hook" >/dev/null 2>&1; code=$?
set -e
if [ "$code" -eq 0 ]; then echo "PASS bad-envelope"; else echo "FAIL bad-envelope: got $code" >&2; fails=$((fails + 1)); fi

[ "$fails" -eq 0 ] && echo "ALL PASS" || { echo "$fails FAILED" >&2; exit 1; }
