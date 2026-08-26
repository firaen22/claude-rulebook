---
name: reference-subordinate-routing-map
description: "Which of the 5 subordinates (codex / agy / grok / opencode / NIM) to route a task to, and why. Spine: 7 same-task-set comparisons exist across the fleet (7th added 2026-08-25) — this file separates those from reasoned defaults. THE cross-fleet rule: no tier is safe on unstated edges, and no tier's self-report is evidence."
metadata:
  node_type: memory
  type: reference
---

# Subordinate routing map — 2026-08-23

Per-tool operating detail lives in the playbooks; this file is ROUTING only.
[[workflow-codex-subordinate]] [[workflow-agy-subordinate]] [[workflow-grok-subordinate]]
[[workflow-opencode-subordinate]] [[reference-nim-via-opencode]]

## 0. Two rules that override every row below

**R-A — No tier defends unstated edges. Spec them, always.** This is the only property
measured on all five and it fails on all five: codex drifty (sol/terra 0/2 on `chunk(arr,0)`
→ family 36/36 twelve days later, same model strings); agy K1 FALSE at every tier both years
(1/5, 0/5, 2/5 at 3.6; 3/5, 0/5, 0/5 at 3.7, N=315 combined); grok 0/16 deterministic, same
naive loop every run; free pool 5 of 7 serving models infinite-loop — **`muse-spark-1.2-contributor-free`
(4/4 across two days) and `nemotron-3-ultra-free` (2/2) are TWO standing exceptions**,
re-probed 2026-08-23 and hand-verified in source. Spelling the edge out costs one line and
grok then guards 11/11.
**Corollary: the "spec the edges" rule has been over-generalized and retracted TWICE**
(08-04, 08-15) — say "no tier is reliable", never "no model can".
**R-A stands as of 2026-08-25, but with one partial exception and one measurement rule:**
- `agy gemini-3.7-flash-low` guards 15/20 on a fresh-day repeat of the frozen probe
  (prior 14/20, p=1.000; `-medium` 4/20 the same day, same prompts). Best non-free
  edge behavior measured on any tier — still 75%, still below the K1 ≥4/5-per-paraphrase
  bar (P1_terse 1/4 even for `-low`), so it does NOT exempt anything from R-A.
- **Never compare an edge-guard number against a prior measured on a DIFFERENT prompt
  phrasing.** Same-day, same model, `-medium` scored 9/10 on a new phrasing and 4/20 on
  the frozen old set (p=0.0004) — pure instrument difficulty. This retracts the
  cross-prior comparisons in the 2026-08-25 fleet probe (agy/grok/NIM/opencode); their
  cross-TIER ranking, which shared one prompt, survives. Same-instrument or no comparison.
  → [[finding-geminimd-and-fleet-probe-2026-08-25]] Result 5.

**R-B — No tier's self-report is evidence. Grade on disk.** grok returned schema-valid
`{file_created: true}` with `num_turns:1` and zero tool calls (3/10); opencode agents narrate
a file and write nothing; agy fabricates claims about files not inlined in the packet; codex
quota exhaustion surfaces as a silent `no-change`, not an error. Read the file back.
**The REVIEW-side corollary (2026-08-27): a reviewer's all-clear is a self-report too.**
grok returned a schema-valid `findings: []` / all-claims-survived verdict on a diff carrying
a defect that two independent lenses (Claude + codex) found and reproduced the same hour.
A clean review verdict counts only when a second lens agrees or you reproduce the pass —
same rule as a green test count, [[finding-test-validity-failure-modes]].

**R-C — Deliverable-is-a-scanner ⇒ the dispatch must require executing it.** Measured on
codex only (2026-08-24, decisive force-load probe): dominant failure 5/18 runs shipped a
scanner whose scan never executes, FLAT across every rule/skill configuration — ambient
doctrine (skills, AGENTS.md prose) did not move it. The countermeasure is in the acceptance
criteria: run the deliverable on one known-positive + one known-negative input, both outputs
in the report (now baked into `30-delegation-templates.md` universal rules). Extension to
the other four tiers is REASONED, not measured — but it composes with R-B, so it costs
nothing to require. Red-test corollary: injected failures must be reachable; a failing line
after `exit` reports green.

