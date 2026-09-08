#!/bin/bash
# test_pairfloor.sh -- fixture suite for harness/pairfloor.py.
# Each case writes input -> expected exit code/token before running the
# checker. Matches are whole tokens. The two controls must fail assertions.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
CHECKER="${1:-$HERE/../harness/pairfloor.py}"
PY="${PYTHON:-python3}"
ROOT="$(mktemp -d "${TMPDIR:-/tmp}/pairfloor.XXXXXX")"
trap 'rm -rf "$ROOT"' EXIT
pass=0; fail=0

make_manifest() {
  local mode="$1" path="$2"
  "$PY" - "$mode" "$path" <<'PYEOF' || { echo "FIXTURE FAIL: could not write $2"; exit 3; }
import json, sys
mode, path = sys.argv[1:]
ids = ["A%d" % n for n in range(1, 13)]
pairs = [[ids[n], ids[n + 1]] for n in range(0, 12, 2)]
base = {"items": [{"id": item_id, "key": "ignored"} for item_id in ids],
        "pairs": pairs}
five = dict(base, pairs=pairs[:5])
six = dict(base, pairs=pairs[:6])
if mode == "six": value = six
elif mode == "five": value = five
elif mode == "empty-items": value = dict(base, items=[], pairs=[])
elif mode == "empty-pairs": value = dict(base, pairs=[])
elif mode == "self": value = dict(base, pairs=[["A1", "A1"]])
elif mode == "conflict": value = dict(base, pairs=[["A1", "A2"], ["A1", "A3"]])
elif mode == "conflict-max": value = dict(base, pairs=[["A1", "A3"], ["A2", "A3"]])
elif mode == "unknown-pair": value = dict(base, pairs=[["A1", "A99"]])
elif mode == "duplicate-id": value = dict(base, items=base["items"] + [{"id": "A1"}])
elif mode == "bad-pair": value = dict(base, pairs=[["A1"]])
elif mode == "nonstring-null": value = dict(base, pairs=[["A1", None]])
elif mode == "nonstring-number": value = dict(base, pairs=[["A1", 123]])
elif mode == "nonstring-list": value = dict(base, pairs=[["A1", ["A2"]]])
elif mode == "surrogate": value = dict(base, items=base["items"] + [{"id": "bad\ud800"}], pairs=[])
elif mode == "unknown-key": value = dict(six, itemz=True)
elif mode == "not-json": open(path, "w").write("not json"); raise SystemExit
elif mode == "list": open(path, "w").write("[]"); raise SystemExit
elif mode == "missing-items": value = {"pairs": pairs}
elif mode == "missing-pairs": value = {"items": base["items"]}
elif mode == "tolerated": value = dict(six, done_when=None, allowlist="not-a-list", overrides=[]) 
elif mode == "duplicate-pairs": value = dict(six, pairs=pairs[:4] + [["A2", "A1"], ["A3", "A4"]])
else: raise SystemExit("unknown fixture mode " + mode)
json.dump(value, open(path, "w"))
PYEOF
}

# check NAME MODE EXPECT_RC EXPECT_TOKEN [extra checker args...]
check() {
  local name="$1" mode="$2" want_rc="$3" want="$4"; shift 4
  local path="$ROOT/$name.json" out rc
  make_manifest "$mode" "$path"
  out="$($PY "$CHECKER" "$path" "$@" 2>&1)"; rc=$?
  if [ "$rc" = "$want_rc" ] && printf '%s\n' "$out" | grep -qE -- "(^|[[:space:]])${want}([[:space:]]|$)"; then
    pass=$((pass+1)); echo "PASS $name"
  else
    fail=$((fail+1)); echo "FAIL $name: want rc=$want_rc + /$want/, got rc=$rc"; printf '%s\n' "$out" | sed 's/^/    /'
  fi
}

