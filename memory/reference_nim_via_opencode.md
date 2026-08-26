---
name: reference-nim-via-opencode
description: "How NVIDIA NIM is wired as a subordinate (model backend behind opencode, not a standalone agent CLI) + benchmarked model picks, IDs, and the catalog-lies/probe gotcha. Full-catalog sweep 08-25: 95 ids, 33 LIVE, 55 dead-404 (new refusal shape), 4 unresolved XPORT-persist"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 9d9ceaff-475d-47a4-871b-5bc9ce1b2498
---

## CURRENT STATUS (as of 2026-08-25) — read this before any dated section below

The sections below are an append-only log; the same model can carry 3-4 superseded verdicts
across dates (e.g. glm-5.2 went 30/30-in-chain → SSE-DEAD → outage-probed → 410 EOL over
five entries). For the ids listed here, this table is the only place to check CURRENT status —
do not trust the first mention you scroll to. **Update 08-25: coverage is no longer limited
to these 8 — the full 95-id catalog was live-probed the same day, see the FULL CATALOG SWEEP
section below.** Any id not appearing in either this table or that section's LIVE list was
not probed and should still be re-probed before routing.

**ALL ROWS BELOW ARE LIVE-PROBE VERIFIED 2026-08-25** (direct curl PONG to
`/v1/chat/completions`, ≤4 retries on 529/transport). They are NOT summaries of the
prose below — where a dated entry disagrees, the probe wins.

| Model | Status | Notes |
|---|---|---|
| `nvidia/nemotron-3-ultra-550b-a55b` | ✅ LIVE (200, PONG) | parsing/dp primary (replaces deepseek-v4-pro) |
| `deepseek-ai/deepseek-v4-flash-0731` | ✅ LIVE (200, PONG) | the `-0731` suffix is load-bearing — bare `deepseek-v4-flash` is 410 |
| `z-ai/glm-5.2` | ⛔ 410 EOL | do not route; not a throttle, do not key-rotate around it |
| `deepseek-ai/deepseek-v4-flash` | ⛔ 410 EOL | suffixless id is dead; use `-0731` |
| `deepseek-ai/deepseek-v4-pro` | ⛔ 410 EOL | removed from PARITY + as parsing/dp primary |
| `mistralai/mistral-small-4-119b-2603` | ⛔ 410 EOL | see L23 default-workhorses caveat |
| `qwen/qwen3-next-80b-a3b-instruct` | ⛔ 410 EOL | ditto |
| `thinkingmachines/inkling` | ⛔ 410 EOL | ⚠️ RETRACTS the dated "OK 6.7s / stays in PARITY" entries below — 410 as of the 08-25 probe; drop from PARITY |
| `meta/llama-4-maverick-17b-128e-instruct` | ⛔ 410 EOL | ⚠️ RETRACTS the "direct-curl still works" claim below — the direct-curl path is gone too, not just the opencode agent layer |

> **529 is a THIRD refusal shape** (alongside 410-EOL and 429-throttle): `{"code":529,
> "type":"Overloaded"}` is TRANSIENT — `deepseek-v4-flash-0731` returned 529 on attempt 1
> and 200/PONG on retry. Never record a 529 as dead; retry ≥3× with backoff first.
> Corollary to the PAID≠DEAD≠INCAPABLE rule in [[reference-subordinate-routing-map]].
>
> **Method warning (learned the hard way 2026-08-25):** the first version of this table
> was written by READING the append-only log below and picking the most recent mention
> per model. Two of eight rows were wrong (inkling, llama-4-maverick — both actually
> 410). A reconciliation table built from prose inherits the prose's rot. **Re-probe,
> don't re-read** — the probe script takes ~30s.

### FULL CATALOG SWEEP (2026-08-25) — every id in `/v1/models`, not just the 8 above

Catalog size: **95 ids** (down from 102 at the 08-07 refresh — 7 more removed from
listing entirely; this is separate from the 410-but-still-listed EOL ids above).
Live-probed all 95 (PONG to `/v1/chat/completions`, retried on transient shapes —
see below). Two-worker parallel sweep, cross-checked for zero coverage gaps, then a
second sanity-check retry pass on every ambiguous result before recording anything.

| Result | Count | Meaning |
|---|---|---|
| **404** | 55 | listed in the catalog but **no backing serving function exists** — a NEW refusal shape, distinct from 410-EOL (410 = existed, retired; 404 here = catalog entry with nothing behind it). Same operational meaning as 410: do not route. |
| **LIVE** | 33 | confirmed PONG, see full id list below |
| **XPORT-persist** | 4 | `RemoteDisconnected` on the ORIGINAL sweep attempt AND on a dedicated retry — genuinely unroutable right now, not proven dead (410/404), just currently broken transport. Re-probe again before using; don't route today. |
| **500** | 1 | `nvidia/ai-synthetic-video-detector` — internal server error both attempts. Not a coding model regardless; low priority. |
| **400** | 1 | `nvidia/nemotron-parse` — **not a status result, a probe-format mismatch**: it rejects plain-text chat content ("Content cannot be a plain string... does not support text input"). Likely alive but needs a structured/multimodal payload our PONG probe doesn't send — don't record this as dead, the probe is wrong for this model. |

