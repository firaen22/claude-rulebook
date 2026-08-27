# LESSONS — write-backs after mistakes (format: 40-maintenance.md §3)

Append-only between compressions. Compress at >150 lines / >20 entries.

Compressed 2026-07-12: six applied entries (2026-07-05 → 2026-07-12) moved
verbatim to `LESSONS-archive.md`.
Compressed 2026-08-25 at 243 lines / 19 entries: ALL 19 entries (2026-07-11 →
2026-08-25) moved verbatim to `LESSONS-archive.md`. What survives here is only
what is NOT closed: one promoted rule-change proposal awaiting approval, one
open external thread, and the recurrence counters.

⚠️ **CORRECTED 2026-08-26.** This block used to claim every moved entry "was
verified applied by grepping its rule in the destination cache before the move."
That was false, and is corrected at the archive's banners — read those, not a
Status line. Both compressions were re-audited 2026-08-26 at PRESCRIPTION
granularity: the 08-25 pass named destinations for only 9 of 19 and verified
those 9 (4 failures among the 10 it never named); the 07-12 pass named no
destinations at all (5 of 10 prescriptions not live as written). Evidence:
`claude code technique/experiments/lessons-applied-audit-2026-08-26/`.
**Moving an entry here closes nothing. Before writing "applied", grep the
destination and quote the operative sentence — a "compiled into §N" reference
decays as files are reorganized and nothing re-checks it.**

## APPLIED RULE CHANGE — 2026-08-26 (§3: recurred ≥3×, promoted on user order)

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
- **APPLIED 2026-08-26** to `skills/operational-rigor/SKILL.md` §4 (Verify by
  execution), inserted after the "a failing check has two suspects" bullet.
  Backup: `~/.claude/backups/operational-rigor.SKILL.md.2026-08-26-fixrule.bak`.
  Ships `unprobed` — incident-derived, never bare/ruled probed.

- **Mechanism trace before shipping** (the 2026-07-14 lesson: a compiled rule is
  executable code — run the prescribed mechanism against its motivating case and
  the nearest edge, because distillation introduces bugs the incidents never had).
  Prescription: *re-derive the fixed behavior from the artifact, not your fix
  description; check what the edit newly touches.*
  - PR #125 (antecedent re-pointed, naming duty silently dropped) → CATCHES.
    Re-deriving means reading the edited sentence and asking what "such a
    component" now refers to and what duty that leaves; the dropped duty is
    visible in the artifact, invisible in the fix description.
  - PR #129 (round-1 mask() fix introduced a DEP-UNUSED false-positive/negative
    pair + a SCAN-INCOMPLETE boundary misfire) → CATCHES, and is the empirical
    proof: round-2 did exactly this (re-derived from the code, not the fix
    description) and that is how the two new defects surfaced.
  - 2026-08-25 NIM table (fix reproduced the rot it was written to remove) →
    catches ONLY under the sharpened wording. "Re-derive from the artifact" read
    naively means re-reading the table, which is what produced the defect. The
    shipped rule therefore names the ground truth as the artifact for summaries
    and tables ("re-probe, don't re-read"). This edge is why that clause exists —
    without it the rule would not catch its own most recent instance.
  - Nearest edge, pure revert: re-derivation is trivial and the rule costs
    nothing. No regress risk — verification is a read, not a change, so it does
    not itself trigger the duty.
