---
name: reference-groq-direct-api
description: "Groq direct-API playbook: the verified transport recipe (UA rule, key resolution, both rate buckets, per-model limits), tool-call emission as a separate axis from the battery, why pooling keys needs an org-independence probe first, why Groq is agent-excluded in opencode, and a §5 pre-flight checklist for handing Groq a subordinate task. Current-state orders; evidence lives in finding-groq-transport-2026-07-30."
metadata:
  node_type: memory
  type: reference
---

# Groq via direct API — playbook

> ## ⛔ SUSPENDED 2026-07-30 — DO NOT CALL GROQ
> Every Groq request from this machine returns **HTTP 403** —
> `{"error":{"message":"Access denied. Please check your network settings."}}`.
> **Cause: NordVPN.** Default route is `utun5`, egress IP 187.15.122.97 (Brazil);
> Groq blocks VPN/datacenter ranges. **MEASURED, not inferred (N=6):** all 4 pooled
> keys 403 — AND SO DOES a deliberately invalid key AND a request with NO
> `Authorization` header at all, same status, same body. A server that read the key
> would answer 401 to those two. So the reject is **pre-auth / network-level**:
> rotating keys, adding keys, or fixing the client cannot help, and no client-side
> setting can influence it. Also: raw `curl` bypassing `groqcall.py` gets the same
> 403, while NIM=200, GitHub=200, OpenAI=401 (reached, unauthed) on the same route.
> NordVPN started 16:37; the last successful Groq calls were ~14:15 the same day.
>
> ⚠️ Method note: the first version of this diagnosis tested key[0] only and
> generalized — the "baseline-vs-all is not pairwise" error from
> [[finding-test-validity-failure-modes]]. The **invalid-key and no-auth controls**
> are what actually prove pre-auth rejection; the 4-key sweep alone would not.
>
> **Use NIM instead** — it works through the VPN unchanged
> ([[reference-nim-via-opencode]], `nimroute.py`).
>
> **To re-enable:** disconnect NordVPN, then verify with the one-liner in §5. If it
> returns `ok=True`, delete this banner — everything below was measured and stays
> valid; the block is purely network-level, so no finding here is retracted.


Current-state orders only. Evidence, N, and retractions live in
[[finding-groq-transport-2026-07-30]] and [[finding_groq_bench_2026-07-29]].
**Client: `~/.claude/lib/groqcall.py`** (moved there 2026-07-30 from the experiments dir,
next to `keypool.py` — it is a durable tool, not scratch; `accept.py` 30/30 before AND
after the move, and `~/.claude/lib/` is the only copy on disk). Consumers add
`sys.path.insert(0, os.path.expanduser("~/.claude/lib"))`.
Harness stays in `claude code technique/experiments/groq-transport-2026-07-30/`
(`accept.py` 30/30, `org_probe.py`, `limits.py`, `bench_gap.py`).
⚠️ `~/.claude/lib/` is mirrored VERBATIM into the Obsidian/Drive vault by
`sync-to-obsidian.sh`, so **never inline a key into this client** — it reads them via
`keypool`. The sync credential guard covers `lib` and is fail-closed.

**There is NO Groq CLI on this machine — none.** No `groq` binary, no `groq-code-cli`
(evaluated 2026-07-30 and REJECTED, never installed — [[decision-groq-code-cli-rejected]]),
and no agentic client can work on this tier (preamble > per-request ceiling, see §3).
If you are about to type `groq ...` in a shell, stop: the ONLY entrypoint is
`~/.claude/lib/groqcall.py` (`from groqcall import Groq`).

**Use Groq by direct API only.** It is agent-EXCLUDED in opencode — opencode's
preamble is ~32k tokens even with all 13 tools off, against a 12,000 TPM ceiling;
`groq/compound` has 70k TPM but returns HTTP 400 "tool calling is not supported".
See [[workflow-opencode-subordinate]].

## 1. Transport — do these four things
0. **A second 403 class exists: network-level block.** 2026-08-03: `{"error":{"message":"Access denied. Please check your network settings."}}` — HTTP 403 on EVERY call including a PONG, via groqcall.py with the UA rule already applied, attempts=1 (no rotation reached). This is not the UA-1010 ban and not key-related; it is Groq/Cloudflare rejecting the client network (VPN/geo class). Diagnose with a tiny PONG probe: same 403 on trivial + real prompts = network block → route the work to NIM direct API instead of retrying Groq that session.
1. **Set an explicit `User-Agent`.** Cloudflare returns 403 `error code: 1010` for the
   literal `Python-urllib/3.x` UA. Any other value works, including `""`.
   `python-requests/*` and `python-httpx/*` defaults are NOT banned — so this bites
   only raw `urllib`. Use `curl/8.7.1`.