**The 4 XPORT-persist ids (confirmed broken on 2 independent attempts each, do not
route until re-verified):** `meta/llama-3.2-1b-instruct`, `meta/llama-guard-4-12b`,
`nvidia/llama-3.1-nemoguard-8b-topic-control`, `nvidia/llama-3.1-nemotron-nano-8b-v1`.

**33 confirmed LIVE ids** (includes the two headline rows in the table above —
`nemotron-3-ultra-550b-a55b` and `deepseek-v4-flash-0731` — both of which threw a
transient error (503, XPORT) on the FIRST sweep pass and came back clean LIVE on
retry, reconfirming the 529-is-transient lesson generalizes to 503/XPORT too):
`deepseek-ai/deepseek-v4-flash-0731`, `google/diffusiongemma-26b-a4b-it`,
`google/gemma-4-31b-it`, `meta/llama-3.1-70b-instruct`, `meta/llama-3.1-8b-instruct`,
`meta/llama-3.2-11b-vision-instruct`, `meta/llama-3.2-3b-instruct`,
`meta/llama-3.2-90b-vision-instruct`, `meta/llama-3.3-70b-instruct`,
`meta/muse-glimmer-30b`, `minimaxai/minimax-m3`, `mistralai/mistral-nemotron`,
`moonshotai/kimi-k3`, `nvidia/ising-calibration-1.5-31b`,
`nvidia/llama-3.1-nemoguard-8b-content-safety`,
`nvidia/llama-3.1-nemotron-nano-vl-8b-v1`,
`nvidia/llama-3.1-nemotron-safety-guard-8b-v3`,
`nvidia/llama-3.3-nemotron-super-49b-v1`, `nvidia/nemotron-3-nano-30b-a3b`,
`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`,
`nvidia/nemotron-3-super-120b-a12b`, `nvidia/nemotron-3-ultra-550b-a55b`,
`nvidia/nemotron-3.5-content-safety`, `nvidia/nemotron-3.5-lightning-30b-a3b`,
`nvidia/nemotron-mini-4b-instruct`, `nvidia/nemotron-nano-12b-v2-vl`,
`nvidia/nvidia-nemotron-nano-9b-v2`, `nvidia/riva-translate-4b-instruct-v1.1`,
`nvidia/riva-translate-4b-instruct-v2`, `openai/gpt-oss-120b`, `openai/gpt-oss-20b`,
`poolside/laguna-xs-2.1`, `stepfun-ai/step-3.7-flash`.

One id needs a flag rather than a clean verdict: **`nvidia/llama-3.3-nemotron-super-49b-v1.5`**
(note the `.5` — distinct from the plain `-v1` id above, which IS clean LIVE) returned
an empty-but-200 response on the first pass and `RemoteDisconnected` on the retry with
a bigger token budget. One data point each way isn't enough to call it either way —
treat as probably-live-but-flaky-transport, re-probe with ≥3 attempts before routing
anything that depends on it.

**Corollary to the 529-transient rule:** 503 and XPORT-level transport errors
(`RemoteDisconnected`) are ALSO transient shapes on this endpoint, not just 529 —
confirmed via retry on `deepseek-v4-flash-0731` (XPORT→LIVE) and `nemotron-3-ultra-550b-a55b`
(503→LIVE) same day. The 4 XPORT-persist ids above are the counter-case: they did NOT
clear on a second attempt, so persistence-across-≥2-tries is what actually
distinguishes "genuinely broken right now" from "noise" — a single failure of any
shape (410/404/429/503/529/XPORT) is never enough to write a dead verdict into memory.

NVIDIA NIM is a model-serving microservice, NOT a coding agent. The `nim` CLI only manages local NIM containers (list/run/status/logs/stop/benchmark), needs x86 + NVIDIA GPU + Docker, and can't run on this Apple-Silicon Mac. So "NIM as a subordinate" = a NIM-served model used as a **backend behind opencode** (which supplies the agent/file-edit/tool-use layer). See [[workflow-opencode-subordinate]].

Setup done 2026-06-19 (hosted path):
- Endpoint: `https://integrate.api.nvidia.com/v1` (OpenAI-compatible, no GPU needed).
- Key: `NVIDIA_NIM_API_KEY` exported in `~/.zshenv` (moved from `~/.zshrc` so non-interactive shells — Bash tool, cron, launchd — see it).
- Provider block in `~/.config/opencode/opencode.jsonc` (id `nvidia`, npm `@ai-sdk/openai-compatible`, apiKey `{env:NVIDIA_NIM_API_KEY}`).

GOTCHAS:
- **Model ID format is double-segmented**: `nvidia/<vendor>/<model>`, e.g. `opencode run -m nvidia/deepseek-ai/deepseek-v4-flash-0731`. Provider id is `nvidia`; the model id itself contains a slash. opencode's display sometimes munges dots→underscores inconsistently (`glm-5.1` keeps the dot, `llama-3.1`→`llama-3_1`); the canonical dotted NIM id worked in `-m` tests. Confirm exact strings via `opencode models | grep nvidia`.
- **Catalog LIES — probe, don't trust the list.** opencode auto-discovers ~84 `nvidia/*` entries from `/v1/models`, but that includes image/embed/rerank models AND ~31 download-only containers that return **404**. Only **~38 are actually callable** for text. The config `models` block only sets display names, doesn't restrict usability.
- **List the live catalog** (definitive, hosted): `curl -s https://integrate.api.nvidia.com/v1/models -H "Authorization: Bearer $NVIDIA_NIM_API_KEY"` → `.data[].id`. **Callability ≠ listing** — a model can be listed yet 404 on use, and (rarely) vice-versa; confirm a specific id with a 3-token `POST /v1/chat/completions` PONG probe (404 = not served, not an auth/quota error).

