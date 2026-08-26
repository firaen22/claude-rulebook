---
name: workflow-grok-subordinate
description: "How to use the xAI Grok CLI as a subordinate — invocation, the isolate-HOME requirement, --json-schema envelope + tool-use short-circuit guard, verified capability profile. DEFAULT MODEL 2026-08-23: grok-4.6. ROUTING MEASURED 2026-08-23 head-to-head vs codex+agy: at parity except HANG/termination edges (0/3 vs 2/3, 2/3 — n=3 one task, p=0.17 pooled / 0.40 per-arm, PROVISIONAL). Unstated-edge GUARDED 0/28 isolated-HOME + 0/6 default-config (i.e. 28/28 and 6/6 MISSES) (08-25 N=6 repeat RETRACTED the earlier 1/2 lift as noise) — deterministic across BOTH configs now — the HANG-class real-brief head-to-head result stays PROVISIONAL at n=3; the synthetic-edge behavior is settled, its link to the real-brief HANG failure remains the hypothesis."
metadata:
  node_type: memory
  type: reference
---

Grok CLI (`~/.grok/bin/grok`, v1.0.5 stable, installed 2026-08-23) as a subordinate.
Evidence for every number here: [[finding-grok-cli-bench-2026-08-23]],
[[finding-fiveway-bench-2026-08-23]], [[finding-geminimd-and-fleet-probe-2026-08-25]].
This file is orders only.

> ⚠️ **THE ONE RULE (provisional).** Grok writes the naive loop. On the 3-way head-to-head
> (4 real-repo briefs, N=12/arm) it tied codex and agy 9/9 on NaN- and fabrication-class
> edges but went **0/3 on the HANG class** vs 2/3 and 2/3, emitting a semantically identical
> unguarded `for` loop every rep and OOM-ing each time. **Caveat: n=3 on ONE task, Fisher
> p=0.17 pooled (0/3 vs 4/6; per-arm 0/3 vs 2/3 is p=0.40), and both incumbents drew the
> same naive loop once each** — the direction matches
> the synthetic record (0/16 then, 0/28 now) but this is a hypothesis with one replication,
> not a proven blind spot.
> Until a second HANG-class brief confirms it: state the termination edge whenever you hand
> grok loop/iteration work. Stated edges it guards 11/11, so the cost of the rule is one line.
>
> ⚠️ **Grok ≠ Groq.** Groq is SUSPENDED (NordVPN egress IP blocklisted, 403s before auth)
> and has no CLI at all. Nothing about that applies here. Never type `groq`.

## Invocation — verified working, copy exactly

Single-turn headless (the delegation form):
```
~/.grok/bin/grok -p "<PROMPT>" -m grok-4.6 --cwd <DIR> \
  --always-approve --disable-web-search --no-subagents --output-format plain
```
- `--cwd` is honoured correctly. Proven with a hostile-PWD split (real cwd + `--cwd` vs a
  decoy `PWD` env): the file landed in cwd, decoy stayed empty. **This is NOT the opencode
  `$PWD` bug** — you do not need the `env["PWD"]` dance, though setting it is harmless.
- Models: `grok-4.6` (default), `grok-4.5`. Both authenticate and answer.
- `--always-approve` auto-approves tool execution. It EDITS FILES — give it an isolated
  cwd for anything you would not want touched.
- Prompt from a file: `--prompt-file <PATH>` (avoids HEREDOC/zsh escaping).
- The stderr line `Shell cwd was reset to <project>` is a **benign exit trailer**. The
  agent's own shell `pwd` returns the sandbox — verified directly. Not an escape.

## ⚠️ MANDATORY for any benchmark or A/B: isolate HOME

`grok inspect` shows the CLI ingests **`~/.claude/Claude.md` (~1692 tokens of R0-R8
doctrine), your user Claude skills, and `settings.local.json` permissions** by default.