2. **Resolve the key with a fallback.** Historically `GROQ_API_KEY` lived in
   `~/.zshrc`, which zsh sources for INTERACTIVE shells only — UNSET under
   `zsh -c`, `zsh -lc`, `sh -c`, so in every cron job, launchd job, and hook.
   Since 2026-07-30 all keys live in `~/.zshenv` (`GROQ_API_KEYS` pool; the
   single `GROQ_API_KEY` export is gone entirely). Keep the fallback anyway:
   a fresh machine has auth.json before it has a populated ~/.zshenv.
   Read `GROQ_API_KEYS` / `GROQ_API_KEY` / `GROQ_API_KEY_1/_2/…` (numbered shape
   added 2026-07-30), then fall back to
   `~/.local/share/opencode/auth.json` -> `groq.key`.
   Parsing lives in `~/.claude/lib/keypool.py` (shared with nimroute.py since
   2026-07-30) — fix resolution bugs THERE, not in groqcall.py.
   To fix globally, put the export in `~/.zshenv`, not `~/.zshrc`.
3. **`stream` is a free choice.** 10/10 either way. Do NOT port NIM's
   "always stream" habit here — on NIM that revived 4 apparently-dead models; on
   Groq it changes nothing (including token accounting).
4. **Keep `max_completion_tokens` tight** — cheap insurance, see §3.

## 2. Model routing + limits — BOTH buckets, per model, per ORGANIZATION
Limits read from live response headers 2026-07-30 (`limits.py`), NOT from docs —
re-run it rather than trusting this table after a few weeks. Scores are the frozen
3-task battery; evidence in [[finding-groq-model-routing-2026-07-30]].

| model | TPM ×4 keys | req/day ×4 | battery | route to it when |
|---|---|---|---|---|
| `llama-3.3-70b-versatile` | **48,000** | 4,000 | **30/30/20/29, N=4 — NOT stable parity** | big payloads only when edges are specced; no longer an unconditional default, see below |
| `openai/gpt-oss-120b` | 32,000 | 4,000 | **30/30, real N=4** | **new default** for correctness-sensitive work; clean `reasoning` split |
| `openai/gpt-oss-20b` | 32,000 | 4,000 | 30/30 **3 of 4** | fallback when 70b/120b are rate-limited — not correctness-interchangeable, see below |
| `llama-3.1-8b-instant` | 24,000 | **57,600** | **26–27/30, N=4** | ONLY option >4,000 calls/day — see warning |
| `qwen/qwen3.6-27b` | 32,000 | 4,000 | **30/30, real N=4** | correctness-sensitive alt to 120b; audit output for `<think>` leaking into `content` on unlike tasks |

**Every model is 1,000 req/day per key except `llama-3.1-8b-instant` at 14,400 — and
that one is the only sub-parity model.** The sharp trade-off: the only large request
budget on the tier is also the only unreliable model.

⚠️ **`llama-3.1-8b-instant` fails specifically on EDGE cases**, not uniformly, and the
failures are **reproducible rather than noisy** — N=4, scores 27/27/26/26, never 30.
`T1_chunk` (happy path) 10/10 in 4/4; the SAME three `T2_parseqs` checks fail in 4/4
runs (`empty`, bare `?`, `+`→space) plus `PRESENT null returned` in 2/4. Use it only
where edge behavior is specced explicitly in the prompt or verified downstream — never
correctness-critical single-shot work. This is the silent-wrong-answer class, but a
*predictable* one, so spec those cases and it is usable.

⚠️ **N=1 parity is not parity — proved twice now.** `openai/gpt-oss-20b` scored 30/30
on its first run, then **20/30 on run 3 of 4** (`TypeError` on a nested-null path).
`llama-3.3-70b-versatile` looked like the safest model of all five (30/30, no thinking
step) and at real N=4 scored **30/30/20/29**: a hard crash on an invalid self-emitted
regex (`/^?\s*/`, `SyntaxError: Nothing to repeat`) plus an edge miss on the same
"PRESENT null returned" check that also costs the 8b model. All 5 Groq free-tier
models now have real N=4 data; only `openai/gpt-oss-120b` and `qwen/qwen3.6-27b` came
back clean 4/4. **No model on this tier should be assumed an unconditional-correctness
default** — spec edge cases regardless of which model is routed to. Each `bench_gap.py`
run persists its own timestamped file, so replication is cheap — do it before trusting
any parity claim, including this one.

