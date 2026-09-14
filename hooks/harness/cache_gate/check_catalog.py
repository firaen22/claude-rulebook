#!/usr/bin/env python3
"""Fail-closed consistency gate for the harness governance catalog.

The inventory is deliberately derived from the filesystem patterns below, not
from the permission table.  The table and registry are then checked against
that independent inventory.
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cachelib  # noqa: E402  (deliberate local import, never via cwd/$PWD)
from cachelib import GateError  # noqa: E402


TABLE_HEADER = "| File | May edit autonomously? | Rule |"
TABLE_SEPARATOR = re.compile(r"^\|\s*:?-{3,}:?\s*\|")
TICKS = re.compile(r"`([^`]+)`")
VERDICT_LINE = "**Edit permission (authoritative copy in §1):**"
# The registry (41) is DRIVEN FROM §1: §1 is the authority, and the registry mirrors a verdict
# for a SUBSET of §1 objects as provenance (measured 2026-09-09: 18 verdicts for 22 §1 objects;
# some §1 objects carry a narrative registry section with no verdict, and some none at all). So a
# registry verdict is recognised by ONE unambiguous rule: a line at column 0 that starts with the
# exact canonical VERDICT_LINE. Every OTHER line is prose and is IGNORED -- never an error. This
# replaced four rounds of leaky per-line Markdown detection (declaration prefix/fingerprint,
# ATX/Setext heading, list/fence heuristics), each of which kept mis-classifying block structure
# and either false-RED'ing legitimate prose (a sentence mentioning edit permission, a quoted
# parenthetical, an indented example, an NBSP delimiter) or, in mixed/nested fences, hiding a
# contradiction (codex+grok rounds 1-4, all reproduced 2026-09-09). A malformed/non-canonical
# verdict declaration is not a governance hole here: §1 still governs the object, coverage still
# requires its §1 row, and any CANONICAL verdict that DOES appear is still matched against §1.
# A fenced-code OPEN: >=3 backticks or tildes at COLUMN 0 + optional info string; the fence closes
# only on a later COLUMN-0 line of the SAME character, length >= the opener's, followed by spaces/
# tabs only (CommonMark closer whitespace is space|tab, NOT any-whitespace -- an NBSP after the
# ticks is content, not a close: codex#1 2026-09-09). Column-0 ONLY is deliberate and fail-SAFE:
# the sole thing we must not miscount is a column-0 canonical verdict that is really fenced-code
# content, and a column-0 line can be code content ONLY inside a top-level (column-0) fence -- a
# list-nested or indented fence's content is itself indented (a column-0 line breaks out of the
# list). Recognising only column-0 fences can therefore only ever SURFACE more column-0 lines
# (matched against §1), never HIDE one, so it cannot fail-open; it retired the list-fence /
# indent desync that swallowed a real contradiction and false-RED'd legit list examples
# (grok+codex round 5, all reproduced 2026-09-09). Tracking char+length -- not a naive toggle --
# keeps a fenced EXAMPLE of the canonical verdict line from counting as live, and an unclosed
# fence from hiding later verdicts (guarded after the loop).
FENCE_OPEN = re.compile(r"^(`{3,}|~{3,})(.*)$")
FENCE_CLOSE = re.compile(r"^(`{3,}|~{3,})[ \t]*$")
STRIKE = re.compile(r"~~(.*?)~~")

EXTERNAL_SNAPSHOT = os.path.expanduser("~/.local/share/opus-pack/skill_snapshot.py")
PROJECT_CLASS = "project-claude-class"
MEMORY_CLASS = "memory-class"


def _read_text(path, label):
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except (OSError, UnicodeError) as exc:
        raise GateError(f"cannot read {label}: {exc}")


def _normalize_verdict(value):
    return re.sub(r"\s+", " ", value.replace("**", "")).strip()


def _split_row(line):
    """Split one GFM table line into stripped cells.

    The leading and trailing pipe are OPTIONAL in GFM, so strip at most one of each
    before splitting (the old parser REQUIRED a leading pipe and silently truncated the
    table at the first pipeless row, reproduced 2026-09-14). An unescaped interior '|'
    over-splits a cell; callers that only read the first N cells inherit GFM's
    "extra cells are ignored" rule.
    """
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def _relative_key(token, first_key=None):
    token = token.strip()
    # normpath EVERY branch: an un-normalized '..' in a key (e.g. `~/.claude/harness/../x`)
    # slipped through as `harness/../x` and neither string-matched the inventory relpath it
    # should nor was rejected as an escape (reproduced 2026-09-14). Normalizing collapses
    # interior '..'; a key that still escapes (leading '../') simply never matches an
    # inventory relpath, so the governed object fails coverage CLOSED rather than binding
    # to the wrong row.
    if token.startswith("~/.claude/"):
        return os.path.normpath(token[len("~/.claude/") :].lstrip("/"))
    if token == "~/.claude":
        return ""
    if token.startswith("~/.local/"):
        return os.path.expanduser(token)
    if token.startswith("/"):
        return os.path.normpath(token)
    if first_key and not first_key.startswith("/"):
        return os.path.normpath(os.path.join(os.path.dirname(first_key), token))
    if "/" not in token:
        return os.path.normpath(os.path.join("harness", token))
    return os.path.normpath(token)


def _keys_from_text(text):
    """Return all path keys, anchoring relative note keys to the first key."""
    tokens = TICKS.findall(text)
    if not tokens:
        return []
    first = _relative_key(tokens[0])
    # Return first key as-is (already resolved); resolve remaining keys anchored to first.
    return [first] + [_relative_key(token, first) for token in tokens[1:]]


def _parse_permission_table(path):
    text = _read_text(path, "40-maintenance.md")
    # Split on newline ONLY. _read_text opened in text mode (universal newlines), so CRLF/CR are
    # already \n; str.splitlines() would ALSO break on \f, \v, \x1c-\x1e, \x85, U+2028, U+2029 --
    # none of which Markdown treats as a line ending -- letting an embedded separator truncate a
    # value or manufacture a column-0 line (codex#2, reproduced 2026-09-09).
    lines = text.split("\n")

    # F5: bind the header search to the §1 section. The permission table is §1's; searching
    # the WHOLE file let a decoy `| File | May edit... |` table placed BEFORE §1 be taken as
    # authoritative (reproduced 2026-09-14). Anchor on the `## §1` heading; search only from
    # there to the next h2 (`## `). §2 (`## §2 ...`) also starts with `## `, so start the
    # end-scan strictly after the §1 line.
    sec_start = None
    for i, line in enumerate(lines):
        if line.startswith("## §1"):
            sec_start = i
            break
    if sec_start is None:
        raise GateError("40-maintenance.md: §1 section heading (## §1) is missing")
    sec_end = len(lines)
    for j in range(sec_start + 1, len(lines)):
        if lines[j].startswith("## "):
            sec_end = j
            break

    # Recognise ONLY column-0 fences (FENCE_OPEN/FENCE_CLOSE) to skip a fenced EXAMPLE of the
    # header: a column-0 line (the header and every data row are column-0) can be fenced-code
    # content ONLY inside a column-0 fence -- see the fence note above. The header is matched
    # EXACTLY at column 0 (not .strip()), so an INDENTED example header can never be mistaken
    # for the real one, and a column-0 fenced example is skipped by this tracking.
    fence = None  # (char, length) of open column-0 fence, or None
    header = None
    for i in range(sec_start + 1, sec_end):
        line = lines[i]
        if fence is None:
            opener = FENCE_OPEN.match(line)
            if opener and not (opener.group(1)[0] == "`" and "`" in opener.group(2)):
                fence = (opener.group(1)[0], len(opener.group(1)))
                continue
            if line == TABLE_HEADER:
                header = i
                break
        else:
            closer = FENCE_CLOSE.match(line)
            if closer and closer.group(1)[0] == fence[0] and len(closer.group(1)) >= fence[1]:
                fence = None

    if header is None:
        raise GateError("40-maintenance.md: §1 permission table header is missing")
    if header + 1 >= sec_end:
        raise GateError("40-maintenance.md: §1 table separator is missing or malformed")
    # F4: the separator must have EXACTLY the header's column count (3), each a valid GFM
    # delimiter. A 4-delimiter separator under the 3-column header was accepted (reproduced
    # 2026-09-14), letting a mis-shaped table parse as §1. _split_row tolerates the optional
    # bounding pipes; the count check is what rejects a wrong column count.
    header_cols = TABLE_HEADER.count("|") - 1  # 3
    sep_cells = _split_row(lines[header + 1])
    if len(sep_cells) != header_cols or not all(re.match(r"^:?-{3,}:?$", cell) for cell in sep_cells):
        raise GateError("40-maintenance.md: §1 table separator is missing or malformed")

    rows = []
    for line_number, line in enumerate(lines[header + 2 : sec_end], header + 3):
        # F3: a GFM table ends at a BLANK line, the §1 boundary, or any non-row line (prose,
        # a fence); every line that still carries pipes before that is a row, its leading and
        # trailing pipe OPTIONAL. The old parser REQUIRED a leading pipe and silently truncated
        # the table at the first pipeless row (reproduced 2026-09-14). A line with NO pipe at
        # all cannot be a table row -- it terminates the table (a fence's ``` and ordinary prose
        # both land here); a line that DOES carry pipes but resolves to too few cells is a
        # malformed row and fails CLOSED below.
        if line.strip() == "" or "|" not in line:
            break
        cells = _split_row(line)
        # >= header_cols (not ==): an unescaped interior '|' in the unused Rule column splits
        # it into extra cells; GFM ignores the extras, so read only the first header_cols. A
        # row with FEWER cells is genuinely malformed -> fail CLOSED.
        if len(cells) < header_cols:
            raise GateError(f"40-maintenance.md:{line_number}: malformed §1 data row (expected {header_cols} cells)")
        col1, verdict_raw, col3 = cells[0], cells[1], cells[2]
        if not col1 or not verdict_raw or not col3:
            raise GateError(f"40-maintenance.md:{line_number}: malformed §1 data row (missing or empty required cells)")
        classes = []
        if "Project `CLAUDE.md` files" in col1:
            classes.append(PROJECT_CLASS)
        if "Memory files" in col1:
            classes.append(MEMORY_CLASS)
        keys = [] if classes else _keys_from_text(col1)
        if not classes and not keys:
            raise GateError(f"40-maintenance.md:{line_number}: §1 row has no backticked key")
        verdict = _normalize_verdict(verdict_raw)
        # `** **` strips to empty (astra: a verdict that is only markup passed the
        # non-empty check on the raw cell but normalizes to nothing).
        if not verdict:
            raise GateError(f"40-maintenance.md:{line_number}: §1 verdict is empty after normalization")
        tokens = TICKS.findall(col1)
        rows.append({
            "line": line_number,
            "keys": keys,
            "classes": classes,
            # A CLASS row (Project/Memory) carries no per-path dir_keys: a stray dir tick in
            # its col1 (e.g. "Memory files (`harness/`)") must not become a directory key,
            # or the registry-side lookup `key in row["dir_keys"]` would let a "## `harness/`"
            # section bind to the class row despite no directory permission row (codex,
            # reproduced 2026-09-09). Class rows are class-scoped only (mirrors _row_matches).
            # F7: select dir_keys from the ALREADY-RESOLVED keys (a trailing-slash token), never
            # by re-resolving the raw token -- re-resolution re-anchored a bare relative dir key
            # to `hooks/harness/hooks/harness/...` (reproduced 2026-09-14). keys[idx] corresponds
            # to tokens[idx] (both derive from col1 in order).
            "dir_keys": set() if classes else {
                keys[idx] for idx, tok in enumerate(tokens) if tok.rstrip().endswith("/")
            },
            "verdict": verdict,
            "text": col1,
        })
    if not rows:
        raise GateError("40-maintenance.md: §1 permission table has no data rows")

    seen = {}
    errors = []
    for row in rows:
        for key in row["keys"] + row["classes"]:
            if key in seen:
                errors.append(f"40-maintenance.md:{row['line']}: duplicate §1 key {key!r} (also line {seen[key]})")
            else:
                seen[key] = row["line"]
    return rows, errors


def _parse_registry(path):
    text = _read_text(path, "41-file-registry.md")
    sections = []
    current = None
    fence = None  # (char, length) of the open code fence, or None outside any fence
    # Newline-only split (see _parse_permission_table): str.splitlines() would break on \f/\v/
    # U+2028 etc., truncating a canonical value or manufacturing a column-0 verdict (codex#2).
    for line_number, line in enumerate(text.split("\n"), 1):
        if fence is None:
            # COLUMN-0 fence open only (see the fence note above): the verdict detector below
            # is column-0-anchored (`line.startswith(VERDICT_LINE)`), and a column-0 line can
            # be fenced-code content ONLY inside a column-0 fence. A prior change widened this
            # to 0-3 leading spaces for "CommonMark validity" but did NOT track container
            # indent, so a 2-space list-nested fence stayed open across a column-0 verdict and
            # HID a contradiction (F2, reproduced 2026-09-14). Recognising only column-0 fences
            # is the fail-safe rule: an indented fence's content is itself indented, so it can
            # never contain a column-0 verdict to hide.
            opener = FENCE_OPEN.match(line)
            # A backtick fence's info string may not contain a backtick -- that makes it inline
            # code ("```x```"), not a fence opener; tilde fences carry no such limit.
            if opener and not (opener.group(1)[0] == "`" and "`" in opener.group(2)):
                fence = (opener.group(1)[0], len(opener.group(1)))
                continue
        else:
            # COLUMN-0 fence close: matching char, >= length, spaces/tabs only.
            closer = FENCE_CLOSE.match(line)
            if closer and closer.group(1)[0] == fence[0] and len(closer.group(1)) >= fence[1]:
                fence = None
            continue
        # Column-0 ATX h2 heading (consistent with the column-0 verdict detector below).
        atx_match = re.match(r"^(#{1,6})[ \t]+(.*)$", line)
        if atx_match and atx_match.group(1) == "##":
            if current:
                sections.append(current)
            heading = atx_match.group(2).strip()
            active = STRIKE.sub("", heading)
            # A 41 heading names its object(s) before the first "(...)"; the parenthetical
            # carries context refs -- a `settings.json` registration, a specific
            # `references/<f>.md` -- that are covered by the parent row, NOT separate
            # governed objects. Extract object keys from the primary part only, else the
            # "every declared object needs a §1 row" check false-reds on those refs.
            primary = re.sub(r"\s*\([^)]*\)", "", active)
            keys = _keys_from_text(primary)
            classes = []
            if "Project `CLAUDE.md` files" in primary:
                classes.append(PROJECT_CLASS)
            if "Memory files" in primary:
                classes.append(MEMORY_CLASS)
            current = {"line": line_number, "heading": heading, "keys": keys, "classes": classes, "verdicts": []}
        elif line.startswith(VERDICT_LINE):
            # A CANONICAL verdict: a column-0 line beginning with the exact VERDICT_LINE. Per the
            # VERDICT_LINE note this is the ONLY recognised verdict form -- every other line is
            # prose and IGNORED (no false-RED on a sentence, quote, list item, or indented
            # example). Fenced examples of the verdict format are already skipped by the fence
            # tracking above. A canonical verdict before the first '## ' has no object to bind to.
            if current is None:
                raise GateError(
                    f"41-file-registry.md:{line_number}: canonical verdict line before any "
                    f"'## ' section (no object to attribute it to)"
                )
            current["verdicts"].append((line_number, _normalize_verdict(line[len(VERDICT_LINE) :])))
    if current:
        sections.append(current)
    # An unclosed fence would swallow every later line -- including a real canonical verdict -- so
    # a contradiction after it could escape unmatched. Fail CLOSED (grok, reproduced 2026-09-09).
    if fence is not None:
        raise GateError("41-file-registry.md: unclosed fenced code block (would hide later verdicts)")
    for section in sections:
        if len(section["verdicts"]) > 1:
            raise GateError(f"41-file-registry.md:{section['line']}: section has multiple verdict lines")
    # A gutted or truncated registry (no verdict-bearing section at all) must fail CLOSED,
    # not silently pass: with zero verdict sections the registry->§1 verdict cross-check
    # never runs, so an emptied 41 exits 0 with the whole provenance layer gone (codex,
    # reproduced 2026-09-09). The live registry always carries governed verdict sections.
    if not any(section["verdicts"] for section in sections):
        raise GateError("41-file-registry.md: no verdict sections found (registry is empty or gutted)")
    return sections


def _relative_file(path):
    resolved = os.path.realpath(path)
    if resolved != cachelib.ROOT and not resolved.startswith(cachelib.ROOT + os.sep):
        raise GateError(f"governed path escapes ~/.claude: {path} -> {resolved}")
    return os.path.relpath(path, cachelib.ROOT)


def _regular_file(path, label):
    try:
        st = os.stat(path)
    except OSError as exc:
        raise GateError(f"cannot stat {label}: {exc}")
    return os.path.isfile(path) and st.st_mode & 0o170000 == 0o100000


def _add_if_file(paths, path, label):
    # _regular_file RAISES on a missing path (os.stat) and returns False for an EXISTING
    # non-regular one (a directory/fifo named CLAUDE.md, a skill's SKILL.md, or a hook).
    # The old silent skip on False dropped that governed path from the inventory with no
    # error -- the same disappearance class as G3, but on these fixed named paths (grok +
    # codex, reproduced 2026-09-09). Every path routed here is REQUIRED, so fail CLOSED.
    if _regular_file(path, label):
        paths.add(_relative_file(path))
    else:
        raise GateError(f"non-regular governed path: {label} ({path})")


def _walk_bundle(paths, root):
    try:
        entries = sorted(os.scandir(root), key=lambda entry: entry.name)
    except OSError as exc:
        raise GateError(f"cannot enumerate cache_gate bundle: {exc}")
    for entry in entries:
        if entry.is_dir(follow_symlinks=False):
            _walk_bundle(paths, entry.path)
        elif entry.is_file(follow_symlinks=False):
            paths.add(_relative_file(entry.path))
        else:
            raise GateError(f"cache_gate bundle contains non-regular entry: {entry.path}")


def _inventory():
    root = cachelib.ROOT
    paths = set()
    harness = os.path.join(root, "harness")
    try:
        entries = sorted(os.scandir(harness), key=lambda entry: entry.name)
    except OSError as exc:
        raise GateError(f"cannot enumerate harness: {exc}")
    for entry in entries:
        if not entry.name.endswith(".md"):
            continue
        # A symlinked .md is skipped by is_file(follow_symlinks=False) and vanishes from the
        # inventory -> an unregistered governed file could hide behind a symlink (astra). A
        # symlink in a governed dir is an anomaly here: fail CLOSED.
        if entry.is_symlink():
            raise GateError(f"unexpected symlink in a governed dir: {entry.path}")
        if entry.is_file(follow_symlinks=False):
            paths.add(_relative_file(entry.path))
        else:
            # A non-regular '*.md' entry -- e.g. a DIRECTORY named foo.md -- is neither a
            # symlink nor a file, so it would be silently skipped and drop a governed path
            # from the inventory (grok, reproduced 2026-09-09). Fail CLOSED, matching
            # _walk_bundle and density's open()-on-a-directory GateError.
            raise GateError(f"non-regular '*.md' entry in a governed dir: {entry.path}")

    _add_if_file(paths, os.path.join(root, "CLAUDE.md"), "global CLAUDE.md")
    for relpath in (
        "hooks/gate-before-commit.sh",
        "hooks/parse-commit-command.py",
        "hooks/gate-credential-destruction.py",
        "hooks/observe-compaction-events.sh",
    ):
        _add_if_file(paths, os.path.join(root, relpath), relpath)

    _walk_bundle(paths, os.path.join(root, "hooks/harness/cache_gate"))
    hardcoded_skills = {
        "cross-model-review",
        "delegation-and-review",
        "ground-truth-gates",
        "operational-rigor",
        "security-architect",
        "skill-authoring",
        "skill-vetting",
    }
    for skill in hardcoded_skills:
        _add_if_file(paths, os.path.join(root, "skills", skill, "SKILL.md"), f"skills/{skill}/SKILL.md")

    # P1b cache-freshness coupling: if a new cache is added to the manifest (distilled by
    # bootstrap_ungated), it must be registered in check_catalog's hardcoded skill list,
    # else P1b_gate will catch ungoverned .cachelock.json files but check_catalog won't
    # govern the SKILL.md. Extract manifest cache names and verify every one is in the
    # hardcoded list (exact membership -- see the fail-open note on the loop below).
    try:
        manifest = cachelib.load_manifest()
    except Exception as exc:
        raise GateError(f"cannot load cache manifest: {exc}")
    # Each manifest cache key must EXACTLY name a hardcoded skill dir (whose SKILL.md the
    # loop above actually inventories). A prefix-stripped match was a fail-open: a key like
    # `skill-cross-model-review` strips to the hardcoded `cross-model-review` and passes, yet
    # cachelib binds it to the DISTINCT `skills/skill-cross-model-review/SKILL.md`, which the
    # hardcoded loop never stats -> an ungoverned SKILL.md slips through (grok+codex, reproduced
    # 2026-09-09). Exact membership only: the live manifest's keys all match a hardcoded name
    # verbatim, so the strip only ever manufactured false coverage.
    uncovered = []
    for cache_key in manifest.keys():
        if cache_key not in hardcoded_skills:
            uncovered.append(cache_key)
    if uncovered:
        raise GateError(
            f"manifest has caches not in check_catalog hardcoded list: {sorted(uncovered)}. "
            f"Add them to the skills loop."
        )

    memory = os.path.join(root, "memory")
    try:
        entries = sorted(os.scandir(memory), key=lambda entry: entry.name)
    except OSError as exc:
        raise GateError(f"cannot enumerate memory: {exc}")
    for entry in entries:
        if not entry.name.endswith(".md"):
            continue
        # A symlinked .md is skipped by is_file(follow_symlinks=False) and vanishes from the
        # inventory -> an unregistered governed file could hide behind a symlink (astra). A
        # symlink in a governed dir is an anomaly here: fail CLOSED.
        if entry.is_symlink():
            raise GateError(f"unexpected symlink in a governed dir: {entry.path}")
        if entry.is_file(follow_symlinks=False):
            paths.add(_relative_file(entry.path))
        else:
            # A non-regular '*.md' entry -- e.g. a DIRECTORY named foo.md -- is neither a
            # symlink nor a file, so it would be silently skipped and drop a governed path
            # from the inventory (grok, reproduced 2026-09-09). Fail CLOSED, matching
            # _walk_bundle and density's open()-on-a-directory GateError.
            raise GateError(f"non-regular '*.md' entry in a governed dir: {entry.path}")
    return sorted(paths)


def _row_matches(row, relpath):
    if MEMORY_CLASS in row["classes"]:
        # A Memory class row covers EXACTLY memory/*.md (except those with explicit rows).
        # The routing map has an explicit row, so don't let the class row also claim it.
        if relpath == "memory/reference_subordinate_routing_map.md":
            return False
        # Don't fall through to keys/dir_keys: a stray dir tick in the Memory row's col1
        # (e.g. "Memory files (`harness/`)") otherwise puts `harness/` in dir_keys and the
        # row then "covers" harness/*.md, masking a deleted §1 row for a harness file (grok,
        # reproduced 2026-09-09). Mirror PROJECT_CLASS: a class row is class-scoped only.
        return relpath.startswith("memory/") and relpath.endswith(".md")
    if PROJECT_CLASS in row["classes"]:
        return False
    for key in row["keys"]:
        if key == relpath:
            return True
    for key in row["dir_keys"]:
        directory = key.rstrip("/")
        if directory and relpath.startswith(directory + "/"):
            return True
    return False


def _print_scope():
    print("check_catalog scope:")
    for pattern in (
        "harness/*.md",
        "CLAUDE.md (global)",
        "hooks/gate-before-commit.sh",
        "hooks/parse-commit-command.py",
        "hooks/gate-credential-destruction.py",
        "hooks/observe-compaction-events.sh",
        "hooks/harness/cache_gate/ (whole directory bundle)",
        "skills/{cross-model-review,delegation-and-review,ground-truth-gates,operational-rigor,security-architect,skill-authoring,skill-vetting}/SKILL.md",
        "memory/*.md",
    ):
        print(f"  pattern: {pattern}")
    print("  special: Project CLAUDE.md files (class row)")
    print("  special: Memory files (class row)")
    print(f"  special: {EXTERNAL_SNAPSHOT} (named external object; not enumerated)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="check the complete governance catalog (default)")
    parser.parse_args()
    _print_scope()

    errors = []
    try:
        rows, table_errors = _parse_permission_table(os.path.join(cachelib.ROOT, "harness/40-maintenance.md"))
        errors.extend(table_errors)
        sections = _parse_registry(os.path.join(cachelib.ROOT, "harness/41-file-registry.md"))
        governed = _inventory()
    except GateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print(f"check_catalog: 0 governed files, {len(errors) + 1} error")
        return 2

    for relpath in governed:
        matches = [row for row in rows if _row_matches(row, relpath)]
        if len(matches) == 0:
            errors.append(f"{relpath}: governed but has no §1 row")
        elif len(matches) > 1:
            lines = ", ".join(str(row["line"]) for row in matches)
            errors.append(f"{relpath}: matches multiple §1 rows (lines {lines})")

    snapshot_rows = [row for row in rows if EXTERNAL_SNAPSHOT in row["keys"]]
    if not snapshot_rows:
        errors.append(f"{EXTERNAL_SNAPSHOT}: named external object has no §1 row")
    elif len(snapshot_rows) > 1:
        errors.append(f"{EXTERNAL_SNAPSHOT}: matches multiple §1 rows")
    else:
        print(f"NOTE: {EXTERNAL_SNAPSHOT} is named in §1 and is outside ROOT; readability is not checked")

    for section in sections:
        if not section["verdicts"]:
            continue
        heading = section["heading"]
        if section["classes"]:
            matches = [row for row in rows if any(c in row["classes"] for c in section["classes"])]
        else:
            # EVERY declared heading key must resolve to a §1 row. A heading naming two
            # objects (`X` + `Y`) where only X is registered must NOT pass through X alone
            # (astra: the old any()-match validated the whole section via one known key).
            # Use the same coverage predicate as inventory (_row_matches) to avoid false-RED
            # when a heading key is covered by a directory row (DIR-MATCH).
            unregistered = []
            matched_by_line = {}
            for key in section["keys"]:
                key_rows = [row for row in rows if _row_matches(row, key)]
                if not key_rows:
                    unregistered.append(key)
                for row in key_rows:
                    matched_by_line[row["line"]] = row
            if unregistered:
                errors.append(
                    f"41-file-registry.md:{section['line']}: verdict section names object(s) with no §1 row: "
                    f"{', '.join(unregistered)} ({heading})"
                )
                continue
            matches = list(matched_by_line.values())
        if not matches:
            errors.append(f"41-file-registry.md:{section['line']}: verdict section has no matching §1 row ({heading})")
            continue
        if len(matches) != 1:
            lines = ", ".join(str(row["line"]) for row in matches)
            errors.append(f"41-file-registry.md:{section['line']}: verdict section matches multiple §1 rows (lines {lines})")
            continue
        row = matches[0]
        # Check ALL verdicts in the section (not just the first) against the matched §1 row (VERDICT-TAIL).
        for verdict_line, actual in section["verdicts"]:
            if actual != row["verdict"]:
                errors.append(
                    f"41-file-registry.md:{verdict_line}: verdict mismatch for {section['heading']!r}: "
                    f"registry={actual!r}, §1={row['verdict']!r} (40-maintenance.md:{row['line']})"
                )

    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    print(f"check_catalog: {len(governed)} governed files, {len(errors)} error")
    return 2 if errors else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as exc:  # noqa: BLE001
        import traceback
        print(f"ERROR: check_catalog crashed: {exc}", file=sys.stderr)
        traceback.print_exc()
        print("check_catalog: 0 governed files, 1 error")
        sys.exit(2)