**BENCHMARKED PICKS (2026-06-20, adversarially audited — see [[finding_free_model_coding_bench]]):** 13 free NIM models tie codex & agy at strict 57/57 on a tight-spec function battery.
- ⚠️ **HISTORICAL 2026-06-20 list — ALL FOUR ids below are now dead: mistral-small-4, qwen3-next, llama-4-maverick, AND bare deepseek-v4-flash are 410 EOL per the CURRENT STATUS table (only the `-0731` deepseek variant lives). Do not route any of them.** Default workhorses: `nvidia/mistralai/mistral-small-4-119b-2603` (fastest, 1.5s) · `nvidia/qwen/qwen3-next-80b-a3b-instruct` (3B-active MoE, 4.9s) · `nvidia/meta/llama-4-maverick-17b-128e-instruct` (4.0s — **direct-curl ONLY; tool-format incompatible with opencode's agent layer, see operational bench below**; **⚠️ 2026-07-10: direct-curl path also DOWN, see probe refresh**) · `nvidia/deepseek-ai/deepseek-v4-flash` (**⚠️ 2026-07-10: 503 ResourceExhausted, see probe refresh**).
- Also parity: deepseek-v4-pro, llama-3.1-70b, minimax-m3, mistral-large-3-675b, mistral-nemotron, nemotron-3-super-120b, gpt-oss-120b, qwen3.5-122b, glm-5.1. AVOID for latency: glm-5.1 (38s), qwen3.5-122b (14.5s).
- **gpt-oss-20b caveat:** ~~reasoning model — sometimes returns code only in `reasoning_content` with empty `content`~~ **REFINED 2026-07-19: that was a NON-STREAMING transport artifact — via SSE its code arrives in `content`. New exclusion reason: intermittent correctness (1-in-3 batteries shipped broken code). Still prefer gpt-oss-120b.**
- **Delegation rule:** the denser the spec (parsing/encoding, DP-optimality, null-safety, unicode), the higher the tier you need; loose algorithmic work goes to almost any free model. To combine sub-parity models, **ROUTE by task type** (audited robust) — don't bother with runtime voting (a wash). Old qwen-coder picks were stale (qwen3-coder-480b is EOL/410).

**Two access modes (pick by job):** (1) **NIM via opencode** (`-m nvidia/...`) = full agent (file edits, tools) but sequential + buffered — verified working (~5s, NOT the 0-byte hang that the opencode/zen *native* free models hit). **⚠️ 2026-07-12 stall repro (link-generator):** this path timed out 2/2 (exit 124, 0 bytes on disk) on a ~65-line one-shot TS port with BOTH gpt-oss-120b AND qwen3-next-80b while direct-curl PONG was healthy and direct-curl codegen of the same brief passed 37/37 first try — so "verified working" is not "reliable": for pure one-shot codegen use direct-curl, reserve opencode-NIM strictly for tasks needing file-edit/tool use, and treat exit-124 there as path-failure, not model-failure. (2) **NIM direct curl** to `integrate.api.nvidia.com/v1` = one-shot completion, parallel-safe — use for batch/fan-out codegen.
- Same opencode operational rules apply: `--auto` headless (`--dangerously-skip-permissions` is an undocumented alias that may silently stop being honored — see [[workflow-opencode-subordinate]] gotcha #1), sequential by default — shared SQLite (parallel OK with isolated `XDG_DATA_HOME` + copied auth.json), `timeout`-wrap, verify via git not narrated output.
- **Rate limit = 40 RPM** (requests/min) **SUSTAINED, per ACCOUNT/per key** — one bucket per *account*; extra keys from the SAME account share that bucket, but keys from SEPARATE accounts each get their own 40-RPM bucket (effective ≈ 40×N_accounts sustained). **User's current setup (confirmed 2026-06-27): 3 keys from 3 separate accounts → ~120/min pooled.** Which path actually exploits the pool: **`nimroute.py` direct-curl merges all 3 keys → ~120/min** (its fan-out path); **NIM-via-opencode uses only the single `NVIDIA_NIM_API_KEY` and is SQLite-serialized to ~6 calls/min**, so it never approaches even the single-key 40-RPM cap — the 2 pool keys sit idle on the opencode path (correctly: rotation can't unlock parallel opencode). **Verified empirically 2026-06-20** with 3 separate-login keys: a fair interleaved 120-call burst returned 52 (>40, evenly balanced ~17/key) → the buckets are genuinely independent, rotation works. CAVEAT: there's ALSO a per-account *burst* cap (~17 calls in <7s → 429), distinct from the 40-RPM sustained limit — so PACE calls, don't fire instantaneous bursts. nimroute.py's per-key 40-RPM token buckets pace correctly and won't trip the burst cap; 429-backoff covers overshoot. A full sweep (~38 models × N) is minutes-bound by the sustained limit, not latency.
- **Router with key-pool:** `nimroute.py` (project dir, `/Users/yauch/Documents/claude code technique/`) — deterministic task-type→parity-model dispatcher with per-key 40-RPM token buckets + 429 backoff + fallback chain + reasoning_content handling. Keys via `NVIDIA_NIM_API_KEYS` (comma-sep), `NVIDIA_NIM_API_KEY`, or `NVIDIA_NIM_API_KEY_1/_2/...` (merged, de-duped). Picks the key with most headroom. `from nimroute import call` for throttled batch fan-out. Verified routed outputs pass hidden tests 10/10.
- ~~Credit-limited too; giant models (550b/397b) time out even at 600s, not viable free.~~ **RETRACTED 2026-07-19: the "timeout" was the gateway's ~60s NON-STREAMING idle kill. Via SSE both are alive; nemotron-ultra-550b benched 60/60 strict, 2.3s warm (75s cold-start) → now IN the nimroute chain; qwen3.5-397b correct-but-flaky (RemoteDisconnected 2/3 passes) → opencode-only. See the 2026-07-19 section.**

**OPERATIONAL AGENT-LAYER BENCH (verified 2026-06-27, 48 runs = 6 models × 4 probes × 2 reps, all via `opencode run -m nvidia/...`, deterministically graded — distinct from the 2026-06-20 *direct-curl function battery* above).** The earlier bench proved raw code capability; this one proves whether each NIM model actually *functions as an opencode agent* (file edits + tool use + review). Probes: P1=in-place file edit, P2=edge robustness (unstated `chunk(arr,0)`), P3=catch `let max=0` bug, P4=no-false-positive on a correct binary search.
- **5/6 work as opencode agents; `llama-4-maverick` is the lone INCOMPATIBLE.** It emits tool calls as **literal JSON text in stdout** (`{"type":"function","name":"edit",...}`) instead of invoking opencode's tools → never reads/writes/reviews → 0/8 across all probes. Not a capability failure (its narrated edits are correct) — a tool-call-protocol mismatch with opencode's agent layer. **⛔ HISTORICAL order — llama-4-maverick is 410 EOL as of 08-25 (CURRENT STATUS table): do not route it via ANY path.** (The 06-27 lesson stands as a pattern: an id can be live AND responsive yet inert as an agent — check tool-call protocol, not just PONG.)
- **File edit (P1): the other 5 are 2/2 PASS** — clean in-place edits, no stray files.
- **Edge blind spot reproduces on NIM too** (matches the Zen-pool pool-wide finding): only **`gpt-oss-120b` guards `chunk(arr,0)` 2/2**; `mistral-small-4` flaky (1/2); `qwen3-next`/`gemma-4-31b`/`deepseek-v4-flash` infinite-loop 0/2 (`timeout`-caught, exit 124). → **spec edges explicitly regardless of backend.**
- **Review quality is excellent across all 5 working models:** 2/2 CAUGHT the maxVal all-negative bug (concrete counterexamples like `[-5,-2,-10]→0`) AND 2/2 correctly returned `CORRECT` on the valid bsearch (zero false-positives). NIM models are strong, trustworthy reviewers through opencode.
- **Best overall agent pick: `gpt-oss-120b`** — only model 8/8 perfect incl. the edge guard, 11.5s avg. **Fastest-correct: `qwen3-next-80b`** (5.4s, perfect bar the edge loop).
- **Latency inverts vs direct-curl:** `deepseek-v4-flash` was a fast pick on the curl battery but is the SLOWEST here (94s avg, one P1 rep hit 120s) — backend/quant/agent-overhead dependent; don't assume curl latency carries to the opencode path.
- **Zero rate-limit errors in all 48 sequential single-key runs** → confirms the single-key opencode path is safe (≈6/min ≪ 40/min cap).

**CATALOG SNAPSHOT (verified 2026-06-23, hosted `/v1/models`): 121 models total.** **GLM 5.2 BENCHED (2026-07-03, 4-probe agent harness ×2 clean reps + 5 direct-curl codegen samples): LIVE, FAST, capable — but has a BRUTAL per-account per-model throttle.** Supersedes the earlier "no GLM 5.2 / all 404" note (catalog changed between 2026-06-23 and 2026-07-03). Detail:
- **Latency FIXED vs 5.1**: direct-curl codegen 1.4–4.0s (N=5; glm-5.1 was 38s AVOID); agent-path probes 5–20s — same class as qwen3-next/gpt-oss-120b.
- **Agent capability (clean reps r1+r4)**: P1 file-edit 2/2, P3 bug-catch 2/2 (concrete counterexample), P4 no-false-positive 2/2, P2 basic 2/2 but **edge `chunk(arr,0)` FLAKY 1/2** (r1 wrote a `size<=0` guard, r4 infinite-looped — hand-verified both files). Pool-wide edge blind spot applies; spec edges explicitly.
- **⚠️ Per-model throttle (the operational gotcha)**: ~30–40 glm-5.2 requests in ~10 min → HTTP 429 on that key for glm-5.2 ONLY (**other models still 200 on the SAME key** — verified qwen 200 while glm 429'd back-to-back). Lockout lasted **>25 min** (still 429 at last check), NOT the standard 40-RPM/60s bucket. Other-account pool keys were unaffected (200 immediately) → per-account per-model. Through opencode this manifests as **silent stalls** (34-byte out.txt banner-only, or hang-after-completing-the-edit, exit 124 on timeout-wrap) — looks like the model is broken when it's actually retry-looping on 429. r2/r3 of the bench were 8 consecutive such stalls = throttle artifacts, not capability data.
- **Ops rules**: `-m nvidia/z-ai/glm-5.2` needed an explicit entry in opencode.jsonc's nvidia models block (auto-discovery cache didn't pick it up — added 2026-07-03). Rotate to a pool key via `NVIDIA_NIM_API_KEY=<poolkey> opencode run ...` when throttled. Fine for a handful of paced calls; do NOT put glm-5.2 in high-volume rotation. Would change conclusion: throttle observed on day-of-week/new-model launch capacity — re-test the request budget if NIM later relaxes it.
- **LAUNCH-UNSTABLE (same day, ~1h after the bench)**: endpoint went HTTP 400 `"DEGRADED function cannot be invoked"` on ALL keys (service-wide, not throttle). So 2026-07-03 sequence: live→throttled→degraded within hours. Treat GLM 5.2 on NIM as launch-window unstable; PONG-probe before every use until it stabilizes. Alternative path exists: `opencode/glm-5.2` appeared natively on Zen (not `-free` — paid, so off-limits under the FREE-ONLY rule). ~~SKIP the giants `qwen/qwen3.5-397b-a17b` + `nvidia/nemotron-3-ultra-550b-a55b` — same non-viable-free timeout class as the 397b/550b noted above.~~ **(retracted 2026-07-19 — streaming artifact; see below)** Everything else new vs the benchmarked 13 is non-coding (embed/vision/safety-guard/retrieval/medical/finance).

**PROBE REFRESH (2026-07-10, PONG-probed hosted endpoint, paced 3–5s; catalog still 121 ids — supersedes the 2026-07-03 candidate list above):**
- **LIVE unbenchmarked candidates (6)** for a future [[finding_delegation_frontier_bench]] run: `mistralai/mistral-medium-3.5-128b` (PONG 2.7s) · `google/gemma-4-31b-it` (0.6s) · ~~`stepfun-ai/step-3.7-flash` (0.8s, reasoning-style — give max_tokens headroom) · `stepfun-ai/step-3.5-flash` (1.8s, same)~~ **(benched 2026-07-19: EXCLUDE both — unbounded thinking exhausts any sane budget before content; 3.5 dead even at 16k, 3.7 intermittent. [[finding-newlab-probe-2026-07-19]])** · `minimaxai/minimax-m2.7` (~10s, reasoning-style; content empty at max_tokens=10, fine at 500) · `nvidia/nemotron-3-nano-30b-a3b` (1.2s — this is the CALLABLE id; the also-listed `nvidia/nemotron-nano-3-30b-a3b` **404s** — catalog-lies strikes again, note the swapped segment order).
- **DEAD/UNUSABLE despite being listed:** `moonshotai/kimi-k2.6` (404 — re-confirmed 2026-07-19, routing-level, transport-independent). ~~`bytedance/seed-oss-36b-instruct` (hang → server drops at 60s, 3/3) · `z-ai/glm-5.2` (hang → 60s drop, 2/2)~~ **both RETRACTED 2026-07-19: the "hang → 60s drop" signature was the NON-STREAMING gateway artifact. seed-oss ALIVE via SSE (28.9s smoke; parity unbenched); glm-5.2 ALIVE, benched 30/30 strict, IN the nimroute chain.**
- **Workhorse changes:** `deepseek-ai/deepseek-v4-flash` ~~503 ResourceExhausted 2/2~~ **RECOVERED (2026-07-19: 3/3 streaming smokes 1.2–4.6s; note it now emits `reasoning_content` alongside content, and one 1-off empty-content flake was seen)**. `meta/llama-4-maverick-17b-128e-instruct` **still DEAD 2026-07-19 — 60s RemoteDisconnected even WITH streaming**, so unlike the others this is a genuine outage, not the transport artifact; keep it out of rotation. Healthy: `mistral-small-4-119b` (0.3s), `qwen3-next-80b` (0.4s), `gpt-oss-120b` (0.7s).
- Would change conclusion: any single later successful call to a "dead" id (these were N=2–3 probes on one day, one key; 503/hang classes have recovered before).

**PARITY CHAIN LIVENESS FIX 2026-07-29 ([[finding-groq-bench-2026-07-29]]):** full
18-model `nimroute.py` PARITY sweep found **5/18 dead** — `mistral-small-4-119b-2603`
(410, was `FAST`/`PARITY[0]`), `mistral-large-3-675b-instruct-2512` (410),
`qwen3-next-80b-a3b-instruct` (410, was the string_unicode/nullish MODEL_MAP primary),
`llama-4-maverick-17b-128e-instruct` (410, already tail/flaky), `thinkingmachines/inkling`
(RemoteDisconnected 4/4, distinct from the 60s-hang transport artifact). Fixed in
`nimroute.py`: removed all 5, `FAST` reassigned to `poolside/laguna-xs-2.1`,
string_unicode/nullish primary reassigned to `mistralai/mistral-nemotron`. Also:
`nvidia-nemotron-nano-9b-v2` looked REASONING-ONLY at a 64-tok PONG budget but is
LIVE-with-clean-content at 512 tokens — that was a token-budget artifact, not a model
property; always PONG it with headroom. **Chain is now 13** (was 18 nominal / already
decayed). This is the second catalog-drift correction in 6 days (see 07-23 below) —
treat the PARITY list as needing a liveness re-probe every session it's load-bearing,
not a durable constant.

**opencode.jsonc nvidia BLOCK, same-day sweep — 4/9 DEAD, pruned.** The nvidia provider
block is a SECOND copy of the model list and had rotted independently: `z-ai/glm-5.2`
(RemoteDisconnected 5/5 — consistent with the 07-22 outage verdict above, still down a
week later), `moonshotai/kimi-k2.6` (404), `qwen/qwen3.5-397b-a17b` (410 Gone — was
"correct-but-flaky, opencode-only" per the 07-19 note; now delisted outright),
`mistralai/mistral-large-3-675b-instruct-2512` (410). Surviving 5, all re-verified LIVE:
`poolside/laguna-xs-2.1`, `deepseek-ai/deepseek-v4-pro`, `deepseek-ai/deepseek-v4-flash`,
`nvidia/nemotron-3-super-120b-a12b`, `nvidia/nemotron-3-ultra-550b-a55b`. (laguna +
v4-flash first read EMPTY, then clean 2/2 on re-probe — the known empty-content flake,
not death. Re-probe before pronouncing.) Verified: JSONC parses, dead ids assertion-
checked absent, live `opencode run` PONG on v4-pro.

> ⚠️ **PROCESS BUG this exposes — a retirement must be swept across BOTH configs.**
> `kimi-k2.6` was recorded 404-dead on **2026-07-19 AND again 07-23** in this very file,
> yet was still sitting in `opencode.jsonc` on 07-29 — the finding was written down but
> only ever applied to `nimroute.py`. Same for `mistral-large-3-675b`, killed in PARITY
> that morning and still live in the jsonc that afternoon. **RULE: when retiring a model
> id, `grep -rn "<id>" ~/Documents/"claude code technique"/nimroute.py ~/.config/opencode/opencode.jsonc`
> and fix every hit. A finding that lands in only one of the two configs is half-applied,
> and the surviving copy silently re-introduces the dead model.**

**Groq provider (added by user 2026-07-29): auth'd but AGENT-EXCLUDED, not a NIM
substitute.** Key is in `~/.local/share/opencode/auth.json`. Free tier is **TPM**-capped
(6k–12k/model) — the inverse of NIM's RPM cap — and opencode's preamble is ~32k tokens
even with all tools disabled, so every tool-capable Groq model 429s before the first
turn. `groq/compound` has 70k TPM but returns HTTP 400 `tool calling is not supported`.
Use Groq by direct API only. **Direct-API gotcha (2026-07-29):
Groq's edge rejects the default python-urllib User-Agent with `HTTP 403 "error code:
1010"` (Cloudflare browser-signature ban) — it looks exactly like an auth/key failure
but is NOT. Send an explicit `User-Agent` (`curl/8.7.1` works); the identical request
went 403 -> 200 with only that header added.** Full detail + the pincer evidence in
[[workflow-opencode-subordinate]] and [[finding-groq-bench-2026-07-29]].

**REFRESH + NEW-MODEL BENCH 2026-07-23 ([[finding-nim-refresh-bench-2026-07-23]]):** catalog 121→**118**. **`qwen/qwen3.5-122b-a10b` DELISTED** (404) and **`z-ai/glm-5.2` still SSE-DEAD** — both are STALE entries in nimroute.py's PARITY chain (positions 14/15), remove/park. **`meta/llama-4-maverick` flipped dead→LIVE** via direct-curl (0.3s PONG) but is now **empty-content-flaky** (empty on ~1 of 3 tasks, shifts between runs; 10/10 when content arrives) — same flake now hits **`deepseek-ai/deepseek-v4-flash`** (was a workhorse; the 07-19 "1-off" empty flake is now RECURRENT → downgrade to flaky, opencode-only not single-shot-chain) and **`bytedance/seed-oss-36b`** (capable + very slow 86s cold). **5 NEW strict-parity (30/30) chain-eligible:** `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` (0.5s) · `nvidia/nemotron-3-nano-30b-a3b` (1.0s) · `thinkingmachines/inkling` (1.0s) · `google/gemma-4-31b-it` (4.3s) · `nvidia/nvidia-nemotron-nano-9b-v2` (5.5s, note double `nvidia/nvidia-` segment). **Reasoning-leak (exclude):** step-3.5-flash (confirmed), minimax-m2.7, sarvam-m — thinking bleeds into content. **Sub-parity:** mistral-medium-3.5-128b (23/30, parseQueryString collapsed). DEAD: kimi-k2.6 (404), step-3.7-flash, ministral-14b-2512. Harness: `experiments/nim-refresh-bench-2026-07-23/`.

**GLM-5.2 PROBE 2026-07-22: DOWN even via SSE** — 3/3 PONG probes returned HTTP 000 (connection drop, 0 bytes) with `stream:true` on the main key, while gpt-oss-120b PONG'd 200 on the same key/transport seconds later. So this is a genuine glm-5.2 outage (llama-4-maverick class), not the non-streaming gateway artifact. Keep the PONG-probe-before-every-use rule; fall back to `nvidia/openai/gpt-oss-120b` for agent work.

**STREAMING TRANSPORT UPDATE (2026-07-19 — supersedes every "hang/timeout = dead" verdict above; [[finding-newlab-probe-2026-07-19]]):**
- **Root cause found: NIM's gateway kills NON-streaming HTTP connections at ~60s idle.** Any model whose first token takes >60s (thinking models, cold-started giants) looks "dead" on a non-streaming call regardless of client timeout. This one artifact produced FOUR false death certificates: glm-5.2, seed-oss-36b, nemotron-3-ultra-550b, qwen3.5-397b. **RULE: before declaring a NIM model dead, smoke it with `stream:true`. A 60s empty-reply drop is transport, not health. (Genuine deaths still exist: kimi-k2.6 404s instantly; llama-4-maverick drops at 60s even WITH streaming.)**
- `nimroute.py`'s `_post` now ALWAYS streams (SSE, reassembles a non-streaming-shaped response; `timeout` = max inter-chunk gap). Reverting it to non-streaming silently re-kills glm-5.2 and the giants.
- **Chain is now 15** (was 12): + `z-ai/glm-5.2` (30/30 strict, ~41-60s, tail) + `poolside/laguna-xs-2.1` (30/30 ×2, 0.3-0.4s, pos 2) + `nvidia/nemotron-3-ultra-550b-a55b` (60/60 ×2, 2.3s warm / **75s cold-start**, pos 3). Cold-start pattern: first call after idle can take 20-75s (scales with model size), then warm calls are fast.
- **qwen3.5-397b: correct-but-flaky** — 10/10 in every cell where code arrived, but 2× RemoteDisconnected + 1× empty across 3 battery passes → NOT chain-eligible (single-shot contract); fine behind opencode where retries are cheap. laguna + glm-5.2 also added to the opencode.jsonc nvidia block and smoke-verified as agents (opencode streams, so the gateway kill doesn't affect that path).
- Latency comments in the PARITY chain are now mixed-transport (pre-fix numbers were non-streaming); re-time all 15 under SSE if strict ordering ever matters.

**⚠️ 2026-08-13 probe refresh:** `qwen/qwen3-next-80b-a3b-instruct` AND `mistralai/mistral-small-4-119b-2603` are EOL — hard **410 Gone** on use (qwen EOL'd 2026-07-27). The 2026-06-20 benchmark picks are stale; always re-list the live catalog before routing. Live-verified this session: `minimaxai/minimax-m3` answered a full review prompt via direct curl; `deepseek-ai/deepseek-v4-flash-0731` (v4-flash successor) is listed but dropped the connection 2/2 (RemoteDisconnected — path-flaky, demote).

**REFRESH 2026-08-15 (SSE PONG, catalog + PARITY liveness sweep):** catalog steady at **102 ids** (same count as 08-07, membership shifted). **`deepseek-ai/deepseek-v4-pro` DELISTED — hard 410 Gone**, confirmed via direct SSE call. This removes it from `nimroute.py` PARITY (was proven-core) AND its role as the `parsing`/`dp` MODEL_MAP primary and as a battery CONTROL model in the 2026-08-07 provisional battery — any future battery needs a new second control (candidates: `nvidia/nemotron-3-ultra-550b-a55b` or `openai/gpt-oss-120b`, both proven-core with 60/60-strict-equivalent track records). `nimroute.py` and `~/.config/opencode/opencode.jsonc`'s nvidia block both updated same day; parsing/dp primary reassigned to `nvidia/nemotron-3-ultra-550b-a55b` (same substitution logic as the earlier qwen3-next swap — correctness is uniform across PARITY, this is not a new capability claim). **All other 9 remaining PARITY ids PONG'd 200** (`meta/llama-3.1-70b-instruct` ran 5.1s vs its documented 10.4s battery time — within normal SSE-vs-battery variance, not flagged). **`deepseek-ai/deepseek-v4-flash-0731`** (the 08-13 "dropped 2/2" model) now answers clean **3/3** (10s warm, one 44s cold-start) — the prior RemoteDisconnected verdict does NOT reproduce; treat as a point-in-time serving fact in both directions, like every verdict in this file, and do not add it to PARITY on PONGs alone (needs the 30-assert battery first, same rule as inkling/nano got before their 08-07 promotion). 

**REFRESH 2026-08-15 PM (differential battery, N=9/model x 3 keys, interleaved
control):** ran `mistralai/mistral-nemotron` before every suspect call as a live
control — **27/27 OK, 0.2-3.2s** — ruling out gateway/key/parsing as the cause of
what follows. Three PARITY members are INTERMITTENT, not dead, none uniformly
failing: `poolside/laguna-xs-2.1` **3/9** (instant ~0.2s EMPTY, all 3 keys — worse
than its already-demoted 08-07 rate); `nvidia/nemotron-3-ultra-550b-a55b` **7/9**
(instant ~1s EMPTY on the 2 misses) — notable because it's the parsing/dp
MODEL_MAP primary as of this morning; `meta/llama-3.1-70b-instruct` **6/9**, all 3
failures `RemoteDisconnected` at exactly **60.2s** — the gateway's idle-kill
boundary — while its successes ran 8-72s, so the failure straddles rather than
undercuts a real answer. `nimroute.py`'s chain fallback absorbs single empties for
all three (they stay in PARITY, rates recorded inline), but **`laguna-xs-2.1`
removed from `opencode.jsonc`** — opencode has no fallback, so 3/9 there is a
2-in-3 failure per run. Same day, **Zen delisted its sibling
`opencode/laguna-s-2.1-free` outright** (see [[workflow-opencode-subordinate]]) —
read together as a poolside-wide serving event, not two coincidences. **Zen pool
churned again same day:** `muse-spark-1.2-contributor-free` NEW (4s PONG,
unbenched), `laguna-s-2.1-free` OUT.

**No `qwen*` ids of any kind on NIM** (`qwen3.5-397b-a17b` still 410, `qwen3.6-27b`/`qwen3.8-max` 404 — NIM has never listed a qwen3.6+ id; Zen/OpenRouter carry the qwen3.7/3.8 family instead, paid only, see the opencode_subordinate playbook's Zen pool table for the free tier).

**GLM-5.2 FORMALLY EOL + opencode DEFAULT-MODEL PIN (2026-08-21).** `z-ai/glm-5.2`
is now **permanently gone**, not merely outage-dead: the API returns HTTP **410**
with an explicit `"reached its end of life on 2026-08-21T09:00:00Z"` detail. This
closes the open question in the 07-22/07-29/08-07 notes above (repeated
RemoteDisconnected) — those were the run-up to a real retirement, so the earlier
"probe before pronouncing" caveat does NOT apply to this id any more. It was
already absent from `nimroute.py`'s PARITY chain and from the opencode nvidia
models block, so the documented sweep was already clean on both configs.

**The failure it actually caused, and the general lesson: a dead model id can break
you through a config you never edited.** `~/.config/opencode/opencode.jsonc` had
**no top-level `"model"` key**, so a bare `opencode run` (no `-m`) fell back to
opencode's **SQLite last-used-model state** (`~/.local/share/opencode/opencode.db`),
which still held `z-ai/glm-5.2` — so every no-flag invocation hard-410'd, with an
error naming a model the caller never chose and that appears nowhere in either
config file. **The two-config sweep rule above is necessary but NOT sufficient: an
id can also be pinned in opaque CLI state.** Fixed by pinning an explicit default:
`"model": "nvidia/openai/gpt-oss-120b"` at the top level of opencode.jsonc (backup:
`opencode.jsonc.bak-2026-08-21`), plus an explicit models-block entry for it (it had
been reachable via auto-discovery only, and auto-discovery has silently missed ids
before — see the 2026-07-03 glm-5.2 note). **Standing rule: keep a top-level
`"model"` pinned to a re-probed-live id, so the default is a fact in a file you
control, not a fossil in a database.**
- Liveness this session (SSE PONG, main key): `openai/gpt-oss-120b` **2/2 OK ~1.0s**
  (also drove a real agent task same day) · `thinkingmachines/inkling` OK 6.7s ·
  `nvidia/nemotron-3-super-120b-a12b` OK 2.1s · `nvidia/nemotron-3-ultra-550b-a55b`
  OK 0.8s (up from its 7/9 flake on 08-15) · `mistralai/mistral-nemotron` OK 0.4s.
- ⚠️ **Probe-harness trap (cost me a false death certificate):** a streaming chunk
  can carry an **empty `choices` array** (usage-only chunks). `json.loads(line[6:])
  ['choices'][0]` then raises `IndexError` and, if you catch broadly, prints as a
  model FAIL. gpt-oss-120b "failed" 1.4s this way while being perfectly healthy.
  **Guard it: `ch = d.get('choices') or []; if ch: ...` — and never record a death
  certificate from a run whose parser you have not exonerated.**
- opencode agent-layer gotcha re-confirmed 2026-08-21: `opencode run` given a
  "create exactly one file" instruction **narrated the file as a fenced ```ts block
  to stdout and wrote nothing to disk** (gpt-oss-120b, isolated scratch dir). Verify
  by `ls`, never by the narration; recovering it is a mechanical
  `awk '/^```ts$/{f=1;next} /^```$/{f=0} f'` extraction from the captured stdout.

### 2026-08-23 — nemotron-3-ultra-550b (NIM) ≠ nemotron-3-ultra-free (Zen) — behaviorally, not just commercially

Same-window five-way bench ([[finding-fiveway-bench-2026-08-23]]) ran NIM-served
`nvidia/nvidia/nemotron-3-ultra-550b-a55b` on the standard chunk-edge-guard probe: **edge
0/2**, indistinguishable from the naive-loop baseline. The SAME base model, Zen-served as
`nemotron-3-ultra-free`, guards edges 2/2 and was hand-verified in source that same day
([[finding-pool-reprobe-2026-08-23]]). N=2, descriptive only — but it lands on the same
lesson as the billing-gate PAID≠DEAD finding: **a NIM-served id and a same-named Zen-served
id are different serving paths and provably CAN diverge on behavior, not just on liveness or
price. Never carry a Zen-free score onto a NIM id of the same family name — re-probe it
independently.**

### 2026-08-22 — gpt-oss-120b empty-output trap (direct API)
`openai/gpt-oss-120b` spends hidden reasoning tokens BEFORE content; with a small `max_tokens` it returns `finish_reason: length`, `content: ''` (PONG at max_tokens=20 → 0 content, 70 reasoning). A review call with max_tokens 4000 on a ~12k-char prompt came back totally empty — looked like a dead model, wasn't. Fix: `max_tokens >= 16000` and `reasoning_effort: 'low'` in the body (accepted by the NIM endpoint); then it returned a full review. Empty content + finish=length is the signature — differential-diagnose with a non-stream call and check `usage.completion_tokens` vs content length.
