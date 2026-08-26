---
name: reference-closed-questions
description: "Questions that were measured, answered, and closed. Do not rebuild these. Extracted from global CLAUDE.md 2026-08-26 when the file hit its 100-line ceiling; the conclusions are unchanged, only the storage moved."
metadata:
  type: reference
---

Extracted verbatim from `~/.claude/CLAUDE.md` on 2026-08-26 (100-line ceiling
enforcement). These are **conclusions with evidence behind them**, not opinions —
re-opening one needs a regime change (new model tier, new tool), not a new hunch.
The global file now carries only a pointer here.

## 1 — No voting / multi-sample aggregation infra

A single verified reviewer using the **expected-before-actual ordering** (write down
input → expected output BEFORE looking at the result) matches a 3-voter panel at 1/3
the cost. Building voting infrastructure buys nothing over the ordering discipline.

Evidence: `finding_voting_vs_single_verification.md` (project memory,
claude-code-technique), corroborated by `finding_hierarchy_verification_pilot.md`
(flat ties-or-beats verified-tall at 1/3 cost).

## 2 — No disposition / scaffold preambles as a performance lever

Opus-scaffolded ≈ Opus-bare, separation 0.000 in 5/5 paired runs. What survives is
only the **reporting format**: location + mechanism + fix, severity-ranked. Keep the
format; do not reintroduce the preamble.

Evidence: `feedback_adopt_fable_habits.md` (project memory) — this is the EXP-6
retraction. Fable's real edge is beyond-the-brief defect discovery, not scaffolding.

## 3 — The highest-ROI per-project artifact is a ground-truth harness

Before tuning any prompt, build a small ground-truth harness: a **real** function,
**frozen real** data, and a **cost-asymmetric** gate. This outranks prompt work,
rule work, and routing work as a first investment in a new project.

This one had no memory home before 2026-08-26 — it lived only in the global
CLAUDE.md line being replaced by this file. Its operational form is the
`ground-truth-gates` skill; the project rule "no harness → no experiment" in
claude-code-technique's `CLAUDE.md` is the same principle stated as a gate.

## What would change these

1 and 2 revert only on a new model tier or a task shape materially unlike the
review/verification tasks they were measured on. 3 is a prior, not a measurement —
it would weaken if a project ever showed prompt tuning beating harness-building on
the same defect set, which has not been observed here.
