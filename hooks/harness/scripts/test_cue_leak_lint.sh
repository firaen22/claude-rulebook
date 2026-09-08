#!/bin/bash
# test_cue_leak_lint.sh -- fixture suite for harness/cue_leak_lint.py.
# Each case writes input -> expected exit code/token before running the
# checker. Matches are whole tokens. The two controls must fail assertions.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
CHECKER="${1:-$HERE/../harness/cue_leak_lint.py}"
PY="${PYTHON:-python3}"
ROOT="$(mktemp -d "${TMPDIR:-/tmp}/cue_leak_lint.XXXXXX")"
trap 'rm -rf "$ROOT"' EXIT
pass=0; fail=0

make_manifest() {
  local mode="$1" path="$2"
  "$PY" - "$mode" "$path" <<'PYEOF' || { echo "FIXTURE FAIL: could not write $2"; exit 3; }
import json, sys
mode, path = sys.argv[1:]
p1 = "new reset-path seam; obligation (2) not shown; the correct subject never reaches the new path"
p4 = "same patch as P1 but obligation (2) shown discharged; a correct subject reaches the guard's new path and is not failed by it"
pos = {"done_when": "Done when a patch that removes a false failure records both the broken state it now catches and a correct subject that reaches the guard's new path and is not failed by it.",
       "items": [{"id": "P1", "key": "NOT_SOUND", "evidence": p1}, {"id": "P4", "key": "SOUND", "evidence": p4}],
       "pairs": [["P1", "P4"]]}
if mode == "pos": value = pos
elif mode == "neg": value = dict(pos, done_when="Done when the patch discharges both obligations the rule names before it is treated as closed.")
elif mode == "override": value = dict(pos, overrides={"P4": "cue is the rule's whole point"})
elif mode == "empty-done": value = dict(pos, done_when="")
elif mode == "missing-evidence": value = dict(pos, items=[pos["items"][0], {"id": "P4", "key": "SOUND"}])
elif mode == "duplicate-id": value = dict(pos, items=[pos["items"][0], dict(pos["items"][1], id="P1")])
elif mode == "unknown-pair": value = dict(pos, pairs=[["P1", "P9"]])
elif mode == "bad-pair": value = dict(pos, pairs=[["P1"]])
elif mode == "unknown-override": value = dict(pos, overrides={"P9": "stale"})
elif mode == "harmless-override": value = dict(dict(pos, done_when="Done when the patch discharges both obligations the rule names before it is treated as closed."), overrides={"P1": "not a leak"})
elif mode == "unlintable": value = dict(pos, items=[dict(pos["items"][0], evidence="x"), pos["items"][1]])
elif mode == "empty-items": value = dict(pos, items=[])
elif mode == "stopwords-done": value = dict(pos, done_when="The and or")
elif mode == "one-token-done": value = dict(pos, done_when="Done.")
elif mode == "allowlist": value = dict(pos, allowlist=["moreover"])
elif mode == "allowlist-effective": value = dict(pos, allowlist=["Guard","Path","Subject","Correct","Reaches"])
elif mode == "allowlist-hyphens": value = dict(pos, allowlist=["guard's","new-path","reset-path"])
elif mode == "surrogate": value = dict(pos, done_when="ok \ud800")
elif mode == "not-json": open(path, "w").write("not json"); raise SystemExit
elif mode == "list": open(path, "w").write("[]"); raise SystemExit
else: raise SystemExit("unknown fixture mode " + mode)
json.dump(value, open(path, "w"))
PYEOF
}

# check NAME MODE EXPECT_RC EXPECT_TOKEN [extra checker args...]
check() {
  local name="$1" mode="$2" want_rc="$3" want="$4"; shift 4
  local path="$ROOT/$name.json" out rc
  make_manifest "$mode" "$path"
  out="$("$PY" "$CHECKER" "$path" "$@" 2>&1)"; rc=$?
  if [ "$rc" = "$want_rc" ] && printf '%s\n' "$out" | grep -qE -- "(^|[[:space:]])${want}([[:space:]]|$)"; then
    pass=$((pass+1)); echo "PASS $name"
  else
    fail=$((fail+1)); echo "FAIL $name: want rc=$want_rc + /$want/, got rc=$rc"; printf '%s\n' "$out" | sed 's/^/    /'
  fi
}

