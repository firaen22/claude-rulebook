#!/bin/bash
# test_reconcile_pairs.sh -- fixture suite for harness/reconcile_pairs.py.
#
# Each case builds a synthetic observed/ dir, writes input -> expected exit code
# and expected SUMMARY counts BEFORE running the checker, then compares.  Every
# expectation is matched on whole tokens (ORPHAN=1 does not match ORPHAN=10 --
# codex F3).  Two positive controls close the run: a stub that always prints
# CLEAN/exit 0 must fail the VOID case, and a wrapper that keeps the real exit
# code but corrupts one count must fail the ORPHAN case.  A test that cannot
# fail is not a test.
#
# Usage: test_reconcile_pairs.sh [path/to/reconcile_pairs.py]
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
CHECKER="${1:-$HERE/../harness/reconcile_pairs.py}"
PY="${PYTHON:-python3}"
ROOT="$(mktemp -d "${TMPDIR:-/tmp}/reconcile_pairs.XXXXXX")"
trap 'rm -rf "$ROOT"' EXIT
pass=0; fail=0

# rec DIR NS PID EVENT SRC SESSION PROMPT  -> one .complete.json the way the hook writes it
rec() {
  local dir="$1" ns="$2" pid="$3" event="$4" src="$5" sid="$6" prompt="${7:-p1}"
  local key="trigger"; [ "$event" = "SessionStart" ] && key="source"
  local raw="{\"session_id\":\"$sid\",\"prompt_id\":\"$prompt\",\"hook_event_name\":\"$event\",\"$key\":\"$src\"}"
  "$PY" - "$dir/$ns-$pid.complete.json" "$raw" <<'EOF' || { echo "FIXTURE FAIL: could not write $1"; exit 3; }
import json, sys
json.dump({"observed_at": "2026-09-06T00:00:00Z", "registered_matcher": "x",
           "truncated": False, "saw_eof": True, "raw": sys.argv[2]}, open(sys.argv[1], "w"))
EOF
}
# rawrec DIR NAME RAW_JSON_OR_LITERAL  -> outer envelope with an arbitrary raw value (already JSON-encoded)
rawrec() {
  printf '{"observed_at":"x","registered_matcher":"x","truncated":false,"saw_eof":true,"raw":%s}' "$3" > "$1/$2" \
    || { echo "FIXTURE FAIL: could not write $1/$2"; exit 3; }
}
S=1000000000  # 1 s in ns

# check NAME DIR EXPECT_RC EXPECT_REGEX [extra checker args...]
# EXPECT_REGEX is anchored on whitespace both sides so every token must match exactly.
check() {
  local name="$1" dir="$2" want_rc="$3" want="$4"; shift 4
  local out rc
  out="$("$PY" "$CHECKER" "$dir" "$@" 2>&1)"; rc=$?
  if [ "$rc" = "$want_rc" ] && printf '%s\n' "$out" | grep -qE -- "(^|[[:space:]])${want}([[:space:]]|\$)"; then
    pass=$((pass+1)); echo "PASS $name"
  else
    fail=$((fail+1)); echo "FAIL $name: want rc=$want_rc + /$want/, got rc=$rc"; printf '%s\n' "$out" | sed 's/^/    /'
  fi
}
CLEAN0="PC=0 SSC=0 pairs=0 VOID=0 ORPHAN=0 ANOMALY=0 UNPARSEABLE=0"

# A1 empty dir
d="$ROOT/a1"; mkdir "$d"
check A1_empty "$d" 0 "files=0 in_scope=0 excluded=0 $CLEAN0 other=0"

# A2 three clean pairs, one session, 1-2 min gaps, distinct prompt_ids
d="$ROOT/a2"; mkdir "$d"
for i in 1 2 3; do rec "$d" $((i*1000*S)) 1$i PreCompact manual S1 p$i; rec "$d" $((i*1000*S+90*S)) 2$i SessionStart compact S1 p$i; done
check A2_clean_pairs "$d" 0 "PC=3 SSC=3 pairs=3 VOID=0 ORPHAN=0 ANOMALY=0"

