# LESSONS — write-backs after mistakes (format: 40-maintenance.md §3)

Append-only between compressions. Compress at >150 lines / >20 entries.

**Moving an entry here closes nothing. Before writing "applied", grep the
destination and quote the operative SENTENCE — a "compiled into §N" reference, a
line number, or a paraphrase all decay, and nothing re-checks them.** Method for
doing that correctly, including when a zero-hit grep means the rule moved rather
than died: `skills/delegation-and-review/references/discovery-sweep.md`
§"A failed grep is not evidence of absence".

**Looking for an entry that is not here?** Every compressed entry is in
`LESSONS-archive.md`, verbatim, under a dated banner — grep THAT file before
concluding a lesson was never written or re-adding it. A heading absent from this
file is not evidence the lesson does not exist.

## Compression ledger

Narrative detail for each pass — what moved, what was verified, what was dropped
and why — lives in that pass's banner in `LESSONS-archive.md`. One line each here.

| Pass | Size at trigger | Moved | Note |
|---|---|---|---|
| 2026-07-12 | — | 6 applied entries | Named no destinations; 5 of 10 prescriptions later found not live as written. |
| 2026-08-25 | 243 lines / 19 entries | all 19 | Named destinations for only 9 of 19; 4 failures among the 10 it never named. Dropped one unsupported claim. |
| 2026-08-27 | 196 lines / 7 items | 5 objects | First pass to grep every destination and quote its sentence. Homed one orphaned order. |
| 2026-08-29 | 181 lines / 4 entries + 3 counters | 4 entries | All 10 destinations re-grepped: all resolve, but 3 line numbers drifted, 1 paraphrase never matched, 1 sentence had been REPLACED by a rule that inverts it. Homed the failed-grep order in discovery-sweep.md. |
| 2026-09-06 | 247 lines / 5 entries | all 5 | 30 destinations re-grepped whitespace-normalised: 29 resolve. 1 REPLACED (`41-file-registry.md` "prospective (new/edited lines only" — that section now records the 09-02 migration instead); the ≤150 rule itself is live in `40-maintenance.md` §4, so the prescription stands and only the citation rotted. Reverse-sweep found no pointer to any moved heading. Nothing dropped. |

⚠️ **CORRECTED 2026-08-26.** The 07-12 and 08-25 passes used to claim every moved
entry "was verified applied by grepping its rule in the destination cache before
the move." That was false. Read the archive's banners, never a `Status:` line.
Evidence: `claude code technique/experiments/lessons-applied-audit-2026-08-26/`.


## RECURRENCE COUNTERS (applied rules that are climbing toward promotion)

Kept as counters only — full text in `LESSONS-archive.md`. At 3, §3 says draft
the rule edit and ask in-session.

- **Subordinate holding write access reverts/wipes concurrent work — 2 instances**
  (2026-07-14 codex constraint-enforcement wiped files silently; 2026-07-28 codex
  deliberately reverted my landed fix and then TRUTHFULLY reported "no other file
  was modified", because it had put it back). Rule is applied at
  `skills/delegation-and-review/SKILL.md:449` — "While ANY subordinate holds
  write access to a tree, land nothing in it yourself: stage in scratch, merge
  after it exits" (re-grepped 2026-08-29; was cited :444); the counter matters because the two
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
  `skills/delegation-and-review/SKILL.md:429` — "Classify an agent by the TOOLS
  IT HOLDS, never by what its brief asks for" (quote corrected 2026-08-29: the
  earlier citation paraphrased it, and the paraphrase matched no text in the
  file) — and `:436` (worktree/enforced-copy boundary; both line numbers were
  cited as :423/:431 before the 08-29 re-grep), routing-map rule R-D
  ("verify the boundary by attempting an escape, never by reading the flag
  name"), and `workflow_grok_subordinate.md` §CONTAINMENT. Full history in
  `LESSONS-archive.md` (08-27 compression). Reopen procedure: if a new
  incident's mechanism is covered by NONE of those four, append a new dated
  LESSONS entry as instance 1 of a NEW counter — never silently increment this
  closed one. (CLOSED here is counter-section vocabulary, not a `Status:`
  value.)

