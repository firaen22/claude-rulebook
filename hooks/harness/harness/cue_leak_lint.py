#!/usr/bin/env python3
"""cue_leak_lint.py -- deterministic pre-registration cue-leak lint.

The manifest contains one ruled prompt clause and item evidence strings.  The
lint reports the per-item share of evidence 2/3-grams found in the clause.

Exit contract: 0 means CLEAN (no non-overridden leak), 1 means LEAK (at least
one non-overridden item leaks), and 2 means ERROR (the manifest or threshold
has an undefined shape, including an unlintable item or an empty items list).

LIMITATION (F1, cross-model review 2026-09-08): the metric is |E n D| / |E| over
the WHOLE evidence, so a verbatim-copied cue padded with a few extra evidence
tokens can fall below threshold and read CLEAN (measured: the P4 fixture evidence
with 5 filler words -> ratio 0.31, where the evidence's copied span is 11/25
n-grams). This is a WARN tripwire for the obvious tight-evidence copy -- the
manual check it automates -- NOT a hard gate. Closing the miss needs a
dilution-proof span-containment signal whose run-length knob must be calibrated
on >=6 matched pairs; we have N=1, so it is deferred until that data exists.
Until then, use overrides for known-and-accepted cues.
"""
import argparse
import json
import math
import sys
import unicodedata


STOPWORDS = {
    "the", "a", "an", "of", "to", "and", "or", "is", "it", "that",
    "this", "not", "no", "in", "on", "for", "with", "as", "by", "at",
    "its", "but", "than", "then", "both", "only", "does", "do", "now",
    "new", "be", "are", "was", "were", "from", "into", "when", "after",
    "before", "itself", "their", "there", "all", "any", "can", "has",
}


def safe(text):
    """Untrusted manifest text for stdout: never emit a lone surrogate."""
    return text.encode("utf-8", "backslashreplace").decode("utf-8")


def normalize(text, allowlist):
    text = unicodedata.normalize("NFC", text).casefold()
    text = "".join(c if c.isalnum() else " " for c in text)
    return [token for token in text.split()
            if token not in STOPWORDS and token not in allowlist]


def ngrams(tokens):
    return {tuple(tokens[i:i + size])
            for size in (2, 3)
            for i in range(len(tokens) - size + 1)}


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
    if "done_when" not in manifest or "items" not in manifest:
        raise ValueError("missing required key 'done_when' or 'items'")
    done_when = checked_string(manifest["done_when"], "done_when")
    items = manifest["items"]
    if not isinstance(items, list):
        raise ValueError("items must be a list")

    allowlist_raw = manifest.get("allowlist", [])
    if not isinstance(allowlist_raw, list):
        raise ValueError("allowlist must be a list")
    allowlist = set()
    for entry in allowlist_raw:
        checked_string(entry, "allowlist entry")
        tokens = normalize(entry, set())
        if len(tokens) != 1:
            raise ValueError("allowlist entry %s must normalize to exactly one token"
                             % safe(entry))
        allowlist.add(tokens[0])

    overrides = manifest.get("overrides", {})
    if not isinstance(overrides, dict):
        raise ValueError("overrides must be an object")
    for key, reason in overrides.items():
        checked_string(key, "override key")
        checked_string(reason, "override reason")

    parsed = []
    ids = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError("item %d is not an object" % index)
        for field in ("id", "key", "evidence"):
            if field not in item:
                raise ValueError("item %d missing '%s'" % (index, field))
        item_id = checked_string(item["id"], "item id")
        key = checked_string(item["key"], "item %s key" % item_id)
        evidence = checked_string(item["evidence"], "item %s evidence" % item_id)
        if item_id in ids:
            raise ValueError("duplicate item id %s" % safe(item_id))
        ids.add(item_id)
        parsed.append((item_id, key, evidence))
    if not parsed:
        raise ValueError("items is empty")

    pairs = manifest.get("pairs", [])
    if not isinstance(pairs, list):
        raise ValueError("pairs must be a list")
    partners = {}
    for index, pair in enumerate(pairs):
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError("pair %d is not a 2-list" % index)
        left = checked_string(pair[0], "pair id")
        right = checked_string(pair[1], "pair id")
        if left not in ids or right not in ids:
            raise ValueError("pair %d names an unknown id" % index)
        if left == right:
            raise ValueError("pair %d is a self-pair" % index)
        if left in partners and partners[left] != right:
            raise ValueError("pair %d: %s already paired with %s, now with %s"
                             % (index, safe(left), safe(partners[left]), safe(right)))
        if right in partners and partners[right] != left:
            raise ValueError("pair %d: %s already paired with %s, now with %s"
                             % (index, safe(right), safe(partners[right]), safe(left)))
        partners[left] = right
        partners[right] = left
    unknown_overrides = set(overrides) - ids
    if unknown_overrides:
        raise ValueError("override names unknown item id %s" % safe(sorted(unknown_overrides)[0]))
    return done_when, parsed, allowlist, overrides, partners


def lint(path, threshold):
    done_when, items, allowlist, overrides, partners = load_manifest(path)
    done_tokens = normalize(done_when, allowlist)
    done_ngrams = ngrams(done_tokens)
    if len(done_tokens) < 2:
        raise ValueError("done_when is UNLINTABLE: fewer than 2 normalized tokens")

    findings = []
    leaks = 0
    overridden = 0
    for item_id, key, evidence in items:
        evidence_ngrams = ngrams(normalize(evidence, allowlist))
        if not evidence_ngrams:
            raise ValueError("item %s is UNLINTABLE: evidence has fewer than 2 normalized tokens"
                             % safe(item_id))
        ratio = len(evidence_ngrams & done_ngrams) / len(evidence_ngrams)
        ratio_text = "%.2f" % ratio
        leak = ratio >= threshold
        if item_id in overrides:
            if leak:
                overridden += 1
                partner = " pair partner %s" % safe(partners[item_id]) if item_id in partners else ""
                findings.append("OVERRIDDEN %s ratio=%s%s :: %s" %
                                (safe(item_id), ratio_text, partner, safe(overrides[item_id])))
            else:
                findings.append("NOTE override %s does not leak" % safe(item_id))
        elif leak:
            leaks += 1
            partner = " pair partner %s" % safe(partners[item_id]) if item_id in partners else ""
            findings.append("LEAK %s ratio=%s%s" % (safe(item_id), ratio_text, partner))
        else:
            findings.append("ok %s ratio=%s" % (safe(item_id), ratio_text))
    if allowlist:
        findings.insert(0, "NOTE allowlist active: "
                        + ", ".join(sorted(safe(a) for a in allowlist)))
    return len(items), leaks, overridden, findings


def main(argv=None):
    sys.stdout.reconfigure(errors="backslashreplace")
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("manifest")
    ap.add_argument("--threshold", default="0.35",
                    help="minimum evidence n-gram overlap ratio in [0,1] (default 0.35)")
    args = ap.parse_args(argv)
    try:
        threshold = float(args.threshold)
        if not math.isfinite(threshold) or not 0 <= threshold <= 1:
            raise ValueError("threshold must be finite and in [0,1]")
        items, leaks, overridden, findings = lint(args.manifest, threshold)
    except (OSError, ValueError, TypeError) as exc:
        print("RESULT: ERROR (%s)" % safe(str(exc)))
        return 2
    print("SUMMARY items=%d leaks=%d overridden=%d threshold=%s" %
          (items, leaks, overridden, args.threshold))
    for finding in findings:
        print(finding)
    print("RESULT: %s" % ("LEAK" if leaks else "CLEAN"))
    return 1 if leaks else 0


if __name__ == "__main__":
    sys.exit(main())