- **Self-application caught two defects in this very edit** (recorded because it
  is the rule's own first live test, N=1): the draft cited
  `harness/LESSONS-archive.md` as holding the mechanism trace when the archive
  holds only the incidents — the trace did not exist anywhere until this block was
  written — and it used a bare relative path where the file's convention (line 8)
  is `~/.claude/`-prefixed. A "did the described fix land" check passes both. Both
  fixed before commit.
- Status: **applied-on 2026-08-26**

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
  40-maintenance §1's hook rows + `~/.claude/projects/-Users-yauch-Documents-claude-code-technique/memory/feedback_hook_block_read_the_repo_line.md`
  (PROJECT memory, not global `~/.claude/memory/` — path corrected 2026-08-26
  after the bare `memory/` prefix sent an audit searching the wrong tree).
  Write literal absolute paths in any commit-adjacent `cd`.
- **A read-only instruction is not a control — 4 instances (3 by 2026-07-28,
  a 4th on a new tier 2026-08-27), THRESHOLD MET, promotion executed 2026-08-26** (2026-07-09 agy, dispatched as an adversarial
  spec REVIEWER, "ignored the review framing, chose to IMPLEMENT" and overwrote a
  file at an absolute real-repo path; 2026-07-14 agy edited 4 files despite
  read-only in sweep-6; 2026-07-28 a review subagent deleted a stale-response
  guard from a live working tree). Only the filesystem boundary is a control.
  Now applied at `skills/delegation-and-review/SKILL.md:423` (classify by tools
  held, not by brief) with the worktree/enforced-copy clause at :431.
  - **4th instance, 2026-08-27, found by probe not by damage — and it extends the
    rule.** grok CLI 1.0.5 dispatched with the playbook's own "Do NOT edit any file"
    brief wrote outside its `--cwd` on first ask; so did `--disallowed-tools` and both
    `--sandbox` names tried (5/5 uncontained configs). Only a positive `--tools`
    allowlist held (2/2). **New mechanism worth carrying: the control flag itself can
    fail OPEN — one unrecognised name in `--tools` silently voids the entire allowlist,
    rc=0, no warning, full write+shell restored.** So "I passed the containment flag" is
    itself a self-report. Verify a boundary by ATTEMPTING AN ESCAPE, never by reading the
    flag name. Landed as routing-map rule R-D + [[workflow-grok-subordinate]] §CONTAINMENT.
  - ⚠️ **Corrected 2026-08-26 — this counter was wrong in two ways at once, and
    the two errors masked each other.** It read "2 instances" (the 07-09 case was
    never counted) AND asserted the rule was already "Applied in
    `delegation-and-review`" when `isolation: 'worktree'` appeared in no rules
    file at all. §3 says promote at 3; the third instance landed 2026-07-28, so
    the promotion was a month overdue and only ran because an audit tripped over
    it. **A counter that believes its rule is already applied never promotes —
    so when you log an instance, re-grep the claimed destination in the same
    edit.**

## 2026-08-27 — Word-presence diffs certify words, not bindings (3 compressions, 3 escapes)
- What happened: Three consecutive rules-file compressions (3ade6e2, 4ab2a56, 514a227)
  were each verified by grep/token-diff and passed; external review then found a real
  loss in every one: a pre-registration TIMING order (words all present, before/after
  lost); a dropped NON-FREE qualifier that made the sentence false against data 8
  lines above; 9/10-vs-4/20 numbers detached from their subject (-medium) and
  re-attaching to the adjacent -low sentence; ">=4 independently-authored unseeded
  defects" silently merging two independence conditions into one.
- Root cause: token-presence checks are order-blind — a binding (subject↔number,
  scope↔claim, condition↔condition, before↔after) can break while every word
  survives, so the check certifies the wrong invariant.
- Rule change needed: skill-authoring §4 or 40-maintenance §5 — after compressing any
  rule text, re-read each compressed sentence asking WHO/WHAT the numbers and
  qualifiers now attach to (a bindings pass, not a words pass); word-diff remains
  necessary for extractions but is never sufficient for rewording. External lens
  stays mandatory for compression commits (this is the existing "self-review is no
  substitute" line — 3/3 rounds confirm it).
- Probe (2026-08-27, same day): pre-registered synthetic probe (6-clause fixture,
  4 planted bindings, real word-budget pressure after two design-review rounds —
  codex and grok both found the first fixture draft satisfiable by line-joining
  alone, 0 bindings at risk). Bare arm 3/4 clean, 1/4 real FAIL (dropped a tier's
  numbers while keeping the adjacent tier's — the exact subject↔number break from
  the production escapes). Ruled arm (rule text appended) 2/2 clean. n small,
  effect consistent with the 3 production escapes above — PROVISIONAL, not proof.
- Status: applied-on 2026-08-27 — folded into skill-authoring SKILL.md §5 step 2
  ("three cuts" bullet) with full text + evidence in
  `references/distilling-rules.md` §Compression and restructuring passes.
