#!/bin/bash
# Full regression + adversarial-review suite for gate-before-commit.sh
# (shlex-based rewrite, round 3, 2026-07-07). Expected exits written down
# before running. Run after ANY edit: bash ~/.claude/hooks/test-gate-before-commit.sh
H=~/.claude/hooks/gate-before-commit.sh

mkrepo() { mkdir -p "$1" && git -C "$1" init -q
  if [ -n "$2" ]; then mkdir -p "$1/checks"
    printf '#!/bin/bash\nexit %s\n' "$2" > "$1/checks/run-all.sh"; fi }
RED=$(mktemp -d)/red;     mkrepo "$RED" 1
GREEN=$(mktemp -d)/green; mkrepo "$GREEN" 0
NOGATE=$(mktemp -d)/ng;   mkrepo "$NOGATE" ""
SPC="$(mktemp -d)/ng with space"; mkrepo "$SPC" ""
RELMARK=$(mktemp -d)/relgate
mkdir -p "$RELMARK/checks" && touch "$RELMARK/marker.txt"
printf '#!/bin/bash\ntest -f marker.txt\n' > "$RELMARK/checks/run-all.sh"
git -C "$RELMARK" init -q
mkdir -p "$RED/subdir"

failures=0
run() { # name expected CPD command
  printf '%s' "{\"tool_input\":{\"command\":$(printf '%s' "$4" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')}}" \
    | CLAUDE_PROJECT_DIR="$3" bash "$H" 2>/dev/null
  got=$?
  if [ "$got" -eq "$2" ]; then s=PASS; else s=FAIL; failures=$((failures+1)); fi
  printf '%s  %-42s expect=%s got=%s\n' "$s" "$1" "$2" "$got"
}

echo "— original 4 —"
run "1 non-commit, red CPD"        0 "$RED"    'ls -la'
run "2 bare commit, red CPD"       2 "$RED"    'git commit -m test'
run "3 bare commit, green CPD"     0 "$GREEN"  'git commit -m test'
run "4 bare commit, no-gate CPD"   0 "$NOGATE" 'git commit -m test'

echo "— target-repo resolution —"
run "5 cd nogate-repo, red CPD"    0 "$RED"    "cd $NOGATE && git add -A && git commit -m x"
run "6 git -C red-repo, nogate CPD" 2 "$NOGATE" "git -C $RED commit -m x"
run "7 cd red-repo, nogate CPD"    2 "$NOGATE" "cd $RED && git commit -m x"
run "8 cd red-repo SUBDIR, ng CPD" 2 "$NOGATE" "cd $RED/subdir && git commit -m x"
run "9 quoted -C red, nogate CPD"  2 "$NOGATE" "git -C \"$RED\" commit -m x"

echo "— prose immunity —"
run "10 printf quoted prose, red"  0 "$RED"    "printf 'how to git commit safely' > /tmp/prose.txt"
run "11 heredoc body prose, red"   0 "$RED"    "$(printf 'cat >> /tmp/l.md <<EOF\nlesson: git commit was blocked\nEOF')"
run "12 hyphenated name, red"      0 "$RED"    'bash ~/.claude/hooks/test-gate-before-commit.sh'
run "13 msg mentions hook, red"    2 "$RED"    'git commit -m "Register gate-before-commit hook"'
run "14 msg mentions -C <dir>, red" 0 "$RED"   "cd \"$NOGATE\" && git commit -m \"resolved from 'git -C <dir>' in the command\""
run "15 quoted cd path w/ space"   0 "$RED"    "cd \"$SPC\" && git commit -m x"
run "16 msg -C prose, red target"  2 "$NOGATE" "cd \"$RED\" && git commit -m \"use git -C <dir> for this\""

echo "— review round: F1 non-git -C hijack —"
run "F1a make -C red, cd green, ng CPD" 0 "$NOGATE" "make -C $RED && cd $GREEN && git commit -m x"
run "F1b tar -C red, cd green, ng CPD"  0 "$NOGATE" "tar -C $RED -cf x.tar . && cd $GREEN && git commit -m x"

echo "— review round: F2 quote mispairing —"
run "F2a apostrophe prose, red CPD"     0 "$RED"    "grep \"don't \" file.txt && echo 'a git commit tip'"
run "F2b escaped quote prose, red CPD"  0 "$RED"    'echo "x \" y" && echo "run git commit now"'
run "F2c apostrophe THEN real commit"   2 "$RED"    "echo \"don't\" && git commit -m 'per git convention x'"

echo "— review round: F3 relative-path gate cwd —"
run "F3 relgate cwd, nogate CPD"        0 "$NOGATE" "git -C $RELMARK commit -m x"

echo "— review round: F4 single-quoted dir args —"
run "F4a cd single-quoted nogate, red" 0 "$RED"    "cd '$NOGATE' && git commit -m x"
run "F4b -C single-quoted red, ng CPD" 2 "$NOGATE" "git -C '$RED' commit -m x"

echo "— review round: F5 heredoc-then-real-commit —"
run "F5a heredoc then commit, red"  2 "$RED"    "$(printf 'cat <<EOF > f\nhello\nEOF\ngit commit -m x')"
run "F5b arithmetic <<, red"        2 "$RED"    'echo $((1<<2)) && git commit -m x'

echo "— review round: F6 non-commit git subcommands —"
run "F6a git help commit, red"      0 "$RED"    'git help commit'
run "F6b git log --grep commit, red" 0 "$RED"   'git log --grep commit'

echo "— sanity: legitimate git forms still detected —"
run "S1 git commit --amend, red"    2 "$RED"    'git commit --amend'
run "S2 git -c cfg commit, red"     2 "$RED"    'git -c user.name=x commit'
run "S3 git -C a -C b commit, ng"   2 "$NOGATE" "git -C $NOGATE -C $RED commit"
run "S4 multiline cd-then-commit"   2 "$NOGATE" "$(printf 'cd %s\ngit add x\ngit commit -m y' "$RED")"
run "S5 commit inside \$(...)"      2 "$RED"    'x=$(git commit -m y)'
run "S6 git log | grep commit"      0 "$RED"    'git log | grep commit'

[ "$failures" -eq 0 ] && echo "ALL 34 PASS" || { echo "$failures FAILURE(S)"; exit 1; }
