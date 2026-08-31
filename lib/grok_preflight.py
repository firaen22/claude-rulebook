#!/usr/bin/env python3
"""
grok_preflight — is grok auth actually usable RIGHT NOW?

WHY. grok.com OAuth access tokens live 6h, and the refresh token dies after ~2 days
IDLE; `RefreshTokenRejected` then DELETES ~/.grok/auth.json. The damage is not the
re-login — it is that a dead-auth dispatch is INDISTINGUISHABLE from the model idling:
on v1.0.5 it returns in seconds, rc=0, with "Not signed in..." on stdout, which reads
like a short/empty review and gets misattributed to grok.
    Measured failures: 2026-08-25T03:27:01Z, 2026-08-31T04:57:48Z.
    See ~/.claude/memory/reference_grok_auth_expiry.md

Call this BEFORE any grok bench, fan-out, or review dispatch.

    python3 ~/.claude/lib/grok_preflight.py           # human line + exit code
    python3 ~/.claude/lib/grok_preflight.py --quiet   # exit code only
    python3 ~/.claude/lib/grok_preflight.py --json
    python3 ~/.claude/lib/grok_preflight.py --self-test

Exit: 0 usable · 1 NOT usable (missing/expired/no refresh) · 2 usable but expiring soon.

NEVER prints token values — only expiry times and presence booleans.
"""
import json, os, sys, argparse
from datetime import datetime, timezone
from pathlib import Path

AUTH = Path.home() / ".grok" / "auth.json"
SOON = 30 * 60          # seconds; below this, refresh before a long fan-out
ISSUER_HINT = "auth.x.ai"


def parse_ts(s):
    if not isinstance(s, str):
        return None
    t = s.strip().replace("Z", "+00:00")
    try:
        d = datetime.fromisoformat(t)
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def check(path=None, now=None):
    """-> dict. Pure: `path` and `now` injectable so --self-test drives the real code."""
    path = Path(path) if path else AUTH
    now = now or datetime.now(timezone.utc)

    if os.environ.get("XAI_API_KEY") or os.environ.get("GROK_API_KEY"):
        # An API key does not expire and is checked before the file: with one set, a
        # stale auth.json is irrelevant. (Binary: "run `grok login`, set XAI_API_KEY,
        # or set a model api_key/env_key".)
        return dict(ok=True, state="api-key", detail="XAI_API_KEY/GROK_API_KEY set — no expiry",
                    expires_at=None, seconds_left=None, refresh_token=None)

    if not path.exists():
        # This is the post-rejection state: the CLI DELETES the file, it does not
        # blank it. An absent file means a browser/device re-login is required.
        return dict(ok=False, state="missing", expires_at=None, seconds_left=None,
                    refresh_token=False,
                    detail=f"{path} absent — refresh was rejected or never logged in")
    try:
        data = json.loads(path.read_text())
    except (ValueError, OSError) as e:
        return dict(ok=False, state="unreadable", expires_at=None, seconds_left=None,
                    refresh_token=None, detail=f"cannot parse {path}: {e}")

    # Key shape is "https://auth.x.ai::<uuid>". Scan values rather than hardcoding the
    # uuid, and prefer an auth.x.ai entry if several exist.
    entries = [v for v in data.values() if isinstance(v, dict)] if isinstance(data, dict) else []
    pref = [v for k, v in (data.items() if isinstance(data, dict) else [])
            if isinstance(v, dict) and ISSUER_HINT in str(k)]
    cand = pref or entries
    if not cand:
        return dict(ok=False, state="no-entry", expires_at=None, seconds_left=None,
                    refresh_token=False, detail="no OIDC entry found in auth.json")

    best, best_left = None, None
    for e in cand:
        exp = parse_ts(e.get("expires_at"))
        if exp is None:
            continue
        left = (exp - now).total_seconds()
        if best_left is None or left > best_left:
            best, best_left = e, left
    if best is None:
        return dict(ok=False, state="no-expiry", expires_at=None, seconds_left=None,
                    refresh_token=bool((cand[0] or {}).get("refresh_token")),
                    detail="entry has no parseable expires_at")

    has_refresh = bool(best.get("refresh_token"))
    exp_s = best.get("expires_at")
    if best_left <= 0:
        # Expired is NOT fatal on its own: a live refresh token usually still mints a
        # new access token at launch. It is fatal when the refresh token is gone.
        state = "expired-refreshable" if has_refresh else "expired-dead"
        return dict(ok=has_refresh, state=state, expires_at=exp_s,
                    seconds_left=int(best_left), refresh_token=has_refresh,
                    detail=("access token expired; refresh token present — grok should "
                            "re-mint at launch, but ~2 days idle kills it"
                            if has_refresh else
                            "access token expired AND no refresh token — re-login required"))
    if best_left < SOON:
        return dict(ok=True, state="expiring-soon", expires_at=exp_s,
                    seconds_left=int(best_left), refresh_token=has_refresh,
                    detail=f"only {int(best_left//60)} min left — refresh before a long fan-out")
    return dict(ok=True, state="ok", expires_at=exp_s, seconds_left=int(best_left),
                refresh_token=has_refresh,
                detail=f"{best_left/3600:.1f}h left"
                       + ("" if has_refresh else " — NO refresh token, dies at expiry"))