# A3 SSC with no PC at all -> VOID
d="$ROOT/a3"; mkdir "$d"; rec "$d" $((10*S)) 1 SessionStart compact S1
check A3_void "$d" 1 "VOID 10000000000-1.complete.json"
check A3_void_summary "$d" 1 "SSC=1 pairs=0 VOID=1 ORPHAN=0"

# A4 PC never followed -> ORPHAN, exit 0
d="$ROOT/a4"; mkdir "$d"; rec "$d" $((10*S)) 1 PreCompact manual S1
check A4_orphan "$d" 0 "PC=1 SSC=0 pairs=0 VOID=0 ORPHAN=1 ANOMALY=0"

# A5 pair gap above --window -> still a pair, but ANOMALY; widened window -> clean
d="$ROOT/a5"; mkdir "$d"; rec "$d" $((10*S)) 1 PreCompact manual S1; rec "$d" $((10*S+2000*S)) 2 SessionStart compact S1
check A5_gap_anomaly "$d" 1 "pairs=1 VOID=0 ORPHAN=0 ANOMALY=1"
check A5_gap_line "$d" 1 "pair gap 2000.0s exceeds --window 1800s"
check A5_window_widened "$d" 0 "pairs=1 VOID=0 ORPHAN=0 ANOMALY=0" --window 3000
check A5_window_exact "$d" 0 "pairs=1 VOID=0 ORPHAN=0 ANOMALY=0" --window 2000

# A6 two sessions interleaved in time -> paired per session; same prompt_id in two sessions is NOT a pair
d="$ROOT/a6"; mkdir "$d"
rec "$d" $((10*S)) 1 PreCompact manual S1 pA; rec "$d" $((11*S)) 2 PreCompact manual S2 pB
rec "$d" $((12*S)) 3 SessionStart compact S2 pB; rec "$d" $((13*S)) 4 SessionStart compact S1 pA
check A6_interleaved "$d" 0 "PC=2 SSC=2 pairs=2 VOID=0 ORPHAN=0"
d="$ROOT/a6b"; mkdir "$d"; rec "$d" $((10*S)) 1 PreCompact manual S1 pX; rec "$d" $((20*S)) 2 SessionStart compact S2 pX
check A6b_session_blind_guard "$d" 1 "PC=1 SSC=1 pairs=0 VOID=1 ORPHAN=1"

# A7 non-compact SessionStarts and InstallCheck are `other`
d="$ROOT/a7"; mkdir "$d"; i=0
for src in startup resume clear fork; do i=$((i+1)); rec "$d" $((i*S)) $i SessionStart $src S1; done
rec "$d" $((99*S)) 99 InstallCheck none S1
check A7_other_ignored "$d" 0 "$CLEAN0 other=5"

