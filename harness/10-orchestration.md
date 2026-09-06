# Model Orchestration Guide

For the main-session model (you) deciding who does what. Written 2026-07-03 against
the tools verified present that day. **§0 tells you how to re-verify — do that
instead of trusting this file if anything errors.**

## §0 — What is actually available (verify, don't assume)

**Internal (Agent tool):** `model` parameter accepts `sonnet`, `opus`, `haiku`, and
(availability varies by session/plan) `fable`. Agent types that matter:
- `Explore` — read-only search/scan. Cheapest way to answer "where is X / what does
  the codebase do about Y". Cannot edit.
- `general-purpose` — multi-step tasks with full tools, including edits.
- `Plan` — read-only architecture/planning.
- `agent-skills:code-reviewer` / `security-auditor` / `test-engineer` — review roles.
- `claude-code-guide` — questions about Claude Code/API itself.

**External CLIs (Bash) — there are FIVE, not three:** `codex` (`gpt-5.6-luna`; review and
unstated-scale work: `gpt-6-astra`, live 2026-09-06 — routing map §3 has the numbers), `agy`
(Gemini `3.7-flash-medium`; review pin `3.6-flash-high`), `grok` (`~/.grok/bin/grok`,
`grok-4.6`), `opencode` (free pool), and NIM (a model backend, not an agent — direct
curl, or via opencode when file edits are needed). Playbooks in
`~/.claude/memory/workflow_*.md` + `reference_nim_via_opencode.md` are the source of
truth for invocation syntax and known traps. Three that bite before you read them:
**grok ingests `~/.claude` by default** — isolate HOME or it is not an independent
review lens; **opencode's `$PWD` is not its cwd** — set `env["PWD"]` AND `--dir`;
**an empty return is never "no findings"** — agy returns empty rc=0 ~17% at ~8KB
(always retry, ≤3×), grok can return a schema-VALID empty review that passes every
guard (tell: `usage.reasoning_tokens` vs input size), and opencode's first real-
generation zero-byte means reroute, not retry.
Two more, measured 2026-09-02: **Bash cwd is reset to the project dir after every
call** — `cd` does not carry; use absolute paths or `git -C <abs>` in each call.
**A subagent's CLAUDE.md + skill list is the parent's LAST system-prompt rebuild**
(`/compact` refreshes it), not session start — a before/after subagent experiment
records which rebuild each arm inherited.
Re-verify a CLI still works with a 5-second probe before batch-dispatching:
`codex exec -m gpt-5.6-luna --skip-git-repo-check -s read-only "PONG"` (always pass
`-m` — the bare config default is NOT the measured model) ·
`~/.grok/bin/grok -p PONG --disable-web-search --no-subagents` ·
`agy -p PONG --model gemini-3.7-flash-medium` (bare `agy -p` is NOT the pinned model).

If this file's tool list disagrees with what the harness offers you, the harness
wins — then update this file per `40-maintenance.md`.

## §1 — The commander does not enter the field

The main conversation is the scarcest resource: it holds the user's intent, the
decision history, and the acceptance gates. Every raw file dump or subordinate
transcript that lands in it displaces judgment.

**Delegate (do NOT do in main context):**
- Any step reading >3 files, any single file >500 lines, or producing >100 lines
  of output you won't act on line-by-line (matches R4) → `Explore` agent.
- Repo-wide scans, "find all callers/usages", convention surveys → `Explore`.
- Web research beyond one quick lookup → `general-purpose` agent (it does the
  searching/fetching; you get conclusions).
- Batch mechanical edits across many files → `general-purpose` (sonnet) or codex.
- Long log/output analysis → agent reads it, returns verdict + line pointers.

**Keep in main context (never delegate):**
- Writing the spec / acceptance criteria.
- The accept/reject decision on any subordinate result.
- Anything requiring the user's full conversation context.
- Small surgical edits below the non-trivial bar defined in
  `20-judgment-rubrics.md` §2 (delegation overhead > task).

## §2 — Routing table (task type → executor)

