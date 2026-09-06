#!/usr/bin/env python3
"""reconcile_template.py -- passive out-of-band pairing detector (reusable).

Extracted 2026-09-06 from reconcile_pairs.py (the compaction-hook VOID detector),
which survived two cross-model review rounds. THE PATTERN worth reusing: two
independent records that SHOULD occur as a BEFORE/AFTER pair are matched on a
shared IDENTITY KEY -- never a time window -- so an AFTER with no BEFORE is a
SILENT failure (the producer exited 0 and wrote nothing) made visible from data
the system already emits, with no polling and no change to the thing under watch.
Reuse it for any "did the paired side-effect land?" question: enqueue/dequeue,
request/response, span-start/span-end, PreCompact/SessionStart.

Time-window pairing has a false negative this design fixes: a cancelled/abandoned
BEFORE gets claimed by the NEXT cycle's AFTER, hiding a real VOID. Identity keys
make that impossible (codex F1 / Fable F-1, 2026-09-06).

Verdicts, per identity key:
  * exactly 1 BEFORE + 1 AFTER  -> pair.  Sanity: AFTER.ts <= BEFORE.ts -> ANOMALY
    (order impossible); AFTER.ts - BEFORE.ts > --window -> ANOMALY (slow/stalled).
  * AFTER with no BEFORE         -> VOID    (the silent drop this exists to catch)
  * BEFORE with no AFTER         -> ORPHAN  (informational: cancelled, still-running,
                                             or the AFTER producer itself dropped)
  * >1 BEFORE or >1 AFTER        -> ANOMALY (identity reuse is undefined)

Fail loud, never silently skip: a record shape the adapter does not define is
UNPARSEABLE and forces exit 2 -- a schema drift must be visible, not swallowed.

--since <cutoff> scopes REPORTING only: an item older than the cutoff is counted
in `excluded` and never reported on its own, BUT pre-cutoff BEFORE/AFTER records
are still loaded as pairing CONTEXT -- a group is judged as soon as ONE member is
in scope, and a wholly-pre-cutoff group is skipped. So a healthy pair straddling
the cutoff is not a false VOID, and a pre-cutoff duplicate cannot hide by being
out of scope (codex r2 F1/F2/F6, Fable r2 F-4/F-F/F-I).

============================ HOW TO REUSE ============================
Subclass Adapter and implement the two ADAPT seams (list_items + load). The
engine below is GENERIC and review-hardened -- do not edit it when adapting.
CompactionAdapter at the bottom is the reference implementation; `python3
reconcile_template.py <dir>` runs it. For a new detector: copy this file, replace
the adapter, keep the engine.
=====================================================================
"""
import argparse
import datetime
import json
import math
import os
import re
import sys

NS = 1_000_000_000
BEFORE, AFTER, OTHER, ANOMALY = "BEFORE", "AFTER", "OTHER", "ANOMALY"


class Unparseable(Exception):
    """Raise from Adapter.load() for any record shape the adapter does not
    define. The engine counts it UNPARSEABLE and exits 2 (fail loud)."""


class Item:
    """One candidate record, classified by the adapter CHEAPLY (no full parse).
      id      -- short identifier for output (a filename, a log offset, ...)
      ts      -- integer sort/scope key (e.g. ns epoch); None = never scoped out
      kind    -- 'load'        : a pairable record; engine will call load()
                 'anomaly'     : a terminal failure record (counts ANOMALY in scope)
                 'unparseable' : structurally undefined (counts UNPARSEABLE, exit 2)
      detail  -- human note for anomaly/unparseable lines
    """
    __slots__ = ("id", "ts", "kind", "detail")

    def __init__(self, id, ts, kind, detail=""):
        # id is coerced to str: the docstring invites non-string ids (a log
        # offset) but the engine prints and joins it, which needs a str.
        self.id, self.ts, self.kind, self.detail = str(id), ts, kind, detail


def safe(text):
    """Untrusted text (ids from records) for stdout: a stray lone surrogate must
    never turn a report into a traceback."""
    return text.encode("utf-8", "backslashreplace").decode("utf-8")


