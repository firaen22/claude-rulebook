#!/usr/bin/env python3
"""Shared, fail-closed helpers for the cache-freshness gate.

Both build_cache.py and check_caches.py import this. Every function here either
returns a validated value or raises GateError; the callers turn GateError into a
controlled exit 2 (never an uncaught traceback, never a silent skip).
"""

import hashlib
import json
import os
import re
import stat

VALID_BUILT_VIA = ("normal", "fresh-init", "unchanged-body-override")

# A skill that distills local harness files declares it with a top line `Cache over ...`
# (a port of an external doc uses "Ported into this local cache"/"Distilled from ..." and
# stays exempt). This matcher went through both failure directions in review before landing
# here: an exact `startswith` fail-OPENED on emphasis/indent variants; a plain literal STILL
# missed `**Cache over**`/`- Cache over`/lower-case/BOM (fable N1: 8 false-neg) and newly
# false-flagged `Cache overflow`/`overwrite`. The regime below (astra R3-3 + fable N1, both
# reproduced, 0 false-neg / 0 false-pos over 14 variants, flags exactly the 3 live caches):
#   ^(?!\s*>)          -- reject a blockquote `> Cache over` (a QUOTED example, not a decl)
#   (?:[\W_]|\d+\.)*   -- consume leading emphasis (** __), list markers (- , 1.), BOM, indent
#   cache[sd]? over    -- Cache/Caches/Cached over, case-insensitive
#   (?![a-z])          -- but NOT overflow/overwrite (over must end the word)
# Residual false-pos is only prose literally beginning "Cache over ..." -- inherent to any
# line-prefix convention, none in the live tree; the reverse-check keeps the literal
# load-bearing for gated skills.
_CACHE_MARKER = re.compile(r"^(?!\s*>)(?:[\W_]|\d+\.)*cache[sd]?\s+over(?![a-z])", re.IGNORECASE)


def has_cache_marker(text):
    """True if any line declares the skill a local-harness cache (see _CACHE_MARKER)."""
    return any(_CACHE_MARKER.match(line) for line in text.splitlines())