- **For MEASUREMENT** this is contamination — grok-with-your-harness vs a bare comparator
  is not a comparison. Run under an isolated HOME:
  ```
  mkdir -p "$TMPHOME" && cp -R ~/.grok "$TMPHOME/.grok"    # auth.json MUST come across
  HOME="$TMPHOME" ~/.grok/bin/grok -p ... 
  ```
  Missing `auth.json` = silent hang (same trap as opencode's isolated XDG). Leave grok's
  own ~22 BUNDLED skills alone — vendor defaults are part of what grok is. Rule:
  **strip the operator's config, keep the vendor's.**
- **For REAL WORK** the ingestion is a FEATURE — grok arrives already knowing your rules.
- **Consequence for review:** grok reading your CLAUDE.md means grok and Claude are NOT
  independent lenses. Do not treat a grok review as a cross-model check without isolating
  HOME first. Cf. [[cross-model-review]].

## `--json-schema` — the good part and the trap

`--json-schema '<SCHEMA>'` constrains output and **implies `--output-format json`**.
Adherence measured **16/16 valid-and-matching**. This is grok's real advantage over
agy/opencode for graded fan-out.

**READ THE ENVELOPE, NOT STDOUT.** Output is
`{text, stopReason, thought, usage, num_turns, total_cost_usd, structuredOutput}`.
- The constrained object is **`structuredOutput`**. Parse that.
- Validating the envelope against your own schema scores 0/N and looks like catastrophic
  model failure. It is your bug, not grok's.
- `text` may hold several concatenated JSON drafts. Ignore it.

### 🔴 Tool-use short-circuit — the one hard safety rule

**3/10 schema runs on a file-creation task made ZERO tool calls (`num_turns: 1`), wrote
no file, and still returned `{"file_created": "chunk.js", ...}`.** Free text on the same
prompt wrote the file 14/14. (Attribution to the flag is p=0.059 — suggestive, not
settled. Does not matter: the rule is the same either way.)

- **NEVER accept a schema field as evidence that a side effect happened.** Check the disk.
- **Guard on `num_turns`.** `num_turns == 1` on a task that requires tools means it never
  used one. Cheap, and it caught every instance.
- Pure JUDGEMENT under schema (no side effects) was clean 8/8. The risk is side-effecting
  work specifically.

## Capability profile — verified, N=56+ on the Zen pool harness

| Axis | Result |
|---|---|
| Overall | **grok-4.6 8/10, grok-4.5 8/10** (5 pts/rep × 2) |
| Effort tiers | **8/10 at low, medium, high AND xhigh — flat.** Only latency moves |
| File edit in place, no strays | 4/4 clean |
| Catch a real bug + counterexample | clean |
| No false alarm on correct code | clean |
| **Unstated edge (`chunk(arr, 0)`)** | **guarded 0/28 isolated-HOME** (0/16 original + 0/2 five-way, same instrument; 0/10 fleet-probe 08-25, different/easier instrument) **+ 0/6 default-config** (08-25 N=6 repeat; retracts the earlier 1/2 default-config "lift") **+ 0/6 via `openrouter/x-ai/grok-4.6`** (opencode/OpenRouter path, [[finding-openrouter-grok-p2-2026-08-25]]) — deterministic under both configs AND across serving paths: a model property, not a CLI-scaffold artifact |
| **Edge when the prompt STATES it** | **guarded 11/11** |
| cwd escapes | 0/56 |
| Cost | telemetry reports median **$0.0054/run**, but per user 2026-08-25 the CLI runs under a **SuperGrok SUBSCRIPTION** (flat plan, like codex's quota) — the `total_cost_usd` field is reported, not billed. `openrouter/x-ai/grok-4.6` IS metered (OpenRouter credits, separate) |

**The headline rule: grok does not volunteer guards, but it delivers them when asked.**
0/28 unstated → 11/11 stated. Consistent with non-volunteering rather than incapacity (the probes measure stated-vs-unstated behavior, not the internal cause). Spec every edge explicitly.

**2026-08-25 fleet probe promoted this from provisional to deterministic-under-isolated-HOME** ([[finding-geminimd-and-fleet-probe-2026-08-25]]): 10 fresh isolated-HOME reps across two passes an hour apart, same-hour replication held exactly (0/5, 0/5), all 10 asserted byte-identical to the naive `for (i=0; i<arr.length; i+=size)` loop in the finding (read-back is explicit for pass 1, partial-count for pass 2). Instrument caveat (the finding's own Result 5): the 08-25 reps used a *different, easier* prompt than the 0/16 leg — pooling is direction-safe for grok only because the easier instrument still gave 0, but it is not a same-instrument replication. Grok was the only tier whose number matched its stored prior in that probe ("the most reproducible fact in the entire fleet corpus") — though Result 5 later attributed the other tiers' apparent moves to the easier instrument, so "moved vs didn't move" is itself instrument-confounded. **Scope: deterministic under isolated HOME on this probe family — and, as of the 08-25 N=6 repeat, deterministic under default config too** (see §Default-config lift below; the earlier 1/2 exception was noise, retracted).

Same probe: **0/9 fabrication on the honesty axis (first honesty measurement on grok)** — with the escape clause present, no rep invented an answer; the one documented reply reached for a tool ("I'll look up ... instead of guessing") rather than the escape clause — non-answer, not invention. Caveat: this measures "takes the escape hatch when offered," not baseline honesty absent the clause — always include it.

**Effort does not adapt.** Unlike codex (where effort is the one axis that adapts), grok
is flat across all four tiers. Use the default; do not build effort routing. This
replicates agy's "effort tier ≠ edge safety" on a second vendor.

## Where to use it

### Head-to-head MEASURED 2026-08-23 (vs codex + agy, N=12/arm)

4 real-repo briefs, each tool in its OWN default config: **grok 9/12, codex
`gpt-5.6-luna` 11/12, agy `gemini-3.7-flash-medium` 11/12** — the entire gap is T-A, the
HANG-class task. Numbers and adjudication: [[finding-grok-cli-bench-2026-08-23]].

- **Everything except HANG edges: no separation at n=3.** On NaN-class and fabrication-class
  briefs grok matched both incumbents 3/3, 3/3, 3/3 — every arm saturated, so this shows
  no separation on tasks at ceiling, not proven parity (the same set returned CONFOUNDED
  for agy on 08-14). Still: a legitimate third option for ordinary spec'd implementation.
- **Loop / iteration / termination work → state the edge before handing it to grok.**
  PROVISIONAL: same direction under two configs (synthetic `chunk(size<=0)` isolated-HOME,
  0/16 at the time and 0/28 as of 08-25; real `degTickAngles(step<=0)` 0/3 default
  config), but the real-brief leg
  is n=3 / p=0.17 pooled (0.40 per-arm) and codex and agy each emitted the identical naive
  loop once.
- **Route to grok to spare codex quota, not to save time.** Median 16.1s vs codex 8.5s /
  agy 9.2s (worst task 42s) — latency IS comparative. Slowest of the three. (The old
  "cheapest metered ~$0.005/run" framing is STALE as of 2026-08-25: the user runs the CLI
  under a SuperGrok subscription, so it is quota/flat-billed like codex, not metered —
  the $0.0054 telemetry is a reported number, not a bill. Route-to-spare-quota now means
  spreading load across two flat plans, not trading quota for pennies.)

### NOT head-to-head — single-arm capability facts and reasoned defaults

No comparative data behind these. They say what grok does, not what to prefer it over.

- **Schema-constrained fan-out** where you need N structured verdicts parsed without
  regex — 16/16 adherence + free `usage`/`cost` telemetry (measured, single-arm; codex and
  agy were never benched on structured output, so "advantage" is inferred from their
  lacking the feature, not from a comparison). Side effects still verified on disk.
- **Well-specced implementation on small briefs**, edges spelled out. *(Reasoned.)*
- **NOT as a cross-model reviewer** until HOME is isolated (see above) — otherwise it is
  reading your own doctrine back to you. *(Reasoned from the `grok inspect` contamination
  finding, not from a review-quality measurement.)*
- **Large packets (~55KB, isolated-HOME, real review dispatch) — first data 2026-08-25:**
  0 empty-return, 0 hang, 6/6 findings reproduced real on TG-bot-helper's iter43 write-
  proposal/reasoning-tier code — notably on code already reviewed by codex×2+agy×2+NIM×2
  in the same campaign round. n=1 packet, but no longer "untested"; the agy-class
  empty-return trap at this size did NOT reproduce here. Full record: TG-bot-helper
  project memory `multitool_improvement_workflow.md` iteration 43b.

## Grok inside OTHER harnesses — probed 2026-08-25

**Standing decision (user, 2026-08-25): grok CLI is the default grok lane** — it is the
only path the SuperGrok subscription covers. The opencode/codex/Claude Code recipes below
all WORK but bill metered OpenRouter credits, and buy no capability (edge-blindness is a
model property, identical in all four harnesses). Reach for them only when grok must run
inside another harness or a bench must exclude the CLI scaffold.

- **opencode**: works via `openrouter/x-ai/grok-4.6` (metered OpenRouter credits; edge
  profile identical to CLI, [[finding-openrouter-grok-p2-2026-08-25]]). Zen's
  `opencode/grok-4.6` is billing-blocked (exits 0 with an Error on stdout).
- **codex (0.149.0): WORKS, verified empirically 2026-08-25** — smoke test + file-write
  task both clean, direct to OpenRouter, no proxy. Recipe (isolated CODEX_HOME):
  top-level `model = "x-ai/grok-4.6"`, `model_reasoning_effort = "low"`, and
  `[model_providers.openrouter]` with `base_url = "https://openrouter.ai/api/v1"`,
  `env_key = "OPENROUTER_API_KEY"`, `wire_api = "responses"` (`"chat"` was removed in
  this codex version). TWO GOTCHAS found on the way: (1) `model_reasoning_effort` MUST
  be top-level — appended after a `[model_providers.*]` table it silently becomes a
  table key, codex then disables reasoning and xAI 400s "Reasoning is mandatory"; an
  earlier BLOCKED verdict here was exactly this TOML-placement error. (2) `codex exec`
  under a non-TTY needs `</dev/null` or it waits on "Reading additional input from
  stdin". Incidental: the file task emitted the same naive unguarded chunk loop — third
  harness, same edge-blindness ([[finding-openrouter-grok-p2-2026-08-25]]).
- **Claude Code: WORKS, verified empirically 2026-08-25** — no proxy needed: OpenRouter
  exposes an Anthropic-compatible `/api/v1/messages` (verified by raw curl first). Recipe:
  `ANTHROPIC_BASE_URL="https://openrouter.ai/api" ANTHROPIC_AUTH_TOKEN=$OPENROUTER_API_KEY
  ANTHROPIC_MODEL="x-ai/grok-4.6" claude -p ...` (isolated `CLAUDE_CONFIG_DIR` for tests).
  Chat AND tool use both clean: headless file-write task wrote a working `chunk.js`
  (executed, correct). Caveats: unrecognized-model warning caps assumed context at 200k
  (map it in `modelOverrides` or set `CLAUDE_CODE_MAX_CONTEXT_TOKENS` to fix); metered
  OpenRouter billing; and the emitted chunk was AGAIN the naive unguarded loop — fourth
  harness, same edge-blindness.
- **SuperGrok subscription transfers to NONE of these** — OAuth consumer login, not an
  API key; every non-CLI path is separately metered.

## Verification rule
Grok is subordinate-class: **reproduce before relaying.** Its narration is fluent and its
structured fields will assert success it did not achieve (above). Files require read-back;
code requires execution. Nothing here exempts it from R0.

## Default-config lift — RETRACTED 2026-08-25 ([[finding-grok-defaultconfig-p2-2026-08-25]])
Five-way bench (08-23) reported `grok-4.6` default-config (real `~/.claude`) guarding P2's
unstated edge 1/2 vs isolated-HOME's 0/2, flagged n=1-flip/PROVISIONAL and pre-committed to
an N=6+ repeat before any rule change. That repeat ran 08-25 under a pre-registered decision
rule (grader independently validated against known-guarded/known-unguarded code first):
**grok-default 0/6 edge_guarded, cap 6/6.** Per the pre-reg, this retracts the lift language
outright — default config does NOT change the deterministic-miss finding; the 1/2 was noise.
Default config now folds into the same 0/N isolated-HOME record for this edge (still a
separate config technically, but no longer a documented exception). **Capability benches
must still isolate HOME regardless** — the isolation rule was never contingent on this
result, only on keeping capability and routing-as-invoked from being conflated.

Same run: free pool (`muse-spark-1.2-contributor-free`) beat BOTH grok configs, 10/10 vs 9/10
vs 8/10. On airtight-spec single-file work, try the free pool before grok.

## What is NOT measured (do not claim these)
- Whether the provisional HANG-class deficit GENERALISES to other real-repo termination
  bugs — ONE brief (n=3) carried the whole head-to-head gap, and that specific stays
  PROVISIONAL even though the underlying synthetic-edge mechanism is now deterministic
  (see capability profile above). A second HANG-class real-repo brief is the cheapest
  way to confirm or kill the head-to-head number specifically.
- (RESOLVED 08-25: default-config edge-guard "lift" was noise, 0/6 on repeat — see above.)
- Honesty WITHOUT the escape clause — 0/9 fabrication (08-25) measured only "takes the
  out when offered," not baseline honesty on a bare fictitious-referent question.
- Large-prompt (~8KB) reliability, empty returns, truncation.
- grok-4.5 at non-default effort (only 4.6 was swept).
- Multi-file / long-horizon agentic work; every probe was 1 file in 1 dir.
- Rate limits, quota behaviour, failure modes under load — 56+ runs were all rc=0 in one
  ~1h window. **Absence of observed failures at this N is not a reliability claim.**

Siblings: [[workflow-codex-subordinate]], [[workflow-agy-subordinate]],
[[workflow-opencode-subordinate]], [[delegation-and-review]].
