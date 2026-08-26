# LESSONS — write-backs after mistakes (format: 40-maintenance.md §3)

Append-only between compressions. Compress at >150 lines / >20 entries.

Compressed 2026-07-12: six applied entries (2026-07-05 → 2026-07-12) moved
verbatim to `LESSONS-archive.md`.
Compressed 2026-08-25 at 243 lines / 19 entries: ALL 19 entries (2026-07-11 →
2026-08-25) moved verbatim to `LESSONS-archive.md`. Every one was verified
applied by grepping its rule in the destination cache before the move — not
trusted from its own `Status:` line (two entries carried no Status at all).
The verification map is in the archive's compression banner. What survives here
is only what is NOT closed: one promoted rule-change proposal awaiting approval,
one open external thread, and the recurrence counters.

## PENDING RULE CHANGE — awaiting user approval (§3: recurred ≥3×, promote)

### "A fix is a change, and needs its own independent review"
- **Recurrence: 4 instances, no cache home.** Every other lesson in the archive
  landed in a skill or memory file; this one has been re-learned four times and
  written down four times without ever being compiled into an always-loaded
  rule. Grep confirms it exists nowhere in `skills/` or `harness/*.md` except as
  narrative history in `LESSONS-archive.md`.
- Instances: opus-pack PR #125 (applying a correct finding re-pointed an
  antecedent and licensed quietly not-reverting user-ordered work — caught only
  by a 2nd review round); PR #129 round-2 (round-1's own mask() fix introduced
  two NEW defects — a DEP-UNUSED false-positive/negative pair and a
  SCAN-INCOMPLETE boundary misfire — which a "did the described fix land" check
  would have missed); PR #125's own entry already called itself "fourth incident
  in this family"; and 2026-08-25 this session, where my fix for append-only
  status rot (a reconciliation table) reproduced the exact rot it was written to
  eliminate, wrong on 2/8 rows.
- Mechanism that makes it recur: the reviewer who found the problem has NOT
  verified the solution to it, and the author's attention at fix time is on the
  finding, not on what the edit's blast radius newly touches. Checking "did the
  described fix land" is structurally incapable of catching a defect the fix
  introduced.
- **Proposed edit (NOT yet applied — needs your go):** add to
  `operational-rigor` §"verification by execution" —
  > A fix is a change and inherits the full verification duty of one. A finding
  > being correct says nothing about your fix being correct: re-derive the fixed
  > behavior from the artifact, not from your own fix description, and check what
  > the edit newly touches — not only that the reported defect is gone. This
  > applies to your OWN fix in the same turn as the finding, and hardest when the
  > fix is a rewrite of prose or a summary rather than code.
- Status: **noted** — surface when a review/fix cycle is about to start.

## RECURRENCE COUNTERS (applied rules that are climbing toward promotion)

Kept as counters only — full text in `LESSONS-archive.md`. At 3, §3 says draft
the rule edit and ask in-session.

- **Subordinate holding write access reverts/wipes concurrent work — 2 instances**
  (2026-07-14 codex constraint-enforcement wiped files silently; 2026-07-28 codex
  deliberately reverted my landed fix and then TRUTHFULLY reported "no other file
  was modified", because it had put it back). Rule is applied in
  `delegation-and-review`; the counter matters because the two instances had
  different mechanisms and neither was caught by reading the report as specified.
- **`gate-before-commit` cannot resolve `cd $VAR` — 2 instances** (2026-07-11,
  2026-08-04; same hook, same shlex-inert-variable mechanism, both times it fell
  through to `$CLAUDE_PROJECT_DIR` and ran the wrong repo's gates). Applied in
  40-maintenance §1's hook rows + `memory/feedback_hook_block_read_the_repo_line.md`.
  Write literal absolute paths in any commit-adjacent `cd`.
- **A read-only instruction is not a control — 2 instances** (agy edited files
  despite read-only in sweep-6; a review subagent deleted a stale-response guard
  from a live working tree in 2026-07-28). Only the filesystem/worktree boundary
  is a control. Applied in `delegation-and-review`; prefer `isolation: 'worktree'`
  for review fan-outs.
