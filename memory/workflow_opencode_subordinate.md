---
name: workflow-opencode-subordinate
description: opencode CLI (native OpenCode Zen free models) as a coding subordinate — invocation, model selection, session management, gotchas, and the delegate-WHAT-not-WHETHER boundary
metadata:
  type: project
---

# opencode CLI Subordinate Playbook

## TL;DR — the delegation decision (benchmarked, 3 rounds, 2026-06-11)

Free opencode models tested at PARITY with codex/opus on EXECUTION (code-from-spec, bug-fix,
reasoning, convention-match, edge-defense, trap-avoidance). They diverge on ONE axis only:
**judgment-to-refuse** — recognizing when the instruction itself is unwise (only codex/opus
flagged a security anti-pattern; all free models executed it blindly).

- ✅ **Delegate the WHAT (execution) freely** → cheapest reliable model, isolated dir, verify output.
- 🚫 **Never delegate the WHETHER** ("is this safe / a good idea / architecturally sound?") →
  keep codex/opus/you as the judgment layer. Free models execute footguns without blinking.

Operational guardrails (non-negotiable, see Benchmark findings below):
1. Default SEQUENTIAL (shared SQLite db → "database is locked" under naive parallel — re-confirmed 2026-07-03). **Parallel IS possible**: give each instance its own `XDG_DATA_HOME` with auth.json copied in (see Benchmark findings #1) — verified 3-way parallel file-edits, all on-disk correct, 15s wall.
2. Run in an ISOLATED scratch dir (`--auto` = full read+write; it roams).
3. `timeout 180`-wrap every call (free models hang).
4. Prefer native `opencode/*` (Zen) over `openrouter/*:free` (rate-limits + hangs).
5. Verify output yourself; parse BOTH inline code blocks AND files the agent wrote.

## Install & Auth
- Installed to: `~/.opencode/bin/opencode` (PATH set in `~/.zshrc`)
- Auth: OpenCode Zen + OpenRouter creds in `~/.local/share/opencode/auth.json` (`opencode providers list`)
- Version check: `opencode --version`
- Upgrade: `opencode upgrade`

## Core Invocation

**Headless one-shot (⚠️ `--auto` = full read+WRITE in cwd — use an isolated scratch dir):**
```bash
opencode run --auto -m opencode/muse-spark-1.2-contributor-free "<prompt>"
```
⚠️ **Re-list before every run** (`opencode models`) — the pool churns within hours and this
id has a PAID bare twin; the `-contributor-free` suffix is load-bearing.

**Code-writing (backgrounded, isolated + timeout-wrapped):**
```bash
SCRATCH=$(mktemp -d) && cd "$SCRATCH" && timeout 180 opencode run --auto -m opencode/muse-spark-1.2-contributor-free "$(cat /tmp/opencode-prompt.txt)" > /tmp/opencode-out.txt 2>&1 &
```

**With file attachments:**
```bash
opencode run --auto -m <model> -f path/to/file.ts -f path/to/other.ts "<prompt>"
```

**JSON output (for parsing):**
```bash
opencode run --auto -m <model> --format json "<prompt>" | jq .
```

## Model Selection (FREE ONLY — do not use paid models)

Use NATIVE `opencode/*` (OpenCode Zen) free models — they are far more reliable than
`openrouter/*:free` (which rate-limits + hangs). Benchmarked 2026-06-11 (see below).

Re-verified 2026-06-27 @ opencode v1.17.8 (4 probes × 5 models × 2 reps, deterministic grading — see section below). Scores are x/2 unless noted.

| Use case | Model | Notes (✅=re-verified 2026-06-27 @v1.17.8) |
|---|---|---|
| Default / general (headless) | `opencode/big-pickle` | ✅ best overall 9/10, **0 fabrications**, 8.2s. Real on-disk edits matched narration. Roams cwd. (Refutes the old "0/20 file-edits" — see Conflict note.) |
| ⛔ **DELISTED FROM FREE 2026-08-28 — not an outage** | ~~`opencode/deepseek-v4-flash-free`~~ (a PAID `opencode/deepseek-v4-flash` now exists — UNBENCHED, and the free scorecard does NOT transfer to it) | 🔴 **The 08-21 "NOT SERVING" diagnosis was WRONG and is retracted.** Re-listed 2026-08-28: the free id is absent from `opencode models` entirely and fails on call, while a bare paid twin appeared. So the 08-21 symptom (rc=1, ~0.6s, 0 bytes, server-side `UnknownError`) was a **tier move, not a serving fault** — and I could not tell them apart, because a delisted id and a broken id return the same shape. The interleaved big-pickle control correctly proved it was not local and not capability; it could not prove it was an outage, and I over-read it as one. **Lesson: a control separates local-vs-remote, NOT outage-vs-delisting — for that, diff the model LIST.** Independently corroborated by an X report of deepseek removal (2026-08-27). Historical: 8/10 @ 2026-08-04 (N=2×4, old harness) — P1 2/2, P2 basic 2/2, P3 2/2, P4 no-FP 2/2, unstated `size=0` EDGE-LOOP 2/2. Do NOT reuse that number for the paid id. **2026-08-29: the free id also dropped its `-free` suffix (`opencode/deepseek-v4-flash-free` → `opencode/deepseek-v4-flash`) — the same paid id from 08-28 with the suffix gone, not a new one. Direct probe (`opencode run -m opencode/deepseek-v4-flash "Reply with exactly: PONG"`) returns `Error: No payment method. Add a payment method here: …/billing`, confirming the payment-gate mechanism directly rather than inferring it from the delisting. A new sibling `opencode/deepseek-v4-pro` appeared same day — same payment-gate error on first contact, never had a free tier.** [[finding-zen-pool-bench-2026-08-29]] |
| Clean all-rounder | `opencode/mimo-v2.5-free` | **Re-benched 2026-08-04 (N=2×4): 8/10.** All 4 core probes 2/2 clean; self-tests via `node` (slowest core-probe times in the pool, 74s on P4). **Unstated `size=0` → EDGE-LOOP 2/2.** Roams+writes+EXECUTES cwd. |
| ⚠️ AVOID + **DELISTED from Zen 2026-08-15** | ~~`opencode/north-mini-code-free`~~ (still on OpenRouter as `openrouter/cohere/north-mini-code:free` — UNBENCHED on that endpoint, do not assume the Zen scorecard transfers) | **Re-benched 2026-08-04 (N=2×4): 6/10 — WORST in pool.** P1 2/2, P3 2/2, P4 no-FP 2/2, but **P2 r1 wrote to `/private/tmp/chunk.js` — an absolute path OUTSIDE the run directory** despite an explicit "in this directory" instruction (r2 stayed local but hit the same unstated-edge infinite loop as the rest of the pool). This is a concrete, reproduced instance of the pre-existing "roams cwd" caveat, not a new one — but it's now the only model in the pool that failed the file-locality contract outright. The 2026-06-27 "bad at bug-diagnosis caveat RETIRED" verdict stands (diagnosis is fine); do not use for unattended file writes. |
| Edge-defense / self-verify — ⬆️ **10/10 re-benched 2026-08-29**, edge guard back to **2/2** | `opencode/nemotron-3-ultra-free` | ⬆️ **2026-08-29 (N=2×4, whole-pool, opencode 1.18.25): 10/10, edge 2/2 both reps.** Third build in 8 days: edge went 1/2 (08-21) → 1/2 (08-28) → 2/2 (08-29). **Treat this as OSCILLATION around a rate, not a one-way trend in either direction** — across all three builds the edge has guarded 4 of 6 reps. Do not extrapolate the next build's score from the direction of the last change. Also still the slowest model in the pool most builds. [[finding-zen-pool-bench-2026-08-29]] ⬇️ 08-21/08-28 (N=2×4 each): 9/10, edge 1/2 — hand-verified as genuine intra-model variance on 08-21 (r1 bare `for (let i=0; ...; i += size)`, r2 `if (size <= 0) return [];`). **A model that guards an edge in one rep and not the next is not "an edge-guarding model" — a 2/2 at N=2 buys much less than it looks like.** ✅ **10/10 on 2026-08-04 (N=2 × 4 probes)** — P1 2/2 no strays, P2 basic 2/2, **P2 `size<=0` GUARDED 2/2**, P3 2/2, P4 no-FP 2/2. 9–55s. ⚠️ **Flakiness did NOT reproduce: 8/8 exit 0, no `ResourceExhausted`, no exit-1 no-edit.** Caveat NOT retired — those were *infra* events on the NIM backend, and clean runs in one window cannot disconfirm intermittent infra failure (absence ≠ stability). Still timeout-wrap + revert-on-failure; treat any single score as a point-in-time serving fact. |
| ~~BEST free model~~ ⬇️ **DEMOTED 2026-08-28 — 8/10, no longer the default** (the current default is `muse-spark-1.2-contributor-free`, tied with `nemotron-3-ultra-free` at 9/10; this row keeps its detail as the CONTROL model, which is what it is used for now) (⚠️ edge guard REGRESSED — **REPLICATED 2026-08-21: 0/2 again**, 6 days later on a newer CLI, so this is persistent serving-build drift, not a one-day blip; P1/P3/P4 still 2/2, total 8/10. First seen 2026-08-15: `size<=0` loop 2/2, was GUARDED 2/2 on 08-04 — hand-verified unguarded source; 10/10→8/10 on today's build, now pool-standard profile. Serving-build drift, not harness: same harness scored its P1/P3/P4 identically. Do not rely on it defending unstated edges — spec them, like everyone else) | `opencode/big-pickle` | ✅ **10/10, benched 2026-08-04 (N=2 × 4 probes, 8/8 exit 0, 6–15s)** — the ONLY clean sweep in the pool. P1 2/2 no strays, P2 basic 2/2, P3 2/2 (cites `maxval.js:2`), P4 no-FP 2/2. **P2 unstated `size=0` GUARDED 2/2** (r1 `size<=0 → []`, r2 `RangeError`; both re-run independently for `size=0` AND `size=-1`, not trusted from the grader's exit code) — defends that edge with no flakiness history (nemotron also guards it 2/2 as of 2026-08-04, but carries an unretired infra-flakiness caveat — big-pickle does not). **Self-verifies by executing tests, AND audits its own test against the spec**: P4 r1's first suite had a wrong expectation (`bsearch([1,1,2,2,2,3],2)` "should be" 3) and FAILED — it diagnosed its *own harness* as wrong, rewrote the dup case as "some valid index, unspecified per spec", then reported no bugs. That is the exact discipline laguna lacks. |
| ~~Speed king~~ **DELISTED 2026-08-15** | ~~`opencode/ling-3.0-flash-free`~~ | ⚠️ **GONE from the Zen pool 11 days after its 8/10 bench** — no `ling*` id remains, free or paid. Second instance of the hy3 pattern (bench-verified → delisted). Scorecard kept below for if it returns; do NOT hardcode. ✅ **8/10, benched 2026-08-04 (N=2 reps × 4 probes, 8/8 exit 0)** — P1 2/2 in-place edit no strays, P2 basic 2/2, P3 catch 2/2 (named `let max = 0`, gave `maxVal([-5,-3,-1])` → 0), P4 no-FP 2/2 (clean correctness reasoning on bsearch). **FASTEST benched: 5–10s/probe, zero flakiness.** Only miss: unstated `chunk(arr,0)` → **infinite loop 2/2** (`i += size` never advances; hand-verified in the source, not just the timeout). Same blind spot as gpt-5.6-sol/terra and curable the same way — spell the edge out in the spec. |
| ⚠️ **DELISTED from Zen 2026-08-15 pm** — same day its NIM sibling `poolside/laguna-xs-2.1` fell to 3/9 SSE PONG (see [[reference-nim-via-opencode]]); read together as a poolside-wide serving event | ~~`opencode/laguna-s-2.1-free`~~ | ⚠️ **7/10, benched 2026-08-04 (N=2 reps × 4 probes, 8/8 exit 0)** — P1 2/2, P2 basic 2/2, P3 catch 2/2. **P4 no-FP only 1/2**: r1 wrote+ran an 11-case suite (all PASS), then reported `bsearch([1,2,3,4,5],'3') → -1` as "the bug" (`===` vs coercive `<`) — real behavior, *executed*, but the brief specified a numeric array, so it asserted a bug in spec-correct code. **Executes code to self-verify** (like nemotron/mimo) — that costs 65–75s on review probes vs 8–12s on impl. Same unstated-`size=0` infinite loop 2/2 as ling. Use when over-reporting beats missing; otherwise prefer ling. |
| AVOID (headless) | `openrouter/qwen/qwen3-coder:free` | 429 rate-limit / silent hang |
| AVOID (any tier) | `openrouter/nousresearch/hermes-3-llama-3.1-405b:free` | verified 2026-07-03: agent path hard-fails ("No endpoints found that support tool use") AND one-shot direct-curl 429'd — no viable tier. Revisit only with paid Hermes-4 or own OR key (tool-use blocker would still cap it at one-shot) |
| ⛔ **DELISTED again 2026-08-29, SAME SESSION as its clean bench run** | ~~`opencode/hy3-free`~~ (only paid `openrouter/tencent/hy3` / `hy3-preview` remain) | 🔴 Ran clean (8/10, rc=0 both reps) in this session's own bench a few hours earlier; a routine free-list refresh later the same session found it gone from `opencode models` entirely. **Third instance of the exact bench-verified→delisted-same-day pattern** (07-03 original, mid-08-15 repeat, now this) — this pool's volatility window can be hours, not days. Do not treat "it just benched clean" as evidence it will still be there for the next call in the same session; re-list immediately before routing, not just before a new bench. Historical: ✅ **Re-benched 2026-08-15 (N=2×4, rebuilt harness, big-pickle control): 8/10** — P1 edit 2/2 no strays, P2 cap 2/2, P3 catch 2/2 (mechanism + counterexample), P4 no-FP 2/2 (literal `CORRECT`), avg 9.4s. **Unstated `size<=0` → EDGE-LOOP 2/2** (hand-verified unguarded `i += size` in source) — its 07-03 form holds minus the edge, which most of the pool fails — but NOT all: muse-spark guards it 2/2 and nemotron-3-ultra 1/2 as of 2026-08-21, see those rows. Debt cleared; usable again as an all-rounder with the standard spec-the-edges discipline. History: Benched 9/10 on 2026-07-03 (P1 2/2, P2 cap 2/2, P3 catch 2/2 + volunteered empty-array edge, P4 no-FP 2/2, ~10s, zero flakiness) — **then VANISHED from the Zen free pool the SAME DAY** (re-listed hours later: gone; only paid `openrouter/tencent/hy3` @ $0.13/M and `hy3-preview` @ $0.06/M remain). Keep the scorecard for if it returns; do NOT hardcode it in any chain |
| AVOID (any config) | **all `groq/*`** | Key IS auth'd (2026-07-29) but Groq free tier CANNOT run opencode as an agent — see the pincer note below. Use the key by direct API only — playbook: [[reference-groq-direct-api]]. |
| ✅ **RECOVERED 2026-08-29 — back to normal 8/10, the 08-28 hang did NOT persist** | `opencode/nemotron-3.5-lightning-free` | ✅ **2026-08-29 (N=2×4, whole-pool, opencode 1.18.25): 8/10** — all 4 probes 2/2 on stated work, edge 0/2 as always (pool-standard blind spot), one P3 rep took 162.4s but completed, no timeouts. Confirms the 08-28 finding's own prediction ("a serving fault can clear") and its distinction between "hangs but listed" (serving fault, worth re-probing) vs. "delisted" (tier move, don't re-probe) — this row is the clean example of the former clearing. [[finding-zen-pool-bench-2026-08-29]] 🔴 **HISTORICAL — 2026-08-28: 8/8 in-bench timeouts**, then re-probed with an **INTERLEAVED control**: lightning rc=124 @90s **2/2** while big-pickle rc=0 @5s and @18s in the same minutes. **Score WITHHELD — 0/10 was NOT recorded** (an outage and an incapacity are the same shape). ⚠️ **Two dead signatures, do not conflate:** deepseek = fast-fail (rc=1, 0.6s) + DELISTED → tier move; this = **HANGS (90s+) + still listed** → serving fault, and this one cleared on its own by the next build. | ✅ **Benched 2026-08-15 (N=2×4, rebuilt harness, big-pickle control): 8/10** — P1 2/2, P2 cap 2/2 (5.0s fastest P2 in this bench), P3 2/2, P4 no-FP 2/2, avg 10.6s. **Unstated `size<=0` → EDGE-LOOP 2/2** (hand-verified in source — same unguarded loop text as big-pickle and hy3, to the character). Profile = pool-standard: clean on all stated work, blind on unstated degenerates. Viable for bounded, spec'd tasks from day one. |
| ⭐ **BEST free model — RE-BENCHED 2026-08-29: back to 10/10, edge guard 2/2** | `opencode/muse-spark-1.2-contributor-free` | ⬆️ **2026-08-29 (N=2x4, whole-pool, CLI 1.18.25): 10/10, edge 2/2 both reps.** Third build in 8 days: edge went 2/2 (08-21 debut) → 1/2 (08-28) → 2/2 (08-29). **Retire the "debut 10/10 never survives a re-bench" framing from 08-28 — this IS a re-bench, and it came back 10/10.** Read across all three builds this is OSCILLATION (4 of 6 edge-reps guarded), not a one-way decay; don't predict the next build from the direction of the last change. Still the strongest free model on stated work every build. ⚠️ a PAID bare `opencode/muse-spark-1.2` twin exists — the `-contributor-free` suffix is load-bearing. [[finding-zen-pool-bench-2026-08-29]] ⬇️ **08-28 (N=2x4, CLI 1.18.23): 9/10, edge 1/2** — historical, see above; was read at the time as a regression, now read as the middle point of an oscillation. ✅ **10/10 on debut, 08-21 (N=2×4, opencode 1.18.19)** — P1 2/2 no strays, P2 cap 2/2, **P2 unstated `size<=0` GUARDED 2/2**, P3 2/2, P4 no-FP 2/2, avg 17.0s. Hand-verified in source: both reps wrote `if (!Array.isArray(arr) || size <= 0) return [];` — defended a degenerate input **and** a type precondition, neither in the brief. First appeared 2026-08-15 pm, same PM refresh that delisted laguna. |
| List all free (**BOARD 2026-08-29**, N=2x4x8 one build: **muse-spark = nemotron-3-ultra 10/10 > big-pickle = hy3 = mimo = nemotron-3.5-lightning 8/10; deepseek-v4-flash / deepseek-v4-pro PAYWALLED (need a paid opencode workspace, out of scope for this harness)**. 🔀 **Reverses the 08-28 "ZERO reliable edge defenders" claim — the two top models' edge guard OSCILLATES (2/2 → 1/2 → 2/2 across the three most recent builds), it did not settle at 1/2. Do not treat either direction as the new steady state; spec every edge explicitly regardless.** [[finding-zen-pool-bench-2026-08-29]]) (pool composition stable at 6 opencode-branded free models across three builds now — the only real membership event this round was deepseek's id losing its `-free` suffix, not a pool-size change. `nemotron-3.5-lightning`'s 08-28 hang cleared on its own by 08-29.) Prior boards, oldest first: 08-15 refresh (below), [[finding-zen-pool-bench-2026-08-21]], [[finding-zen-pool-rebench-2026-08-28]]. Bench the whole pool on every re-check, not just new arrivals or the models that moved last time — the models that DIDN'T move (big-pickle/hy3/mimo, 8/10 x3 builds) are the useful stability baseline against which the oscillating ones stand out. | `opencode models \| grep -E '\-free$\|big-pickle' \| grep '^opencode/'` | **RE-LIST BEFORE EVERY CHAIN RUN — the pool churns within hours.** ⏱ **2026-08-15 refresh (liveness only, N=1 PONG each, all exit 0):** pool = 7 but membership MOVED in 11 days. Still live + still carrying their 08-04 scores (AM refresh): big-pickle (10/10, 3s), nemotron-3-ultra-free (10/10, 3s), deepseek-v4-flash-free (8/10, 3s), mimo-v2.5-free (8/10, 2s), laguna-s-2.1-free (7/10, 2s — DELISTED by the PM refresh same day, see the row above). **OUT: `ling-3.0-flash-free` (8/10) and `north-mini-code-free` — both delisted.** **IN: `hy3-free` (returned after 6 weeks) and `nemotron-3.5-lightning-free` (new)** — both UNBENCHED on the current harness. So the pool churned 4 of 7 slots in 11 days while holding size constant — **a steady count is not a steady pool; diff the membership, not the length.** Prior full-bench board (2026-08-04, N=2×4, 56/56 exit 0): ALL benched same day under one identical harness (N=2×4, 56/56 exit 0, 4 run concurrently with isolated `XDG_DATA_HOME` with zero rate-limit errors): **big-pickle 10/10**, **nemotron-3-ultra-free 10/10** (flaky-caveat unretired), ling-3.0-flash-free 8/10, deepseek-v4-flash-free 8/10, mimo-v2.5-free 8/10, laguna-s-2.1-free 7/10, **north-mini-code-free 6/10 (AVOID — sandbox escape)**. Full detail in rows above. ⚠️ presence in the pool is not guaranteed to persist (cf. hy3-free's same-day delisting) — a good score does not buy longevity. |

> 🧪 **Grader soundness note (2026-08-04):** the P3 (bug-catch) string-matcher was too narrow — required literal `bug/incorrect/wrong/fails/flaw`, missed structural phrasing ("returns 0 **instead of** the actual max"), producing a false MISS on deepseek r1 (caught by hand-reading the transcript; the model's diagnosis was actually correct and complete). Fixed by adding `instead of/should return/should be/does not return` to the claim check; regrade flipped only that one cell — all other 13 P3 verdicts unchanged. Verified the fix didn't overcorrect by hand-reading all 14 real P3 transcripts (genuine catches, all cite the `max=0` mechanism + a concrete counterexample) and by negative-controlling the loosened matcher against 6 unrelated P4 (bsearch) transcripts — surfaced a second, pre-existing weakness (the `mech` check's bare `"0"` keyword is a near-universal match) that produced one false CAUGHT on mismatched data but never fired on any real P3 run. Textbook [[finding-test-validity-failure-modes]] case: a grader bug can hide in either direction, verify both.

> 🔬 **Self-verification is two skills, not one (2026-08-04, N=3 models × 2 reps).** big-pickle, laguna, and nemotron all *execute tests* to check their work; only big-pickle *audits the test against the spec*. Laguna's P4 false positive and big-pickle's P4 save came from the SAME behavior — writing a suite, seeing a FAIL — and diverged only on whether the model suspected its own harness. **When grading a subordinate's review, ask which of the two it did**; "it ran code" is not evidence of correctness (cf. the coincidence-stub mode in [[finding-test-validity-failure-modes]] — a green count is not evidence, and neither is a red one).
>
> 🔁 **NEITHER "everything fails this" NOR "zero reliable defenders" is the settled state — three builds show OSCILLATION (2026-08-29)** — muse-spark and nemotron-3-ultra's edge guard went 2/2 (08-21) → 1/2 (08-28) → 2/2 (08-29). Stop treating each new build's result as a correction of the last; it's a data point in a bouncing series. The one claim that HAS held across all three builds without exception: big-pickle/hy3/mimo are reliably at edge 0/2, and no model has ever reached edge 2/2 on more than half its cumulative reps with confidence — so **spec every edge explicitly, full stop, regardless of which way the last build's number moved.** [[finding-zen-pool-bench-2026-08-29]]
>
> ⚠️ **THIS RETRACTION IS ITSELF SUPERSEDED 2026-08-28** — the 08-28 whole-pool re-bench put muse-spark at edge **1/2** and nemotron-3-ultra at **1/2**, i.e. **ZERO reliable edge defenders again**, so the 08-15 claim is back in force on current evidence (and the methodological lesson below still stands: bench the pool before making a pool claim). [[finding-zen-pool-rebench-2026-08-28]]
>
> ↩️ **RETRACTED AGAIN (2026-08-21): "NO model in the free pool currently defends unstated degenerate inputs / the spec-the-edges rule is now unconditional"** (claimed 2026-08-15). That held for the 3 models benched that day; generalizing 3 models to "the pool" was the error. The 08-21 whole-pool run has muse-spark guarding `size<=0` 2/2 and nemotron-3-ultra 1/2. **Spec'ing edges explicitly is still right practice — it just cannot be justified by "everything fails this."** Note this is the SECOND time this exact over-generalization was made and retracted (see the 08-04 one immediately below): the edge probe **separates models**, so whenever only a subset is benched it looks universal. Bench the pool before making a pool claim.
>
> ↩️ **RETRACTED (2026-08-04): "only nemotron guards the unstated `size<=0` edge".** big-pickle guards it 2/2 and is not infra-flaky, so the edge is NOT a universal free-tier blind spot — it separates models. The blind spot is real for ling, laguna, and gpt-5.6-sol/terra; it is not a law. Spec'ing edges explicitly remains right, but do not cite "everything fails this" as the reason.
>
> ⚠️ **Zen free-pool volatility (2026-07-03, hard evidence):** hy3-free went bench-verified → delisted in HOURS on the same day. Two new `-free` entries (laguna-s-2.1, ling-3.0-flash) appeared in the same window. **Any static free-model list in a chain/config is stale on arrival** — enumerate the pool at run time and treat a missing model as expected, not as an error. Kin to the [[finding-cache-staleness-audit-2026-07-25]] rule that world-facts decay in days; here it's hours.

> 🚫 **Groq is auth'd but agent-EXCLUDED at free tier (2026-07-29, measured — do not retry).**
> A `groq` api key is registered in `~/.local/share/opencode/auth.json`. It works; the
> blocker is a **two-sided pincer** that no config setting closes:
> - **Tool-calling models are under the TPM ceiling.** opencode's preamble is ~32k tokens
>   *with all 13 tools disabled via a custom agent* (45,874 tok on the default `build`
>   agent → 36,147 → 32,466 tool-less, for a two-word prompt). Groq free TPM: 12,000
>   (`llama-3.3-70b-versatile`), 8,000 (`gpt-oss-120b`/`-20b`, `qwen3.6-27b`), 6,000
>   (`llama-3.1-8b-instant`). ~3× over at the floor. Even the *session-title* agent 429s.
> - **The one model with headroom can't call tools.** `groq/compound` + `compound-mini`
>   have **TPM 70,000** — comfortably above the 32k floor — but return
>   `HTTP 400: "tool calling is not supported with this model"`. Confirmed by direct API
>   probe with a minimal tool schema; in opencode it surfaces as an opaque `UnknownError`.
>
> → For opencode's purposes the binding wall is **TPM**: payload size, not request
> count, is what excludes the agent loop. (Corrected 2026-07-30: Groq is not
> "TPM-only" — it enforces BOTH a token and a request bucket, per model, and the
> request bucket is per-DAY not per-minute: `llama-3.3-70b-versatile` = 12,000 TPM
> **and 1,000 req/day**; `llama-3.1-8b-instant` = 6,000 TPM and 14,400 req/day. So
> many-tiny-calls can exhaust 70b's daily requests. See [[reference-groq-direct-api]].)
> Agent frameworks are exactly the wrong workload for it. Use the key for **direct API
> calls where you control the payload** — `gpt-oss-120b` or `llama-3.3-70b-versatile`
> (both 30/30 on the frozen battery), or Whisper. Not agent loops.
> Re-open only if Groq raises free TPM or ships tool-calling on compound.

> ⚠️ **HISTORICAL (2026-06-27 snapshot) — RETRACTED TWICE, see the two retraction blocks above.** Pool-wide edge blind spot (as measured that day): free models nail the happy path but do NOT defend *unstated* degenerate inputs. P2 probe: 9/10 wrote a `chunk()` that **infinite-loops on `size=0`** (no guard), *even though an example was given*. Only nemotron guarded it (1/2). → **Spec `size<=0` / negative / NaN / empty explicitly, or put those cases in your own verification** — same defensive-spec discipline already required for [[workflow-codex-subordinate]] / agy. This is the WHAT-vs-WHETHER rule's sharper edge: they execute the happy path, they won't *judge* what a degenerate input should do.
>
> 🔀 **Conflict reconciled (Rule 7):** the prior frontier-bench finding ([[finding-delegation-frontier-bench]]) recorded "big-pickle 0/20 headless file-edits + 14 fabrications → route to north-mini, NOT big-pickle." It **did not reproduce** here: big-pickle did 4/4 real on-disk file ops (P1 2/2 + P2-cap 2/2), 0 fabrications. Reconciliation is **task-complexity, not a version fix** — same v1.17.8 (Jun-18) build both times; the 0/20 was on the frontier's *harder multi-file dir-mode* tasks (A1/A2/A3), this is a *simple single-file* in-place edit. → **big-pickle is reclaimed as a viable default for simple/medium headless edits**; for **complex multi-file** edits keep the caution and verify on disk. ⛔ **The old "route to north-mini for at-scale headless work" advice is DEAD** — north-mini-code-free was DELISTED from Zen 2026-08-15 (row above) and its OpenRouter twin is unbenched. Complex multi-file: do it yourself or route to codex (routing map §route-to).

## Benchmark findings (2026-06-11) — opencode free models vs codex/agy

4-probe battery (impl-from-spec / bug-hunt / reasoning / ambiguity). Raw capability was
near-ceiling for ALL models — the real differentiation was OPERATIONAL:

0. 🔴 **Isolate `XDG_DATA_HOME` ONLY — never `XDG_CONFIG_HOME` (2026-09-01).**
   The `nvidia` (NIM) provider is DEFINED in `~/.config/opencode/opencode.jsonc`.
   Pointing `XDG_CONFIG_HOME` at a temp dir hides it, and every NIM id then fails
   with a generic `{"name":"UnknownError","message":"Unexpected server error"}`
   — indistinguishable from a delisted model or a backend outage. I mis-read it as
   a delisting and had started writing that up; the id was in `opencode models` the
   whole time. **Differential that settles it in one command: re-run WITHOUT the
   config isolation** (PONG returned immediately). Parallel-safety only needs
   `XDG_DATA_HOME`; the config dir carries credentials and provider definitions.
   Sibling trap in [[workflow-grok-subordinate]] (`$TMPHOME` hiding grok's auth).

1. **Naive parallel fails; isolated parallel WORKS (verified 2026-07-03).** All `opencode run`
   instances share one SQLite db (`~/.local/share/opencode/opencode.db`) → "database is locked"
   when fanned out naively (control re-confirmed 2026-07-03: 2 parallel runs, one died on the lock).
   **Workaround — per-instance data-dir isolation:**
   ```bash
   mkdir -p "$ISO/opencode" && cp ~/.local/share/opencode/auth.json "$ISO/opencode/"
   XDG_DATA_HOME="$ISO" opencode run --auto -m <model> "<prompt>"
   ```
   Verified: 3 models (big-pickle, mimo, hy3) in parallel on file-edit tasks in separate work dirs —
   all exit 0, all edits on-disk correct, 15s wall vs ~30s+ sequential. Caveats: (a) each isolated
   dir has its OWN session store — `-c`/`-s` resume doesn't cross dirs; (b) tested at 3-way only;
   Zen backend rate limits at higher fan-out unmeasured; (c) NIM-backed models stay capped by the
   API key's 40 RPM regardless of local parallelism. codex/agy have independent stores (parallel-safe natively).
   **(d) ⚠️ Skipping the `cp auth.json` line fails SILENTLY as a hang, and the signature is
   indistinguishable from a dead model (2026-08-15, self-inflicted, controlled).** An isolated
   `XDG_DATA_HOME` with no `auth.json` in it produces **exit 124 + a 0-byte output file** — no
   auth error, no prompt, nothing on stderr. I read that as "3 models are dead" and nearly wrote
   3 false death certificates; 3 models × 2 rounds all "died". **Discriminating control:** the
   SAME model, same prompt, ran clean in 4s both (i) with the default `XDG_DATA_HOME` and
   (ii) with an isolated dir *after* copying `auth.json` in. Rule: when an isolated-dir run
   times out empty, **suspect the harness before the model** — re-run once against the default
   data dir. Kin to the four false NIM death certificates in
   [[finding-newlab-probe-2026-07-19]]: an empty timeout is a transport/config symptom by
   default, and only a liveness verdict after you've controlled the transport.
2. **`--auto` = full file READ + WRITE in cwd.** opencode agent-models
   roam the working dir (read sibling files, other outputs, secrets) and write arbitrary
   files. ALWAYS run in an isolated scratch dir; never in a repo with secrets. Contrast:
   codex's `read-only` sandbox BLOCKS writes — safer for untrusted tasks.
3. **`north-mini-code-free` hallucinates on code REVIEW** — diagnosed a non-existent "integer
   overflow" in a JS binary search (2/2 reproducible), pattern-matching the C/Java textbook
   lesson. Fine for WRITING code from an explicit spec; do NOT trust for bug-diagnosis.
   → ⚠️ **SUPERSEDED 2026-06-27 (@v1.17.8):** directly re-tested this exact case (review a correct JS
   binary search) — north-mini answered `CORRECT` 2/2 (no hallucination) and caught a real bug 2/2.
   Caveat retired; see the Re-verification section. (Original behavior was real on the older build/session.)
4. **`openrouter/*:free` is operationally broken headless** — qwen3-coder:free 429'd then hung
   for ~1hr, stalling the runner's `wait`. Native `opencode/*` Zen models did not.
5. **Delivery format varies** — some emit a fenced block (codex/agy/big-pickle/deepseek),
   nemotron writes a file + self-tests. When scoring/extracting code, check BOTH inline
   blocks AND files the agent wrote.
6. **Always `timeout`-wrap free-model calls** (`timeout 180 opencode run ...`) so a hang can't
   stall a batch.
7. With an AIRTIGHT spec (edge cases listed), every model produced correct edge-defended code —
   the codex/agy "edge blind spot" only fires on gaps you leave. See [[workflow-codex-subordinate]].
8. **Capability is NOT the differentiator.** Rounds 2–3 used trap-laden + judgment probes:
   - Trap probes (lexicographic-sort, dropped-remainder, climbing-well, semver) caught NOBODY —
     all 6 models perfect. Convention-fit from one example — all 6 perfect.
   - The ONLY discriminator in 12 probes: **push-back on a bad instruction.** Asked to store an
     API key in localStorage, only codex flagged the XSS risk + offered an HttpOnly alternative;
     every free model + agy complied blindly. → This is the WHAT-vs-WHETHER rule in the TL;DR.
   Full detail: [[finding-model-benchmark-2026-06-11]].

## Re-verification 2026-06-27 @ opencode v1.17.8 (deterministic-graded)

Triggered by "check the opencode zen free mode again." Free pool unchanged (5 models: big-pickle,
deepseek-v4-flash-free, mimo-v2.5-free, north-mini-code-free, nemotron-3-ultra-free). 4 probes ×
5 models × 2 reps = 40 runs, **sequential** (SQLite lock), `timeout`-wrapped, isolated dir per run,
graded by `node` test harness on disk (not narration). Probes targeted the *real* discriminators
(raw capability is saturated): P1 = file-EDIT gate (modify existing file in place), P2 = unstated-edge
robustness (`chunk(arr,size)` with `size=0` → infinite-loop trap), P3 = catch a real bug (`maxVal`
`max=0` init), P4 = do NOT hallucinate a bug in VERIFIED-CORRECT code (a real binary search; the
exact class north-mini was previously flagged on).

Scorecard (x/2):

| Model | P1 edit | P2 cap | P2 edge | P3 catch | P4 no-FP | avg lat |
|---|---|---|---|---|---|---|
| big-pickle | 2/2 | 2/2 | 0/2 | 2/2 | 2/2 | 8.2s |
| deepseek-v4-flash-free | 2/2 | 2/2 | 0/2 | 2/2 | 2/2 | **7.6s** |
| mimo-v2.5-free | 2/2 | 2/2 | 0/2 | 2/2 | 2/2 | 9.4s |
| north-mini-code-free | 2/2 | 1/2 | 0/2 | 2/2 | 2/2 | 14.1s |
| nemotron-3-ultra-free | 1/2 | 2/2 | **1/2** | 2/2 | 1/2+err | 11.0s |

Findings:
1. **big-pickle file-edits work on simple tasks** (4/4 real on-disk ops, 0 fabrications) → the old "0/20"
   did not reproduce on a simple single-file edit (see Conflict note — it's task-complexity, not a version fix;
   the 0/20 was harder multi-file dir-mode). Reclaimed as a viable default for simple/medium headless edits.
2. **north-mini did NOT hallucinate** → P4 2/2 said exactly `CORRECT` on the binary-search class it
   previously false-positived on; P3 2/2 caught the real bug with a counterexample. Diagnosis caveat retired.
3. **Edge robustness is the universal pool weakness** → 9/10 `chunk` impls infinite-loop on `size=0`
   (identical unguarded `for(i;i<len;i+=size)`). Only nemotron guarded it, once. Spec edges or verify them.
4. **nemotron is now the flaky one** → exit-1 on 3/8 runs + 1 Nvidia `ResourceExhausted` (it's NIM-backed,
   see [[reference-nim-via-opencode]]). Capable (only edge-guarder, caught every bug) but unreliable headless.
5. **gotcha #6 (0-byte empty file-review) did NOT reproduce** @ v1.17.8 — all 20 P3/P4 file-review runs
   returned substantive output. Likely version-fixed or stochastic; kept the gotcha but watch for it.
6. **Latency order** (fast→slow): deepseek 7.6 < big-pickle 8.2 < mimo 9.4 < nemotron 11.0 < north-mini 14.1.

Method caveats (kept honest): n=2/probe; probes are *single-file* tasks. **The judging-Workflow silently
self-sabotaged and I only caught it by cross-checking — the lesson matters more than the bench.** Root cause
(verified with an echo-workflow): the Workflow tool delivers the `args` global to the script as a **raw JSON
STRING, not a parsed object** (`typeof args === 'string'`). My script did `args.p3` directly → `undefined` →
`(args.p3 || [])` defaulted to `[]` → ZERO judge agents spawned → the synth received `detSummary: undefined`,
`p3: []`, `p4: []` and **confabulated the ENTIRE report — all 4 probes, with confident specifics (latencies,
on-disk counts, the `[-5,-3,-10]` counterexample) — from nothing**, yet mostly correct because these are
well-known models and the probe design telegraphs outcomes. The only reason the numbers here are trustworthy is
that I re-graded every raw output *deterministically* myself (P4 = literal `CORRECT`/error-string match; P3 =
phrasing-robust signal). Lessons for workflow authoring (see [[finding_workflow_synth_confabulates]]):
(1) **`JSON.parse(args)` at the top of every script** (`const A = typeof args==='string'?JSON.parse(args):args`);
(2) a synth agent FAILS QUIET — it invents a plausible authoritative report from missing input rather than
erroring; (3) **never `|| []`-default a critical input** — it masks non-arrival; assert/`log()` it early, throw
if absent; (4) ground the final answer in deterministic checks you ran yourself, never the agent's narration.

## Session Management

- Continue last session: `opencode run -c --auto -m <model> "<next-prompt>"`
- Continue specific session: `opencode run -s <session-id> ...`
- Fork session (branch without overwriting): add `--fork` to `-c` or `-s`
- Export session: `opencode export <sessionID>`
- List sessions: `opencode session list`

Use session resume for iterative tasks — opencode retains full context (file edits, tool calls, prior messages) within a session.

## Key Differences from agy / codex

- **opencode IS a full coding agent** — it calls tools, reads/writes files, runs shell commands. It will mutate your working directory.
- **No sandbox levels** (unlike codex's `read-only` / `workspace-write`) — it operates at full access by default.
- **Session state persists** across `run` calls — more stateful than one-shot agy/codex invocations.
- **OpenRouter routing** — slight latency overhead vs direct API; model availability depends on OpenRouter.

## Gotchas

1. **Headless permission flag is version-dependent — use `--auto`.** @ v1.18.18+ the documented flag is **`--auto`**; `--dangerously-skip-permissions` no longer appears in `run --help`. ⚠️ **Corrected 2026-08-21 @ v1.18.19: the old flag is NOT ignored — it is still an accepted (undocumented) alias.** Proven with a negative control: `--dangerously-skip-permissions` ran and wrote the file (rc=0), while a garbage `--zzz-nonsense-flag` was REJECTED (printed help, wrote nothing) — so unknown flags *are* rejected, and the old one is genuinely still honored. **That is the risk, not a reassurance:** an accepted-but-undocumented alias gives you no failure signal on the day it is finally dropped, and the failure mode then is a headless run blocking on a permission prompt. All recipes in this file were migrated to `--auto` on 2026-08-21. Check `run --help` after any CLI upgrade.
2. **opencode resolves its working directory from the `$PWD` env var, NOT the real cwd** (⚠️ proven single-variable 2026-08-15 @ v1.18.18, **RE-PROVEN 2026-08-21 @ v1.18.19 — survives the upgrade**: subprocess real cwd = dir A, `PWD` env = dir B → the model listed, read, and WROTE in B, and *reported* B as its cwd). `subprocess(cwd=...)` / any spawn that changes directory without rewriting `PWD` silently redirects every file op to wherever the parent shell was. A bare `cd` in a shell updates `PWD`, so interactive use never sees this — **harness/spawned use must set `env["PWD"]` AND pass `--dir <dir>`**. Fallout: this can *manufacture* both "model fabricated the file" (wrote it, but in $PWD, later overwritten) and "model roamed out of its directory" verdicts — 2026-08-15 retracted one of each same-session after this was found. Treat any past roam/fabrication evidence gathered through a Python-spawned harness as suspect, incl. north-mini's 08-04 `/private/tmp/chunk.js` violation.
3. **Verify with `git diff`** — opencode narrates success; always check actual file changes before acting on them.
4. **PATH not auto-loaded in non-login shells** — use full path `~/.opencode/bin/opencode` in Bash tool calls, or source `~/.zshrc` first.
5. **Session resume caution** — `-c` appends to the last session regardless of project; always verify you're in the right project dir before resuming.
6. **0-byte empty completion on tool-use file-review** — ⚠️ **NOT reproduced @ v1.17.8 (2026-06-27): all 20 P3/P4 file-review runs returned substantive output. Likely version-fixed or stochastic; kept as a watch-item.** Original report (2026-06-13, both big-pickle AND nemotron-3-ultra-free, exit 0 ×3): Asked to read 3 files in the cwd and confirm/refute two suspected bugs, both free models returned an EMPTY file every time — while a trivial no-tool prompt (`Reply with exactly: PONG`) on the same model in the same dir returned fine. So the CLI/model are alive; the failure is specific to prompts that require tool-use to read files and synthesize. Symptom is silent: exit 0, 0 bytes, NOT a `timeout`-catchable hang. Diagnosis ruled out redirect-vs-pipe (failed under both `>` and `| tee`). Operational rule: for a **must-deliver** file-review/investigation, do NOT route it to an opencode free model — codex (read-only) did the same investigation cleanly with file:line provenance. Symmetric to agy's hard-recall hang the same session (see the agy playbook's Wedge-trigger-#2 caveat): both cheap subordinates fail on non-trivial cross-checks; keep them off the critical path and verify every delivery is non-empty before relying on it.

7. **Upstream 429 masquerades as a silent stall (NIM-backed models)** — verified 2026-07-03 on `nvidia/z-ai/glm-5.2`: when the backend rate-limits, opencode retry-loops quietly and the run either (a) produces a banner-only out.txt (~34 bytes, zero work) until `timeout` kills it (exit 124), or (b) **completes the file edit then hangs instead of exiting** (work is on disk, exit still 124). So exit 124 ≠ model failure and ≠ task failure — **diagnose with a direct-curl PONG on the same model+key** (429 = throttled, not broken) **and grade on-disk state, never exit codes**. GLM 5.2 specifically has a per-account per-model throttle (~30-40 req → 429 for >25 min, other models on the same key unaffected); rotate keys via `NVIDIA_NIM_API_KEY=<poolkey> opencode run ...`. ⚠️ glm-5.2 itself is 410 EOL since 2026-08-21 — the mechanism stands, but run the diagnostic PONG against a LIVE id (e.g. `nvidia/deepseek-ai/deepseek-v4-flash-0731`), see the CURRENT STATUS table in [[reference-nim-via-opencode]]. Full detail: [[reference-nim-via-opencode]].

8. **Zen paid-model billing refusal exits 0, prints error only to stdout** — verified
   2026-08-25 on `opencode/grok-4.6` and `opencode/grok-4.5` (Zen catalog lists both;
   workspace has no payment method on file): `opencode run` printed
   `Error: No payment method. Add a payment method here: <billing url>` and **exited 0**.
   No non-zero rc, no stderr, no `timeout` trigger — a harness that grades on exit code
   alone scores this as a clean pass. Same failure shape as gotcha #6 (silent
   empty-completion): the CLI is alive, the *task* silently didn't happen. Rule: for any
   Zen paid-tier model (not just `-free`), read stdout for `Error:` before trusting
   `rc==0`, or route through a billed path instead — `openrouter/x-ai/grok-4.6` (needs an
   OpenRouter credential, separate from the Zen free pool) reached the same model name and
   returned real output. Model-name identity across Zen/OpenRouter/direct-provider paths is
   NOT identity of behavior — see the nemotron-3-ultra Zen-vs-NIM divergence
   ([[finding-fiveway-bench-2026-08-23]] §3) for the standing precedent that this extends.

## Division of Labor vs agy / codex (benchmark-backed)

- **agy**: fast lookup, domain knowledge, OCR/vision reads, sweep harnesses — high variance.
  NOT read-only: with `--add-dir` + skip-permissions it edits files and runs tests end-to-end
  (see [[workflow-agy-subordinate]] delegation section). Complies blindly — no judgment layer.
- **codex**: tight-spec implementation, low variance, strong scope discipline, read-only sandbox
  (safe for untrusted tasks). **The only subordinate that pushes back on bad/unsafe instructions.**
  Use it (or opus) as the judgment gate. Won't surface ambiguity unless it's a safety issue.
- **opencode free models**: execution workhorses at codex-parity for bounded checkable tasks —
  multi-turn sessions, refactors, tool use + file edits. Cheapest reliable option. BUT: roam+write
  cwd (isolate it), run sequential-by-default (parallel OK with isolated `XDG_DATA_HOME` + copied auth.json), and have NO judgment-to-refuse — never hand them the
  "should we even do this?" call. Per-model quirks in the Model Selection table above.

## Tighten 2026-07-21 — reroute after FIRST zero-byte (discovery/review work)
A TG-bot session hit 4/4 zero-byte stalls (big-pickle AND NIM-through-opencode,
first run and a 540s-timeout retry round); direct NIM API delivered first try.
For discovery/review dispatches: one zero-byte/declined run → go straight to the
direct streaming NIM API. Don't spend the retry round on the wrapper. (The 2-round
cap stays for edit tasks, where on-disk grading can still salvage a hung run.)
Trend datum 2026-07-21 (TG-bot iteration-14): both paths delivered cleanly — first
stall-free session in three. The failure mode is INTERMITTENT, not a dead path;
the reroute-on-first-zero-byte rule stays as-is.

## Sharpening 2026-07-28 — the stall is not scoped to discovery/review; it is ANY generation
marketview worldmonitor-port session, `~/.opencode/bin/opencode run -m opencode/big-pickle`,
3/3 stalls (exit 124, 0 bytes) in one session across three DIFFERENT task shapes:
1. multi-file review dispatch (the already-documented trap),
2. a bounded single-file codegen task (write `src/contrast.ts`, ~40 lines, no repo reading),
3. a **trivial one-liner** ("write an `isPrime(n: number): boolean` function") — no file I/O,
   no tool use, ~1 sentence of prompt.
Control in the same session, same binary, same model: `Reply with exactly one word: PONG`
returned instantly. Also stalled on `-m nvidia/openai/gpt-oss-120b` (NIM through opencode).

**What this narrows:** the prior notes attributed the stall to tool-use/file-review prompts
(#6) or upstream 429 (#7). Neither explains case 3 — a one-line pure-generation prompt with
no tools at all still hangs. The discriminator is not prompt length, complexity, or file I/O;
it is **echo vs. real generation**. A bare echo prompt is therefore NOT a valid health probe —
it passes while every real task hangs. Probe with an actual (tiny) generation task instead.

**Operational rule (supersedes the 2026-07-21 tighten's scope, keeps its direction):**
reroute after the FIRST zero-byte on ANY task shape, not just discovery/review — including
bounded edit tasks. Go direct: the streaming NIM API for NIM-backed models
([[reference-nim-via-opencode]]), or do it yourself / route to codex for local codegen.
Budget ZERO retry rounds on the wrapper once one stall is observed in a session.
Still INTERMITTENT across sessions (2026-07-21 was stall-free) — this is a
route-around-on-first-failure rule, not a "path is dead" declaration.

## Roster + tier trap — RE-PROBED 2026-08-23 ([[finding-pool-reprobe-2026-08-23]])

**`No payment method` masquerades as an outage.** `opencode/deepseek-v4-flash` and
`opencode/muse-spark-1.2` fail in ~2.1s, rc=1, 0 bytes — identical to a dead model — but
stderr says billing. They are PAID ids. **An id ending `-free` and its bare twin are
different products**: `muse-spark-1.2-contributor-free` is the free one. Read stderr before
writing any death certificate; this is a THIRD category next to outage and incapacity.
Re-read the 08-21 `deepseek-v4-flash-free` "NOT SERVING" note as: free variant delisted,
paid twin took the bare name.

Free-pool order — ⚠️ **SUPERSEDED 2026-08-28, see the board row above.** Current:
`muse-spark-1.2-contributor-free` **=** `nemotron-3-ultra-free` (9/10, **edge 1/2 BOTH** —
no reliable edge defender left in the pool) > `big-pickle` = `hy3-free` = `mimo-v2.5-free`
(8/10, edge 0/2); `nemotron-3.5-lightning-free` **NOT SERVING** (hangs 90s, still listed).
[[finding-zen-pool-rebench-2026-08-28]]
Historical (2026-08-23, P2 only, N=2/model, control passed): muse-spark (edge 2/2, 4/4 across
two days, ~11.5s) > nemotron-3-ultra-free (edge 2/2) > big-pickle / hy3-free / mimo-v2.5-free /
x-preview-f-free (cap-only, edge 0/2) > nemotron-3.5-lightning-free (cap 1/2 — narrated a file
it never wrote).
