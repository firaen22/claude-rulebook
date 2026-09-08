#!/usr/bin/env python3
"""Fail-closed freshness gate for the locally distilled skill caches.

Exit 0 = every cache is fresh (its pinned sources AND its own body are unchanged
since the last build_cache); 1 = at least one DRIFT/BODYDRIFT (rebuild needed);
2 = at least one hard ERROR (bad manifest/lock/path, missing/unreadable file). 2
outranks 1. It NEVER exits 0 on an empty/corrupt manifest or an ungated cache.

Scope: freshness of SOURCES + integrity of the pin. NOT parity (a distillation is
not byte-compared to its source). The body pin covers each cache's SKILL.md only,
NOT its references/**/*.md (fable S7): a stale reference file vs its harness source
is out of scope here. Enforcement point: run_all.sh + pre-commit only (NOT
SessionStart) -- so this does not protect the pre-source cache load order; it
catches drift at commit/verify time.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cachelib  # noqa: E402  (deliberate: robust local import, never via cwd/$PWD)
from cachelib import GateError  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true")
    group.add_argument("--cache")
    args = parser.parse_args()

    try:
        caches = cachelib.load_manifest()
    except GateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print("check_caches: 0 caches, 0 drift, 1 error")
        return 2

    drift = 0
    errors = 0

    if args.cache:
        if args.cache not in caches:
            print(f"ERROR: unknown cache {args.cache}", file=sys.stderr)
            print("check_caches: 0 caches, 0 drift, 1 error")
            return 2
        names = [args.cache]
    else:
        names = list(caches)
        # Completeness: a harness cache with no manifest row would be silently ungated.
        # Wrap the scan (fable N4): a listdir/stat/read failure inside it is a GateError,
        # which must land as a controlled ERROR + summary line, not the crash backstop's
        # traceback (still exit 2 either way, but the controlled path names the cause).
        try:
            ungated_names = cachelib.bootstrap_ungated(caches)
        except GateError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            ungated_names = []
            errors += 1
        for ungated in ungated_names:
            print(f"ERROR: {ungated} caches harness files (Cache over ...) but has no manifest row", file=sys.stderr)
            errors += 1
    for name in names:
        entry = caches[name]
        try:
            lock = cachelib.load_lock(name, entry)
            # Body pin (F3/S1): the lock certifies THIS cache body against these
            # sources. A stale cache swapped back in, or an edited cache not re-pinned,
            # must not pass. Missing/unreadable skill = ERROR (the cache is gone).
            skill_path = cachelib.resolve_within_root(entry["skill"])
            body_now = cachelib.sha256_file(skill_path)
        except GateError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            errors += 1
            continue
        except OSError as exc:
            print(f"ERROR: {name}: skill unreadable ({exc})", file=sys.stderr)
            errors += 1
            continue

        # Reverse-check (fable S8): a manifest'd skill MUST carry the 'Cache over' marker,
        # so the conservative forward matcher (cachelib.has_cache_marker) stays load-bearing
        # -- if a gated cache drops the marker, catch it here rather than widen the matcher.
        try:
            with open(skill_path, encoding="utf-8", errors="replace") as handle:
                if not cachelib.has_cache_marker(handle.read()):
                    print(f"ERROR: {name}: gated skill lacks the 'Cache over' marker ({entry['skill']})", file=sys.stderr)
                    errors += 1
        except OSError as exc:
            print(f"ERROR: {name}: skill unreadable ({exc})", file=sys.stderr)
            errors += 1

        via = lock.get("built_via", "normal")
        # WARN only on the AUDIT-worthy override -- a force-sync that skipped the body
        # change. fresh-init is the benign initial state (still recorded in the lock and
        # visible in its git diff, fable S5); WARNing on it every run just desensitizes
        # the operator to WARNs (the reflex fable S4 warns against).
        if via == "unchanged-body-override":
            print(f"WARN {name}: lock built via {via} (audit the cache re-sync)")

        if body_now != lock["body_sha"]:
            print(f"BODYDRIFT {name}: {entry['skill']} lock={lock['body_sha'][:8]} now={body_now[:8]}")
            drift += 1

        for relpath in entry["sources"]:
            try:
                current = cachelib.sha256_file(cachelib.resolve_within_root(relpath))
            except GateError as exc:
                print(f"ERROR: {exc}", file=sys.stderr)
                errors += 1
                continue
            except OSError as exc:
                print(f"ERROR: {name}: {relpath} unreadable ({exc})", file=sys.stderr)
                errors += 1
                continue
            if lock["sources"][relpath] != current:
                print(f"DRIFT {name}: {relpath} lock={lock['sources'][relpath][:8]} now={current[:8]}")
                drift += 1

    print(f"check_caches: {len(names)} caches, {drift} drift, {errors} error")
    if errors:
        return 2
    return 1 if drift else 0


if __name__ == "__main__":
    # Backstop: any unforeseen exception fails CLOSED with a controlled exit 2,
    # never a bare exit-1 traceback that reads as "drift" (fable S6).
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as exc:  # noqa: BLE001
        import traceback
        # Fail CLOSED but name WHERE (fable S6): a bare message hid which file/line
        # crashed the gate; the full traceback goes to stderr, still exit 2.
        print(f"ERROR: check_caches crashed: {exc}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(2)
