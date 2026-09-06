# Review packet — reconcile_pairs.py (passive VOID detector for the compaction hook)

You are reviewing ONE new harness instrument (a python3 script + its bash fixture
suite). You cannot see the repo; everything is inlined. Return a structured
verdict; last line `PROCEED` or `FIX <ids>`.

## Context
`observe-compaction-events.sh` is a macOS Claude Code hook (bash 3.2) registered
on PreCompact (matchers manual/auto) AND SessionStart (matchers startup/resume/
clear/compact/fork). Each firing writes ONE file into `~/.claude/session-state/
observed/`: `<time.time_ns()>-<pid>.complete.json` on success (fields observed_at
[UTC seconds], registered_matcher, truncated, saw_eof, raw = the JSON the host
piped on stdin, which carries hook_event_name, session_id, and trigger [PreCompact]
or source [SessionStart]); `*.error.txt` / `*.partial.json` on its own failure
paths. One known failure class (fixed in v30, cross-model reviewed) was a SILENT
drop: exit 0 and NO file. A directory watcher can never see that.

Idea under review: every compaction fires PreCompact first and SessionStart
source=compact afterwards (same session_id; live gaps seen 60-90s, compaction of
a large context may take minutes). So a SessionStart/compact record with no
preceding unclaimed PreCompact record from the same session IS a PreCompact VOID
made visible — from data already written, no polling, no hook change. Unclaimed
PreCompacts are ORPHANs (informational: cancelled compaction, session exit, or
the SessionStart hook dropping instead). Not folded into run_all.sh (which grades
synthetic state) — run on demand.

Verified before dispatch (2026-09-06): the ns filename prefix is monotone with
observed_at over all 396 live complete.json files (0 inversions, |ns/1e9 -
observed_at| <= 1.0s). Fixture suite 21/21 + stub-checker positive control
(a checker that always says CLEAN makes the VOID case FAIL). Live run over 403
files, prediction written BEFORE running: PC=70 SSC=66 pairs=66 VOID=0 ORPHAN=4
ANOMALY=7 (legacy .error.txt from 08-30/31 empty-stdin tests) rc=1; with
--since past them rc=0. Actual matched exactly.

## Rubric — answer each, probe the SILENT side hardest
Cost asymmetry: a FALSE NEGATIVE (a real PreCompact VOID the pairing rule
hides) is the expensive failure — it is the very class this exists to catch. A
false positive costs one file to inspect.
1. False negatives: enumerate concrete file sequences where a PreCompact VOID
   is NOT reported (orphan masking inside the window, session_id semantics
   across compaction/resume/fork, ordering-key edge cases, auto vs manual,
   two compactions inside one window, host writes SessionStart/compact without
   a PreCompact for a legitimate reason). For each: is it a real gap, and the
   minimal change.
2. False positives / mis-classification: sequences reported VOID or ORPHAN
   that are actually healthy.
3. Exit-code and --since semantics: any path that returns 0 while something
   was skipped or unrecognised? Any silent cap or swallowed exception?
4. The fixture suite: can each assertion actually fail? Are any substring
   patterns so loose they pass on wrong output? Is the positive control real?
5. bash 3.2 / macOS portability of the test script; python3 version assumptions.
6. Anything in the README paragraph (below) that the code does not actually do.

Report each finding as: location (file:line) + mechanism + concrete minimal fix,
severity-ranked, tagged [verified: how] / [reasoned]. Last line `PROCEED` or
`FIX <ids>`.