class Adapter:
    """Fill the two ADAPT seams. Everything else has a working default."""

    # ---- ADAPT seam 1 -------------------------------------------------------
    def list_items(self, source):
        """Enumerate candidate records from `source`, yielding Item(...).
        Classify by CHEAP signal only (name/prefix/offset) -- defer the full
        parse to load(). Return them in a stable order (sorted)."""
        raise NotImplementedError

    # ---- ADAPT seam 2 -------------------------------------------------------
    def load(self, item, source):
        """Fully parse one kind=='load' item. Return (role, key, detail):
          role   -- BEFORE / AFTER  (pairable) or OTHER (recognised, not paired)
          key    -- hashable identity tuple for BEFORE/AFTER, else None
          detail -- note (unused for BEFORE/AFTER)
        Raise Unparseable for any shape you did not define. May also return
        (ANOMALY, None, detail) for a recognised-but-bad record.

        Contract the engine enforces (violations become a loud UNPARSEABLE, not
        a traceback): role must be BEFORE / AFTER / OTHER / ANOMALY; a BEFORE or
        AFTER MUST carry a non-None hashable, mutually-orderable key. Any OTHER
        exception you let escape (OSError, ValueError, ...) is also counted
        UNPARSEABLE -- but raising Unparseable yourself gives a cleaner line."""
        raise NotImplementedError

    def validate_source(self, source):
        """Return None if `source` is usable as-is, else an error message (no
        'ERROR: ' prefix); the engine prints 'ERROR: <msg>' and exits 2 before
        scanning. Default accepts anything -- a file/URL/socket adapter need not
        be a directory. Override to reject a bad source with a clean message
        instead of a mid-scan traceback."""
        return None

    # ---- optional overrides -------------------------------------------------
    def parse_cutoff(self, text):
        """--since parser. Default: integer ns, or ISO-8601 UTC (…Z)."""
        if text is None:
            return None
        if text.isdigit():
            return int(text)
        dt = datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")
        return int(dt.replace(tzinfo=datetime.timezone.utc).timestamp() * NS)

    def describe_key(self, key):
        """One-line tag for a group in output. Default: safe, truncated parts."""
        return " ".join(safe(str(p))[:8] for p in key)

    # labels/help are class attrs so a subclass can rename without code changes
    before_label, after_label = "BEFORE", "AFTER"
    ts_word = "ts"     # the time-unit word in the inversion ANOMALY line ("ns", ...)
    window_help = ("a paired BEFORE->AFTER gap wider than this many seconds is "
                   "ANOMALY (default 1800)")
    since_help = ("report only items with ts >= this (int ns or YYYY-MM-DDTHH:MM:SSZ); "
                  "older records still serve as pairing context")


# ============================ GENERIC ENGINE ============================
# Review-hardened. Do not edit when adapting -- change the Adapter instead.