⚠️ **Tool-call emission is a SEPARATE axis from the battery — check it before any
tool-using delegation.** N=6/model, 3 prompts ×2, measured 2026-07-30:
`openai/gpt-oss-120b` **6/6** valid `tool_calls`; `qwen/qwen3.6-27b` 4/4 then rate-limited;
`llama-3.3-70b-versatile` **2/6** — the other 4 hard-failed HTTP 400 `tool_use_failed`,
emitting Llama-style `<function=name>{…}` as plain text instead of the API structure.
**For a subordinate that is a dead turn, not a degraded answer.** The frozen 3-task
battery never tested this and cannot: it discriminates exactly where the battery
saturates, and it independently corroborates the 70b retraction above from a second
unrelated harness. If a Groq call needs tools, use `gpt-oss-120b`.

⚠️ **A reasoning model + small `max_tokens` returns `ok=True` with EMPTY content.**
Measured 2026-07-30: `openai/gpt-oss-120b` on "Reply with exactly: PONG" gives
`content=''` at `max_tokens=16` and `'PONG'` at 300 — it spends the budget on
`reasoning` first. `llama-3.3-70b-versatile` returns `'PONG'` at both. **Status 200,
`ok` true, nothing usable** — silent success, so a caller that only checks `ok` sees a
pass. Give `120b`/`qwen3.6-27b` `max_tokens >= ~300`, or check `content` non-empty.
This is why `DEFAULT_MODEL` in `groqcall.py` is the *predictable* 70b and NOT the
higher-scoring 120b: a transport client must not silently pick a correctness/verbosity
tradeoff for the caller. Correctness-sensitive work passes `model=` **explicitly**.

Also: many tiny calls exhaust the **1,000/day request bucket** long before the token
bucket. Groq is not "TPM-only" — that earlier claim is retracted.

The four 30/30 models **cannot be ranked against each other** by this battery (3 tasks,
saturated above the 8b tier). Choose among them by TPM and reasoning-split, not quality.

## 3. Token accounting is NOT predictable — pace belt-and-braces
Two regimes observed from identical code ~40 min apart: one debits
`max_completion_tokens + prompt` (429 after 4 calls), the other debits ~104 flat
regardless of `max_completion_tokens` (12 calls at up to 4800 against a 6000 bucket,
no 429). `stream` was tested and FALSIFIED as the cause. **Trigger unknown.**

So a client must do BOTH:
- refuse a call the advertised `x-ratelimit-remaining-tokens` cannot cover, AND
- honour `retry-after` on a 429 that arrives anyway.

Purely predictive needlessly throttles in the actual-usage regime; purely reactive
eats avoidable 429s in the reservation regime.

**Parse `x-ratelimit-reset-*` with `ms` matched BEFORE `m`.** Groq emits `220ms` and
`285ms`; a naive scan reads 220 *minutes*. This silently over-waits and never errors.

### The per-request ceiling EQUALS TPM — pooling cannot raise it (measured 2026-07-30)
A single request larger than one key's TPM fails **HTTP 413 "Request too large … on
tokens per minute (TPM)"**, and it fails on a *fresh, undrained* key. Verified with each
probe on a different key: `gpt-oss-120b` OK at 5,072 tok, **413 at ~9,000** (ceiling
8,000); `llama-3.3-70b` OK at 9,036, **413 at ~14,000** (ceiling 12,000) — and the two
413s came back from two DIFFERENT `org_…` ids, so this is not a drained bucket.

**Consequence: key pooling buys requests-per-minute, NOT context size.** One request goes
to one key, so max usable context per call is that model's TPM, pool or no pool — 8,000
on `gpt-oss-120b`, 12,000 on `70b`. This is a hard cap on anything that accumulates
context (agent loops, long histories, big file reads); do not try to fix a 413 by
rotating keys. `bench_gap.py` already encodes the rotation half of this rule; these are
the numbers behind it. See [[decision-groq-code-cli-rejected]] for the case it killed.

### Four pacing bugs review caught 2026-07-30 — the shapes, not just the fixes
All four were in `groqcall.py`, all shipped green under a 24-check suite, all fixed
and now regression-tested (`accept.py` T7–T10, 30/30):
1. **A 5xx is not a drained bucket.** Treating a transient 500 as "rotate to the next
   key" meant a single-key client fell through to the all-drained wait and paid ~61s
   for one server error (measured). Retry the SAME key on 5xx.
2. **Absorb-then-setdefault makes the vendor's header dead code.** A generic
   "read all rate headers" step ran first and set the wait from
   `x-ratelimit-reset-tokens`, so the later `retry-after` branch could never fire —
   the docstring claimed a guard the code did not have. Order matters: let the 429
   handler override.
3. **Store refill times as ABSOLUTE deadlines, never durations.** A `44s` absorbed
   minutes earlier was still slept in full.