## File 1: harness/reconcile_pairs.py
```python
     1	#!/usr/bin/env python3
     2	"""reconcile_pairs.py -- passive VOID detector for the compaction hook.
     3	
     4	A v30 PreCompact VOID is SILENT: the hook exits 0 and writes no file, so no
     5	directory watcher can ever see it.  But every compaction fires TWO hooks that
     6	both write into the same observed/ dir: `PreCompact` (before) and
     7	`SessionStart` with `source: "compact"` (after, same session_id).  A
     8	SessionStart/compact record with no preceding unclaimed PreCompact record from
     9	the same session is therefore a PreCompact VOID made visible -- detected from
    10	data the hooks already write, with no polling and no hook change.
    11	
    12	Pairing rule, per session_id, in filename-ns order (the worker's time.time_ns,
    13	verified monotone with observed_at over 396 live files):
    14	  * PreCompact (any trigger)          -> pushed on the session's unclaimed list
    15	  * SessionStart source=="compact"    -> claims the MOST RECENT unclaimed
    16	    PreCompact whose age is <= --window seconds; none available -> VOID
    17	  * unclaimed PreCompact at the end   -> ORPHAN (compaction cancelled, session
    18	    exited, or the SessionStart hook itself dropped -- informational)
    19	Other SessionStart sources (startup/resume/clear/fork) and InstallCheck are
    20	counted as `other` and ignored.
    21	
    22	Exit codes: 0 clean; 1 >=1 VOID or anomaly file (*.error.txt, *.partial.json,
    23	*.dropped.txt, or a *.complete.json with truncated/no-EOF) in scope;
    24	2 an unparseable *.complete.json or an unrecognized filename (fail loud --
    25	never silently skip a shape this script did not define).  --since excludes
    26	files whose ns prefix is older than the cutoff and PRINTS the excluded count.
    27	"""
    28	import argparse
    29	import datetime
    30	import json
    31	import os
    32	import re
    33	import sys
    34	
    35	NAME_RE = re.compile(r"^(\d+)-(\d+)\.(complete\.json|partial\.json|error\.txt|dropped\.txt)$")
    36	ANOMALY_SUFFIXES = ("partial.json", "error.txt", "dropped.txt")
    37	DEFAULT_DIR = os.path.expanduser("~/.claude/session-state/observed")
    38	
    39	
    40	def parse_since(text):
    41	    """--since accepts an integer ns timestamp or an ISO-8601 UTC instant
    42	    (YYYY-MM-DDTHH:MM:SSZ, the observed_at format)."""
    43	    if text is None:
    44	        return None
    45	    if text.isdigit():
    46	        return int(text)
    47	    dt = datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")
    48	    return int(dt.replace(tzinfo=datetime.timezone.utc).timestamp() * 1_000_000_000)
    49	
    50	
    51	def load_complete(path):
    52	    """Return (kind, session_id, detail).  kind in {PC, SSC, other, anomaly}.
    53	    Raises ValueError on any shape this script does not define."""
    54	    with open(path, "rb") as fh:
    55	        outer = json.loads(fh.read().decode("utf-8"))
    56	    if not isinstance(outer, dict):
    57	        raise ValueError("outer JSON is not an object")
    58	    for key in ("observed_at", "registered_matcher", "raw"):
    59	        if key not in outer:
    60	            raise ValueError("missing key %r" % key)
    61	    if outer.get("truncated") is not False or outer.get("saw_eof") is not True:
    62	        return ("anomaly", None, "complete.json with truncated=%r saw_eof=%r"
    63	                % (outer.get("truncated"), outer.get("saw_eof")))
    64	    raw = json.loads(outer["raw"])
    65	    if not isinstance(raw, dict):
    66	        raise ValueError("raw JSON is not an object")
    67	    event = raw.get("hook_event_name")
    68	    if event == "PreCompact":
    69	        kind = "PC"
    70	    elif event == "SessionStart" and raw.get("source") == "compact":
    71	        kind = "SSC"
    72	    else:
    73	        return ("other", None, "%s/%s" % (event, raw.get("trigger") or raw.get("source")))
    74	    sid = raw.get("session_id")
    75	    if not isinstance(sid, str) or not sid:
    76	        raise ValueError("%s record has no session_id" % event)
    77	    return (kind, sid, event)
    78	
    79	
    80	def reconcile(directory, window_s, since_ns):
    81	    window_ns = int(window_s * 1_000_000_000)
    82	    counts = dict(files=0, in_scope=0, excluded=0, PC=0, SSC=0, pairs=0,
    83	                  VOID=0, ORPHAN=0, ANOMALY=0, UNPARSEABLE=0, other=0)
    84	    lines = []          # human-readable findings, one per line
    85	    events = {}         # session_id -> list of (ns, kind, filename)
    86	
    87	    for name in sorted(os.listdir(directory)):
    88	        counts["files"] += 1
    89	        m = NAME_RE.match(name)
    90	        if not m:
    91	            counts["UNPARSEABLE"] += 1
    92	            lines.append("UNPARSEABLE %s :: filename does not match <ns>-<pid>.<known suffix>" % name)
    93	            continue
    94	        ns = int(m.group(1))
    95	        if since_ns is not None and ns < since_ns:
    96	            counts["excluded"] += 1
    97	            continue
    98	        counts["in_scope"] += 1
    99	        suffix = m.group(3)
   100	        if suffix in ANOMALY_SUFFIXES:
   101	            counts["ANOMALY"] += 1
   102	            lines.append("ANOMALY %s :: hook failure-path record (%s)" % (name, suffix))
   103	            continue
   104	        try:
   105	            kind, sid, detail = load_complete(os.path.join(directory, name))
   106	        except (ValueError, json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
   107	            counts["UNPARSEABLE"] += 1
   108	            lines.append("UNPARSEABLE %s :: %s" % (name, exc))
   109	            continue
   110	        if kind == "anomaly":
   111	            counts["ANOMALY"] += 1
   112	            lines.append("ANOMALY %s :: %s" % (name, detail))
   113	        elif kind == "other":
   114	            counts["other"] += 1
   115	        else:
   116	            counts[kind] += 1
   117	            events.setdefault(sid, []).append((ns, kind, name))
   118	
   119	    for sid, evs in sorted(events.items()):
   120	        evs.sort()                      # ns order; filenames are unique so no ties
   121	        unclaimed = []                  # list of (ns, name) PreCompacts, oldest first
   122	        for ns, kind, name in evs:
   123	            if kind == "PC":
   124	                unclaimed.append((ns, name))
   125	                continue
   126	            # SSC: claim the most recent unclaimed PC within the window
   127	            for i in range(len(unclaimed) - 1, -1, -1):
   128	                if ns - unclaimed[i][0] <= window_ns:
   129	                    unclaimed.pop(i)
   130	                    counts["pairs"] += 1
   131	                    break
   132	            else:
   133	                counts["VOID"] += 1
   134	                lines.append("VOID %s :: SessionStart/compact for session %s with no PreCompact "
   135	                             "record in the preceding %ds" % (name, sid[:8], window_s))
   136	        for ns, name in unclaimed:
   137	            counts["ORPHAN"] += 1
   138	            lines.append("ORPHAN %s :: PreCompact for session %s never followed by a "
   139	                         "SessionStart/compact" % (name, sid[:8]))
   140	
   141	    return counts, lines
   142	
   143	
   144	def main(argv=None):
   145	    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
   146	    ap.add_argument("directory", nargs="?", default=DEFAULT_DIR)
   147	    ap.add_argument("--window", type=float, default=1800.0,
   148	                    help="max seconds between a PreCompact and the SessionStart/compact "
   149	                         "that claims it (default 1800; live gaps seen so far are ~1-2 min)")
   150	    ap.add_argument("--since", default=None,
   151	                    help="exclude files whose ns prefix is older than this (int ns or "
   152	                         "YYYY-MM-DDTHH:MM:SSZ); the excluded count is always printed")
   153	    args = ap.parse_args(argv)
   154	
   155	    if not os.path.isdir(args.directory):
   156	        print("ERROR: not a directory: %s" % args.directory)
   157	        return 2
   158	    try:
   159	        since_ns = parse_since(args.since)
   160	    except ValueError as exc:
   161	        print("ERROR: bad --since %r: %s" % (args.since, exc))
   162	        return 2
   163	
   164	    counts, lines = reconcile(args.directory, args.window, since_ns)
   165	    print("SUMMARY " + " ".join("%s=%d" % (k, counts[k]) for k in
   166	          ("files", "in_scope", "excluded", "PC", "SSC", "pairs", "VOID", "ORPHAN",
   167	           "ANOMALY", "UNPARSEABLE", "other")))
   168	    for line in lines:
   169	        print(line)
   170	    if counts["UNPARSEABLE"]:
   171	        print("RESULT: ERROR (unparseable/unrecognized files -- fix the shape or the script)")
   172	        return 2
   173	    if counts["VOID"] or counts["ANOMALY"]:
   174	        print("RESULT: VOID" if counts["VOID"] else "RESULT: ANOMALY")
   175	        return 1
   176	    print("RESULT: CLEAN")
   177	    return 0
   178	
   179	
   180	if __name__ == "__main__":
   181	    sys.exit(main())
```

