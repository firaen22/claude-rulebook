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

> ⚠️ **THE ONE RULE.** Grok writes the naive loop. **State the termination edge whenever
> you hand grok loop/iteration work** — unstated it guards 0/28, stated 11/11, so the rule
> costs one line. (The real-repo leg is PROVISIONAL: 0/3 HANG-class vs 2/3 and 2/3, but
> n=3 on ONE task, p=0.17, and both incumbents drew the same loop once —
> [[finding-grok-cli-bench-2026-08-23]]. The synthetic 0/28 is not provisional.)
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
- `text` may hold several concatenated JSON drafts. Ignore it. Even in the clean
  single-draft case `text` is a JSON **string** (`"{\"reply\":\"PONG\"}"`), not your
  object — `.text` never gives you a parsed result.
- 🔴 **The envelope is PRETTY-PRINTED multi-line JSON — never parse it line-wise.**
  `tail -1` yields the bare `}`, and `... | tail -1 | jq` dies with
  `parse error: Unmatched '}'`. Line-oriented parsing (`tail -1`, `read` loops,
  last-line-wins log scrapers) is the #1 way a perfectly healthy grok run reads as
  **"grok always returns empty."** Redirect to a file and parse the whole buffer:
  ```
  grok -p "..." -m grok-4.6 --json-schema '<SCHEMA>' > out.json
  jq -r '.structuredOutput.<field>' out.json
  ```
  Verified 2026-08-26: same run, `tail -1 | jq` → parse error, whole-buffer `jq` →
  the value. Before reporting grok as broken, re-probe with `--output-format plain`
  and a "reply with exactly: PONG" prompt — plain mode prints 4 bytes and no
  envelope, so it isolates transport/auth from your parser.

### 🔴 "Empty" has TWO causes — separate them before blaming either