def reconcile(adapter, source, window_s, cutoff_ns):
    window_ns = int(window_s * NS)
    c = dict(files=0, in_scope=0, excluded=0, BEFORE=0, AFTER=0, pairs=0,
             VOID=0, ORPHAN=0, ANOMALY=0, UNPARSEABLE=0, other=0)
    lines = []
    groups = {}    # key -> {BEFORE: [(ts, id, in_scope)], AFTER: [...]}

    for item in adapter.list_items(source):
        c["files"] += 1
        if item.kind == "unparseable":
            # no reliable ts to scope on -> always in scope, always fatal
            c["in_scope"] += 1
            c["UNPARSEABLE"] += 1
            lines.append("UNPARSEABLE %s :: %s" % (safe(item.id), item.detail))
            continue

        in_scope = cutoff_ns is None or item.ts is None or item.ts >= cutoff_ns
        if not in_scope:
            c["excluded"] += 1
            if item.kind != "load":
                continue                      # pre-cutoff anomaly file: excluded only
            try:                              # pre-cutoff pairable: CONTEXT only
                role, key, _ = adapter.load(item, source)
            except Exception:                 # any load failure drops as context;
                continue                      # an in-scope partner (if any) VOIDs loud
            if role in (BEFORE, AFTER) and key is not None:
                groups.setdefault(key, {BEFORE: [], AFTER: []})[role].append(
                    (item.ts, item.id, False))
            continue

        c["in_scope"] += 1
        if item.kind == "anomaly":
            c["ANOMALY"] += 1
            lines.append("ANOMALY %s :: %s" % (safe(item.id), item.detail))
            continue
        try:
            role, key, detail = adapter.load(item, source)
        except Unparseable as exc:
            c["UNPARSEABLE"] += 1
            lines.append("UNPARSEABLE %s :: %s" % (safe(item.id), exc))
            continue
        except Exception as exc:              # load() should raise Unparseable; a
            c["UNPARSEABLE"] += 1             # stray OSError/ValueError must fail loud
            lines.append("UNPARSEABLE %s :: %s: %s"   # here, not abort the whole scan
                         % (safe(item.id), type(exc).__name__, exc))
            continue
        if role == ANOMALY:
            c["ANOMALY"] += 1
            lines.append("ANOMALY %s :: %s" % (safe(item.id), detail))
        elif role == OTHER:
            c["other"] += 1
        elif role in (BEFORE, AFTER):
            if key is None:                   # contract: pairable roles need a key
                c["UNPARSEABLE"] += 1
                lines.append("UNPARSEABLE %s :: adapter returned %s with no identity key"
                             % (safe(item.id), role))
                continue
            c[role] += 1
            groups.setdefault(key, {BEFORE: [], AFTER: []})[role].append(
                (item.ts, item.id, True))
        else:                                 # unknown role -> loud, never KeyError
            c["UNPARSEABLE"] += 1
            lines.append("UNPARSEABLE %s :: adapter returned unknown role %r"
                         % (safe(item.id), role))
            continue

    for key, g in sorted(groups.items()):
        befores, afters = g[BEFORE], g[AFTER]
        if not any(scoped for _, _, scoped in befores + afters):
            continue                          # wholly pre-cutoff group: context only
        tag = adapter.describe_key(key)
        if len(befores) > 1 or len(afters) > 1:
            c["ANOMALY"] += 1
            lines.append("ANOMALY %s :: %d %s + %d %s records share %s"
                         % (" ".join(safe(n) for _, n, _ in befores + afters),
                            len(befores), adapter.before_label,
                            len(afters), adapter.after_label, tag))
            continue
        if befores and afters:
            (bns, bid, _), (ans, aid, _) = befores[0], afters[0]
            c["pairs"] += 1
            if bns is None or ans is None:    # ts=None adapter: count the pair,
                pass                          # skip order/gap sanity (nothing to sort)
            elif ans <= bns:
                c["ANOMALY"] += 1
                lines.append("ANOMALY %s %s :: %s %s is not after its %s (%s)"
                             % (safe(bid), safe(aid), adapter.after_label,
                                adapter.ts_word, adapter.before_label, tag))
            elif ans - bns > window_ns:
                c["ANOMALY"] += 1
                lines.append("ANOMALY %s %s :: pair gap %.1fs exceeds --window %gs (%s)"
                             % (safe(bid), safe(aid), (ans - bns) / NS, window_s, tag))
        elif afters:
            c["VOID"] += 1
            lines.append("VOID %s :: %s with no %s record (%s)"
                         % (safe(afters[0][1]), adapter.after_label, adapter.before_label, tag))
        elif befores[0][2]:                   # in-scope BEFORE with no AFTER
            c["ORPHAN"] += 1
            lines.append("ORPHAN %s :: %s never followed by a %s (%s)"
                         % (safe(befores[0][1]), adapter.before_label, adapter.after_label, tag))

    return c, lines


def run(adapter, argv=None, default_source=None):
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    ap.add_argument("source", nargs="?", default=default_source)
    ap.add_argument("--window", type=float, default=1800.0, help=adapter.window_help)
    ap.add_argument("--since", default=None, help=adapter.since_help)
    args = ap.parse_args(argv)

    if args.source is None:
        print("ERROR: no source given")
        return 2
    err = adapter.validate_source(args.source)   # seam: reject bad source cleanly,
    if err is not None:                          # before the scan, exit 2 (F3)
        print("ERROR: " + err)
        return 2
    if not (math.isfinite(args.window) and 0 <= args.window <= 10**9):
        print("ERROR: bad --window %r: need a finite value in [0, 1e9] seconds" % args.window)
        return 2
    try:
        cutoff_ns = adapter.parse_cutoff(args.since)
    except ValueError as exc:
        print("ERROR: bad --since %r: %s" % (args.since, exc))
        return 2
    try:
        c, lines = reconcile(adapter, args.source, args.window, cutoff_ns)
    except OSError as exc:
        print("ERROR: cannot read source %s: %s" % (args.source, exc))
        return 2

    print("SUMMARY " + " ".join("%s=%d" % (k, c[k]) for k in
          ("files", "in_scope", "excluded", "BEFORE", "AFTER", "pairs", "VOID",
           "ORPHAN", "ANOMALY", "UNPARSEABLE", "other")))
    for line in lines:
        print(line)
    if c["UNPARSEABLE"]:
        print("RESULT: ERROR (unparseable/unrecognized records -- fix the shape or the adapter)")
        return 2
    if c["VOID"] or c["ANOMALY"]:
        print("RESULT: VOID" if c["VOID"] else "RESULT: ANOMALY")
        return 1
    print("RESULT: CLEAN")
    return 0