## 1. The FIRST routing question: WHETHER vs WHAT

The sharpest measured separation in the whole corpus, and it is not about capability.
On N=12 probes containing an insecure pattern (API key → localStorage), **only codex and
Opus refused; every free model complied blindly.** Execution parity is real; judgment parity
is not.

> **Delegate the WHAT, never the WHETHER.** "Is this sound / safe / the right approach?"
> → codex or Opus. "Build this specified thing" → cheapest tier that clears the bar.

## 2. Route-to table

| Task | Route to | Basis |
|---|---|---|
| "Should we?" / safety / soundness / accepting a design | **codex** (or Opus) | MEASURED N=12, only tier that refuses |
| Airtight-spec implementation, single file | **free pool** (`muse-spark-1.2-contributor-free` → `nemotron-3-ultra-free` → `big-pickle`; AVOID `nemotron-3.5-lightning-free`) | MEASURED — Zen 4-probe pool bench 08-21 + P2 re-probe 08-23 (the N=57 battery is the NIM direct-curl line, not these Zen ids) |
| Tight-spec pure function, no file edit needed | **NIM direct curl** | fan-out at 40rpm×3 keys; opencode wrapper is ~6/min |
| Same, but needs the file actually edited | **opencode** (only free tier with an agent layer) | 4/4 clean on simple single-file |
| Enumerating ambiguities in a spec BEFORE building | **codex as spec-reviewer** | MEASURED N=1016; run this pass first |
| Adversarial edge-hunting, PRE-implementation | **agy** `gemini-3.7-flash-medium` | 24/24 recall, 0/32 fabrication w/ escape clause |
| Reviewing a large real-repo packet | **agy** `gemini-3.6-flash-high` (review pin) | pin held on measurement, N=30, p=1.000 |
| Structured/JSON-schema fan-out, N verdicts parsed | **grok** | 16/16 adherence + free cost telemetry (SINGLE-ARM) |
| Third review lens after codex (diff/rules-file review) | **grok, ONLY as: everything inline in the prompt + pure judgement (zero file reads) + `--json-schema` + isolated HOME** | 2/2 delivered with this shape vs 0/3 idle (narrates, exits) with read-then-analyze packets — fix is packet SHAPE, not retry, [[finding-grok-idle-vs-parser-2026-08-27]]. n=2/n=3, one task family. Its finds are real (caught a dropped order codex passed) but its all-clears are void (R-B corollary) |
| Ordinary spec'd implementation, want to spare codex quota | **free pool first** (`muse-spark-1.2-contributor-free`), grok if the free pool is unavailable | MEASURED 08-23 same-window five-way: free 10/10 > grok-default 9/10 > grok-isolated/NIM/big-pickle 8/10 |
| Anything with a loop / iteration / termination edge | codex or agy — or grok WITH the edge stated | PROVISIONAL, n=3, p=0.17 pooled |
| Same, but the edge CANNOT be stated (unstated-edge exposure is the risk) | **agy `gemini-3.7-flash-low`** — then verify by execution regardless | 15/20 fresh-day repeat (prior 14/20, p=1.000); `-medium` 4/20 same day. NOT safe, just least-bad |
| Post-implementation code review on a real repo | **NOT agy** | adoption 0/5, 0/5, 1/5, 3/8 across 4 sweeps. Scope note 2026-08-25: on a SMALL single-file seeded-defect review, codex and agy TIED 8/8 vs 8/8 (saturated instrument) — this row does not generalize down to small single-file review, stays scoped to large real-repo packets → [[finding-step4-seeded-review-2026-08-25]] |
| Multi-file / long-horizon agentic work | **none of them — do it yourself** | UNMEASURED on all five; opencode 0 edits on 20/20 hard |

## 3. Per-tool one-liners

- **codex** `gpt-5.6-luna` — the only judgment tier. Whole 5.6 family saturates every hard
  axis, so pick on cost not capability; lowest run-to-run variance (1 run is representative).
  *Weakness:* silently fills spec gaps — never hand it an ambiguous brief; quota strands
  mid-batch with no error; long final answers can vanish from captured stdout.
