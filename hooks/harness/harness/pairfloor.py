#!/usr/bin/env python3
"""pairfloor.py -- deterministic pre-registration matched-pair floor gate.

The manifest contains observation ids and their matched pairs.  The gate refuses
to run a design with fewer distinct matched pairs than the operator's floor.

Exit contract: 0 means OK (enough pairs), 1 means UNDERPOWERED (too few pairs),
and 2 means ERROR (the manifest or floor has an undefined shape).
"""
import argparse
import json
import re
import sys


FLOOR_RE = re.compile(r"[1-9][0-9]*\Z", re.ASCII)


def safe(text):
    """Untrusted manifest text for stdout: never emit a lone surrogate."""
    return text.encode("utf-8", "backslashreplace").decode("utf-8")


def checked_string(value, label):
    if not isinstance(value, str) or not value:
        raise ValueError("%s must be a nonempty string" % label)
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        raise ValueError("%s contains a lone surrogate" % label)
    return value


def load_manifest(path):
    try:
        with open(path, "rb") as fh:
            manifest = json.loads(fh.read().decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError("cannot read or parse manifest: %s" % exc)
    if not isinstance(manifest, dict):
        raise ValueError("outer JSON is not an object")
    known = {"done_when", "items", "pairs", "allowlist", "overrides"}
    unknown = set(manifest) - known
    if unknown:
        raise ValueError("unknown top-level key %s" % safe(sorted(unknown)[0]))
    for key in ("items", "pairs"):
        if key not in manifest:
            raise ValueError("missing required key '%s'" % key)

    items = manifest["items"]
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    ids = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError("item %d is not an object" % index)
        if "id" not in item:
            raise ValueError("item %d missing 'id'" % index)
        item_id = checked_string(item["id"], "item id")
        if item_id in ids:
            raise ValueError("duplicate item id %s" % safe(item_id))
        ids.add(item_id)
    if not ids:
        raise ValueError("items is empty")

    pairs = manifest["pairs"]
    if not isinstance(pairs, list):
        raise ValueError("pairs must be a list")
    raw_pairs = []
    for index, pair in enumerate(pairs):
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError("pair %d is not a 2-list" % index)
        left = checked_string(pair[0], "pair id")
        right = checked_string(pair[1], "pair id")
        if left not in ids or right not in ids:
            raise ValueError("pair %d names an unknown id" % index)
        if left == right:
            raise ValueError("pair %d is a self-pair" % index)
        raw_pairs.append((left, right))

    # Empty pairs is a valid design; it is maximally underpowered, not malformed.
    distinct_pairs = {(min(left, right), max(left, right))
                      for left, right in raw_pairs}
    partners = {}
    for left, right in distinct_pairs:
        if left in partners and partners[left] != right:
            raise ValueError("%s has conflicting pair partners" % safe(left))
        if right in partners and partners[right] != left:
            raise ValueError("%s has conflicting pair partners" % safe(right))
        partners[left] = right
        partners[right] = left
    return sorted(distinct_pairs)


def parse_floor(raw):
    if not isinstance(raw, str) or not FLOOR_RE.fullmatch(raw):
        raise ValueError("floor must be a positive base-10 integer")
    return int(raw)


def main(argv=None):
    sys.stdout.reconfigure(errors="backslashreplace")
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("manifest")
    ap.add_argument("--floor", default="6",
                    help="minimum distinct matched pairs (default 6)")
    args = ap.parse_args(argv)
    try:
        floor = parse_floor(args.floor)
        distinct_pairs = load_manifest(args.manifest)
    except (OSError, ValueError, TypeError) as exc:
        print("RESULT: ERROR (%s)" % safe(str(exc)))
        return 2
    count = len(distinct_pairs)
    print("SUMMARY pairs=%d floor=%d" % (count, floor))
    for left, right in distinct_pairs:
        print("pair %s %s" % (safe(left), safe(right)))
    result = "OK" if count >= floor else "UNDERPOWERED"
    print("RESULT: %s" % result)
    return 0 if result == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