# A8 undefined shapes -> exit 2, each named
d="$ROOT/a8"; mkdir "$d"; printf 'not json' > "$d/$((5*S))-5.complete.json"
check A8_malformed "$d" 2 "UNPARSEABLE 5000000000-5.complete.json"
d="$ROOT/a8b"; mkdir "$d"; touch "$d/.DS_Store"
check A8b_unrecognized_name "$d" 2 "UNPARSEABLE .DS_Store"
check A8b_unrecognized_name_since_cannot_hide "$d" 2 "UNPARSEABLE .DS_Store" --since $((999*S))
# codex r2 F6: an unrecognised name is counted in_scope (files == in_scope + excluded)
check A8b_unrecognized_name_counted "$d" 2 "files=1 in_scope=1 excluded=0 PC=0 SSC=0 pairs=0 VOID=0 ORPHAN=0 ANOMALY=0 UNPARSEABLE=1 other=0" --since $((999*S))
d="$ROOT/a8c"; mkdir "$d"; rawrec "$d" $((5*S))-5.complete.json '"{\"hook_event_name\":\"PreCompact\",\"trigger\":\"manual\",\"prompt_id\":\"p\"}"'
check A8c_missing_session_id "$d" 2 "UNPARSEABLE .*no session_id"
d="$ROOT/a8d"; mkdir "$d"; rawrec "$d" $((5*S))-5.complete.json '"{\"hook_event_name\":\"SessionStart\",\"source\":\"compact\",\"session_id\":\"S1\"}"'
check A8d_missing_prompt_id "$d" 2 "UNPARSEABLE .*no prompt_id"
d="$ROOT/a8e"; mkdir "$d"; rawrec "$d" $((5*S))-5.complete.json 'null'
check A8e_raw_null "$d" 2 "UNPARSEABLE .*raw is NoneType, not a JSON string"
d="$ROOT/a8f"; mkdir "$d"; rawrec "$d" $((5*S))-5.complete.json '{}'
check A8f_raw_object "$d" 2 "UNPARSEABLE .*raw is dict, not a JSON string"
d="$ROOT/a8g"; mkdir "$d"; rawrec "$d" $((5*S))-5.complete.json '"{\"hook_event_name\":\"SessionStart\",\"session_id\":\"S1\",\"prompt_id\":\"p\"}"'
check A8g_ss_missing_source "$d" 2 "UNPARSEABLE .*unknown source None"
d="$ROOT/a8h"; mkdir "$d"; rawrec "$d" $((5*S))-5.complete.json '"{\"hook_event_name\":\"Stop\",\"session_id\":\"S1\"}"'
check A8h_unknown_event "$d" 2 "UNPARSEABLE .*unknown hook_event_name 'Stop'"
d="$ROOT/a8i"; mkdir "$d"; rawrec "$d" $((5*S))-5.complete.json '"{\"hook_event_name\":\"SessionStart\",\"source\":\"teleport\",\"session_id\":\"S1\"}"'
check A8i_unknown_source "$d" 2 "UNPARSEABLE .*unknown source 'teleport'"
d="$ROOT/a8j"; mkdir "$d"; "$PY" -c 'import sys;open(sys.argv[1],"w").write("["*3000+"]"*3000)' "$d/$((5*S))-5.complete.json"
check A8j_deep_nesting "$d" 2 "UNPARSEABLE .*(nesting too deep|is not an object)"
# codex r2 F4: a lone surrogate in an id must be UNPARSEABLE, not a UnicodeEncodeError traceback
d="$ROOT/a8k"; mkdir "$d"; rawrec "$d" $((5*S))-5.complete.json '"{\"hook_event_name\":\"PreCompact\",\"trigger\":\"manual\",\"session_id\":\"\\ud800\",\"prompt_id\":\"p\"}"'
check A8k_surrogate_id "$d" 2 "UNPARSEABLE .*session_id contains a lone surrogate"
# codex r2 F5: a filename with a trailing newline is not a record name; --since cannot hide it
d="$ROOT/a8l"; mkdir "$d"; touch "$d/$((5*S))-5.complete.json"$'\n'
check A8l_newline_name "$d" 2 "filename does not match"
check A8l_newline_name_since_cannot_hide "$d" 2 "files=1 in_scope=1 excluded=0 .*UNPARSEABLE=1" --since $((999*S))
# Fable r2 F-E: outer JSON is a list -> UNPARSEABLE, not an AttributeError traceback
d="$ROOT/a8n"; mkdir "$d"; printf '[]' > "$d/$((5*S))-5.complete.json"
check A8n_outer_list "$d" 2 "UNPARSEABLE .*outer JSON is not an object"
# Fable r2 F-E: unreadable in-scope file -> UNPARSEABLE rc 2, not a traceback
d="$ROOT/a8o"; mkdir "$d"; rec "$d" $((5*S)) 5 PreCompact manual S1; chmod 000 "$d/$((5*S))-5.complete.json"
check A8o_unreadable_file "$d" 2 "UNPARSEABLE .*Permission denied:"
# Fable r2 F-E: empty-string prompt_id is not an identity
d="$ROOT/a8p"; mkdir "$d"; rawrec "$d" $((5*S))-5.complete.json '"{\"hook_event_name\":\"PreCompact\",\"trigger\":\"manual\",\"session_id\":\"S1\",\"prompt_id\":\"\"}"'
check A8p_empty_prompt_id "$d" 2 "UNPARSEABLE .*no prompt_id"

