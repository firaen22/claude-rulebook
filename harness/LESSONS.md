# LESSONS — write-backs after mistakes (format: 40-maintenance.md §3)

Append-only between compressions. Compress at >150 lines / >20 entries.

Compressed 2026-07-12: six applied entries (2026-07-05 → 2026-07-12) moved
verbatim to `LESSONS-archive.md`.
Compressed 2026-08-25 at 243 lines / 19 entries: ALL 19 entries (2026-07-11 →
2026-08-25) moved verbatim to `LESSONS-archive.md`. Its summary line — "what
survives here is only what is NOT closed: one promoted rule-change proposal
awaiting approval, one open external thread, and the recurrence counters" — was
already stale before the 08-27 pass: the proposal was applied 08-26, and the
"open external thread" had no entry in the pre-compression file at all — a
claim never supported by an entry, not one that aged out. Dropped as
unsupported, not resolved; recorded here so the deletion is visible. No `noted` entry existed in
the 08-27 pre-image, so this compression removed none (§4 forbids that);
whether 07-12 or 08-25 compressed a `noted` entry away was NOT re-checked.
Compressed 2026-08-27 at 196 lines (wc -l) / 7 items (4 dated or applied
entries + 3 counter bullets) — LINE trigger only (>150); the >20-entry trigger
was nowhere near met. Moved verbatim, 5 objects: the applied "a fix is a change"
rule change, the applied "word-presence diffs" entry, both grok output-empty
entries (the "truncates" claim, superseded; its idle correction), and the
read-only-is-not-a-control counter now that its promotion is EXECUTED. Left in
place: the two still-climbing counters. **Every destination was grepped and its operative sentence
quoted in the archive banner before the move** — the check both earlier
compressions skipped. One order found homed nowhere (re-grep a claimed
destination in the same edit) was written into `40-maintenance.md` §3 first;
two rules files back-referencing moved entries were re-pointed in the same edit.

⚠️ **CORRECTED 2026-08-26.** The 07-12 and 08-25 blocks above used to claim every
moved entry "was verified applied by grepping its rule in the destination cache
before the move." That was false, and is corrected at the archive's banners —
read those, not a Status line. Both were re-audited 2026-08-26 at PRESCRIPTION
granularity: the 08-25 pass named destinations for only 9 of 19 and verified
those 9 (4 failures among the 10 it never named); the 07-12 pass named no
destinations at all (5 of 10 prescriptions not live as written). Evidence:
`claude code technique/experiments/lessons-applied-audit-2026-08-26/`.
**Moving an entry here closes nothing. Before writing "applied", grep the
destination and quote the operative sentence — a "compiled into §N" reference
decays as files are reorganized and nothing re-checks it.**

## RECURRENCE COUNTERS (applied rules that are climbing toward promotion)

Kept as counters only — full text in `LESSONS-archive.md`. At 3, §3 says draft
the rule edit and ask in-session.

