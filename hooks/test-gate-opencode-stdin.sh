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

# --- round 1 review (sol 6.1 + grok 4.7 + own probes), all reproduced 2026-10-05 ---
assert_exit 2 r-comment       $'echo start # progress\nopencode run "hi"'
assert_exit 2 r-timeout-sig   'timeout --signal TERM 90 opencode run "hi"'
assert_exit 2 r-timeout-s     'timeout -s KILL 60 opencode run "hi"'
assert_exit 2 r-timeout-k     'timeout -k 10 600 opencode run "hi"'
assert_exit 2 r-timeout-eq    'timeout --signal=TERM 90 opencode run "hi"'
assert_exit 2 r-env-u         'env -u DEBUG opencode run "hi"'
assert_exit 2 r-command-dd    'command -- opencode run "hi"'
assert_exit 2 r-nice-n        'nice -n 10 opencode run "hi"'
assert_exit 2 r-time-p        'time -p opencode run "hi"'
assert_exit 2 r-usr-bin-env   '/usr/bin/env opencode run "hi"'
assert_exit 2 r-subst-dq      'echo "$(opencode run hi)"'
assert_exit 2 r-subst-bare    'echo $(opencode run hi)'
assert_exit 2 r-backtick      'echo `opencode run hi`'
assert_exit 2 r-continuation  $'opencode \\\nrun "hi"'
assert_exit 2 r-quoted-lt     'opencode run "<"'
assert_exit 2 r-fd2-only      'opencode run "hi" 2</dev/null'
assert_exit 2 r-if-then       'if true; then opencode run "hi"; fi'
assert_exit 2 r-else          'if false; then echo no; else opencode run "hi"; fi'
assert_exit 2 r-while-do      'while read l; do opencode run "$l"; done'
assert_exit 2 r-for-do        'for m in a b; do opencode run -m $m "hi"; done'
assert_exit 2 r-brace-group   '{ opencode run "hi"; }'
assert_exit 2 r-tee           'opencode run "hi" 2>&1 | tee out'
assert_exit 0 r-heredoc-doc   $'cat <<\'EOF\'\nopencode run "hi"\nEOF'
assert_exit 0 r-heredoc-dash  $'cat <<-EOF\n\topencode run "hi"\n\tEOF'
assert_exit 2 r-after-heredoc $'cat <<EOF\nx\nEOF\nopencode run "hi"'
assert_exit 0 r-quoted-semi   'printf "%s\\n" ";" opencode run'
assert_exit 0 r-pipe-amp      'echo hi |& opencode run'
assert_exit 0 r-loop-redirect 'while read m; do opencode run -m "$m" hi; done </dev/null'
assert_exit 0 r-fd0-dup-close 'opencode run "hi" <&-'
assert_exit 0 r-arith         'echo $((1+2)) opencode run'
assert_exit 0 r-comment-only  '# opencode run "hi"'
assert_exit 0 r-sq-mention    "echo 'opencode run hi'"

assert_exit 2 r-comment-quote $'echo hi # don\'t stop\nopencode run "hi"'
assert_exit 0 r-run-help      'opencode run --help 2>&1 | head -40'
assert_exit 2 r-time-subshell 'time (timeout 240 ~/.opencode/bin/opencode run --auto -m x "hi" > out 2>&1)'

assert_exit 2 r-heredoc-bt    $'python3 - <<PY\nq = "use `opencode run` here"\nPY'
assert_exit 2 r-heredoc-subst $'cat <<EOF\nx $(opencode run hi)\nEOF'
assert_exit 0 r-heredoc-q-bt  $'python3 - <<\'PY\'\nq = "use `opencode run` here"\nPY'
assert_exit 0 r-heredoc-bs-bt $'cat <<\\EOF\nx `opencode run hi`\nEOF'

assert_exit 2 r-oc-value-opt  'opencode --log-level debug run "hi"'
assert_exit 2 r-oc-server-opt '~/.opencode/bin/opencode --server http://127.0.0.1:4096 run "hi"'
assert_exit 2 r-timeout-s9    'timeout -s 9 10 opencode run "hi"'
assert_exit 2 r-sudo          'sudo opencode run "hi"'

# --- round 2 review (sol 6.1), all reproduced 2026-10-05 ---
assert_exit 2 r2-help-leak    "opencode run hi; printf '%s\\n' --help"
assert_exit 2 r2-proc-subst   'cat <(opencode run hi)'
assert_exit 0 r2-proc-subst-o 'echo hi > >(opencode run)'
assert_exit 2 r2-subst-comment $'echo $(printf ok # don\'t stop\n); opencode run hi'
assert_exit 0 r2-array        'commands=(opencode run)'
assert_exit 2 r2-array-then   'a=(x y); opencode run hi'
assert_exit 0 r2-command-v    'command -v opencode run'
assert_exit 2 r2-arith-subst  'echo $(( $(opencode run hi) + 1 ))'
assert_exit 0 r2-lead-redir   '</dev/null opencode run hi'
assert_exit 0 r2-pipe-subshell 'echo hi | (opencode run hi)'
assert_exit 0 r2-pipe-group   'echo hi | { opencode run hi; }'
assert_exit 2 r2-subshell-bare '(opencode run hi)'

assert_exit 2 r2-ansi-c       "printf \$'it\\'s\\n'; opencode run hi"
assert_exit 2 r2-heredoc-in-subst $'gh pr create --body "$(cat <<\'EOF\'\nit\'s (fine\nEOF\n)"; opencode run hi'
assert_exit 0 r2-heredoc-in-subst-ok $'gh pr create --body "$(cat <<\'EOF\'\ndon\'t run `opencode run x`\nEOF\n)"'

