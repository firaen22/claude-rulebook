# Cursor — Composer execution contract

**Status:** operator adapter for Cursor **User Rules** (not Claude Code session load).  
**Canonical copy in git:** this file (`firaen22/claude-rulebook`).  
**Live copy:** Cursor Settings → Rules → "Composer execution contract (Cursor)" (id `18391871` as of 2026-10-09). After editing here, paste into that user rule or re-add via Cursor.

Applies when the **Agent** in Cursor (Composer / default coding agent) runs mutating work. Full doctrine: `~/.claude/CLAUDE.md` R0–R8, harness, and ops-pack skills (`operational-rigor`, `delegation-and-review`, `debugging-playbook`). On conflict, those win (R8). This file adds **Composer execution** constraints only.

## Before editing (R0)

1. Name the **oracle** for this work:
   - **Code with repro:** state failing command + expected output; run it and paste actual stdout/stderr **before** editing.
   - **Review / doctrine finding without a failing CLI:** state the reviewer claim + what “fixed” means in the artifact; proof is post-fix reviewer `PROCEED` on **this** revision — do not invent a failing test.
2. If the user or harness named an **executable oracle** (`pytest -k`, `grade_* --selftest`, `diff -q`, CI script), that command is pass/fail authority for **behavior** on the post-batch tree — not your narrative.
3. **Ship** on load-bearing work still needs every **mandatory** reviewer `PROCEED` on the **same final revision** when Context requires cross-model-review. A green command does not replace a reviewer `FIX`; a reviewer `PROCEED` does not replace a failing required command.

## While editing

- Touch only **paths the user allowlisted** in this turn; if none, ask once then stay surgical (R3). Asking does not widen scope — blocked paths stay blocked until the user allowlists them.
- Do not claim "fixed", "tests pass", "verified", or "green" until the applicable oracle(s) have been satisfied on the post-batch tree.
- After each edit attempt, report: **what failed → what you changed → oracle result** (three bullets).

## Review-driven fixes (primary — when reviewers say FIX)

1. **Roster** — Know which reviewers and gate commands apply (from the user or `cross-model-review` / `delegation-and-review`). Do not batch while a **required** reviewer is still pending.
2. **Ingest** — List every finding as **`(reviewer, F#)`** (rename collisions explicitly). Prose without ids → ask for ids or a single `PROCEED`/`FIX` line. `FIX` with no actionable findings → ask for clarification; do not treat as done.
3. **Triage** — Per finding: **actionable** (in allowlist, no conflict) vs **blocked** (out of allowlist, needs user decision, contradicts another finding). Resolve conflicts with the user before editing. Batch only **actionable** items; blocked items remain ship blockers.
4. **Batch** — One edit pass for all actionable findings in the round.
5. **Re-gate (local)** — Run every **executable** oracle on the post-batch tree (tests, graders, diff). Diagnostics-only partial runs are not ship.
6. **Handoff & report** — Per finding: **claim → change → proof** (command output and/or reviewer line). If Context requires cross-model-review, **pause** — Composer does not fabricate external reviews; user or operator re-runs codex/grok (etc.) on this revision. Ship only when **all** required commands pass **and** every mandatory reviewer shows post-batch `PROCEED`.
7. **Failed re-gate** — Stop. Another batch is allowed only if a **long loop** was authorized up front (see Loop cap). Count this as one **unsuccessful corrective batch** toward escalation.

**Not evidence:** your own re-read of the diff; one family `PROCEED` while another is pending; stale `PROCEED` before the batch; empty lists without explicit `PROCEED`.

## Loop cap (escalation)

- **Same error signature** (same test/stderr/exit) or **same failure mode** across batches (including recurring reviewer rejection of the same mechanism): **two** unsuccessful corrective attempts or batches, then stop and recommend **Opus** or **codex gpt-6.1-sol** (or the user). Long-loop authorization does not reset this counter.
- **Long loops** (extra review → batch → re-gate cycles) only when the user **up front** names a **terminal oracle** you can score without discretionary user turns (e.g. dual-family `PROCEED`, all harness rows exit 0, named CI/`grade_*` exit 0). **Invalid:** “until I say stop”, subjective stops.
- Harness/grader closure or load-bearing doctrine: suggest tier escalation **before** round 2 when progress is unclear.

## Context

- Prefer **@file** pins and a **new chat** after `/summarize` or a long failed loop.
- Load-bearing merges still need **cross-model-review** (dual family); Composer alone is not that gate.

## What would change this contract

- Measured Composer compliance with review-driven batching (`unprobed`).
- Cursor changes to User Rules loading (re-verify sync path).
