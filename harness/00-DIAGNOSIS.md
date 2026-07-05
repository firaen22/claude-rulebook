# Harness Diagnosis — 2026-07-03 (written by Fable 5, one-time session)

The three places this harness wastes the most tokens, loses focus, and makes errors.
Every other file in ~/.claude/harness/ exists to fix one of these. Read this file when
you want to know WHY a rule exists; read the other files for WHAT to do.

---

## Problem 1 — CLAUDE.md carried history, not rules (token waste + misreads)

**Evidence:** The pre-rewrite global CLAUDE.md was 183 lines. Roughly half was
experiment narrative: "EXP-6 RETRACTED the Test-1 win", "earlier claim X RETRACTED",
benchmark scores, dates, N counts. Every session paid ~3–4k tokens for it, and a
weaker model reading "X was retracted" can easily act on X anyway, because the
retracted claim is still *in context*, stated first, and stated confidently.

**Failure mode for weaker models:** history-mixed-with-rules forces the reader to
compute current truth from a sequence of updates. Strong models do this; weak models
latch onto whichever sentence pattern-matches the task.

**Fix (implemented):** CLAUDE.md now contains only current-state imperatives and
pointers. Evidence, dates, N, and retraction chains live in memory files, loaded only
when someone questions a rule. Rule for the future: **CLAUDE.md sentences must be
executable orders in present tense. If a sentence contains a date, an N, or the word
"retracted", it belongs in a memory file, not CLAUDE.md.**

## Problem 2 — The commander enters the field (focus loss + context burn)

**Evidence:** Session history shows large sweeps run in the main conversation
(62-session map-reduce sweep, multi-hundred-run benchmarks, bulk file reads). Raw
subordinate output, full file dumps, and long tool transcripts land in the main
context. Result: the main loop hits ~70% context mid-task, /compacts, and loses the
thread — the exact "breadth outrunning depth" risk already flagged in memory.

**Failure mode for weaker models:** worse. A weaker main model with a polluted
context degrades faster and rationalizes more. The main context is the scarcest and
most quality-critical resource in the whole system.

**Fix (implemented):** `10-orchestration.md` — delegation-by-default with a hard
reporting contract: subagents return conclusions + file:line pointers only; anything
long goes to a file, and the path comes back. The main conversation holds decisions,
not data. Trigger rule: **if a step will read >3 files or produce >100 lines of
output you won't act on line-by-line, delegate it.**

## Problem 3 — Verification is judgment-based, so it silently degrades (errors)

**Evidence:** Rule 0 (reproduce before trusting) is the measured keystone habit, but
as written it relies on the reader's discipline: "verify with my own eyes", "enumerate
boundaries". Fable/Opus apply that judgment natively. Sonnet/Haiku under time pressure
will read a subordinate's "all tests pass", find it plausible, and move on — that is
the documented fabrication channel for all three subordinate CLIs (codex, agy,
opencode all narrate success falsely).

**Failure mode for weaker models:** self-verification collapses into re-reading
one's own conclusion. The check must be *structural* (a different agent, a required
artifact, a forced expected-vs-actual comparison), not *dispositional*.

**Fix (implemented):** `20-judgment-rubrics.md` turns the judgment calls into
mechanical checklists with pass/fail criteria and examples; `10-orchestration.md`
mandates fresh-context acceptance review and the input→expected→actual ordering
(measured: 98% vs 93% per-reviewer accuracy — that ordering is the single
highest-value verification lever, cheaper than any voting/redundancy scheme).

---

## What did NOT make the top three (so you don't re-fix it)

- **Subordinate tooling quality** — codex/agy/opencode quirks are already well
  documented in playbooks and were re-verified recently. Don't re-benchmark; see
  the closed-threads list in the project CLAUDE.md.
- **Voting/multi-sample infrastructure** — measured to be a wash (single verified
  reviewer ≈ 3-voter panel, 1/3 cost). Do not build aggregation infra; invest in
  the reviewer prompt. See finding_voting_vs_single_verification.md in the
  claude-code-technique project memory (loads only in that project).
- **Scaffolding/disposition injection** — measured zero benefit (EXP-6). Do not add
  "think like a senior engineer" preambles as a performance lever; keep only the
  reporting FORMAT (location+mechanism+fix, severity-ranked).