## File 2: scripts/test_reconcile_pairs.sh
```bash
     1	#!/bin/bash
     2	# test_reconcile_pairs.sh -- fixture suite for harness/reconcile_pairs.py.
     3	#
     4	# Each case builds a synthetic observed/ dir, writes input -> expected exit code
     5	# and expected SUMMARY counts BEFORE running the checker, then compares.  The
     6	# final step is a positive control: the same VOID fixture is graded by a stub
     7	# checker that always prints CLEAN/exit 0, and the suite must go red -- a test
     8	# that cannot fail is not a test.
     9	#
    10	# Usage: test_reconcile_pairs.sh [path/to/reconcile_pairs.py]
    11	set -u
    12	HERE="$(cd "$(dirname "$0")" && pwd)"
    13	CHECKER="${1:-$HERE/../harness/reconcile_pairs.py}"
    14	PY="${PYTHON:-python3}"
    15	ROOT="$(mktemp -d "${TMPDIR:-/tmp}/reconcile_pairs.XXXXXX")"
    16	trap 'rm -rf "$ROOT"' EXIT
    17	pass=0; fail=0
    18	
    19	# rec DIR NS PID EVENT SRC SESSION   -> writes one .complete.json the way the hook does
    20	rec() {
    21	  local dir="$1" ns="$2" pid="$3" event="$4" src="$5" sid="$6"
    22	  local key="trigger"; [ "$event" = "SessionStart" ] && key="source"
    23	  local raw="{\"session_id\":\"$sid\",\"hook_event_name\":\"$event\",\"$key\":\"$src\"}"
    24	  "$PY" - "$dir/$ns-$pid.complete.json" "$raw" <<'EOF'
    25	import json, sys
    26	json.dump({"observed_at": "2026-09-06T00:00:00Z", "registered_matcher": "x",
    27	           "truncated": False, "saw_eof": True, "raw": sys.argv[2]}, open(sys.argv[1], "w"))
    28	EOF
    29	}
    30	S=1000000000  # 1 s in ns
    31	
    32	# check NAME DIR EXPECT_RC EXPECT_SUBSTR [extra checker args...]
    33	check() {
    34	  local name="$1" dir="$2" want_rc="$3" want="$4"; shift 4
    35	  local out rc
    36	  out="$("$PY" "$CHECKER" "$dir" "$@" 2>&1)"; rc=$?
    37	  if [ "$rc" = "$want_rc" ] && printf '%s\n' "$out" | grep -q -- "$want"; then
    38	    pass=$((pass+1)); echo "PASS $name"
    39	  else
    40	    fail=$((fail+1)); echo "FAIL $name: want rc=$want_rc + /$want/, got rc=$rc"; printf '%s\n' "$out" | sed 's/^/    /'
    41	  fi
    42	}
    43	
    44	# A1 empty dir
    45	d="$ROOT/a1"; mkdir "$d"
    46	check A1_empty "$d" 0 "files=0 in_scope=0 excluded=0 PC=0 SSC=0 pairs=0 VOID=0 ORPHAN=0"
    47	
    48	# A2 three clean pairs, one session, 1-2 min gaps
    49	d="$ROOT/a2"; mkdir "$d"
    50	for i in 1 2 3; do rec "$d" $((i*1000*S)) 1$i PreCompact manual S1; rec "$d" $((i*1000*S+90*S)) 2$i SessionStart compact S1; done
    51	check A2_clean_pairs "$d" 0 "PC=3 SSC=3 pairs=3 VOID=0 ORPHAN=0"
    52	
    53	# A3 SSC with no PC at all -> VOID
    54	d="$ROOT/a3"; mkdir "$d"; rec "$d" $((10*S)) 1 SessionStart compact S1
    55	check A3_void "$d" 1 "VOID .*1000000000[0-9]*-1.complete.json"
    56	check A3_void_summary "$d" 1 "SSC=1 pairs=0 VOID=1"
    57	
    58	# A4 PC never followed -> ORPHAN, exit 0
    59	d="$ROOT/a4"; mkdir "$d"; rec "$d" $((10*S)) 1 PreCompact manual S1
    60	check A4_orphan "$d" 0 "PC=1 SSC=0 pairs=0 VOID=0 ORPHAN=1"
    61	
    62	# A5 PC older than window -> not claimable: VOID + ORPHAN
    63	d="$ROOT/a5"; mkdir "$d"; rec "$d" $((10*S)) 1 PreCompact manual S1; rec "$d" $((10*S+2000*S)) 2 SessionStart compact S1
    64	check A5_window_expired "$d" 1 "pairs=0 VOID=1 ORPHAN=1"
    65	check A5_window_widened "$d" 0 "pairs=1 VOID=0 ORPHAN=0" --window 3000
    66	
    67	# A6 two sessions interleaved in time -> paired per session
    68	d="$ROOT/a6"; mkdir "$d"
    69	rec "$d" $((10*S)) 1 PreCompact manual S1; rec "$d" $((11*S)) 2 PreCompact manual S2
    70	rec "$d" $((12*S)) 3 SessionStart compact S2; rec "$d" $((13*S)) 4 SessionStart compact S1
    71	check A6_interleaved "$d" 0 "PC=2 SSC=2 pairs=2 VOID=0 ORPHAN=0"
    72	
    73	# A7 non-compact SessionStarts and InstallCheck are `other`
    74	d="$ROOT/a7"; mkdir "$d"
    75	for src in startup resume clear fork; do rec "$d" $((RANDOM*S)) $RANDOM SessionStart $src S1; done
    76	rec "$d" $((99*S)) 99 InstallCheck none S1
    77	check A7_other_ignored "$d" 0 "PC=0 SSC=0 pairs=0 VOID=0 ORPHAN=0 ANOMALY=0 UNPARSEABLE=0 other=5"
    78	
    79	# A8 malformed complete.json -> exit 2
    80	d="$ROOT/a8"; mkdir "$d"; printf 'not json' > "$d/$((5*S))-5.complete.json"
    81	check A8_malformed "$d" 2 "UNPARSEABLE 5000000000-5.complete.json"
    82	d="$ROOT/a8b"; mkdir "$d"; touch "$d/.DS_Store"
    83	check A8b_unrecognized_name "$d" 2 "UNPARSEABLE .DS_Store"
    84	d="$ROOT/a8c"; mkdir "$d"
    85	"$PY" -c 'import json,sys;json.dump({"observed_at":"x","registered_matcher":"x","truncated":False,"saw_eof":True,"raw":json.dumps({"hook_event_name":"PreCompact","trigger":"manual"})},open(sys.argv[1],"w"))' "$d/$((5*S))-5.complete.json"
    86	check A8c_missing_session_id "$d" 2 "UNPARSEABLE .*no session_id"
    87	
    88	# A9 anomaly files -> exit 1; --since past them -> excluded (count printed), exit 0
    89	d="$ROOT/a9"; mkdir "$d"
    90	printf 'empty stdin' > "$d/$((1*S))-1.error.txt"; printf '{}' > "$d/$((2*S))-2.partial.json"; printf 'x' > "$d/$((3*S))-3.dropped.txt"
    91	rec "$d" $((10*S)) 4 PreCompact manual S1; rec "$d" $((11*S)) 5 SessionStart compact S1
    92	check A9_anomalies "$d" 1 "pairs=1 VOID=0 ORPHAN=0 ANOMALY=3 UNPARSEABLE=0"
    93	check A9_since_ns "$d" 0 "in_scope=2 excluded=3 .*ANOMALY=0" --since $((4*S))
    94	check A9_since_iso "$d" 0 "excluded=3" --since 1970-01-01T00:00:04Z
    95	check A9_since_bad "$d" 2 "bad --since" --since yesterday
    96	# a complete.json that says truncated/no-EOF is an anomaly too
    97	d="$ROOT/a9b"; mkdir "$d"
    98	"$PY" -c 'import json,sys;json.dump({"observed_at":"x","registered_matcher":"x","truncated":True,"saw_eof":False,"raw":"{}"},open(sys.argv[1],"w"))' "$d/$((5*S))-5.complete.json"
    99	check A9b_truncated_complete "$d" 1 "ANOMALY .*truncated=True saw_eof=False"
   100	
   101	# A10 one PC claims one SSC: PC, SSC, SSC -> 1 pair + 1 VOID
   102	d="$ROOT/a10"; mkdir "$d"; rec "$d" $((10*S)) 1 PreCompact manual S1; rec "$d" $((11*S)) 2 SessionStart compact S1; rec "$d" $((12*S)) 3 SessionStart compact S1
   103	check A10_claim_once "$d" 1 "pairs=1 VOID=1 ORPHAN=0"
   104	
   105	# A11 two PCs then one SSC: the MOST RECENT is claimed, the older is the orphan
   106	d="$ROOT/a11"; mkdir "$d"; rec "$d" $((10*S)) 1 PreCompact manual S1; rec "$d" $((20*S)) 2 PreCompact manual S1; rec "$d" $((21*S)) 3 SessionStart compact S1
   107	check A11_most_recent_claimed "$d" 0 "ORPHAN .*10000000000-1.complete.json"
   108	
   109	# A12 trigger auto counts as PreCompact
   110	d="$ROOT/a12"; mkdir "$d"; rec "$d" $((10*S)) 1 PreCompact auto S1; rec "$d" $((11*S)) 2 SessionStart compact S1
   111	check A12_auto_trigger "$d" 0 "PC=1 SSC=1 pairs=1 VOID=0"
   112	
   113	# A13 missing directory -> exit 2
   114	check A13_no_dir "$ROOT/does-not-exist" 2 "not a directory"
   115	
   116	echo "---- $pass passed, $fail failed"
   117	suite_fail=$fail
   118	
   119	# Positive control: a stub that always says CLEAN must make the VOID case FAIL.
   120	stub="$ROOT/stub.py"; printf 'print("SUMMARY stub\\nRESULT: CLEAN")\n' > "$stub"
   121	CHECKER="$stub"; pass=0; fail=0
   122	check CONTROL_stub_on_void "$ROOT/a3" 1 "VOID=1" >/dev/null
   123	if [ "$fail" = 1 ]; then echo "CONTROL PASS: stub checker made the VOID case fail (suite can go red)"
   124	else echo "CONTROL FAIL: stub checker passed the VOID case -- the suite cannot detect a broken checker"; suite_fail=$((suite_fail+1)); fi
   125	
   126	[ "$suite_fail" = 0 ] && { echo "SUITE GREEN"; exit 0; } || { echo "SUITE RED ($suite_fail)"; exit 1; }
```

