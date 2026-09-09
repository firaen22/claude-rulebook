#!/usr/bin/env python3
"""Fail-closed gate for §4's two density twins (see 40-maintenance.md §4).

Over the harness rules files + global CLAUDE.md, enforces:
  - prose words/line (non-table, non-blank lines) must be <= 13.0
  - any single table row (^\\s*\\|) must have <= 150 whitespace-fields (>= awk NF:
    equal on ASCII whitespace, strict on Unicode spaces; the scoped files carry none)
The line-count-exempt evidence files (41-file-registry, LESSONS-archive) are NOT
density-exempt (§4: "exempt from the line count is not exempt from measurement").

The metric mirrors §4's two documented commands exactly; the thresholds are §4's
(~13 w/l, ~150 fields) with equality passing (150 is the documented cap).

exit 0 = both twins clean for every file
exit 1 = at least one twin violated
exit 2 = GateError / any unexpected exception (unreadable file, path escape, IO error)
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cachelib  # noqa: E402  (deliberate local import, never via cwd/$PWD)
from cachelib import GateError  # noqa: E402


PROSE_MAX = 13.0  # §4 twin 1: ~13 w/l ceiling (corpus 8.9-12.1; the defect measured 64)
ROW_MAX = 150     # §4 twin 2: ~150 fields/row cap (the defect measured 2716)


def _scoped_files():
    """Global CLAUDE.md + every harness/*.md, as relpaths under ROOT (sorted, stable).

    Enumerate with os.scandir, NOT glob: glob silently returns fewer paths when harness/
    is missing/unreadable (cachelib documents this hazard), which would collapse the scope
    to CLAUDE.md alone and exit 0 -- a false PASS. A missing/unreadable/empty harness dir is
    itself a scope error and must fail CLOSED (GateError -> exit 2).
    """
    harness_dir = os.path.join(cachelib.ROOT, "harness")
    try:
        names = sorted(e.name for e in os.scandir(harness_dir) if e.name.endswith(".md"))
    except OSError as exc:
        raise GateError(f"cannot enumerate harness/: {exc}")
    if not names:
        raise GateError("harness/ has no .md files -- density scope collapsed")
    return ["CLAUDE.md"] + [os.path.join("harness", name) for name in names]


def check_file(relpath):
    """Measure one file's two density twins. Returns (nlines, ratio, max_row_nf, [violations]).

    Mirrors §4's commands exactly:
      prose = non-blank lines whose lstrip does NOT start with '|'; ratio = words/lines
      row   = lines whose lstrip starts with '|'; fields = len(line.split()) (>= awk NF)
    Raises GateError (never a silent skip) if the file cannot be read.
    """
    abspath = cachelib.resolve_within_root(relpath)
    try:
        with open(abspath, encoding="utf-8") as handle:
            lines = handle.readlines()
    except (OSError, UnicodeError) as exc:
        raise GateError(f"cannot read {relpath}: {exc}")

    prose = [ln for ln in lines if ln.split() and not ln.lstrip().startswith("|")]
    words = sum(len(ln.split()) for ln in prose)
    ratio = round(words / max(len(prose), 1), 1)

    row_nfs = [len(ln.split()) for ln in lines if ln.lstrip().startswith("|")]
    max_nf = max(row_nfs) if row_nfs else 0

    violations = []
    if ratio > PROSE_MAX:
        violations.append(f"DENSITY {relpath}: prose {ratio} w/l > {PROSE_MAX}")
    if max_nf > ROW_MAX:
        violations.append(f"DENSITY {relpath}: row {max_nf} fields > {ROW_MAX}")
    return len(lines), ratio, max_nf, violations


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")  # accepted for suite symmetry
    parser.parse_args()

    try:
        files = _scoped_files()
        violations = []
        for relpath in files:
            nlines, ratio, max_nf, viol = check_file(relpath)
            print(f"density {relpath}: {nlines} lines, {ratio} w/l, max-row {max_nf}")
            violations.extend(viol)
    except GateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print("check_density: 0 files, 1 error")
        return 2

    for line in violations:
        print(line)
    print(f"check_density: {len(files)} files, {len(violations)} violation(s)")
    return 1 if violations else 0


if __name__ == "__main__":
    # Backstop: any unforeseen exception fails CLOSED with a controlled exit 2,
    # never a bare exit-1 traceback that reads as a density violation.
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as exc:  # noqa: BLE001
        import traceback
        print(f"ERROR: check_density crashed: {exc}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(2)
