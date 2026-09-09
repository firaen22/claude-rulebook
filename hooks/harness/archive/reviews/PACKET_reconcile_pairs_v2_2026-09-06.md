# Review packet v2 — reconcile_pairs.py (passive VOID detector), round 2 after cross-model FIX

You are reviewing ONE harness instrument (python3 script + bash 3.2 fixture suite)
in its SECOND round. Round 1 (codex gpt-6-astra: FIX F1–F7; fresh Fable: FIX F-1..F-4)
found that pairing PreCompact→SessionStart/compact by session_id + time window let a
cancelled PreCompact be claimed by the NEXT compaction's SessionStart, hiding a real
VOID. Both files were REWRITTEN, not patched. You cannot see the repo; everything is
inlined. Return a structured verdict; last line `PROCEED` or `FIX <ids>`.

## Context (unchanged)
`observe-compaction-events.sh` is a macOS Claude Code hook (bash 3.2) registered on
PreCompact (manual/auto) and SessionStart (startup/resume/clear/compact/fork). Each
firing writes ONE file to `~/.claude/session-state/observed/`:
`<time.time_ns()>-<pid>.complete.json` on success — outer JSON {observed_at,
registered_matcher, truncated, saw_eof, raw}; `raw` is the JSON string the host piped
on stdin, carrying hook_event_name, session_id, prompt_id, and trigger (PreCompact) or
source (SessionStart). `*.error.txt` / `*.partial.json` / `*.dropped.txt` are the
hook's own failure paths. The failure class this detects: PreCompact hook exits 0 and
writes NO file (silent). The SessionStart/compact hook for that same compaction
normally still fires, so the compaction leaves ONE record instead of two.

## What changed in round 2 (design)
Pairing key is now the compaction IDENTITY `(session_id, prompt_id)`, not a time
window. Verified on the live dir before this rewrite (script over all 405 files):
67/67 completed compactions have identical prompt_id on PC and SSC; 0 PC/SSC records
lack prompt_id; 0 prompt_ids recur across sessions; 0 pairs with SSC ns < PC ns; gaps
39.3–282.1 s (median 94). Live event inventory: SessionStart/startup 186, /resume 73,
/compact 67, PreCompact/manual 70, /auto 1, InstallCheck 1 — nothing else.
`--window` is now a sanity check on a paired gap (ANOMALY), not a pairing criterion.