4. **Never sleep on the last retry round** — that nap is followed only by `return`.

Also: `dict(HTTPMessage)` preserves the WIRE case while every lookup here is
lower-case, so lower-case the header dict at the transport boundary or one CDN change
makes the client silently go blind.

## 4. Key pooling — CONFIRMED real, 2026-07-30
Rate limits bind on the **organization**, not the key (the 429 body says so:
`...in organization org_... service tier on_demand`). Keys from ONE account share a
single bucket — pooling them would buy zero throughput while every call still
succeeds, a no-op that looks like a win. **Measured, not assumed:** 4 distinct keys
now live in `GROQ_API_KEYS` (`~/.zshenv`); `org_probe.py` drains each key in turn and
compares **every pair** on `llama-3.1-8b-instant`. All 6 pairs cleared the 1500-token
threshold (gaps 2335–2675). **4 keys = 4 distinct orgs. Effective ceiling for that
model: 24,000 TPM (4x).**

⚠️ **Probe design rule, learned the hard way here:** draining only key[0] and
comparing every other key against it does **not** establish pooling. It proves each
key is outside key[0]'s org while saying nothing about whether keys 1..n share an org
with EACH OTHER — and the tiny read call cannot tell the difference, because a
~110-token debit is masked by ~100 tok/s of refill over the sleep plus latency, so a
shared pool reads back near-identical too. The first run made exactly this mistake and
over-claimed 4x from evidence that only supported 2x. The conclusion happened to
survive re-measurement, which is luck, not method. **Baseline-vs-all is not pairwise;
independence needs every pair.** Old flawed output kept as
`results_org_probe_key0only_FLAWED.json`.

`groqcall.Groq()` defaults to the whole pool and
rotates to a fresh key on 429 **without sleeping**, only pausing once every key is
drained (verified both offline against a stubbed transport and live via
`org_probe.py`).

**Adding a 5th key later:** append to the SAME `GROQ_API_KEYS` line, do not add a
new `export` line — 3 separate `export GROQ_API_KEYS=` lines in `.zshenv` clobber to
the LAST one, silently discarding the earlier keys (hit this exact bug 2026-07-30,
fixed by `consolidate_keys.py`, one-time). Then **re-run `org_probe.py`** — it must
be re-proven per key, not assumed, in case the new key shares an org with an existing
one. The probe is pairwise, so it re-verifies the whole pool, not just the addition:
```bash
python3 "experiments/groq-transport-2026-07-30/org_probe.py"
```

## 5. Using Groq AS A SUBORDINATE — the pre-flight checklist
Sections above are the mechanism; this is the order to check them in before handing
Groq a task. Ranked by how likely each is to bite.

1. **Does the task accumulate context?** (agent loop, long history, whole-file reads)
   → **do not use Groq at all.** Per-request ceiling == TPM, 8–12k, and pooling cannot
   raise it (§3). Route to codex, or opencode+NIM. This is not a tuning problem.
2. **Does it need tools?** → `openai/gpt-oss-120b` only. 70b fails 2/6 (§2).
3. **Is a wrong answer costly?** → spec edge behavior EXPLICITLY in the prompt. No model
   on this tier is a safe unconditional default (§2); 4 of 5 show sub-30/30 at N=4.
4. **Is the payload near the ceiling?** → keep the request under ~6k tokens. Above that
   you are betting on which token-accounting regime is live (§3), which is not
   predictable.
5. **Many small calls?** → check the **request/day** bucket, not TPM: 1,000/key
   (4,000 pooled) for everything except `8b-instant` (§2). That bucket runs out first.
6. **Parsing the output?** → `qwen3.6-27b` can leak `<think>` into `content` on Groq
   (no reasoning field); `gpt-oss-120b` splits cleanly.
7. **Wrote a new client instead of using `groqcall.py`?** → don't. It already encodes
   the UA rule, `ms`-before-`m` parsing, retry-same-key-on-5xx, absolute deadlines, and
   both pacing halves (§1, §3). Four of those were bugs that shipped green under a
   24-check suite.

Verdict-shaped default: **`openai/gpt-oss-120b`, edges specced, request under ~6k, no
accumulated context.** Anything outside that envelope is a different subordinate's job.

## §6 OUTAGE NOTE 2026-08-04
Blanket HTTP 403 `{"error":{"message":"Access denied. Please check your network settings."}}`
on ALL 4 keys (all 4 orgs), reproduced via both groqcall.py and raw curl with correct UA.
Not rate-limiting, not the urllib UA ban — a network/IP-or-region-level block (user is
Taiwan-based). Before next Groq use: re-probe with one cheap curl; if still 403, route the
work to NIM or agy instead of debugging the transport.