- **agy** `3.7-flash-medium` (review: `3.6-flash-high`; **unstated-edge exposure:
  `3.7-flash-low`, 15/20 vs medium's 4/20 same day — effort is NON-monotonic on edges,
  so this is a per-task pick, not a tier upgrade**) — free, fast, best PRE-impl adversary,
  zero fabrication with the escape clause. *Weakness:* useless post-impl on real repos;
  17% empty returns at ~8KB (ALWAYS retry, an empty is not "no findings"); bare `agy -p`
  is not the pinned model — always pass `--model`. `-low` is NOT promoted to general
  default: medium's justification is transport, and `-low` had the worst transport of the
  3.6 arms (3 timeouts/35 vs medium's 1); 3.7-low transport is unmeasured at scale.
- **grok** `grok-4.6` — third option at ceiling, best structured output, SUBSCRIPTION-billed
  (SuperGrok flat plan — the ~$0.005/run telemetry is reported, not billed; the metered path
  is `openrouter/x-ai/grok-4.6`, a separate product), effort tiers are FLAT (don't build effort routing). *Weakness:* slowest of
  the three (16.1s vs 8.5/9.2); provisional HANG-class miss; **ingests `~/.claude` by
  default → not an independent review lens, and any benchmark without an isolated HOME is void**;
  IDLES on multi-step read-then-analyze packets (narrates a plan, exits, rc=0 — re-shape
  inline + pure judgement + schema, do not retry); its review all-clears are void per R-B.
- **opencode** — the free agent layer: the only free path that edits files. Isolated scratch
  dir + `timeout` + sequential by default (parallel OK with isolated `XDG_DATA_HOME` + copied auth.json). *Weakness:* no judgment-to-refuse; reliability (not
  reasoning) ceiling on multi-file; `$PWD`-not-cwd bug still live at 1.18.19 — set `env["PWD"]`
  AND `--dir` or your verdicts are artifacts (it has manufactured two retracted findings).
- **NIM** — a model backend, not an agent; `nvidia/<vendor>/<model>`. Direct curl for
  parallel fan-out; opencode-NIM only when file edits are needed. *Weakness:* catalog lies
  (listed ≠ callable); non-streaming gateway kills at ~60s and has produced FOUR false death
  certificates — always smoke with `stream:true`.

## 4. Compose them: routing beats any single tool

**Routing > best-single is the most replicated result in the corpus** — 2024/2024 enumerated
triples (mean +4.5, never negative) and 97% vs 93% at N=1016. **Runtime voting is a wash
(54.9%) — do not build voting infra** ([[finding-voting-vs-single-verification]]).

Default chain for a non-trivial build:
1. **codex** spec-review → enumerate ambiguities (kills R-A and codex's own gap-filling).
2. **agy** pre-impl adversary → edge list, before code exists.
3. Cheapest tier that clears the bar implements, edges now STATED.
4. Fresh-context acceptance review (R1) — never the implementer, never self.

**Steps 1-3 MEASURED 2026-08-25** (first end-to-end test, previously reasoned-only): same
implementer (`muse-spark-1.2-contributor-free`, this table's own §2 pick), same model,
same grader, only the upstream ambiguity/edge text differs — **CHAIN 5/5 GUARD vs
BASELINE 0/5 GUARD** on the unstated `size<=0` edge (Fisher p≈0.008). All 5 codex lists
named the target edge — the chain worked because it manufactured the missing spec, not by
accident. N=5/arm, PROVISIONAL, single task shape (one pure function, one classic edge).
→ [[finding-chain-vs-direct-2026-08-25]]

**Step 4 MEASURED THREE TIMES 2026-08-25, all SATURATED — and the replication is what
makes it a finding.** Run 1 (8 defects / 41 lines, billing): 15/15 reviews scored 8/8
([[finding-step4-seeded-review-2026-08-25]]). Run 2 (3 defects / 195 lines, access
control — **12.7× lower density**): 15/15 scored 3/3
([[finding-step4-sparse-density-2026-08-25]]). Run 3 (4 defects / 140 lines, scheduling,
instrument written by an **independent hypothesis-blind author**): 14/14 non-empty scored
4/4 ([[finding-step4-independent-ledger-2026-08-25]]). Saturating across three domains,
three densities and an outside author is not an easy-instrument artifact — **step-4
seeded recall is ROBUST, and step 4 earns its place in the chain.** All three runs: zero
tier differentiation on seeded recall (codex = agy = free), which is what retracts §2's
"NOT agy post-impl" as a blanket rule — see the scope note on that row.

**Seeded recall is still the wrong metric, but the tier gap on the right metric is now
REFUTED, not merely unproven.** Run 2's Rule-3 pass found 7 real defects where the ledger
claimed 3 — and one soundness-gate REFERENCE carried a missed bug while scoring 13/13 —
which produced a post-hoc split of codex 6.2 total-verified-real/run vs agy 4.2 ≈ free
4.0. Run 3 pre-registered exactly that question with the metric narrowed to UNSEEDED
defects and the ledger authored by someone other than the experimenter: **codex 0.6 vs
free 0.4 vs agy 0.0, gap 0.2, inside the frozen ≤0.5 "H1 fails" band.** Do not cite
6.2/4.2/4.0 — it is withdrawn. What survives: a tie on a seeded ledger is weak evidence
of reviewer equivalence, and **no tier ranking for step 4 is established in either
direction.** Route step 4 on cost. N=5/arm throughout, PROVISIONAL.

## 5. What is NOT established (do not claim these)

- The §4 chain's steps 1-3 are no longer purely reasoned — see the citation in §4 above
  ([[finding-chain-vs-direct-2026-08-25]], N=5/arm, single task shape). Step 4 is now
  measured three times and holds — see §4. What is still NOT established for step 4: any
  tier ranking, in either direction. All three runs tied on seeded recall; the one axis
  that appeared to separate them (unseeded real-defect discovery) was post-hoc, and the
  pre-registered independent-author replication **failed to reproduce it** (gap 0.2 vs a
  frozen 0.5 threshold — [[finding-step4-independent-ledger-2026-08-25]]). Route step 4
  on cost. Caveat before anyone re-opens this: that instrument contained only ONE unseeded
  defect, so it cannot distinguish "no edge" from "no resolving power" — a re-test needs
  ≥4 independent unseeded defects, still independently authored.
- **Crediting a review for naming the topic is not the same as crediting it for a claim
  that verifies.** In run 3, executing each file's OWN cited example (rather than accepting
  the topic match) removed two codex files whose examples produced byte-identical output to
  both references. That single granularity change moved codex 5/5 → 3/5, the gap 0.6 → 0.2,
  and the verdict INDETERMINATE → FAILS. Rule 3 applies per claim, not per topic.
- **A seeded ledger is not the defect count.** Three separate experiments in this corpus
  have now had the harness author's ground truth turn out incomplete, with reviewer
  "false positives" verifying as real (EXP-6 9→12; the 08-25 billing rounding-order find;
  the 08-25 sparse run 3→7, where a soundness-gate REFERENCE also carried a missed bug
  while passing 13/13). Rule 3 (execute every extra before scoring it a false positive)
  is load-bearing, not ceremony — and padding tests added to bound unintended defects
  bounded nothing, because missed defects live off the tested surface by construction.
- Only SEVEN same-task-set comparisons exist across the fleet. The 7th (2026-08-25,
  agy/grok/NIM/opencode on one edge probe + one honesty probe,
  [[finding-geminimd-and-fleet-probe-2026-08-25]]) is **cross-TIER valid only** — all four
  shared one prompt, so the ranking holds (agy 9/10 > NIM 8/10 > opencode 5/10 > grok 0/10),
  but every comparison it made against a STORED prior is retracted: that prompt turned out
  to be an easier instrument than the priors were measured on (Result 5). It did establish
  **0 fabrication in 54/54 honesty reps across all four** — the first honesty measurement on
  grok/NIM/opencode, though with the escape clause present, so it measures "takes the out",
  not baseline. The six older ones: grok/codex/agy (N=12/arm,
  3 of 4 tasks saturated); codex-vs-agy Round 2 (N=60, TIE — Round 1's "codex=correctness,
  agy=architecture" split was a LENS artifact and is RETRACTED); free-NIM vs codex vs agy
  tight-spec (N=57, parity); judgment-to-refuse (N=12); routing-vs-single; grok vs
  opencode-free vs NIM one-window five-way (N=2/arm, [[finding-fiveway-bench-2026-08-23]]).
  Everything else here is single-arm capability plus reasoning.
- **08-23 same-window five-way bench closed this**: `muse-spark-1.2-contributor-free` (free)
  10/10 beat `grok-4.6` default-config 9/10, grok-isolated/NIM/opencode-control all 8/10 —
  free pool wins on this task set ([[finding-fiveway-bench-2026-08-23]]). Same run found
  grok-default guarded 1/2 unstated edges vs grok-isolated's 0/2 (⛔ RETRACTED 08-25: the
  N=6 default-config repeat scored 0/6 — the 1/2 was noise, [[finding-grok-defaultconfig-p2-2026-08-25]];
  isolate for capability benches regardless) and NIM-served `nemotron-3-ultra-550b` scored
  edge 0/2, the OPPOSITE of Zen-free `nemotron-3-ultra-free`'s 2/2 — do not carry a Zen-free
  score onto a same-named NIM id.
- No tool has been measured on multi-file, long-horizon, or ambiguous-spec work. The
  parity claims explicitly do NOT extend there.
- Free-pool scores are point-in-time SERVING facts, not model properties (big-pickle's edge
  guard regressed 2/2→0/2 across two days). Re-probe; never reuse a stale number.
  **Sharpened 2026-08-25: before blaming serving drift, check the INSTRUMENT.** An apparent
  agy 5/30→9/10 jump looked like drift and was pure prompt phrasing — the frozen old prompts
  still scored 4/20 vs 2/20 eleven days earlier (p=0.661). Two consequences: (a)
  `muse-spark`'s 4/4 "standing exception" above scored 5/10 on the 08-25 prompt — flagged,
  NOT overwritten, because that comparison is instrument-crossed; (b) a re-probe only
  supersedes a prior if it reuses that prior's prompt set byte-for-byte.
- **PAID ≠ DEAD ≠ INCAPABLE.** A fast rc!=0 with 0 bytes reads exactly like an outage but
  may be `No payment method` — read stderr before recording a model as not-serving. TWO
  billing-refusal shapes are documented: Zen `opencode/deepseek-v4-flash` / `muse-spark-1.2`
  fail rc=1, 0 bytes, stderr-only; Zen paid `grok-4.6`/`grok-4.5` exit **0** with the error
  only on stdout. Match on the `Error:`/`No payment method` string, never on rc alone. A THIRD
  transient shape: NIM HTTP 529 `{"type":"Overloaded"}` — retry ≥3× with backoff before recording
  anything (deepseek-v4-flash-0731 went 529 → 200/PONG on retry, 08-25). NIM HTTP 503 and
  transport-level `RemoteDisconnected` are ALSO transient on this endpoint, not just 529 —
  confirmed same day (nemotron-3-ultra-550b-a55b 503→LIVE, deepseek-v4-flash-0731
  XPORT→LIVE). The distinguishing test is persistence across ≥2 attempts, not the shape:
  4 other ids stayed `RemoteDisconnected` on a dedicated retry and are genuinely unroutable
  right now — see [[reference-nim-via-opencode]] FULL CATALOG SWEEP. Also: NIM catalog 404
  (listed in `/v1/models` but no backing function) behaves like 410-EOL operationally —
  don't route it — but is a distinct shape (55/95 ids in the 08-25 full sweep). An id
  ending `-free` and its bare twin are DIFFERENT PRODUCTS on different tiers
  ([[finding-pool-reprobe-2026-08-23]]).
- Cost comparisons are inferred, not measured — NOTHING is CLI-metered in dollars any more
  (grok CLI moved to the SuperGrok subscription 2026-08-25; the metered grok is the separate
  `openrouter/x-ai/grok-4.6` product).
