# Cursor — Composer execution contract

**Status:** operator adapter for Cursor **User Rules** (not Claude Code session load).  
**Canonical copy in git:** this file (`firaen22/claude-rulebook`).  
**Live copy:** Cursor Settings → Rules → "Composer execution contract (Cursor)" (id `18391871` as of 2026-10-09). After editing here, paste into that user rule or re-add via Cursor.

Applies when the **Agent** in Cursor (Composer / default coding agent) runs mutating work. Full doctrine: `~/.claude/CLAUDE.md` R0–R8, harness, and ops-pack skills (`operational-rigor`, `delegation-and-review`, `debugging-playbook`). On conflict, those win (R8). This file adds **Composer execution** constraints only.

## Before editing (R0)

1. Name the **failing command** (or the oracle) and state **expected** output in one line **before** you run anything — input → expected, then actual; do not rationalize from stderr you already saw without stating expected first.
2. Run or request that command; paste **actual** stdout/stderr.
3. If the user gave an **oracle** (`pytest -k`, `grade_* --selftest`, `diff -q`, CI script), that command is the only pass/fail authority — not your narrative.

## While editing

- Touch only **paths the user allowlisted** in this turn; if none, ask once then stay surgical (R3).
- Do not claim "fixed", "tests pass", "verified", or "green" until the oracle command has been run in this session and output shown.
- After each edit attempt, report: **what failed → what you changed → oracle result** (three bullets).

## Loop cap (escalation)

- **Two** edit attempts max for the **same error signature** (same failing test name, same stderr tail, same exit code). After that: stop, summarize repro + hypothesis, and recommend **Opus** or **codex gpt-6.1-sol** (or the user) — do not start attempt 3 on the same signature.
- If the task is harness/grader closure, adversarial scope, or load-bearing doctrine: suggest tier escalation **before** round 2 when progress is unclear.

## Context

- Prefer **@file** pins and a **new chat** after `/summarize` or a long failed loop — do not carry eight rounds of wrong diffs forward.
- Load-bearing merges still need **cross-model-review** (dual family); Composer alone is not that gate.

## What would change this contract

- A measured bench showing a different loop cap or oracle rule moves behavior on Composer Fast (`unprobed` today).
- Cursor product changes how User Rules load (re-verify sync path).