# ============================ REFERENCE ADAPTER ============================
# The compaction-hook detector, rebuilt on the engine above. This is both the
# worked example and the faithfulness check (its verdicts must match the
# original reconcile_pairs.py on the same directory). Replace this class to
# build a different detector.

_NAME_RE = re.compile(r"([0-9]+)-([0-9]+)\.(complete\.json|partial\.json|error\.txt|dropped\.txt)")
_ANOMALY_SUFFIXES = ("partial.json", "error.txt", "dropped.txt")
_KNOWN_SS_SOURCES = ("startup", "resume", "clear", "compact", "fork")
_LOAD_ERRORS = (ValueError, json.JSONDecodeError, UnicodeDecodeError, OSError, RecursionError)


class CompactionAdapter(Adapter):
    before_label, after_label = "PreCompact", "SessionStart/compact"
    ts_word = "ns"                            # filenames carry an ns epoch prefix

    def validate_source(self, source):
        if not os.path.isdir(source):         # matches the original's exact message
            return "not a directory: %s" % source
        return None

    def describe_key(self, key):
        sid, pid = key
        return "session %s prompt %s" % (safe(sid[:8]), safe(pid[:8]))

    def list_items(self, source):
        for name in sorted(os.listdir(source)):
            m = _NAME_RE.fullmatch(name)      # fullmatch: a trailing newline / .DS_Store is unparseable
            if not m:
                yield Item(name, None, "unparseable",
                           "filename does not match <ns>-<pid>.<known suffix>")
                continue
            ns, suffix = int(m.group(1)), m.group(3)
            if suffix in _ANOMALY_SUFFIXES:
                yield Item(name, ns, "anomaly", "hook failure-path record (%s)" % suffix)
            else:
                yield Item(name, ns, "load")

    def load(self, item, source):
        try:
            with open(os.path.join(source, item.id), "rb") as fh:
                outer = json.loads(fh.read().decode("utf-8"))
            if not isinstance(outer, dict):
                raise ValueError("outer JSON is not an object")
            for k in ("observed_at", "registered_matcher", "raw"):
                if k not in outer:
                    raise ValueError("missing key %r" % k)
            if outer.get("truncated") is not False or outer.get("saw_eof") is not True:
                return (ANOMALY, None, "complete.json with truncated=%r saw_eof=%r"
                        % (outer.get("truncated"), outer.get("saw_eof")))
            if not isinstance(outer["raw"], str):
                raise ValueError("raw is %s, not a JSON string" % type(outer["raw"]).__name__)
            raw = json.loads(outer["raw"])
            if not isinstance(raw, dict):
                raise ValueError("raw JSON is not an object")
            event = raw.get("hook_event_name")
            if event == "InstallCheck":
                return (OTHER, None, "InstallCheck")
            if event == "PreCompact":
                role = BEFORE
            elif event == "SessionStart":
                src = raw.get("source")
                if src not in _KNOWN_SS_SOURCES:
                    raise ValueError("SessionStart with unknown source %r" % (src,))
                if src != "compact":
                    return (OTHER, None, "SessionStart/%s" % src)
                role = AFTER
            else:
                raise ValueError("unknown hook_event_name %r" % (event,))
            ids = []
            for field in ("session_id", "prompt_id"):
                v = raw.get(field)
                if not isinstance(v, str) or not v:
                    raise ValueError("%s record has no %s" % (event, field))
                try:
                    v.encode("utf-8")         # a lone surrogate id cannot be printed
                except UnicodeEncodeError:
                    raise ValueError("%s %s contains a lone surrogate" % (event, field))
                ids.append(v)
            return (role, tuple(ids), event)
        except RecursionError:
            raise Unparseable("JSON nesting too deep")
        except _LOAD_ERRORS as exc:
            raise Unparseable(str(exc))


if __name__ == "__main__":
    sys.exit(run(CompactionAdapter(),
                 default_source=os.path.expanduser("~/.claude/session-state/observed")))
