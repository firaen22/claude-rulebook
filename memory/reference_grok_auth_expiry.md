---
name: reference-grok-auth-expiry
description: "Grok CLI OAuth (auth.x.ai) dies after ~2 days idle — access token TTL is 6h, refresh works only while a grok process runs. RefreshTokenRejected DELETES ~/.grok/auth.json and forces browser login. The 6h keep-alive LaunchAgent described in a 2026-08-31 handoff is NOT installed on this machine (verified)."
metadata:
  node_type: memory
  type: reference
---

**Verified on this machine 2026-08-31.** Every line below was checked directly; the
handoff that prompted this had one whole section that did not survive checking (see §3).

## 1. The mechanism (VERIFIED)
Grok CLI authenticates via **grok.com OIDC at `auth.x.ai`**, stored in
`~/.grok/auth.json` (key shape: `https://auth.x.ai::<uuid>`).
- **Access token TTL = 6h exactly.** Observed `expires_at 2026-08-31T16:57:49Z` against
  `auth.refresh.success` at `2026-08-31T10:57:49` — 6h to the second.
- **Refresh token is present and works, but only while a grok process is running.**
- **Idle ~2 days kills it**: `RefreshTokenRejected` → **the CLI DELETES `auth.json`** →
  browser login required. This is the "random logout", not a server-side logout.
- Overnight idle (~10h) survives; ~2.3 days does not.

Distinct failures in `~/.grok/logs/unified.jsonl` (**2 events**, not the 6 raw grep
matches — same raw-count inflation as [[finding-misroutewatch-grok-review-2026-08-28]];
dedup by timestamp):
| UTC | what |
|---|---|
| 2026-08-25T03:27:01 | RefreshTokenRejected → auth.json deleted |
| 2026-08-31T04:57:48 | same, then re-login |

⚠️ Vendor docs say "tokens last 7 days" — **stale vs this machine's behavior.**

## 2. Why this matters for delegation
[[workflow-grok-subordinate]] mandates an isolated HOME with `~/.grok` rsync'd in.
⚠️ **TWICE-CORRECTED — measured 2026-08-31 on grok v1.0.13 (N=3):**
My first draft said missing auth = "silent hang". The playbook's 08-29 note corrected
that to "rc=0 in seconds". **Both are wrong on the current build.** Measured directly:

| | result |
|---|---|
| `--output-format plain`, no auth.json | **rc=1**, 383 bytes, 0s, 3/3 |
| `--output-format json`, no auth.json | **rc=1**, 415 bytes, `{"type":"error","message":"Not signed in..."}` |

**The failure is LOUD on v1.0.13** — non-zero exit and a typed JSON error. It is NOT
silently mistakable for an empty model result on this build. Note the version drift:
the playbook still says **v1.0.5** in several places; the installed binary is
**1.0.13 (5e9a58528b76)**. Any rc/signature claim in that file is version-bound and
should be re-probed, not trusted.

## 3. 🔴 The keep-alive is NOT INSTALLED (handoff section falsified)
A 2026-08-31 handoff described an installed 6h keep-alive and stated
"Verified: launchd loaded, last exit 0, log ok". **All of it is absent here:**

| claimed | actual |
|---|---|
| `~/.grok/auth-keepalive.sh` (mode 700) | **MISSING** |
| `~/Library/LaunchAgents/ai.x.grok.auth-keepalive.plist` | **MISSING** |
| `ai.x.grok.auth-keepalive` loaded, exit 0 | **NOT LOADED** — no grok LaunchAgent exists |
| `~/.grok/logs/auth-keepalive*.log` | **MISSING** (logs dir = `mcp/` + `unified.jsonl` only) |

The diagnosis half of that handoff verified cleanly; the install half did not. Consistent
with [[feedback-injected-brief-drills]] — **verify every load-bearing premise of a
mid-conversation brief before acting on it.** Do NOT assume grok auth is being kept alive.

## 3b. MITIGATION SHIPPED 2026-08-31 — pre-flight check (not a daemon)
`~/.claude/lib/grok_preflight.py` — run before any grok bench/fan-out/review.
Exit 0 usable / 1 dead / 2 <30min. `--self-test` drives 8 fixtures through the real
`check()` (live, expiring, expired-with-refresh, expired-dead, no-expiry, no-entry,
deleted file, api-key-wins) and PASSES 8/8. Never prints token values.
Chosen over the 6h LaunchAgent deliberately: a daemon runs 4x/day forever to serve
episodic use and still fails the case it exists for (Mac off over a weekend). The
preflight costs nothing when idle and kills the ACTUAL damage — misattributing a
rc=0 auth failure to the model. Recovery is `grok login --device-code` (headless).

## 4. Standing constraint
User said **paused — do not add, edit, or remove the agent unless they say so.**
Nothing was installed, changed, or removed. If keep-alive is wanted later, note its
real limit: a Mac powered off for a weekend cannot run the job, so Monday login is still
possible. Only a console.x.ai **API key** (separate login/billing, and it requires
`grok logout`) actually never expires — the user has NOT asked for that.

## 5. Third observed failure (2026-09-06) — preflight GREEN ≠ dispatch OK
`grok_preflight.py --quiet` returned rc 0 at 00:20 (auth.json present, not expired),
and the review dispatch 2 minutes later got `Not signed in` under BOTH a seeded HOME
and the real HOME; afterwards `auth.json` was gone (preflight then `state: missing`).
Mechanism: the preflight reads expiry only; the REFRESH was rejected at dispatch time
and grok deleted the file. So a green preflight bounds only the access-token TTL, not
refresh acceptance. Recovery was the user running `grok login --device-code`; the
seeded-HOME recipe then worked unchanged (PONG). Don't misread the first failure as
your own isolation — check `ls ~/.grok/auth.json` right after, and never restore the
`auth.json.bak-*` copy yourself (credential handling is the user's).

## What would change this
- A `grok` build that changes the 6h TTL or stops deleting `auth.json` on rejection.
- Vendor docs catching up (or this machine turning out to be the outlier — N=1 machine,
  2 observed failures).