# --- round 3 review (sol 6.1), all reproduced 2026-10-05 ---
assert_exit 2 r3-array-subst  'replies=($(timeout 90 opencode run "hi"))'
assert_exit 2 r3-heredoc-multiline $'cat <<EOF\n$(\n  opencode run "hi"\n)\nEOF'
assert_exit 2 r3-redirect-before-run 'timeout 90 opencode > /dev/null run "hi"'
assert_exit 0 r3-pipe-newline $'printf "%s\\n" "hi" |\n  opencode run'
assert_exit 0 r3-piped-group-seq 'printf "%s\n" "hi" | { echo start; opencode run "hi"; }'
assert_exit 2 r3-group-unpiped '{ echo start; opencode run "hi"; }'
assert_exit 2 r3-after-piped-group 'echo x | { cat; }; opencode run "hi"'
assert_exit 2 r3-and-newline  $'true &&\n  opencode run "hi"'

# --- round 4 review (astra), all reproduced 2026-10-05 ---
assert_exit 2 r4-wrapper-redirect 'timeout > /dev/null 90 opencode run hi'
assert_exit 2 r4-wrapper-redirect-fd 'timeout 2>&1 90 opencode run hi'
assert_exit 0 r4-wrapper-stdin   'timeout < /dev/null 90 opencode run hi'
assert_exit 0 r4-redirect-mid    'opencode </dev/null run hi'
assert_exit 0 r4-piped-while     'printf "%s\n" a b | while read -r m; do opencode run -m "$m" hi; done'
assert_exit 0 r4-piped-until     'printf "x\n" | until false; do opencode run hi; done'
assert_exit 0 r4-piped-for       'echo hi | for m in a b; do opencode run -m $m; done'
assert_exit 0 r4-piped-if        'echo hi | if true; then opencode run; fi'
assert_exit 2 r4-after-piped-loop 'printf "x\n" | while read l; do echo "$l"; done; opencode run hi'
assert_exit 2 r4-arith-shift     'echo $((1 << 2)); opencode run hi'
assert_exit 2 r4-arith-shift-dq  'echo "$((1 << 2))"; opencode run hi'

assert_exit 2 r4-override-in-prompt 'opencode run "what is OPENCODE_STDIN_OK=1 for?"'
assert_exit 2 r4-override-in-comment 'opencode run -m x "hi" # OPENCODE_STDIN_OK=1'
assert_exit 0 r4-override-env    'env OPENCODE_STDIN_OK=1 opencode run "hi"'
assert_exit 0 r4-override-wrapped 'OPENCODE_STDIN_OK=1 timeout 90 opencode run "hi"'
assert_exit 0 r4-override-export 'export OPENCODE_STDIN_OK=1; opencode run "hi"'
assert_exit 2 r4-function-kw     'function f { opencode run "hi"; }; f'
assert_exit 2 r4-function-kw-paren 'function f() { opencode run "hi"; }; f'
assert_exit 2 r4-plus-assign     'PATH+=":$HOME/.opencode/bin" opencode run "hi"'
assert_exit 2 r4-env-plus-assign 'env PATH+=:/usr/bin opencode run "hi"'
assert_exit 2 r4-index-assign    'a[0]=x opencode run "hi"'
assert_exit 2 r4-help-after-dd   'opencode run -m x -- add a --help option'
assert_exit 0 r4-help-before-dd  'opencode run --help -- x'

# --- astra pre-commit gate (round 5), all reproduced 2026-10-05 ---
assert_exit 0 g5-cond-regex     'cmd="opencode run"; [[ "$cmd" =~ (opencode run) ]]'
assert_exit 2 g5-cond-then-run  '[[ -n x ]] && opencode run hi'
assert_exit 2 g5-cond-subst     '[[ $(opencode run hi) ]]'
assert_exit 2 g5-nested-arith   'budget=$(echo $((1 << 8))); opencode run hi'
assert_exit 2 g5-export-unset   'export OPENCODE_STDIN_OK=1; unset OPENCODE_STDIN_OK; opencode run hi'
assert_exit 2 g5-export-subshell '(export OPENCODE_STDIN_OK=1); opencode run hi'
assert_exit 0 g5-export-in-subshell '(export OPENCODE_STDIN_OK=1; opencode run hi)'
assert_exit 0 g5-export-brace   '{ export OPENCODE_STDIN_OK=1; }; opencode run hi'
assert_exit 2 g5-export-n       'export OPENCODE_STDIN_OK=1; export -n OPENCODE_STDIN_OK; opencode run hi'
assert_exit 2 g5-reassign       'export OPENCODE_STDIN_OK=1; OPENCODE_STDIN_OK=0; opencode run hi'
assert_exit 0 g5-export-redirect 'export > /dev/null OPENCODE_STDIN_OK=1; opencode run hi'

# --- malformed envelope fails open ---
set +e
printf 'not json' | python3 "$hook" >/dev/null 2>&1; code=$?
set -e
if [ "$code" -eq 0 ]; then echo "PASS bad-envelope"; else echo "FAIL bad-envelope: got $code" >&2; fails=$((fails + 1)); fi

[ "$fails" -eq 0 ] && echo "ALL PASS" || { echo "$fails FAILED" >&2; exit 1; }
