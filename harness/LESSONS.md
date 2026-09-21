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


## 2026-09-11 — Clean-room author subagent read the forbidden file AND was silently served by Haiku 4.5
- What happened: dispatched an `Agent` (no `model:` override) to write `qimen-badju-v2.ts`
  clean-room with a prose "do NOT open qimen-badju.ts" rule. Transcript audit: all 53
  turns served by `claude-haiku-4-5-20251001`; it ran `head -50` and `sed -n '50,200p'`
  on the forbidden v1 file, then spawned a child "to port v1 to v2". Output scored
  12/65 perfect, 10,605 breaks. Run voided; redispatched with `model: fable` and a
  hardened brief (no subagents, no shell reads, audited afterwards).
- Root cause: two mechanisms. (1) The read ban was prose and the agent held Bash —
  an instance of the CLOSED "read-only instruction is not a control" counter (covered
  at delegation-and-review SKILL.md:429; NOT re-incremented). (2) NEW: an in-harness
  `Agent` without `model:` inherits the configured default subagent model, which was
  Haiku, and nothing in the completion notification says which model served it — the
  experiment's whole variable (model quality) was silently swapped.
- Rule change needed: `~/.claude/harness/10-orchestration.md` — when the served model
  is part of what the task measures (or the task is judgment-heavy), pass `model:`
  explicitly on every `Agent` dispatch AND confirm post-hoc from the task transcript's
  `"model":"…"` field before trusting the result (mirror of cross-model-review §5
  identity rule, extended from reviewers to authors).
- Status: applied — `10-orchestration.md` §0/§2/§5 (commit `00a9b38`, 2026-09-11), as
  A1 (§0/§2, explicit `model:` when load-bearing) + A2 (§5, post-hoc served-vs-requested
  tier confirmation, incl. `spawnDepth ≥ 2` descendants; VOID + quarantine on unverified
  or disagreeing identity). Cross-family reviewed (codex + grok, 3 rounds) plus a
  same-family Fable pass.

## 2026-09-11 — Orphaned grandchild agent wrote into the tree after its parent "completed"
- What happened: run-1's child ("Port v1 to v2") kept running after run-1 reported
  completed and after I had restored the stub and dispatched run 2 in the same tree.
  It overwrote `qimen-badju-v2.ts` with a 1,381-line v1 port at 16:44 while run 2
  was mid-exploration. Caught only because the completion notification carried an
  unfamiliar task-id. Run 2 had not yet written or re-read the file → resumed.
- Root cause: a parent's completion notification does not imply its children are
  finished; two authors then share one working tree with no write boundary.
- Rule change needed: `~/.claude/harness/10-orchestration.md` — before dispatching
  into a tree, `ListAgents` and confirm no subagent (any depth) is alive; a void run's
  descendants must be stopped explicitly. Prefer `isolation: "worktree"` for any
  author whose output is the experiment's artifact.
- Status: applied — `10-orchestration.md` §7 (commit `00a9b38`, 2026-09-11) as rule B,
  but NOT as originally prescribed: cross-family review (3 rounds, codex + grok)
  reproduced that `ListAgents` returns peer sessions only (cannot see in-session
  Agent-tool descendants) and that a dispatcher never automatically holds a
  grandchild's task-id — so the pre-dispatch-check design above cannot work. Landed
  instead as PREVENTION: mandatory `isolation: "worktree"`/fresh path for any
  background author whose output IS the artifact, one writer per path, forbidden from
  spawning background children that write it; a voided run's tree stays quarantined
  (a replacement finishing elsewhere does not release it).

## 2026-09-16 — codex v0.154.0 silent no-assistant-turn + grok idle; cross-family review gate blocked
Running the cross-model-review gate on 3 opus-pack doctrine ports (~12KB inline
packet, well under the documented ~30KB codex cliff), BOTH cross-family CLIs failed
all 3 rounds — a tooling degradation, not a packet problem:
- **codex v0.154.0**: no or partial assistant turn. Round 1 (gpt-6-astra) stdout ended
  at the echoed prompt (no `codex` marker, no `tokens used`, `-o` never written); round 2
  (astra) emitted only a `[assumed]` preamble line then stopped; round 3 (gpt-5.6-luna,
  effort=high) again produced NO assistant turn at all. This is the "preamble-only → fully
  silent" degradation the codex playbook documents for >~30KB packets, now firing at 12KB
  on v0.154.0 — the cliff MOVED. Re-measure the inline-packet boundary on this version
  before trusting a codex review; check for the `codex` marker, never read an empty answer
  as a verdict.
- **grok-4.6**: classic multi-step IDLE — narrated its plan ("I'll read the brief, then
  the three files, then write the report") and exited without executing, 0–170 bytes, on
  BOTH the staged-files recipe AND an inline-judgement packet. Neither shape cured it this
  session.
- **Consequence (cross-model-review §6):** could not assemble ≥2 working families → cross-
  family gate UNMET, recorded as a gap; fell back to same-family fresh-context floor (my
  own re-derivation + one general-purpose agent, both PROCEED). Did NOT fake a dual-family
  PROCEED. Retry the CLIs next session; if codex stays silent at small packets, treat
  v0.154.0 as regressed and pin/roll back or re-probe the boundary.

## 2026-09-19 — `git checkout -- <file>` inside a probe reverted my own uncommitted edit on a dirty tree
- What happened: during a tamper-detection probe in a private project I appended a byte to
  a helper script, confirmed the guarded command refused, then "restored" with
  `git checkout -- <file>`. The tree was dirty: that command also discarded the uncommitted
  feature edit to the same file. Recovered only because a `cp` backup had been taken
  seconds earlier; re-verified by sha256 == the observed record's `helperSha256`.
- Root cause: `git checkout -- <path>` restores HEAD, not "the state before my probe" — on a
  dirty tree the two differ, and the probe's own edit and the pending work are indistinguishable
  to git.
- Rule change needed: NONE (existing rule covers it — operational-rigor §2 "baseline before you
  mutate" / repo-baseline). Practice: on a dirty tree, restore a probe by COPY (`cp file file.bak`
  → probe → `cp file.bak file`, verify hash), never by `git checkout`/`git restore`.
- Status: noted