**Cross-family REVIEW rows below (codex-as-reviewer, agy, "second opinion") are
gated by the `cross-model-review` skill — load it before dispatching any of them;
this table only picks WHO. A phase boundary does not reset this gate: in "fix X,
then review", load it immediately before dispatching the review.** (2026-09-02,
[[finding-cross-model-review-trigger-2026-09-02]]; the phase-boundary miss was 2/4)

| Task | First choice | Notes |
|---|---|---|
| Find code / understand unfamiliar repo | Agent: `Explore`, model `sonnet` | `haiku` for simple "which file defines X" |
| Spec'd implementation with tests | **see the routing map first** — it wins on executor choice (global CLAUDE.md: "Route with `reference_subordinate_routing_map.md`") | Airtight spec + single file → **free pool**, not codex: that is measured work and codex quota is finite. codex when the spec needs judgment, spans files, or the free pool has failed once. Watch codex quota — exhaustion is a SILENT no-change. |
| Mechanical batch edits (pattern proven) | Agent `general-purpose` `haiku`, or codex | prove the pattern on 1–2 instances yourself first |
| Refactor needing convention judgment | Agent `general-purpose` `opus` | codex is bad at cross-cutting taste calls |
| Web/doc research | Agent `general-purpose` `sonnet` | require citations + confidence per claim |
| Code review (briefed scope) | Agent `agent-skills:code-reviewer` `sonnet`/`opus` | |
| Miss-is-costly audit (security, money paths) | `opus` + a SECOND independent reviewer (codex-as-reviewer or agy) | if `fable` is offered by the harness, it replaces `opus` in this row; keep the second reviewer either way. No single model is trusted alone here; see §6 honesty note |
| Second-opinion / adversarial read | agy (one sample) or codex-as-reviewer | codex volunteers risks when ASKED to review that it hides while implementing |
| Bulk summarization / pattern discovery | agy | prose-only prompts |
| Acceptance review of any delegated work | fresh-context agent, §5 | NEVER the agent that did the work |

🔴 **This table covers the INTERNAL (Agent-tool) tiers. For routing across the five
external CLIs it is NOT authoritative and is not complete — `grok` and NIM have no row
here at all. The authority is `~/.claude/memory/reference_subordinate_routing_map.md`
(global CLAUDE.md routes THROUGH it), which carries the measured evidence and the four
fleet-wide rules R-A–R-D. On any disagreement between that map and this table, THE MAP
WINS; fix this table in the same turn.** Its rows that this table's "second-opinion"
row predates: agy is NOT the pick for post-implementation review of a real repo, and
grok on the staged-files recipe is a measured third lens complementary to codex.

Default model when unsure: `sonnet`. Drop to `haiku` only for tasks where a wrong
answer is cheap and obvious (you'll instantly see it's wrong). Raise to `opus` for
ambiguity, cross-cutting judgment, or when sonnet has already failed once (§4).

## §3 — The three-part delegation package (mandatory in every dispatch)

Every delegation prompt contains, explicitly labeled:

1. **GOAL & WHY** — what to produce and what decision it feeds. The "why" lets the
   subagent make sane micro-decisions without asking.
2. **ACCEPTANCE CRITERIA** — testable statements. Include edge behavior explicitly
   (NaN/undefined/empty/zero/negative/oversized) — unstated edges are the shared
   blind spot of every model tier measured. "Done" = every criterion checked, or the
   miss reported loudly.
3. **REPORTING FORMAT** — see §4. Say it every time; don't assume the agent knows.

Fill-in templates per task type: `30-delegation-templates.md`.

## §4 — Reporting contract (what comes back to the main conversation)

- Conclusions + `file:line` pointers. NOT file contents, NOT full diffs, NOT logs.
- Anything >30 lines goes to a file (scratchpad or agreed path); the report returns
  the path plus a ≤3-line summary.
- Every claim tagged `[verified: <how>]`, `[relayed: <source>]`, or `[assumed]` (the
  global CLAUDE.md syntax). An agent saying "tests pass" must include the command it
  ran and the exit status.
- A quantitative claim sourced from a subordinate is recomputed from the cited
  evidence before you publish it (e.g. `rg -c '<label>' <evidence-file>`) — "8 genuine
  reviews" was 2 in the file it cited (2026-09-02). Mismatch = the claim does not ship.