# Expected exit/token are declared in each call before that call runs.
check POS_drill_treadmill pos 1 'LEAK P4'
check POS_summary pos 1 'SUMMARY items=2 leaks=1 overridden=0 threshold=0.35'
check POS_pair_partner pos 1 'pair partner P1'
check POS_ok_partner pos 1 'ok P1 ratio=0.05'
check BOUNDARY_EQ pos 1 'RESULT: LEAK' --threshold 0.44
check BOUNDARY_GT pos 0 'RESULT: CLEAN' --threshold 0.45
check NEG_de_cued neg 0 'RESULT: CLEAN'
check OVERRIDE override 0 'OVERRIDDEN P4'
check OVERRIDE_summary override 0 'SUMMARY items=2 leaks=0 overridden=1 threshold=0.35'
check OVERRIDE_result override 0 'RESULT: CLEAN'
check EMPTY_DONE empty-done 2 'RESULT: ERROR'
check NAN pos 2 'RESULT: ERROR' --threshold nan
check NEG_THRESHOLD pos 2 'RESULT: ERROR' --threshold -0.1
check HIGH_THRESHOLD pos 2 'RESULT: ERROR' --threshold 1.5
check NOT_JSON not-json 2 'RESULT: ERROR'
check OUTER_LIST list 2 'RESULT: ERROR'
check MISSING_EVIDENCE missing-evidence 2 'RESULT: ERROR'
check DUP_ID duplicate-id 2 'RESULT: ERROR'
check UNKNOWN_PAIR unknown-pair 2 'RESULT: ERROR'
check BAD_PAIR bad-pair 2 'RESULT: ERROR'
check UNKNOWN_OVERRIDE unknown-override 2 'RESULT: ERROR'
check HARMLESS_OVERRIDE harmless-override 0 'NOTE override P1 does not leak'
check UNLINTABLE unlintable 2 'RESULT: ERROR'
check EMPTY_ITEMS empty-items 2 'RESULT: ERROR'
check STOPWORDS_DONE stopwords-done 2 'RESULT: ERROR'
check ONE_TOKEN_DONE one-token-done 2 'RESULT: ERROR'
check ALLOWLIST_NOTE allowlist 1 'NOTE allowlist active:'
check ALLOWLIST_EFFECTIVE allowlist-effective 0 'RESULT: CLEAN'
check ALLOWLIST_HYPHENS allowlist-hyphens 2 'RESULT: ERROR'
check LONE_SURROGATE surrogate 2 'RESULT: ERROR'

echo "---- $pass passed, $fail failed"
suite_fail=$fail

# CONTROL1: an always-CLEAN checker must fail the POS assertion.
stub="$ROOT/stub.py"
printf '%s\n' 'print("SUMMARY items=2 leaks=0 overridden=0 threshold=0.35\nRESULT: CLEAN")' > "$stub"
CHECKER="$stub"; pass=0; fail=0
check CONTROL1_stub_on_pos pos 1 'LEAK P4' >/dev/null
if [ "$fail" = 1 ]; then echo "CONTROL1 PASS: always-CLEAN stub fails the POS case"
else echo "CONTROL1 FAIL: the suite cannot detect an always-CLEAN checker"; suite_fail=$((suite_fail+1)); fi

# CONTROL2: require successful wrapper execution and count corruption.
real="${1:-$HERE/../harness/cue_leak_lint.py}"
wrap="$ROOT/wrap.py"
printf '%s\n' 'import subprocess, sys' "p=subprocess.run([sys.executable, sys.argv[1]]+sys.argv[2:],capture_output=True,text=True)" 'success=(p.returncode==1 and "leaks=10 " in p.stdout); sys.stdout.write(p.stdout.replace("leaks=1 ", "leaks=10 ")) if success else sys.stdout.write(p.stdout); sys.exit(p.returncode if success else 2)' > "$wrap"
CHECKER="python3"; pass=0; fail=0
check CONTROL2_corrupt_count pos 1 'SUMMARY items=2 leaks=10 overridden=0 threshold=0.35' "$wrap" "$real" >/dev/null
if [ "$fail" = 1 ]; then echo "CONTROL2 PASS: corrupted-count wrapper fails exact-token assertion"
else echo "CONTROL2 FAIL: wrapper did not demonstrate count corruption"; suite_fail=$((suite_fail+1)); fi

[ "$suite_fail" = 0 ] && { echo "SUITE GREEN"; exit 0; } || { echo "SUITE RED ($suite_fail)"; exit 1; }