## Live run output (2026-09-06)
```
SUMMARY files=403 in_scope=403 excluded=0 PC=70 SSC=66 pairs=66 VOID=0 ORPHAN=4 ANOMALY=7 UNPARSEABLE=0 other=260
ANOMALY 1788170473957460000-60475.error.txt :: hook failure-path record (error.txt)
ANOMALY 1788170474021900000-60487.error.txt :: hook failure-path record (error.txt)
ANOMALY 1788170474088781000-60499.error.txt :: hook failure-path record (error.txt)
ANOMALY 1788170474149953000-60512.error.txt :: hook failure-path record (error.txt)
ANOMALY 1788170474220110000-60524.error.txt :: hook failure-path record (error.txt)
ANOMALY 1788219238759979000-57073.error.txt :: hook failure-path record (error.txt)
ANOMALY 1788592104188565000-67533.error.txt :: hook failure-path record (error.txt)
ORPHAN 1788251125324710000-2374.complete.json :: PreCompact for session 7a51bbf0 never followed by a SessionStart/compact
ORPHAN 1788449569849309000-80032.complete.json :: PreCompact for session 846598ea never followed by a SessionStart/compact
ORPHAN 1788592499997568000-90661.complete.json :: PreCompact for session d8a69179 never followed by a SessionStart/compact
ORPHAN 1788248763009382000-20498.complete.json :: PreCompact for session e22ca458 never followed by a SessionStart/compact
RESULT: ANOMALY
rc=1
SUMMARY files=403 in_scope=89 excluded=314 PC=21 SSC=20 pairs=20 VOID=0 ORPHAN=1 ANOMALY=0 UNPARSEABLE=0 other=48
ORPHAN 1788592499997568000-90661.complete.json :: PreCompact for session d8a69179 never followed by a SessionStart/compact
RESULT: CLEAN
rc=0
```

