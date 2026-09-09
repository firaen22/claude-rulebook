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


def _relative_key(token, first_key=None):
    token = token.strip()
    if token.startswith("~/.claude/"):
        return token[len("~/.claude/") :].lstrip("/")
    if token == "~/.claude":
        return ""
    if token.startswith("~/.local/"):
        return os.path.expanduser(token)
    if token.startswith("/"):
        return os.path.normpath(token)
    if first_key and not first_key.startswith("/"):
        return os.path.normpath(os.path.join(os.path.dirname(first_key), token))
    if "/" not in token:
        return os.path.join("harness", token)
    return os.path.normpath(token)


def _keys_from_text(text):
    """Return all path keys, anchoring relative note keys to the first key."""
    tokens = TICKS.findall(text)
    if not tokens:
        return []
    first = _relative_key(tokens[0])
    return [_relative_key(token, first) for token in tokens]


def _is_dir_key(key, row_text, token):
    # A dir-scoped key is spelled with a trailing slash in col1 (`cache_gate/`,
    # `ground-truth-gates/`, `references/`). The earlier heuristic also promoted EVERY
    # token in a row whose text mentioned "references/" or "cachelib" -- that made a
    # file token like `.../SKILL.md` a bogus directory prefix (astra: unjustified
    # inference). The trailing slash is the only real signal; use it alone.
    return token.rstrip().endswith("/")


def _parse_permission_table(path):
    text = _read_text(path, "40-maintenance.md")
    lines = text.splitlines()
    try:
        header = next(i for i, line in enumerate(lines) if line.strip() == TABLE_HEADER)
    except StopIteration:
        raise GateError("40-maintenance.md: §1 permission table header is missing")
    if header + 1 >= len(lines) or not TABLE_SEPARATOR.match(lines[header + 1]):
        raise GateError("40-maintenance.md: §1 table separator is missing or malformed")

    rows = []
    for line_number, line in enumerate(lines[header + 2 :], header + 3):
        if not line.startswith("|"):
            break
        fields = line.split("|")
        # A well-formed row is `| File | verdict | Rule |` -> ['', c1, c2, c3, ''] (len>=5).
        # `| c1 | c2 |` (len 4) is missing the Rule cell; an empty fields[3] is the same
        # defect written with a stray delimiter (astra: malformed rows passed on len>=4).
        if (len(fields) < 5 or not fields[1].strip() or not fields[2].strip()
                or not fields[3].strip()):
            raise GateError(f"40-maintenance.md:{line_number}: malformed §1 data row")
        col1 = fields[1].strip()
        classes = []
        if "Project `CLAUDE.md` files" in col1:
            classes.append(PROJECT_CLASS)
        if "Memory files" in col1:
            classes.append(MEMORY_CLASS)
        keys = [] if classes else _keys_from_text(col1)
        if not classes and not keys:
            raise GateError(f"40-maintenance.md:{line_number}: §1 row has no backticked key")
        verdict = _normalize_verdict(fields[2])
        # `** **` strips to empty (astra: a verdict that is only markup passed the
        # non-empty check on the raw cell but normalizes to nothing).
        if not verdict:
            raise GateError(f"40-maintenance.md:{line_number}: §1 verdict is empty after normalization")
        rows.append({
            "line": line_number,
            "keys": keys,
            "classes": classes,
            "dir_keys": {
                _relative_key(token, keys[0] if keys else None)
                for token in TICKS.findall(col1)
                if _is_dir_key(_relative_key(token, keys[0] if keys else None), col1, token)
            },
            "verdict": verdict,
            "text": col1,
        })
    else:
        raise GateError("40-maintenance.md: §1 table has no terminating non-table line")
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
    for line_number, line in enumerate(text.splitlines(), 1):
        if line.startswith("## "):
            if current:
                sections.append(current)
            heading = line[3:].strip()
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
        elif current and "edit permission" in line.lower():
            # Detect any form of verdict line (indented, list marker, blockquote, variant
            # casings) and REQUIRE the canonical form (fable). A non-canonical form fails
            # closed, not silent-skip. lstrip first: indentation is allowed (a paragraph
            # in Markdown). But list marker "- **Edit...**", blockquote "> **Edit...**",
            # colon-outside-bold "**Edit...**:", no-bold "Edit permission..." all FAIL.
            stripped = line.lstrip()
            if not stripped.startswith(VERDICT_LINE):
                raise GateError(
                    f"41-file-registry.md:{line_number}: verdict line is non-canonical "
                    f'(must be "{VERDICT_LINE} <text>", not a list, blockquote, or variant)'
                )
            current["verdicts"].append((line_number, _normalize_verdict(stripped[len(VERDICT_LINE) :])))
    if current:
        sections.append(current)
    for section in sections:
        if len(section["verdicts"]) > 1:
            raise GateError(f"41-file-registry.md:{section['line']}: section has multiple verdict lines")
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
    if _regular_file(path, label):
        paths.add(_relative_file(path))


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
    # govern the SKILL.md. Extract manifest cache names (some have prefix, some don't) and
    # verify every one is either in the hardcoded list or has an exemption recorded.
    try:
        manifest = cachelib.load_manifest()
    except Exception as exc:
        raise GateError(f"cannot load cache manifest: {exc}")
    # Normalize manifest keys: "skill-authoring" → "skill-authoring", "delegation-and-review" → "delegation-and-review"
    # (the manifest uses both forms; check if each is in the hardcoded set, accounting for either form)
    uncovered = []
    for cache_key in manifest.keys():
        # Try exact match and prefix-stripped match
        if cache_key not in hardcoded_skills and cache_key.replace("skill-", "", 1) not in hardcoded_skills:
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
    return sorted(paths)


def _row_matches(row, relpath):
    if MEMORY_CLASS in row["classes"] and relpath.startswith("memory/") and relpath.endswith(".md"):
        return True
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
        elif len(matches) > 1 and not (len(matches) == 2 and any(MEMORY_CLASS in row["classes"] for row in matches)):
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
            unregistered = []
            matched_by_line = {}
            for key in section["keys"]:
                key_rows = [row for row in rows if key in row["keys"] or key in row["dir_keys"]]
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
        actual = section["verdicts"][0][1]
        if actual != row["verdict"]:
            errors.append(
                f"41-file-registry.md:{section['verdicts'][0][0]}: verdict mismatch for {section['heading']!r}: "
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