The parser bug above is one. The other is grok genuinely idling: on a multi-step
read-then-analyze brief it **narrates its plan and exits** ("Next I'll locate the
repo, read the changed files") without executing — 3/3 on one review task, and
copying every file INTO `--cwd` did NOT fix it. **The fix is packet SHAPE, not
retry: inline everything, demand pure judgement, add `--json-schema`.** That
re-shape turned the same failing review into a clean 5-finding run. Numbers and
the falsifier: [[finding-grok-idle-vs-parser-2026-08-27]].

Triage, in order. **Size alone does not separate the two causes — a mis-parsed
short answer and pure narration are both small. READ the bytes.**
1. `wc -c "FILE"; head -c 400 "FILE"` — narration announces steps it never took
   ("Next I'll locate the repo, read the changed files"). Intent ≠ a short answer.
2. `jq '.num_turns, .structuredOutput, .structuredOutputError' "FILE"` — **the
   filename is load-bearing.** Omit it and `jq` reads stdin: at EOF it prints
   NOTHING and exits 0, which a script reads as "clean." Verified 2026-08-27.
   - **Decisive:** `structuredOutput` null / `structuredOutputError` set / the
     required fields carrying placeholder strings.
   - **Suspicion only:** low `num_turns`. The proven guard is `== 1` on a
     tool-requiring task (§Tool-use short-circuit, the NEXT heading below);
     `<= 2` on an analysis task is a prompt to go look, not a verdict — a
     genuine run can finish in two turns, and a pure-judgement run with
     everything inline legitimately finishes in ONE (verified 2026-08-27).
3. Only then suspect your parser (whole-buffer `jq`, PONG probe).

**Never read a schema-shaped object as evidence of work — a `"pending"` string in
your field is grok filling the shape, not answering.** For review-class delegation
where this bites, route to codex; agy is the substitute third lens.

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

**Headline: grok does not volunteer guards, but delivers them when asked** (0/28 → 11/11).
Spec every edge explicitly. The measurement is stated-vs-unstated behaviour, not the
internal cause — so route on it, do not theorise from it.

- **Settled enough to route on** under isolated HOME AND (separate N=6) default config.
  Still owed: a SAME-INSTRUMENT replication — the 08-25 reps used an easier prompt than
  the 0/16 leg, making it direction-safe pooling, not replication.
  [[finding-geminimd-and-fleet-probe-2026-08-25]]
- **Always include an escape clause.** 0/9 fabrication WITH one present; that measures
  "takes the out when offered", never baseline honesty (see What is NOT measured).
- **Use the default effort; do not build effort routing.** Flat across all four tiers —
  replicates agy's "effort tier ≠ edge safety" on a second vendor.

## Where to use it

### Head-to-head MEASURED 2026-08-23 (vs codex + agy, N=12/arm)

4 real-repo briefs, each tool in its OWN default config: **grok 9/12, codex
`gpt-5.6-luna` 11/12, agy `gemini-3.7-flash-medium` 11/12** — the whole gap is one
HANG-class task. Numbers, adjudication, and the saturation caveat (every arm hit
ceiling on the other three briefs, so that is no-separation, NOT proven parity):
[[finding-grok-cli-bench-2026-08-23]].

- **A legitimate third option for ordinary spec'd implementation.**
- **Loop / iteration / termination work → state the edge first** (THE ONE RULE above).
- **Route to grok to spare codex quota, not to save time** — slowest of the three,
  median 16.1s vs 8.5s / 9.2s, worst task 42s. Both run on flat plans, so this is
  spreading load across two subscriptions, not trading quota for pennies.

### NOT head-to-head — single-arm capability facts and reasoned defaults

No comparative data behind these. They say what grok does, not what to prefer it over.

- **Schema-constrained fan-out** — 16/16 adherence plus free `usage`/`cost` telemetry.
  "Advantage" is inferred from codex/agy lacking the feature, never measured against
  them. Side effects still verified on disk.
- **Well-specced implementation on small briefs**, edges spelled out. *(Reasoned.)*
- **NOT as a cross-model reviewer until HOME is isolated** — otherwise it reads your own
  doctrine back to you. *(Reasoned from `grok inspect`, not a review-quality measurement.)*
- **Large inline packets delivered twice: ~55KB (6/6 findings real, iter 43b) and
  ~139KB (7 findings, 3 confirmed convergent with codex, 2026-08-27).** n=2, both
  isolated-HOME schema reviews: existence proofs that size alone doesn't break it,
  NOT a reliability claim. Budget for latency: the 139KB run took ~17min at
  `num_turns: 3` with ZERO bytes on stdout/stderr until done — a silent long run at
  this size is normal, not a hang; set a deadline ≥25min before killing.
  Records: TG-bot-helper `multitool_improvement_workflow.md` iter 43b; this repo's
  routing-map review 7194600.

## Grok inside OTHER harnesses

**Standing decision (user, 2026-08-25): the grok CLI is the default grok lane** — the
only path the SuperGrok subscription covers. It is an OAuth consumer login, so it
transfers to NONE of the others; every non-CLI path bills metered OpenRouter credits
and buys no capability (edge-blindness is a model property — identical in all four
harnesses, 4/4). Reach for another harness only when grok must run inside it, or when
a bench must exclude the CLI scaffold.

- **opencode** `openrouter/x-ai/grok-4.6` — works. Zen's `opencode/grok-4.6` is
  billing-blocked (exits 0 with an Error on stdout: not a capability failure).
- **codex 0.149.0** and **Claude Code** — both WORK, verified empirically.
- ⚠️ Both carry a gotcha that reads as BLOCKED-but-isn't, and one already produced a
  false BLOCKED verdict. **Copy the recipe, do not reconstruct it:**
  [[reference-grok-other-harnesses]].

## Verification rule
Grok is subordinate-class: **reproduce before relaying.** Its narration is fluent and its
structured fields will assert success it did not achieve (above). Files require read-back;
code requires execution. Nothing here exempts it from R0.

## Default-config lift — RETRACTED 2026-08-25 ([[finding-grok-defaultconfig-p2-2026-08-25]])

The 08-23 five-way bench's default-config 1/2 edge-guard was **noise**: the
pre-committed N=6 repeat scored 0/6, so default config is no longer a documented
exception and folds into the same 0/N record. Two orders survive it:
- **Capability benches still isolate HOME, always.** That rule never depended on
  this result — only on not conflating capability with routing-as-invoked.
- **On airtight-spec single-file work, try the free pool before grok** —
  `muse-spark-1.2-contributor-free` beat BOTH grok configs in that run, 10/10 vs
  9/10 vs 8/10.

## What is NOT measured (do not claim these)
- Whether the HANG-class deficit GENERALISES beyond the ONE brief (n=3) that carried
  the entire head-to-head gap. The synthetic mechanism is deterministic; this specific
  is not. A second HANG-class real-repo brief confirms or kills it.
- Honesty WITHOUT the escape clause — 0/9 measured "takes the out when offered" only.
- grok-4.5 at non-default effort (only 4.6 was swept).
- Long-horizon agentic work. Multi-STEP is now partly measured and it went badly:
  [[finding-grok-idle-vs-parser-2026-08-27]], n=1 task each way.
- Output TRUNCATION — never probed on grok (the truncation note in the 08-25 fleet
  finding is about a NIM model). Large-packet RELIABILITY likewise: two clean packets
  (~55KB, ~139KB) are the entire record.
- Rate limits, quota behaviour, failure modes under load — 56+ runs were all rc=0 in one
  ~1h window. **Absence of observed failures at this N is not a reliability claim.**

Siblings: [[workflow-codex-subordinate]], [[workflow-agy-subordinate]],
[[workflow-opencode-subordinate]], [[delegation-and-review]].