HERE = os.path.dirname(os.path.abspath(__file__))
# Derive the harness root from THIS file's location (<root>/hooks/harness/cache_gate),
# never from $HOME: the gate must check the tree it lives in, so a worktree/clone at
# another path checks ITS OWN sources, not always ~/.claude (fable S4).
ROOT = os.path.realpath(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
MANIFEST_PATH = os.path.join(HERE, "cache_manifest.json")


class GateError(Exception):
    """Any manifest/lock/path integrity violation. Callers -> exit 2 (fail closed)."""


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def resolve_within_root(relpath):
    """Resolve a manifest path against ROOT and PROVE it stays inside ROOT.

    Rejects absolute paths, '..' traversal, and symlink escape (F4/S4): a manifest
    typo like '/etc/hostname' or '../../x' must never make the gate hash an
    unrelated file and report green.
    """
    if not isinstance(relpath, str) or not relpath:
        raise GateError(f"path must be a non-empty string: {relpath!r}")
    if os.path.isabs(relpath):
        raise GateError(f"path must be relative to ~/.claude, not absolute: {relpath}")
    resolved = os.path.realpath(os.path.join(ROOT, relpath))
    if resolved != ROOT and not resolved.startswith(ROOT + os.sep):
        raise GateError(f"path escapes ~/.claude: {relpath} -> {resolved}")
    return resolved


def load_manifest():
    """Load AND fully validate the manifest. Any schema violation -> GateError.

    Guarantees to callers: returns {name: {"skill": str, "sources": [str, ...]}} with
    a non-empty caches map and every cache carrying a non-empty sources list. An empty
    or truncated manifest is an ERROR, never a vacuous '0 caches, 0 drift' green (F4).
    """
    try:
        with open(MANIFEST_PATH, encoding="utf-8") as handle:
            manifest = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise GateError(f"cannot read manifest: {exc}")
    if not isinstance(manifest, dict):
        raise GateError("manifest is not a JSON object")
    caches = manifest.get("caches")
    if not isinstance(caches, dict) or not caches:
        raise GateError("manifest has no non-empty 'caches' object")
    for name, entry in caches.items():
        if not isinstance(entry, dict):
            raise GateError(f"{name}: cache entry is not an object")
        skill = entry.get("skill")
        if not isinstance(skill, str) or not skill:
            raise GateError(f"{name}: missing/invalid 'skill'")
        # Canonical-path bind (F3): a cache's skill MUST be its own skills/<name>/SKILL.md.
        # Otherwise the manifest could point `skill` at a decoy file (skills/<name>/OTHER.md),
        # body-pin that decoy, and leave the actually-loaded SKILL.md ungated (bootstrap keys
        # on the dir name, so it still sees a manifest row). Forcing the canonical path makes
        # the pinned body and the consumed cache the same file, so no redirect is possible.
        expected_skill = f"skills/{name}/SKILL.md"
        if skill != expected_skill:
            raise GateError(f"{name}: skill must be {expected_skill}, not {skill}")
        sources = entry.get("sources")
        if not isinstance(sources, list) or not sources:
            raise GateError(f"{name}: 'sources' must be a non-empty list")
        for src in sources:
            if not isinstance(src, str) or not src:
                raise GateError(f"{name}: source entries must be non-empty strings")
    return caches


def lock_path_for(skill_relpath):
    return os.path.join(os.path.dirname(resolve_within_root(skill_relpath)), ".cachelock.json")


def bootstrap_ungated(caches):
    """Return skill dirs that cache harness files but have NO manifest row (fable S2c).

    Convention: a skill that distills local harness files opens with a line
    `Cache over ...` (a port of an external doc uses "Ported into this local cache"
    instead, and stays exempt). Any such skill missing from the manifest is silently
    ungated -> the caller turns a non-empty result into a controlled error exit 2.

    Fail CLOSED (F2): enumerate with os.listdir (which RAISES on a permission/IO error,
    unlike glob, which silently returns fewer paths) and treat an unreadable candidate
    SKILL.md as a GateError, never a `continue` that drops it from the scan -- a skill we
    cannot read is exactly the one that might be an ungated cache.
    """
    skills_dir = os.path.join(ROOT, "skills")
    try:
        entries = sorted(os.listdir(skills_dir))
    except FileNotFoundError:
        return []  # no skills/ tree at all -> nothing to bootstrap-check (not an error)
    except OSError as exc:
        raise GateError(f"cannot enumerate skills dir: {exc}")
    ungated = []
    for name in entries:
        skill = os.path.join(skills_dir, name, "SKILL.md")
        # os.path.isfile SWALLOWS a permission error on the dir and returns False (astra
        # R3-2: `chmod 000 skills/<name>` then hid an ungated cache). Stat explicitly:
        # genuine absence is skipped, a permission/IO failure is a GateError (fail closed).
        try:
            st = os.stat(skill)
        except (FileNotFoundError, NotADirectoryError):
            continue
        except OSError as exc:
            raise GateError(f"cannot stat skill {name}/SKILL.md: {exc}")
        if not stat.S_ISREG(st.st_mode):
            continue
        try:
            # errors="replace" (fable S6): invalid UTF-8 in ANY skill must not crash
            # bootstrap with a location-less traceback -- a replacement char never
            # forges a marker match, so this stays fail-closed without the crash.
            with open(skill, encoding="utf-8", errors="replace") as handle:
                text = handle.read()
        except OSError as exc:
            raise GateError(f"cannot read skill {name}/SKILL.md: {exc}")
        if has_cache_marker(text) and name not in caches:
            ungated.append(name)
    return ungated


def load_lock(name, entry):
    """Load AND validate a lockfile against its manifest entry. Violation -> GateError.

    Binds the lock to THIS cache (F3/S6): the lock must name this cache, carry a
    body_sha, and its source-key set must equal the manifest's sources exactly — so a
    lock copied from another cache, or a partial hand-crafted lock, is an error, not a
    green.
    """
    path = lock_path_for(entry["skill"])
    try:
        with open(path, encoding="utf-8") as handle:
            lock = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise GateError(f"{name}: no valid lockfile ({exc})")
    if not isinstance(lock, dict):
        raise GateError(f"{name}: lock is not an object")
    if lock.get("cache") != name:
        raise GateError(f"{name}: lock cache-id mismatch ({lock.get('cache')!r})")
    if not isinstance(lock.get("body_sha"), str) or not lock["body_sha"]:
        raise GateError(f"{name}: lock missing body_sha")
    locked_sources = lock.get("sources")
    if not isinstance(locked_sources, dict):
        raise GateError(f"{name}: lock 'sources' is not an object")
    if set(locked_sources) != set(entry["sources"]):
        raise GateError(f"{name}: lock source set != manifest ({sorted(locked_sources)} vs {sorted(entry['sources'])})")
    for value in locked_sources.values():
        if not isinstance(value, str) or not value:
            raise GateError(f"{name}: lock contains a non-string source hash")
    # Audit field must be present AND valid (fable S3c): a lock lacking built_via must
    # not slip through as an implicit "normal" and mute the WARN on a re-synced cache.
    if lock.get("built_via") not in VALID_BUILT_VIA:
        raise GateError(f"{name}: lock has invalid/absent built_via ({lock.get('built_via')!r})")
    return lock