## Round-1 dispositions (all reproduced by the author before fixing)
| id | finding | disposition |
|---|---|---|
| codex F1 / Fable F-1 | cancelled PC inside window claimed by later SSC → CLEAN hides VOID | FIXED: identity pairing; fixtures A11, A11b |
| codex F2 / Fable F-3 | unknown event/source → `other`, rc 0 | FIXED: explicit whitelist, else UNPARSEABLE rc 2; A8g–A8i |
| codex F3 | `ORPHAN=1` substring matched `ORPHAN=10`; A11 under-asserted; control weak | FIXED: anchored exact-token regex, A11 counts, CONTROL2 corrupted-count wrapper |
| codex F4 / Fable F-2 | raw:null → TypeError rc 1; RecursionError; --window nan/inf/-1; listdir error | FIXED: type check, RecursionError→UNPARSEABLE, window validated finite∈[0,1e9], OSError→rc 2; A8e/A8f/A8j/A13 |
| codex F5 | equal-ns sorted by kind name | FIXED: no ordering-by-kind; SSC ns <= PC ns → ANOMALY (A15) |
| codex F6 / Fable F-4 | --since between PC and SSC → false VOID | FIXED: pre-cutoff PCs loaded as pairing context, never reported/counted; A16 |
| codex F7 | README said 7 error files were 08-30/31 | FIXED: six 08-31, one 09-05 (dates computed from ns) |
| Fable F-5 | SSC ns before PC ns → VOID+ORPHAN | CHANGED: identity pairs it, reports ANOMALY (loud, not tolerated) — REJECTED tolerance window with reason in docstring |
| Fable F-6 | no fixture fails on a session-blind checker | FIXED: A6b same prompt_id across two sessions → VOID+ORPHAN |
| Fable F-7 | --since off-by-one & lexical-sort mutants survive | FIXED: A16c (cutoff == ns included), A17 (9s/10s digit-count) |
| Fable F-8 | docstring/README claims; .DS_Store can't be scoped out | FIXED docs: whitelist stated; unrecognised names are rc 2 until removed, by design |
| codex "irreducible ambiguity" | cancelled PC + dropped PC + SSC looks like one slow compaction | CLOSED by identity — residual only when both share prompt_id (Fable's note), documented |

## Rubric — probe the SILENT side hardest
Cost asymmetry: a FALSE NEGATIVE (a real PreCompact drop reported CLEAN) is the
expensive failure. A false positive costs one file to inspect.
1. False negatives under identity pairing: any file sequence where a SessionStart/
   compact exists, its PreCompact was never written, and the result is rc 0?
   Consider prompt_id semantics (could two compactions in one session legitimately
   share prompt_id? could the host omit/rename it?), --since interplay, duplicates.
2. Fail-loud contract: any input that produces rc 0 or rc 1 where rc 2 is documented,
   or a traceback instead of a SUMMARY? Any path that silently skips a file?
3. Exit-code semantics and SUMMARY field correctness (counts must add up: in_scope =
   PC + SSC + other + ANOMALY-files + UNPARSEABLE-files ... state what you checked).
4. Fixture rigor: can you write a WRONG checker (or a mutation of this one) that still
   passes all 46 cases + 2 controls? Name it. Run the suite if you can (bash 3.2,
   python3 ≥3.6, no f-strings by design).
5. Shell portability (bash 3.2.57 on macOS; no arrays/mapfile/assoc), python
   portability (3.9 system CLT python).
6. README/docstring accuracy against the code as inlined.
Report each finding as location (file:line) + mechanism + concrete minimal fix,
severity-ranked, every claim tagged [verified: how] / [reasoned]. Report honestly if
you found nothing — "no findings" needs evidence of what you tried.

## Live output (2026-09-06, after rewrite)
```
$ python3 harness/reconcile_pairs.py
SUMMARY files=405 in_scope=405 excluded=0 PC=71 SSC=67 pairs=67 VOID=0 ORPHAN=4 ANOMALY=7 UNPARSEABLE=0 other=260
ORPHAN <4 lines, sessions 7a51bbf0 846598ea d8a69179 e22ca458>
ANOMALY <7 x .error.txt: hook failure-path record>
RESULT: ANOMALY          (rc 1)
$ python3 harness/reconcile_pairs.py --since 2026-09-06T00:00:00Z
SUMMARY files=405 in_scope=68 excluded=337 PC=14 SSC=14 pairs=14 VOID=0 ORPHAN=0 ANOMALY=0 UNPARSEABLE=0 other=40
RESULT: CLEAN            (rc 0)
$ /bin/bash scripts/test_reconcile_pairs.sh   →  46 passed, 0 failed; CONTROL1 PASS; CONTROL2 PASS; SUITE GREEN (rc 0)
```

## File 1: harness/reconcile_pairs.py
```python
#!/usr/bin/env python3
"""reconcile_pairs.py -- passive VOID detector for the compaction hook.

A v30 PreCompact VOID is SILENT: the hook exits 0 and writes no file, so no
directory watcher can ever see it.  But every compaction fires TWO hooks that
both write into the same observed/ dir: `PreCompact` (before) and
`SessionStart` with `source: "compact"` (after).  Both carry the same
`session_id` AND the same `prompt_id` -- verified 2026-09-06 on the live dir:
67/67 completed compactions share prompt_id PC<->SSC, 0 records lack it, 0
prompt_ids recur across sessions.  prompt_id is therefore a compaction
IDENTITY, and a SessionStart/compact whose (session_id, prompt_id) has no
PreCompact record is a PreCompact VOID made visible -- detected from data the
hooks already write, with no polling and no hook change.

Grouping rule, per (session_id, prompt_id):
  * one PC + one SSC                  -> pair.  Sanity checks on the pair:
      SSC ns <= PC ns                 -> ANOMALY (order unknowable/impossible)
      SSC - PC  > --window seconds    -> ANOMALY (default 1800; live 39-282s)
  * SSC with no PC                    -> VOID  (the silent drop)
  * PC with no SSC                    -> ORPHAN (informational: cancelled
    compaction, session exit, or the SessionStart hook itself dropping)
  * >1 PC or >1 SSC in one group      -> ANOMALY (identity reuse is undefined)
Identity pairing means a cancelled PreCompact can never be claimed by a later
compaction's SessionStart (the time-window design this replaces had exactly
that false negative -- codex F1 / Fable F-1, 2026-09-06).  It still cannot see
a compaction where BOTH hooks dropped, or a PreCompact drop on a compaction
that was then cancelled (no SSC witness), and one residual (Fable): a
cancelled PC and a dropped PC that share a prompt_id (two auto-compactions in
one user turn) pair as if healthy -- only the --window sanity check can catch
that, and only when the gap is long.  VOID=0 is clean for every compaction
that completed with a distinct prompt_id, nothing more.
An SSC whose ns is not after its PC is reported ANOMALY rather than tolerated:
a PreCompact worker delayed past the SessionStart worker is the M19-M22 stall
class this harness exists to surface, so a loud false alarm beats a silent
tolerance (0/67 live pairs are inverted).

Recognised record shapes are an explicit whitelist: PreCompact (any trigger),
SessionStart with source in KNOWN_SS_SOURCES, InstallCheck.  Anything else --
missing/unknown hook_event_name or source, non-string raw, non-object JSON,
PC/SSC missing session_id or prompt_id -- is UNPARSEABLE and exits 2 (fail
loud: never silently skip a shape this script did not define; a schema change
must be visible, including a file that does not match the hook's own naming,
which --since cannot scope out -- delete or move such a file).

Exit codes: 0 clean; 1 >=1 VOID or anomaly in scope (*.error.txt,
*.partial.json, *.dropped.txt, a *.complete.json with truncated/no-EOF, or a
pair sanity failure); 2 unparseable/unrecognised file, bad --window, bad
--since, or an unreadable directory.

--since <ns|YYYY-MM-DDTHH:MM:SSZ> scopes REPORTING: files older than the
cutoff are never reported and never counted (excluded count is printed), but
pre-cutoff PreCompact records are still loaded as pairing CONTEXT so a healthy
pair straddling the cutoff is not mislabelled VOID (codex F6 / Fable F-4).
"""
import argparse
import datetime
import json
import math
import os
import re
import sys

NAME_RE = re.compile(r"^(\d+)-(\d+)\.(complete\.json|partial\.json|error\.txt|dropped\.txt)$")
ANOMALY_SUFFIXES = ("partial.json", "error.txt", "dropped.txt")
KNOWN_SS_SOURCES = ("startup", "resume", "clear", "compact", "fork")
LOAD_ERRORS = (ValueError, json.JSONDecodeError, UnicodeDecodeError, OSError, RecursionError)
DEFAULT_DIR = os.path.expanduser("~/.claude/session-state/observed")
NS = 1_000_000_000


def parse_since(text):
    """--since accepts an integer ns timestamp or an ISO-8601 UTC instant
    (YYYY-MM-DDTHH:MM:SSZ, the observed_at format)."""
    if text is None:
        return None
    if text.isdigit():
        return int(text)
    dt = datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")
    return int(dt.replace(tzinfo=datetime.timezone.utc).timestamp() * NS)


def load_complete(path):
    """Return (kind, key, detail).  kind in {PC, SSC, other, anomaly}; key is
    (session_id, prompt_id) for PC/SSC else None.  Raises ValueError on any
    shape this script does not define."""
    with open(path, "rb") as fh:
        outer = json.loads(fh.read().decode("utf-8"))
    if not isinstance(outer, dict):
        raise ValueError("outer JSON is not an object")
    for k in ("observed_at", "registered_matcher", "raw"):
        if k not in outer:
            raise ValueError("missing key %r" % k)
    if outer.get("truncated") is not False or outer.get("saw_eof") is not True:
        return ("anomaly", None, "complete.json with truncated=%r saw_eof=%r"
                % (outer.get("truncated"), outer.get("saw_eof")))
    if not isinstance(outer["raw"], str):
        raise ValueError("raw is %s, not a JSON string" % type(outer["raw"]).__name__)
    raw = json.loads(outer["raw"])
    if not isinstance(raw, dict):
        raise ValueError("raw JSON is not an object")
    event = raw.get("hook_event_name")
    if event == "InstallCheck":
        return ("other", None, "InstallCheck")
    if event == "PreCompact":
        kind = "PC"
    elif event == "SessionStart":
        src = raw.get("source")
        if src not in KNOWN_SS_SOURCES:
            raise ValueError("SessionStart with unknown source %r" % (src,))
        if src != "compact":
            return ("other", None, "SessionStart/%s" % src)
        kind = "SSC"
    else:
        raise ValueError("unknown hook_event_name %r" % (event,))
    ids = []
    for field in ("session_id", "prompt_id"):
        v = raw.get(field)
        if not isinstance(v, str) or not v:
            raise ValueError("%s record has no %s" % (event, field))
        ids.append(v)
    return (kind, tuple(ids), event)


def reconcile(directory, window_s, since_ns):
    window_ns = int(window_s * NS)
    counts = dict(files=0, in_scope=0, excluded=0, PC=0, SSC=0, pairs=0,
                  VOID=0, ORPHAN=0, ANOMALY=0, UNPARSEABLE=0, other=0)
    lines = []          # human-readable findings, one per line
    groups = {}         # (session_id, prompt_id) -> {"PC": [(ns, name, in_scope)], "SSC": [...]}

    for name in sorted(os.listdir(directory)):
        counts["files"] += 1
        m = NAME_RE.match(name)
        if not m:
            counts["UNPARSEABLE"] += 1
            lines.append("UNPARSEABLE %s :: filename does not match <ns>-<pid>.<known suffix>" % name)
            continue
        ns = int(m.group(1))
        suffix = m.group(3)
        in_scope = since_ns is None or ns >= since_ns
        if not in_scope:
            counts["excluded"] += 1
            if suffix != "complete.json":
                continue
            # pre-cutoff PreCompacts are pairing CONTEXT only: never reported,
            # never counted, never fatal
            try:
                kind, key, _ = load_complete(os.path.join(directory, name))
            except LOAD_ERRORS:
                continue
            if kind == "PC":
                groups.setdefault(key, {"PC": [], "SSC": []})["PC"].append((ns, name, False))
            continue
        counts["in_scope"] += 1
        if suffix in ANOMALY_SUFFIXES:
            counts["ANOMALY"] += 1
            lines.append("ANOMALY %s :: hook failure-path record (%s)" % (name, suffix))
            continue
        try:
            kind, key, detail = load_complete(os.path.join(directory, name))
        except LOAD_ERRORS as exc:
            counts["UNPARSEABLE"] += 1
            lines.append("UNPARSEABLE %s :: %s" % (name, exc if not isinstance(exc, RecursionError)
                                                   else "JSON nesting too deep"))
            continue
        if kind == "anomaly":
            counts["ANOMALY"] += 1
            lines.append("ANOMALY %s :: %s" % (name, detail))
        elif kind == "other":
            counts["other"] += 1
        else:
            counts[kind] += 1
            groups.setdefault(key, {"PC": [], "SSC": []})[kind].append((ns, name, True))

    for (sid, pid), g in sorted(groups.items()):
        tag = "session %s prompt %s" % (sid[:8], pid[:8])
        pcs, sscs = g["PC"], g["SSC"]
        if len(pcs) > 1 or len(sscs) > 1:
            counts["ANOMALY"] += 1
            lines.append("ANOMALY %s :: %d PreCompact + %d SessionStart/compact records share %s"
                         % (" ".join(n for _, n, _ in pcs + sscs), len(pcs), len(sscs), tag))
            continue
        if pcs and sscs:
            (pns, pname, _), (sns, sname, _) = pcs[0], sscs[0]
            counts["pairs"] += 1
            if sns <= pns:
                counts["ANOMALY"] += 1
                lines.append("ANOMALY %s %s :: SessionStart/compact ns is not after its PreCompact (%s)"
                             % (pname, sname, tag))
            elif sns - pns > window_ns:
                counts["ANOMALY"] += 1
                lines.append("ANOMALY %s %s :: pair gap %.1fs exceeds --window %gs (%s)"
                             % (pname, sname, (sns - pns) / NS, window_s, tag))
        elif sscs:
            counts["VOID"] += 1
            lines.append("VOID %s :: SessionStart/compact with no PreCompact record (%s)"
                         % (sscs[0][1], tag))
        elif pcs[0][2]:                 # in-scope PC with no SSC
            counts["ORPHAN"] += 1
            lines.append("ORPHAN %s :: PreCompact never followed by a SessionStart/compact (%s)"
                         % (pcs[0][1], tag))

    return counts, lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("directory", nargs="?", default=DEFAULT_DIR)
    ap.add_argument("--window", type=float, default=1800.0,
                    help="a paired PreCompact->SessionStart/compact gap above this many "
                         "seconds is reported as ANOMALY (default 1800; live gaps 39-282s)")
    ap.add_argument("--since", default=None,
                    help="report only files whose ns prefix is >= this (int ns or "
                         "YYYY-MM-DDTHH:MM:SSZ); older PreCompacts still serve as "
                         "pairing context; the excluded count is always printed")
    args = ap.parse_args(argv)

    if not os.path.isdir(args.directory):
        print("ERROR: not a directory: %s" % args.directory)
        return 2
    if not (math.isfinite(args.window) and 0 <= args.window <= 10**9):
        print("ERROR: bad --window %r: need a finite value in [0, 1e9] seconds" % args.window)
        return 2
    try:
        since_ns = parse_since(args.since)
    except ValueError as exc:
        print("ERROR: bad --since %r: %s" % (args.since, exc))
        return 2
    try:
        counts, lines = reconcile(args.directory, args.window, since_ns)
    except OSError as exc:
        print("ERROR: cannot read directory %s: %s" % (args.directory, exc))
        return 2
    print("SUMMARY " + " ".join("%s=%d" % (k, counts[k]) for k in
          ("files", "in_scope", "excluded", "PC", "SSC", "pairs", "VOID", "ORPHAN",
           "ANOMALY", "UNPARSEABLE", "other")))
    for line in lines:
        print(line)
    if counts["UNPARSEABLE"]:
        print("RESULT: ERROR (unparseable/unrecognized files -- fix the shape or the script)")
        return 2
    if counts["VOID"] or counts["ANOMALY"]:
        print("RESULT: VOID" if counts["VOID"] else "RESULT: ANOMALY")
        return 1
    print("RESULT: CLEAN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## File 2: scripts/test_reconcile_pairs.sh
```bash
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
```

## File 3: README.md section (the only README text touched)
```
## Passive VOID detection on the LIVE dir (added 2026-09-06)

A v30 `D_pid_INT`-class VOID is silent (exit 0, no file), so no directory
watcher can see it — the 5-second polling monitor used on install day could
only ever count files that appeared. `harness/reconcile_pairs.py` detects the
silent case from data the hooks already write: every compaction produces a
`PreCompact` record and then a `SessionStart` record with `source: "compact"`
carrying the same `session_id` AND the same `prompt_id` (verified on the live
dir: 67/67 completed compactions, 0 records without it, 0 reuse across
sessions). Records are grouped by `(session_id, prompt_id)`: PC+SSC → pair;
SSC alone → **VOID** (the silent drop); PC alone → ORPHAN (informational —
cancelled compaction, session exit, or the SessionStart hook dropping);
duplicate identity, SSC not after its PC, or a pair gap over `--window`
(default 1800s; live gaps 39–282s) → ANOMALY. Hook failure-path files
(`*.error.txt` / `*.partial.json` / `*.dropped.txt`) are ANOMALY. Exit 0
clean, 1 VOID/anomaly, 2 unparseable — an explicit whitelist of shapes, so a
missing/unknown `hook_event_name`/`source`, non-string `raw`, or a file not
named `<ns>-<pid>.<known suffix>` (a stray `.DS_Store`) is rc 2 until removed;
`--since` cannot hide it. `--since <ns|ISO-Z>` scopes REPORTING: older files
are not counted or reported (excluded count printed) but pre-cutoff
PreCompacts still serve as pairing context, so a pair straddling the cutoff is
not a false VOID. Known blind spots: both hooks dropping on one compaction;
a PreCompact drop on a compaction that was then cancelled; two compactions
in one user turn sharing a prompt_id. Zero standing cost: run it whenever you
want, e.g. `python3 harness/reconcile_pairs.py --since 2026-09-06T00:00:00Z`.
Deliberately NOT folded into `run_all.sh`, which grades synthetic state — a
live-dir check would go permanently red on any historical anomaly.

History: the first version (packet `reviews/PACKET_reconcile_pairs_2026-09-06.md`)
paired on `session_id` + time window only. Cross-model review the same day
(codex gpt-6-astra FIX F1–F7, fresh Fable FIX F-1..F-4, both reproduced here)
showed a cancelled PreCompact inside the window would be claimed by the next
compaction's SessionStart and turn a real VOID into `CLEAN`; Fable found the
`prompt_id` identity that closes it. Fixture suite:
`scripts/test_reconcile_pairs.sh` (46 cases incl. both reviewers' masking
fixtures, exact-token assertions, plus two positive controls — an always-CLEAN
stub and a correct-exit/corrupted-count wrapper — that prove the suite can go
red). Live run 2026-09-06 over 405 files: PC=71 SSC=67 pairs=67 **VOID=0**
ORPHAN=4 ANOMALY=7 (six `.error.txt` from 2026-08-31 empty-stdin tests, one
from 2026-09-05), matching the pre-written prediction; `--since
2026-09-06T00:00:00Z`: 14/14 pairs CLEAN.
```

Last line of your reply must be exactly `PROCEED` or `FIX <ids>`.
