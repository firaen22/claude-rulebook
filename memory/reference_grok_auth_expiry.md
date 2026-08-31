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
⚠️ **Correction to my own first draft of this file:** I wrote that missing `auth.json`
causes a "silent hang". The playbook's own measured 2026-08-29 note says otherwise for
**v1.0.5** — it returns in SECONDS, rc=0, with `Not signed in. To authenticate without a
browser, run: grok login --device-code` on stdout. Read the output before diagnosing:
rc=0 plus a ~383-byte "report" is an auth failure, not a review.
The live risk is therefore **misreading a cheap rc=0 auth failure as a real (empty)
result** — not a hang. Before any grok bench or fan-out, check `expires_at` in
`~/.grok/auth.json`; stale auth otherwise gets misattributed to the model.
Current state: logged in via grok.com; `XAI_API_KEY` and `GROK_API_KEY` both **unset**,
so the CLI has no key fallback — when OAuth dies, everything dies.
Account on the OIDC entry is a different gmail from the primary user email.

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

## 4. Standing constraint
User said **paused — do not add, edit, or remove the agent unless they say so.**
Nothing was installed, changed, or removed. If keep-alive is wanted later, note its
real limit: a Mac powered off for a weekend cannot run the job, so Monday login is still
possible. Only a console.x.ai **API key** (separate login/billing, and it requires
`grok logout`) actually never expires — the user has NOT asked for that.

## What would change this
- A `grok` build that changes the 6h TTL or stops deleting `auth.json` on rejection.
- Vendor docs catching up (or this machine turning out to be the outlier — N=1 machine,
  2 observed failures).
