---
name: Workflow: Spawned-Session Subordinate
description: spawn_task / Claude Code sessions as full-agent in-repo subordinates — when to use, failure signatures, verify-don't-trust
metadata:
  type: reference
---
# Spawned-Session Subordinate (spawn_task)

**Status: v0.1 — provisional, N=4 spawned sessions (2026-06-16). Refine with use; bump replication counts as evidence accrues.**

The fourth delegation tier, alongside [[Workflow: Codex Subordinate]], agy, and opencode. Distinct mechanism:
`mcp__ccd_session__spawn_task` → emits a **chip** in the UI → user clicks → a **fresh Claude Code session** starts in its own cwd (optionally a worktree), with full tools + that repo's CLAUDE.md + its own context budget. Not a CLI; not the inline Agent tool.

## When to use which tier
- **Inline Agent tool** (Explore / general-purpose): read-only or short research; result returns to MY context THIS turn. Use when I need the conclusion now.
- **CLI subordinate** (codex / agy / opencode): bounded code task, I own an airtight spec, runs headless in background, no full repo context. Use for disjoint single-file impl / lookups.
- **Workflow tool**: deterministic, in-process, PROGRAMMATIC fan-out (pipeline/parallel, verify gates, adversarial panels, loop-until-dry). Use when I want scripted multi-agent control flow with cost/variance numbers.
- **Spawned session** (this): a self-contained, MULTI-STEP task in a SPECIFIC repo that benefits from full tools + repo conventions + its own budget, and should ACT (edit, commit, PR). User-gated. Use for "go audit / harden / implement X in repo Y."

## Failure signatures & rules (verified this session unless noted)
1. **SILENT STALL is the signature failure.** A mis-scoped/blocked session sits at `isRunning: true` with a STALE `lastActivityAt` — dead, not working (the mis-scoped #4 hung a full day, zero output). Diagnose via `list_sessions` (check `lastActivityAt` age), confirm via ground truth (did any files change?). Don't wait on a stalled chip.
2. **MIS-SCOPE → STALL.** Given a target that doesn't exist ("harden the *script*" when it's an agentic pipeline with no script), a spawned session HANGS rather than pushing back — the won't-surface-ambiguity blind spot, same as codex, different tool. FIX: scope to a verified-real target; if unsure, instruct "map the system before changing anything; if there's no clear target, STOP and report — don't invent work."
3. **VERIFY BY GROUND TRUTH ACROSS THE FULL BLAST RADIUS — not the cwd.** A session writes wherever it has access. The digest hardening landed in `~/.claude/scheduled-tasks/.../SKILL.md`, OUTSIDE the vault cwd; checking only the cwd produced a FALSE "half-done" verdict that fuller verification overturned. Check `git log/status`, file mtimes, AND likely out-of-cwd targets (scheduled tasks, ~/.claude, sibling repos).
4. **CANNOT reliably read its transcript.** `search_session_transcripts` needs interactive approval (unavailable headless); the `.output` symlink is the full JSONL and overflows context. So HARVEST via ground truth, or have the session WRITE a structured findings file to a known path (e.g. `~/.claude/findings/<task>.json`). Never rely on reading what it "said."
5. **USER-GATED.** The chip needs a human click — it does NOT auto-run like an `&`-backgrounded CLI call. Don't assume it started; confirm via `list_sessions`.
6. **QUALITY IS HIGH WHEN SCOPED RIGHT.** Full tools + repo CLAUDE.md + own budget often beats a CLI subordinate: the audit found a real Rule-12 gap; the hardening added an unasked idempotency guard (12pm vs 6pm double-trigger). Give SUCCESS CRITERIA, not steps (Rule 4).
7. **PROMPT MUST BE SELF-CONTAINED.** The session has NO memory of the originating conversation. Include absolute paths, architecture context, and an explicit "confirm before X" gate for anything outward-facing/live.
8. **CONFIRM-BEFORE-LIVE works.** Instructing "ask before editing the live scheduled task / credentials" produced correct stop-at-gate behavior (safe half done, live half deferred for approval). Use it for hard-to-reverse work — it does NOT silently barrel ahead the way a raw CLI subordinate might.
9. **CLEANUP.** A stalled/superseded chip the user ALREADY started can't be withdrawn via `dismiss_task` ("already started") — note it for manual close. Only un-started chips are dismissable. To replace: spawn the corrected one first, then (try to) dismiss the old.
10. **THE DELEGATE MUST VERIFY THE PROMPT'S PREMISES against repo state before editing — and surface corrections in its report (R7).** A self-contained prompt can carry a stale factual premise. A worktree session was told it branched "off master after chore/lightweight-structure merged" — but the merge hadn't happened (master still at the old SHA, the worktree lacking the shared components). The delegate detected the mismatch from git state, fast-forwarded its branch onto the correct base itself, completed the task, and reported the correction in its final message instead of silently absorbing it or editing on the wrong base. So instruct the delegate to ground the prompt's git/topology claims (base branch, what's merged, which files exist) against the actual repo before the first edit, and to report any premise it had to correct. Complements rule 3 (orchestrator verifies output) — this is the inbound twin (delegate verifies the prompt). (2026-07-24, moira worktree hardening.)

## Verify-don't-trust (same law as every subordinate)
Never chain spawned-session → ship. Ground-truth-check every claimed completion. This session I nearly reported BOTH a false negative ("half-done") — verification overturned it; the work was actually complete and well done. The lesson cuts both ways: verify before believing failure OR success.