- A returned artifact path is output, not idleness: `ls -l` it before classifying
  the return (a 19.6 KB grok design was once declared "idle", 2026-09-02).
- Findings format: location + mechanism + suggested fix, severity-ranked.
- "I could not do X because Y" is a valid, welcome report. Fabricated success is the
  #1 failure mode of every subordinate — say so in the prompt.

## §5 — Verification is not self-verification

- **Acceptance review goes to a fresh-context agent** that did not produce the work.
  Give it: the spec, the acceptance criteria, and WHERE the work is — not the
  producer's claims about the work.
- **Order of operations for the reviewer (and for you):** write input → expected
  output FIRST, then look at actual. This ordering is the single highest-value
  verification lever measured (98% vs 93% per-reviewer accuracy). Put it in the
  review prompt verbatim.
- Files: read back after write (existence + spot-check content, not just `ls`).
- Code: run tests or execute the real path. "It compiles" is not verification.
- High-risk judgment calls (irreversible, outward-facing, money, security): second
  opinion from a DIFFERENT model family (codex or agy), or present options to user.
- Verify your own output as hard as a subordinate's. The main model's "I just wrote
  it, it's fine" is the same fabrication channel.
- A reviewer report that contradicts itself (e.g. ACCEPT while its own checklist
  shows an unchecked criterion) is a REJECT of the review: close the gap yourself
  or re-dispatch to a DIFFERENT reviewer one tier up. If the same reviewer type
  self-contradicts twice, log it in `~/.claude/harness/LESSONS.md`.

## §6 — Escalation and de-escalation

**Escalate (upgrade the executor):**
- haiku produces one wrong/garbled result on a task → redo on sonnet immediately.
  Do not retry haiku with a better prompt; the retry costs more than the upgrade.
- sonnet (or codex/agy) fails the SAME subtask twice → escalate to opus, and hand
  the escalated agent the full failure trail: both attempts, what was wrong with
  each, and the acceptance criteria. Never escalate with just the original prompt —
  the failures are the most valuable part of the brief.
- **Hard cap: 2 retry rounds of the same approach at the same tier.** Third attempt
  must change something structural: model tier, decomposition, or approach. See
  `20-judgment-rubrics.md` §4 for wrong-direction signals.
- **What counts as "the same":** the retry counter attaches to the acceptance
  criterion that keeps failing, not to the prompt wording. Rewording/clarifying the
  prompt = same approach, next attempt number. A genuinely different approach means
  a different diagnosed MECHANISM (write it down). Even then: after 2 total failed
  rounds on the same criterion at one tier, escalate anyway — cheap tiers don't get
  unlimited "fresh" approaches.

**De-escalate (downgrade for batch application):**
- Once a pattern is SOLVED and VERIFIED on 1–2 instances (by you or opus), batch-
  apply the remaining instances on haiku/sonnet/codex with the solved instance
  included in the prompt as a worked example.
- Spot-check the batch: verify ~20% of results (minimum 2), chosen at random, plus
  every instance the executor flagged as unusual. Any spot-check failure → verify
  100% of that batch.

**Honesty note (limits of this ladder):** escalation ceiling in future sessions is
opus. Some judgment quality (taste, beyond-the-brief defect discovery) does not come
back at any amount of retries below the top tier. When an opus-level attempt with a
clean brief still feels wrong, the correct outputs are: (a) a second opinion from a
different model family, (b) presenting the options to the user with your best
recommendation, or (c) an explicit "this needs human judgment / a stronger model" —
not a confident guess. Decomposition and review improve execution; they cannot
manufacture taste.

## §7 — Parallelism rules

- Independent read-only agents: launch in parallel freely (one message, many calls).
- Anything that EDITS: parallel only on disjoint files; overlap → worktrees or
  sequential. opencode: sequential by DEFAULT (shared SQLite lock) — parallel
  verified only with per-instance `XDG_DATA_HOME` + copied auth.json, 3-way
  (recipe: `~/.claude/memory/workflow_opencode_subordinate.md`).
- Never launch a second wave before accepting/rejecting the first — unaccepted work
  compounds errors.