# A9 anomaly files -> exit 1; --since past them -> excluded (count printed), exit 0
d="$ROOT/a9"; mkdir "$d"
printf 'empty stdin' > "$d/$((1*S))-1.error.txt"; printf '{}' > "$d/$((2*S))-2.partial.json"; printf 'x' > "$d/$((3*S))-3.dropped.txt"
rec "$d" $((10*S)) 4 PreCompact manual S1; rec "$d" $((11*S)) 5 SessionStart compact S1
check A9_anomalies "$d" 1 "pairs=1 VOID=0 ORPHAN=0 ANOMALY=3 UNPARSEABLE=0"
check A9_since_ns "$d" 0 "in_scope=2 excluded=3 .*ANOMALY=0" --since $((4*S))
check A9_since_iso "$d" 0 "excluded=3" --since 1970-01-01T00:00:04Z
check A9_since_bad "$d" 2 "bad --since" --since yesterday
d="$ROOT/a9b"; mkdir "$d"
printf '{"observed_at":"x","registered_matcher":"x","truncated":true,"saw_eof":false,"raw":"{}"}' > "$d/$((5*S))-5.complete.json"
check A9b_truncated_complete "$d" 1 "ANOMALY .*truncated=True saw_eof=False"
# Fable r2 F-B: saw_eof=false ALONE, with a valid PC raw, must not be accepted as a healthy PC
PCRAW='"{\"hook_event_name\":\"PreCompact\",\"trigger\":\"manual\",\"session_id\":\"S1\",\"prompt_id\":\"p1\"}"'
d="$ROOT/a9c"; mkdir "$d"
printf '{"observed_at":"x","registered_matcher":"x","truncated":false,"saw_eof":false,"raw":%s}' "$PCRAW" > "$d/$((5*S))-5.complete.json"
check A9c_no_eof_only "$d" 1 "PC=0 SSC=0 pairs=0 VOID=0 ORPHAN=0 ANOMALY=1 UNPARSEABLE=0"
check A9c_no_eof_line "$d" 1 "ANOMALY .*truncated=False saw_eof=False"
# Fable r2 F-C: `truncated` key absent is ANOMALY, not healthy
d="$ROOT/a9d"; mkdir "$d"
printf '{"observed_at":"x","registered_matcher":"x","saw_eof":true,"raw":%s}' "$PCRAW" > "$d/$((5*S))-5.complete.json"
check A9d_truncated_key_absent "$d" 1 "ANOMALY .*truncated=None saw_eof=True"

# A10 PC, SSC(same id), SSC(other id) -> 1 pair + 1 VOID
d="$ROOT/a10"; mkdir "$d"; rec "$d" $((10*S)) 1 PreCompact manual S1 p1; rec "$d" $((11*S)) 2 SessionStart compact S1 p1; rec "$d" $((12*S)) 3 SessionStart compact S1 p2
check A10_second_ssc_void "$d" 1 "PC=1 SSC=2 pairs=1 VOID=1 ORPHAN=0"

# A11 codex F1: cancelled PC(p1), healthy PC(p2)+SSC(p2), then SSC(p3) whose PC dropped -> VOID not masked
d="$ROOT/a11"; mkdir "$d"
rec "$d" $((10*S)) 1 PreCompact manual S1 p1; rec "$d" $((20*S)) 2 PreCompact manual S1 p2
rec "$d" $((21*S)) 3 SessionStart compact S1 p2; rec "$d" $((30*S)) 4 SessionStart compact S1 p3
check A11_masking_closed "$d" 1 "PC=2 SSC=2 pairs=1 VOID=1 ORPHAN=1 ANOMALY=0"
check A11_orphan_is_p1 "$d" 1 "ORPHAN 10000000000-1.complete.json"
check A11_void_is_p3 "$d" 1 "VOID 30000000000-4.complete.json"
# Fable F-1: orphan PC inside the window, next compaction's PC dropped
d="$ROOT/a11b"; mkdir "$d"; rec "$d" $((10*S)) 1 PreCompact manual S1 p1; rec "$d" $((300*S)) 2 SessionStart compact S1 p2
check A11b_orphan_not_claimed "$d" 1 "pairs=0 VOID=1 ORPHAN=1"

# A12 trigger auto counts as PreCompact
d="$ROOT/a12"; mkdir "$d"; rec "$d" $((10*S)) 1 PreCompact auto S1; rec "$d" $((11*S)) 2 SessionStart compact S1
check A12_auto_trigger "$d" 0 "PC=1 SSC=1 pairs=1 VOID=0"

