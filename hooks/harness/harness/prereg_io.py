#!/usr/bin/env python3
"""prereg_io.py -- shared pre-registration I/O helpers for the harness gates.

`safe()` extracted 2026-09-09 from reconcile_pairs.py / reconcile_template.py /
cue_leak_lint.py, whose bodies were byte-identical (AST-verified; only the
docstrings differed). Extracting ONLY the proven-identical subset:

  - pairfloor.py keeps its OWN safe() -- it additionally escapes C0 (0x00-0x1f)
    and DEL (0x7f) control chars, a deliberately stricter policy. NOT shared.
  - checked_string is likewise NOT shared: pairfloor's rejects control chars,
    cue_leak_lint's does not. They are distinct helpers, not a duplicate.

Import mechanics: every gate that imports this runs as a top-level script (the
reconcile_template fixture drives it via a subprocess shim), so the script's own
directory is sys.path[0] and `from prereg_io import safe` resolves to this
sibling file. There is deliberately NO try/except ImportError fallback: a
missing prereg_io must fail loud, never silently fall back to a divergent inline
copy (that is exactly the escaping-drift the extraction exists to prevent).
"""


def safe(text):
    """Untrusted text (filenames, ids, record fields) for stdout: never let a
    stray lone surrogate turn a report into a traceback."""
    return text.encode("utf-8", "backslashreplace").decode("utf-8")
