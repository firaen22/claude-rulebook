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
PC/SSC missing session_id or prompt_id, an id containing a lone surrogate
(codex r2 F4: it cannot be printed) -- is UNPARSEABLE and exits 2 (fail
loud: never silently skip a shape this script did not define; a schema change
must be visible, including a file that does not match the hook's own naming
exactly -- fullmatch on ASCII digits, so a trailing newline or a `.DS_Store`
is UNPARSEABLE and counted in_scope; --since cannot scope it out -- delete or
move such a file).

Exit codes: 0 clean; 1 >=1 VOID or anomaly in scope (*.error.txt,
*.partial.json, *.dropped.txt, a *.complete.json with truncated/no-EOF, or a
pair sanity failure); 2 unparseable/unrecognised file, bad --window, bad
--since, or an unreadable directory.

SUMMARY invariants: files == in_scope + excluded;
in_scope == PC + SSC + other + <anomaly FILES> + UNPARSEABLE.  ANOMALY also
counts group-level findings (duplicate identity, inversion, gap), so it may
exceed the anomaly-file count -- it is a findings count, not a file count.

--since <ns|YYYY-MM-DDTHH:MM:SSZ> scopes REPORTING: a file older than the
cutoff is counted only in `excluded` and is never reported ON ITS OWN, but
pre-cutoff PreCompact AND SessionStart/compact records are still loaded as
pairing CONTEXT: a group is checked (pair / dup / inversion / gap) as soon as
one of its members is in scope, and a group with no in-scope member is
skipped entirely.  So a healthy pair straddling the cutoff is not a false VOID
(codex F6 / Fable F-4), a pre-cutoff duplicate cannot steal an in-scope
member's partner and hide a dup ANOMALY (codex r2 F1), a wholly pre-cutoff
duplicate is not reported (codex r2 F2), and a pre-cutoff record can appear
as the OTHER half of an in-scope pair's ANOMALY line (Fable r2 F-F/F-I).
"""
import argparse
import datetime
import json
import math
import os
import re
import sys

# fullmatch + ASCII digit classes: `$` would accept a trailing newline (codex r2 F5)
NAME_RE = re.compile(r"([0-9]+)-([0-9]+)\.(complete\.json|partial\.json|error\.txt|dropped\.txt)")
ANOMALY_SUFFIXES = ("partial.json", "error.txt", "dropped.txt")
KNOWN_SS_SOURCES = ("startup", "resume", "clear", "compact", "fork")
LOAD_ERRORS = (ValueError, json.JSONDecodeError, UnicodeDecodeError, OSError, RecursionError)
DEFAULT_DIR = os.path.expanduser("~/.claude/session-state/observed")
NS = 1_000_000_000


def safe(text):
    """Untrusted text (filenames, ids) for stdout: never let a stray surrogate
    turn a report into a traceback."""
    return text.encode("utf-8", "backslashreplace").decode("utf-8")


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
        try:
            v.encode("utf-8")
        except UnicodeEncodeError:
            raise ValueError("%s %s contains a lone surrogate" % (event, field))
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
        m = NAME_RE.fullmatch(name)
        if not m:
            # an unrecognised name has no ns to scope on, so it is always in scope
            counts["in_scope"] += 1
            counts["UNPARSEABLE"] += 1
            lines.append("UNPARSEABLE %s :: filename does not match <ns>-<pid>.<known suffix>" % safe(name))
            continue
        ns = int(m.group(1))
        suffix = m.group(3)
        in_scope = since_ns is None or ns >= since_ns
        if not in_scope:
            counts["excluded"] += 1
            if suffix != "complete.json":
                continue
            # pre-cutoff PC/SSC are pairing CONTEXT only: never reported on
            # their own, never counted, never fatal
            try:
                kind, key, _ = load_complete(os.path.join(directory, name))
            except LOAD_ERRORS:
                continue
            if kind in ("PC", "SSC"):
                groups.setdefault(key, {"PC": [], "SSC": []})[kind].append((ns, name, False))
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
        pcs, sscs = g["PC"], g["SSC"]
        if not any(scoped for _, _, scoped in pcs + sscs):
            continue                    # wholly pre-cutoff group: context only (codex r2 F2)
        tag = "session %s prompt %s" % (safe(sid[:8]), safe(pid[:8]))
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