# A13 missing directory / bad window -> exit 2
check A13_no_dir "$ROOT/does-not-exist" 2 "ERROR: not a directory:"
check A13_window_nan "$ROOT/a1" 2 "bad --window" --window nan
check A13_window_negative "$ROOT/a1" 2 "bad --window" --window -1
check A13_window_inf "$ROOT/a1" 2 "bad --window" --window inf

# A14 identity reuse -> ANOMALY (two PCs same id; two SSCs same id)
d="$ROOT/a14"; mkdir "$d"; rec "$d" $((10*S)) 1 PreCompact manual S1 p1; rec "$d" $((11*S)) 2 PreCompact manual S1 p1; rec "$d" $((12*S)) 3 SessionStart compact S1 p1
check A14_dup_pc "$d" 1 "pairs=0 VOID=0 ORPHAN=0 ANOMALY=1"
check A14_dup_pc_line "$d" 1 "2 PreCompact \+ 1 SessionStart/compact records share"
# codex r2 F3 / Fable r2 F-A: two SSCs same id (a second compaction whose PC dropped, reusing the id) -> ANOMALY, never a healthy pair
d="$ROOT/a14b"; mkdir "$d"; rec "$d" $((10*S)) 1 PreCompact manual S1 p1; rec "$d" $((11*S)) 2 SessionStart compact S1 p1; rec "$d" $((12*S)) 3 SessionStart compact S1 p1
check A14b_dup_ssc "$d" 1 "PC=1 SSC=2 pairs=0 VOID=0 ORPHAN=0 ANOMALY=1"
check A14b_dup_ssc_line "$d" 1 "1 PreCompact \+ 2 SessionStart/compact records share"
d="$ROOT/a14c"; mkdir "$d"; rec "$d" $((10*S)) 1 SessionStart compact S1 p1; rec "$d" $((11*S)) 2 SessionStart compact S1 p1
check A14c_dup_ssc_no_pc "$d" 1 "PC=0 SSC=2 pairs=0 VOID=0 ORPHAN=0 ANOMALY=1"

# A15 SSC ns not after PC ns (equal, and reversed) -> pair counted but ANOMALY
d="$ROOT/a15"; mkdir "$d"; rec "$d" $((10*S)) 9 SessionStart compact S1; rec "$d" $((10*S)) 1 PreCompact manual S1
check A15_equal_ns "$d" 1 "pairs=1 VOID=0 ORPHAN=0 ANOMALY=1"
d="$ROOT/a15b"; mkdir "$d"; rec "$d" $((20*S)) 1 PreCompact manual S1; rec "$d" $((10*S)) 2 SessionStart compact S1
check A15b_reversed "$d" 1 "ns is not after its PreCompact"