RECOVERY = ("recover with:  ~/.grok/bin/grok login --device-code   "
            "(headless, no browser dance)")


def self_test():
    """Drive the real check() over fixtures. Traversal is not enough — prove the
    verdicts, since a preflight that never says NO is worse than none."""
    import tempfile
    now = datetime(2026, 8, 31, 12, 0, tzinfo=timezone.utc)
    K = "https://auth.x.ai::b1a00492-073a-47ea-816f-4c329264a828"
    cases = [
        ("live 6h",      {K: {"expires_at": "2026-08-31T16:00:00Z", "refresh_token": "x"}}, True,  "ok"),
        ("20 min left",  {K: {"expires_at": "2026-08-31T12:20:00Z", "refresh_token": "x"}}, True,  "expiring-soon"),
        ("expired+refr", {K: {"expires_at": "2026-08-31T06:00:00Z", "refresh_token": "x"}}, True,  "expired-refreshable"),
        ("expired,dead", {K: {"expires_at": "2026-08-31T06:00:00Z"}},                       False, "expired-dead"),
        ("no expiry",    {K: {"refresh_token": "x"}},                                       False, "no-expiry"),
        ("empty",        {},                                                                False, "no-entry"),
    ]
    fails = 0
    saved = {k: os.environ.pop(k, None) for k in ("XAI_API_KEY", "GROK_API_KEY")}
    try:
        with tempfile.TemporaryDirectory() as td:
            for name, blob, want_ok, want_state in cases:
                p = Path(td) / "a.json"
                p.write_text(json.dumps(blob))
                r = check(path=p, now=now)
                good = (r["ok"] == want_ok and r["state"] == want_state)
                fails += (not good)
                print(f"  {'ok ' if good else 'FAIL'} {name:14s} -> {r['state']:20s} ok={r['ok']}"
                      + ("" if good else f"   WANTED {want_state}/{want_ok}"))
            missing = check(path=Path(td) / "nope.json", now=now)
            good = (missing["state"] == "missing" and not missing["ok"])
            fails += (not good)
            print(f"  {'ok ' if good else 'FAIL'} {'deleted file':14s} -> {missing['state']}")
        os.environ["XAI_API_KEY"] = "dummy-not-a-real-key"
        r = check(path=Path(td) / "nope.json", now=now)
        good = r["ok"] and r["state"] == "api-key"
        fails += (not good)
        print(f"  {'ok ' if good else 'FAIL'} {'api-key wins':14s} -> {r['state']}")
    finally:
        os.environ.pop("XAI_API_KEY", None)
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v
    print("SELF-TEST PASS" if not fails else f"SELF-TEST FAILED ({fails})")
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true", help="exit code only")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(self_test())

    r = check()
    if a.json:
        print(json.dumps(r, indent=2))
    elif not a.quiet:
        tag = {"ok": "GROK AUTH OK", "api-key": "GROK AUTH OK (api key)",
               "expiring-soon": "GROK AUTH EXPIRING SOON"}.get(r["state"], "GROK AUTH NOT USABLE")
        print(f"{tag}: {r['detail']}")
        if r["expires_at"]:
            print(f"  expires_at {r['expires_at']}  refresh_token={r['refresh_token']}")
        if not r["ok"]:
            print(f"  {RECOVERY}")
            print("  a dead-auth dispatch returns rc=0 + 'Not signed in' — do NOT read "
                  "that as an empty model result")
    sys.exit(0 if r["ok"] and r["state"] != "expiring-soon" else (2 if r["ok"] else 1))


if __name__ == "__main__":
    main()