check SIX_OK six 0 'SUMMARY pairs=6 floor=6'
check SIX_RESULT six 0 'RESULT: OK'
check FIVE_UNDERPOWERED five 1 'RESULT: UNDERPOWERED'
check FIVE_COUNT five 1 'SUMMARY pairs=5 floor=6'
check FLOOR_BOUNDARY five 0 'SUMMARY pairs=5 floor=5' --floor 5
check DUPLICATE_DEDUP duplicate-pairs 1 'SUMMARY pairs=4 floor=6'
check EMPTY_ITEMS empty-items 2 'RESULT: ERROR'
check EMPTY_PAIRS empty-pairs 1 'SUMMARY pairs=0 floor=6'
check SELF_PAIR self 2 'RESULT: ERROR'
check CONFLICT conflict 2 'RESULT: ERROR'
check CONFLICT_MAX conflict-max 2 'RESULT: ERROR'
check UNKNOWN_PAIR unknown-pair 2 'RESULT: ERROR'
check DUPLICATE_ID duplicate-id 2 'RESULT: ERROR'
check BAD_PAIR bad-pair 2 'RESULT: ERROR'
check NONSTRING_NULL nonstring-null 2 'RESULT: ERROR'
check NONSTRING_NUMBER nonstring-number 2 'RESULT: ERROR'
check NONSTRING_LIST nonstring-list 2 'RESULT: ERROR'
check LONE_SURROGATE surrogate 2 'RESULT: ERROR'
check UNKNOWN_KEY unknown-key 2 'RESULT: ERROR'
check NOT_JSON not-json 2 'RESULT: ERROR'
check OUTER_LIST list 2 'RESULT: ERROR'
check MISSING_ITEMS missing-items 2 'RESULT: ERROR'
check MISSING_PAIRS missing-pairs 2 'RESULT: ERROR'
check TOLERATED_FIELDS tolerated 0 'RESULT: OK'
check REVERSED_CANONICAL duplicate-pairs 1 'pair A1 A2'
check BAD_FLOOR_ZERO six 2 'RESULT: ERROR' --floor 0
check BAD_FLOOR_NEGATIVE six 2 'RESULT: ERROR' --floor -1
check BAD_FLOOR_FLOAT six 2 'RESULT: ERROR' --floor 6.5
check BAD_FLOOR_NAN six 2 'RESULT: ERROR' --floor nan
check BAD_FLOOR_PLUS six 2 'RESULT: ERROR' --floor +6
check BAD_FLOOR_DECIMAL six 2 'RESULT: ERROR' --floor 6.0
check BAD_FLOOR_LEADING_ZERO six 2 'RESULT: ERROR' --floor 06
check BAD_FLOOR_SPACE six 2 'RESULT: ERROR' --floor ' 6 '
check BAD_FLOOR_EMPTY six 2 'RESULT: ERROR' --floor ''

# ERROR output must not expose an undefined count or pair listing.
error_path="$ROOT/error-output.json"; make_manifest empty-items "$error_path"
error_out="$($PY "$CHECKER" "$error_path" 2>&1)"; error_rc=$?
if [ "$error_rc" = 2 ] && ! printf '%s\n' "$error_out" | grep -qE '(^|[[:space:]])(SUMMARY|pair )'; then
  pass=$((pass+1)); echo "PASS ERROR_has_no_summary_or_pairs"
else
  fail=$((fail+1)); echo "FAIL ERROR_has_no_summary_or_pairs: got rc=$error_rc"; printf '%s\n' "$error_out" | sed 's/^/    /'
fi

echo "---- $pass passed, $fail failed"
suite_fail=$fail

# CONTROL1: an always-OK checker must fail the UNDERPOWERED assertion.
stub="$ROOT/stub.py"
printf '%s\n' 'print("SUMMARY pairs=5 floor=6\nRESULT: OK")' > "$stub"
CHECKER="$stub"; pass=0; fail=0
check CONTROL1_stub_on_five five 1 'RESULT: UNDERPOWERED' >/dev/null
if [ "$fail" = 1 ]; then echo "CONTROL1 PASS: always-OK stub fails the UNDERPOWERED case"
else echo "CONTROL1 FAIL: the suite cannot detect an always-OK checker"; suite_fail=$((suite_fail+1)); fi

# CONTROL2: require successful wrapper execution and count corruption, then
# ensure the exact expected count assertion rejects the corrupted output.
real="${1:-$HERE/../harness/pairfloor.py}"
wrap="$ROOT/wrap.py"
printf '%s\n' 'import subprocess, sys' "p=subprocess.run([sys.executable, sys.argv[1]]+sys.argv[2:],capture_output=True,text=True)" 'success=(p.returncode==0 and "pairs=6 " in p.stdout); mutated=p.stdout.replace("pairs=6 ", "pairs=5 "); sys.stdout.write(mutated if success else p.stdout); sys.exit(p.returncode if success else 2)' > "$wrap"
control2_path="$ROOT/control2.json"; make_manifest six "$control2_path"
control2_out="$($PY "$wrap" "$real" "$control2_path" 2>&1)"; control2_rc=$?
# Wrapper must execute (rc 0) AND emit the mutated pairs=5 token...
control2_bites=0
if [ "$control2_rc" = 0 ] && printf '%s\n' "$control2_out" | grep -qE -- '(^|[[:space:]])SUMMARY pairs=5 floor=6([[:space:]]|$)'; then
  control2_bites=1
fi
# ...and the suite's own exact-count ERE (the one check() uses for SIX_OK) must
# MISS on the corrupted output, proving the assertion reads the count, not just rc.
control2_rejects=0
if ! printf '%s\n' "$control2_out" | grep -qE -- '(^|[[:space:]])SUMMARY pairs=6 floor=6([[:space:]]|$)'; then
  control2_rejects=1
fi
if [ "$control2_bites" = 1 ] && [ "$control2_rejects" = 1 ]; then
  echo "CONTROL2 PASS: corrupted-count wrapper executes (rc 0, pairs=5) and the exact pairs=6 assertion rejects it"
else echo "CONTROL2 FAIL: wrapper did not demonstrate count corruption (bites=$control2_bites rejects=$control2_rejects)"; suite_fail=$((suite_fail+1)); fi

[ "$suite_fail" = 0 ] && { echo "SUITE GREEN"; exit 0; } || { echo "SUITE RED ($suite_fail)"; exit 1; }
