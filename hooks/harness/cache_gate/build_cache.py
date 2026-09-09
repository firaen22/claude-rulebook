#!/usr/bin/env python3
"""(Re)build freshness lockfiles for the locally distilled skill caches.

Run after re-syncing a cache to its sources: writes .cachelock.json pinning each
source's sha and the cache body's sha at build time.

LIMITATION (F2, by design, single-operator harness): the --allow-unchanged-body
anti-cheat is an UNCHANGED-BODY SPEED-BUMP, not a security control. It catches the
"bump the pin without re-syncing the cache" slip; it cannot prove the operator
re-synced correctly, and deleting the lockfile bypasses it (check_caches then errors
exit 2 until a rebuild, so the bypass is a visible, deliberate act in the diff).
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cachelib  # noqa: E402  (deliberate: robust local import, never via cwd/$PWD)
from cachelib import GateError  # noqa: E402


def _read_lock_raw(lock_path):
    """Lenient read of an existing lock for the reflex guard ONLY (fable S3b).

    Deliberately NOT cachelib.load_lock: a manifest whose source SET changed makes
    the strict loader reject the still-informative old lock, which would reset the
    guard to fresh-init and let a drifted source through with an unchanged body.
    Returns a dict (possibly partial) or None if there is no usable prior lock.
    """
    try:
        with open(lock_path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    # Require BOTH a sources dict and a non-empty string body_sha (fable N3): a lock with
    # body_sha missing/non-string must be treated as NO usable prior lock (-> fresh-init),
    # not laundered through the reflex guard as "normal" while a drifted source rides along.
    if not isinstance(data, dict) or not isinstance(data.get("sources"), dict):
        return None
    if not isinstance(data.get("body_sha"), str) or not data["body_sha"]:
        return None
    return data


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true")
    group.add_argument("--cache")
    parser.add_argument("--allow-unchanged-body", action="store_true")
    args = parser.parse_args()

    try:
        caches = cachelib.load_manifest()
    except GateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.cache:
        if args.cache not in caches:
            print(f"ERROR: unknown cache {args.cache}", file=sys.stderr)
            return 2
        names = [args.cache]
    else:
        names = list(caches)

    for name in names:
        entry = caches[name]
        try:
            body_sha = cachelib.sha256_file(cachelib.resolve_within_root(entry["skill"]))
            source_shas = {
                src: cachelib.sha256_file(cachelib.resolve_within_root(src))
                for src in entry["sources"]
            }
            lock_path = cachelib.lock_path_for(entry["skill"])
        except GateError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        except OSError as exc:
            print(f"ERROR: {name}: {exc}", file=sys.stderr)
            return 2

        # Reflex guard (NOT a security control -- see module docstring): only a VALID
        # prior lock arms it (a missing/corrupt lock is a fresh init, not a bypass).
        # Record how the lock was built so an override/init is visible in the committed
        # lock's `git diff` and in run_all's log (fable S5), never a silent equal-looking
        # rebuild.
        old = _read_lock_raw(lock_path)
        if old is None:
            built_via = "fresh-init"
        else:
            old_sources = old.get("sources") or {}
            old_body = old.get("body_sha")
            # A source SET change (add/remove) is drift too (fable S3b) -- not just a
            # value change on a shared key; either with an unchanged body must REFUSE.
            set_changed = set(old_sources) != set(source_shas)
            common_drift = any(
                old_sources.get(s) != source_shas.get(s)
                for s in set(old_sources) & set(source_shas)
            )
            source_changed = set_changed or common_drift
            body_unchanged = isinstance(old_body, str) and old_body == body_sha
            if source_changed and body_unchanged:
                if not args.allow_unchanged_body:
                    print(
                        f"REFUSED: {name} source(s) changed but cache body unchanged; "
                        "re-sync the cache text or pass --allow-unchanged-body",
                        file=sys.stderr,
                    )
                    return 3
                built_via = "unchanged-body-override"
            elif not source_changed and body_unchanged:
                # True no-op rebuild: nothing was re-synced, so CARRY the prior audit
                # signal forward instead of laundering an override back to "normal"
                # (fable S3a). A real re-sync (body changes) legitimately clears it.
                prev = old.get("built_via")
                built_via = prev if prev in cachelib.VALID_BUILT_VIA else "normal"
            else:
                built_via = "normal"

        lock = {"cache": name, "sources": source_shas, "body_sha": body_sha, "built_via": built_via}
        with open(lock_path, "w", encoding="utf-8") as handle:
            json.dump(lock, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print(f"BUILT {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