- **Subordinate holding write access reverts/wipes concurrent work — 2 instances**
  (2026-07-14 codex constraint-enforcement wiped files silently; 2026-07-28 codex
  deliberately reverted my landed fix and then TRUTHFULLY reported "no other file
  was modified", because it had put it back). Rule is applied at
  `skills/delegation-and-review/SKILL.md:444` — "While ANY subordinate holds
  write access to a tree, land nothing in it yourself: stage in scratch, merge
  after it exits" (grepped 2026-08-28); the counter matters because the two
  instances had different mechanisms and neither was caught by reading the
  report as specified.
- **`gate-before-commit` cannot resolve `cd $VAR` — 2 instances** (2026-07-11,
  2026-08-04; same hook, same shlex-inert-variable mechanism, both times it fell
  through to `$CLAUDE_PROJECT_DIR` and ran the wrong repo's gates). Applied in
  40-maintenance §1's hook rows + `~/.claude/projects/-Users-yauch-Documents-claude-code-technique/memory/feedback_hook_block_read_the_repo_line.md`
  (PROJECT memory, not global `~/.claude/memory/` — path corrected 2026-08-26
  after the bare `memory/` prefix sent an audit searching the wrong tree).
  Write literal absolute paths in any commit-adjacent `cd`.

## CLOSED COUNTERS (promotion executed — reopen rules only)

The at-3 promotion duty above does NOT apply to entries here.

- **A read-only instruction is not a control — CLOSED at 4 instances.** Promotion
  executed 2026-08-26 (3rd instance had landed 2026-07-28); 4th instance
  2026-08-27: grok — prose brief, isolated `--cwd`, `--disallowed-tools`, and
  both `--sandbox` names all uncontained (5/5), only the `--tools` allowlist held
  (2/2), and the NEW mechanism is that `--tools` FAILS OPEN on one unrecognised
  name (rc=0, no warning). Live at FOUR destinations:
  `skills/delegation-and-review/SKILL.md:423` (classify by tools held, not by
  brief) and `:431` (worktree/enforced-copy boundary), routing-map rule R-D
  ("verify the boundary by attempting an escape, never by reading the flag
  name"), and `workflow_grok_subordinate.md` §CONTAINMENT. Full history in
  `LESSONS-archive.md` (08-27 compression). Reopen procedure: if a new
  incident's mechanism is covered by NONE of those four, append a new dated
  LESSONS entry as instance 1 of a NEW counter — never silently increment this
  closed one. (CLOSED here is counter-section vocabulary, not a `Status:`
  value.)

## 2026-08-28 — cross-model review of the 08-27 compression (codex + grok)
- What happened: user-ordered review of the compression + §3 rule by codex
  (inline packet, read-only) and grok (staged-files recipe, `--tools` contained,
  containment verified by post-run dir diff). codex: 4 findings. grok: 23, incl.
  3 CRITICAL my own verification pass missed — the closed-counter stub was a
  REWORD that dropped 2 of 4 destinations, the archived counter lost its section
  heading (a section-membership binding the "verbatim, no BINDINGS pass owed"
  claim didn't cover), and the new §3 rule collided with append-only.
  Reproducing codex's mildest finding also exposed that commit `cb6a9ae`
  (another session, same morning) had deleted the grok playbook's §"Empty has
  TWO causes" triage AND §"Tool-use short-circuit" hard safety rule without
  re-homing them — restored same day, reconciled with that commit's legitimate
  retraction. All fixes applied 2026-08-28; UNVERIFIABLE-tagged banner claims
  were re-grepped against live destinations before accepting.
- Root cause (of the misses): my compression verified MOVED TEXT (verbatim) and
  ORDER HOMES (grep) but never re-derived the REWRITTEN summaries against their
  originals — the exact "a fix is a change" / bindings-pass duty the moved
  entries themselves prescribe. Section membership is a binding; a stub is a
  reword.
- Rule change needed: one PENDING item needs user sign-off (below); everything
  else was fixable within existing autonomous-edit permissions.
- Status: applied-on 2026-08-28, except the two `noted` items below.

## 2026-08-28 — two governance gaps closed on user order
- **`40-maintenance.md` had no row in its own §1 permissions table** (found by me
  and independently by grok F15) — so the 08-27 compression's addition of a §3
  standing rule was self-authorized with no permission bit governing it.
- **A general diagnostic order was homed nowhere** (grok F9): the grok-SPECIFIC
  triage lives in the playbook, but the general rule survived only in the
  archive — which §4 forbids as a home.
- Root cause, both: a file that governs every other file's edit permissions never
  had its own row, and a compression is a tempting silent channel for adding one.
  The new row closes the channel explicitly.
- Rule change needed: both applied on user order 2026-08-28.
- Status: applied-on 2026-08-28
- Destination (§1 row): `harness/40-maintenance.md:22` — "| `40-maintenance.md`
  (this file) | YES wording; **ASK USER** for new standing orders / thresholds |
  … **Compression is not a rule-addition channel** …" (grepped 2026-08-28)
- Destination (diagnostic rule): `skills/operational-rigor/SKILL.md:274` —
  "**Naming a mechanism from a symptom is a claim, not an observation — read the
  output bytes before naming the cause.**" (grepped 2026-08-28). Ships
  `unprobed`.