# A16 codex F6 / Fable F-4: --since between PC and SSC -> still a pair, not VOID; pre-cutoff PC not counted
d="$ROOT/a16"; mkdir "$d"; rec "$d" $((10*S)) 1 PreCompact manual S1; rec "$d" $((20*S)) 2 SessionStart compact S1
check A16_since_straddle "$d" 0 "in_scope=1 excluded=1 PC=0 SSC=1 pairs=1 VOID=0 ORPHAN=0" --since $((15*S))
# a pre-cutoff orphan is excluded, not reported
check A16b_since_hides_old_orphan "$ROOT/a4" 0 "in_scope=0 excluded=1 $CLEAN0" --since $((15*S))
# --since equal to a file's ns includes it (>= semantics; Fable M6 off-by-one mutant)
check A16c_since_boundary_inclusive "$ROOT/a4" 0 "in_scope=1 excluded=0 PC=1 SSC=0 pairs=0 VOID=0 ORPHAN=1" --since $((10*S))
# Fable r2 F-D: a pre-cutoff lone SSC is excluded, not reported as VOID
check A16d_since_hides_old_void "$ROOT/a3" 0 "in_scope=0 excluded=1 $CLEAN0" --since $((15*S))
# codex r2 F1: pre-cutoff PC+SSC plus an in-scope duplicate SSC -> the dup is still an ANOMALY (context includes SSCs)
d="$ROOT/a16e"; mkdir "$d"; rec "$d" $((10*S)) 1 PreCompact manual S1 p1; rec "$d" $((11*S)) 2 SessionStart compact S1 p1; rec "$d" $((20*S)) 3 SessionStart compact S1 p1
check A16e_since_dup_ssc_not_hidden "$d" 1 "in_scope=1 excluded=2 PC=0 SSC=1 pairs=0 VOID=0 ORPHAN=0 ANOMALY=1" --since $((15*S))
check A16e_since_dup_ssc_line "$d" 1 "1 PreCompact \+ 2 SessionStart/compact records share" --since $((15*S))
# codex r2 F2: a wholly pre-cutoff duplicate is context only, not reported
d="$ROOT/a16f"; mkdir "$d"; rec "$d" $((10*S)) 1 PreCompact manual S1 p1; rec "$d" $((11*S)) 2 PreCompact manual S1 p1
check A16f_since_hides_old_dup "$d" 0 "in_scope=0 excluded=2 $CLEAN0" --since $((15*S))
# Fable r2 F-I: an inverted pair straddling the cutoff stays visible (pre-cutoff SSC is context)
d="$ROOT/a16g"; mkdir "$d"; rec "$d" $((10*S)) 1 SessionStart compact S1 p1; rec "$d" $((20*S)) 2 PreCompact manual S1 p1
check A16g_since_inversion_visible "$d" 1 "in_scope=1 excluded=1 PC=1 SSC=0 pairs=1 VOID=0 ORPHAN=0 ANOMALY=1" --since $((15*S))
check A16g_since_inversion_line "$d" 1 "ns is not after its PreCompact" --since $((15*S))

# A17 ns compared numerically, not lexically: 9s PC then 10s SSC (different digit counts) is a healthy pair
d="$ROOT/a17"; mkdir "$d"; rec "$d" $((9*S)) 1 PreCompact manual S1; rec "$d" $((10*S)) 2 SessionStart compact S1
check A17_numeric_ns_order "$d" 0 "pairs=1 VOID=0 ORPHAN=0 ANOMALY=0"

echo "---- $pass passed, $fail failed"
suite_fail=$fail

# Control 1: a stub that always says CLEAN must make the VOID case FAIL.
stub="$ROOT/stub.py"; printf 'print("SUMMARY stub\\nRESULT: CLEAN")\n' > "$stub"
CHECKER="$stub"; pass=0; fail=0
check CONTROL1_stub_on_void "$ROOT/a3" 1 "VOID=1" >/dev/null
if [ "$fail" = 1 ]; then echo "CONTROL1 PASS: always-CLEAN stub fails the VOID case"
else echo "CONTROL1 FAIL: the suite cannot detect an always-CLEAN checker"; suite_fail=$((suite_fail+1)); fi

# Control 2: correct exit code, one corrupted count (ORPHAN=1 -> ORPHAN=10) must FAIL the ORPHAN case.
real="${1:-$HERE/../harness/reconcile_pairs.py}"
wrap="$ROOT/wrap.py"; cat > "$wrap" <<EOF
import subprocess, sys
p = subprocess.run([sys.executable, "$real"] + sys.argv[1:], capture_output=True, text=True)
sys.stdout.write(p.stdout.replace("ORPHAN=1 ", "ORPHAN=10 ")); sys.exit(p.returncode)
EOF
CHECKER="$wrap"; pass=0; fail=0
check CONTROL2_wrap_on_orphan "$ROOT/a4" 0 "PC=1 SSC=0 pairs=0 VOID=0 ORPHAN=1 ANOMALY=0" >/dev/null
if [ "$fail" = 1 ]; then echo "CONTROL2 PASS: corrupted-count wrapper fails the ORPHAN case (tokens are exact)"
else echo "CONTROL2 FAIL: ORPHAN=10 satisfied an ORPHAN=1 assertion"; suite_fail=$((suite_fail+1)); fi

[ "$suite_fail" = 0 ] && { echo "SUITE GREEN"; exit 0; } || { echo "SUITE RED ($suite_fail)"; exit 1; }