## README paragraph added
## Passive VOID detection on the LIVE dir (added 2026-09-06)

A v30 `D_pid_INT`-class VOID is silent (exit 0, no file), so no directory
watcher can see it — the 5-second polling monitor used on install day could
only ever count files that appeared. `harness/reconcile_pairs.py` detects the
silent case from data the hooks already write: every compaction produces a
`PreCompact` record and then a `SessionStart` record with `source: "compact"`
for the same `session_id`; a SessionStart/compact with no unclaimed PreCompact
in the preceding `--window` (default 1800s) is a PreCompact VOID made visible.
Unclaimed PreCompacts are reported as ORPHAN (informational — cancelled
compaction, session exit, or the SessionStart hook dropping), hook failure-path
files (`*.error.txt` / `*.partial.json` / `*.dropped.txt`) as ANOMALY. Exit 0
clean, 1 VOID/anomaly, 2 unparseable (fail loud); `--since <ns|ISO-Z>` scopes
out legacy files and prints the excluded count. Zero standing cost: run it
whenever you want, e.g. `python3 harness/reconcile_pairs.py --since
2026-09-06T00:00:00Z`. Deliberately NOT folded into `run_all.sh`, which grades
synthetic state — a live-dir check would go permanently red on any historical
anomaly. Fixture suite: `scripts/test_reconcile_pairs.sh` (21 cases + a stub-
checker positive control that proves the suite can go red). First live run
2026-09-06 over 403 files: PC=70 SSC=66 pairs=66 **VOID=0** ORPHAN=4, 7 legacy
`.error.txt` (2026-08-30/31 empty-stdin tests) — matched the pre-written
prediction exactly.
