"""Shared API-key pool loader — ONE parser for every provider.

Consumers: nimroute.py (NVIDIA_NIM), groqcall.py (GROQ).
Extracted 2026-07-30 from two divergent copies. The divergence was not cosmetic:
nimroute understood three env shapes, groqcall two, opencode.jsonc one — which is
why opencode still drives a single NIM key while nimroute pools three. New
providers get pooling by construction here instead of by remembering to.

Shapes read, in this order, de-duped preserving first appearance:
  <PREFIX>_API_KEYS          comma-separated pool
  <PREFIX>_API_KEY           single
  <PREFIX>_API_KEY_1, _2 ... numbered; stops at the first missing OR empty one

Pooling only raises throughput when the keys belong to SEPARATE provider
organizations — Groq and NIM both meter per-org, so same-org keys share one
bucket. Measure with org_probe.py; never assume the multiplier.

Secrets live in ~/.zshenv (chmod 600) only. Nothing here reads a file inside the
Obsidian vault or any cloud-synced directory, by design.
"""
import json
import os


def pool(prefix, fallback=None):
    """Return the de-duped ordered key list for PREFIX, or raise RuntimeError.

    fallback: optional callable returning a list of keys, consulted only when the
    environment yields none. It may raise; the reason is folded into the error.
    """
    base = f"{prefix}_API_KEY"
    raw = (os.environ.get(base + "S") or "").split(",")
    raw.append(os.environ.get(base) or "")
    i = 1
    while os.environ.get(f"{base}_{i}"):
        raw.append(os.environ[f"{base}_{i}"])
        i += 1

    keys, seen = [], set()
    for k in raw:
        k = k.strip()
        if k and k not in seen:      # same key in two places is ONE bucket
            seen.add(k)
            keys.append(k)

    msg = (f"no {prefix} key: set {base}S in ~/.zshenv "
           "(note: ~/.zshrc is NOT read by non-interactive shells — Claude Code's "
           "Bash tool, cron and launchd all miss it)")
    if not keys and fallback is not None:
        try:
            keys = [k.strip() for k in fallback() if k and k.strip()]
        except Exception as e:
            raise RuntimeError(f"{msg}; fallback also failed: {e}") from e
    if not keys:
        raise RuntimeError(msg)
    return keys


def opencode_auth(provider):
    """Fallback source: opencode's own credential store. Raises if unusable."""
    p = os.path.expanduser("~/.local/share/opencode/auth.json")
    with open(p) as fh:
        return [json.load(fh)[provider]["key"]]
