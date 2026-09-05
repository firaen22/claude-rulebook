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

### 2026-09-02 — a skill's description loses to a hard route that names it nowhere
- Observed: a sampled (not exhaustive) transcript pass found genuine cross-family
  review dispatches where `cross-model-review` never loaded even though CLAUDE.md's
  own `codex = ... reviewer` bullet or the routing map's review rows fired the
  dispatch — including the literal ask "review with codex and grok" (2026-08-25
  03:34, classified OTHER by the sampling subagent's own classifier despite being
  a genuine acceptance-gate review, a discrepancy the classifier itself did not
  catch). A cross-model review of the original diagnosis (codex `gpt-5.6-luna`,
  grok `grok-4.6`, both FIX verdicts) found the first-drafted evidence write-up
  overclaimed precision the sampled data didn't support ("8 genuine reviews ran
  without it" — the sample contains only 2 occasions classified GENUINE-REVIEW,
  both misses) and the first-drafted CLAUDE.md patch left the actual competing
  hard route (the codex bullet) untouched, so the collision it was meant to fix
  would have persisted. Both defects were confirmed by reading the real files,
  not accepted on the reviewers' say-so.
- Candidate mechanism (not causally established — the sample shows misses
  co-occurring with available hard routes, not that the routes caused them): a
  skill `description` is a soft match the model must volunteer; a route already
  sitting in an always-loaded file (CLAUDE.md, the routing map) is a hard match
  already in context. A nearby paragraph pointing at the skill may not help if
  the reader's eyes go straight to the bullet/row — untested until the re-probe.
- Rule: when a skill gates a dispatch that CLAUDE.md or the routing map already
  hard-routes, the hard-route text ITSELF (the bullet, the table row/header) must
  point at the skill — not just a preceding sentence a scanning reader can skip.
- Status: patched 2026-09-02 (CLAUDE.md `codex` bullet now says "loads the
  skill first"; routing map §2, 10-orchestration.md §2, 30-delegation-templates.md
  T5 each got a header note). **Re-probe run same day, PRE arm: the candidate
  mechanism did NOT reproduce.** Fresh sonnet subagents holding the OLD CLAUDE.md
  snapshot fired `cross-model-review` on 6/6 firing phrasings (Skill was the FIRST
  tool call in 5/6 — before any disk file, so the new map/harness notes are not the
  cause either); collision controls 0/2; grader POS/NEG sound. So in fresh context
  the description alone routes these asks; the historical misses were the MAIN
  session model mid-task with a large context — fresh-context routing ≠ mid-session
  routing, and this harness cannot separate "large context dilutes the description"
  from "hard route wins". **POST arm run same day (session started after `455e60c`,
  precondition-checked snapshot): 5/6 fire (Skill first tool in 4/6), C1/C2 0/2,
  B1 none — vs PRE 6/6.** Net: the CLAUDE.md pointer has NO measurable effect on
  fresh-context routing in either direction, and does not over-trigger. The single
  POST miss was the "fix first, then review" shape (F2), the closest analogue to a
  mid-session second-phase review; suggestive at N=1, not evidence. **MID-SESSION
  arm run same day (sonnet subagents, ask sent into ~180k of doctrine context):
  PRE snapshot 3/5 fire (M3 "fix them all…" MISS; M2 "proceed…" HALTED to ask
  review-vs-fix, fired once answered), control silent.** Large context alone does
  not reproduce the misses. The pre-registered "re-run the misses" step landed on
  the POST snapshot by accident — `/compact` rebuilds the subagent CLAUDE.md from
  disk, so "start-time snapshot" was wrong; it is last-rebuild snapshot — and both
  fired 2/2 (N=1 each, directional only). The "fix, then review" phrasing flips 2/4
  across all four arms regardless of the pointer: that is the historical miss shape,
  and the pointer is not shown to fix it. The fix stays harmless and unmeasured,
  NOT verified; the PRE mid-session re-run is closed as not-completable without
  reverting the live CLAUDE.md. Evidence:
  `claude code technique/experiments/cross-model-review-trigger-reprobe-2026-09-02/`.

### 2026-09-02 — harness audit against 22 of one session's own incidents: the shared-tree rules lived only in caches
- What happened: cross-family review (grok-4.6 + codex luna, staged-files recipe;
  then codex sol acceptance ×2, cap reached; then a grok + sol ADVICE round on the
  sign-off set) of the seven rules files against 22 incidents mined from this
  session's transcript. Reproduced on disk before editing: `~/.claude/CLAUDE.md`,
  `10-`, `20-`, `30-` had ZERO hits for backup/stash/dirty-tree/bare-HEAD — the rules
  behind the three worst incidents (filter-repo wiping 172 foreign uncommitted lines,
  2026-08-28; a codex packet diffed from bare `HEAD` on the shared tree, 2026-08-29; a
  stale `/tmp` scratch `cp`'d over a shared MEMORY.md, 2026-09-02) existed only in
  skill caches. Also found: a false quote in `10-orchestration.md` §2 ("START HERE"),
  a self-declared-stale count in `40-maintenance.md` §4, the §1 self-row ordering both
  "ASK USER for new orders" and "add it and say so", and CLAUDE.md line 3 carrying
  history that line 1 bans.
- Root cause: rules were written cache-first and never written back to the harness
  source; §5 write-back runs source→cache only. Second: my first shared-tree checkbox
  inherited the shape of the worst incident (mutation-only) and missed the read-only
  packet case. Third: my own review round reordered the §2 agy/codex row — a
  routing-strategy change I did not list for sign-off; the advice round caught it.
  Fourth: I recommended "approve all / defer all"; both advisers rejected that in the
  same places (a third copy of load-skill-first; a threshold the corpus already fails
  170×; two zero-growth contradictions I had deferred). Rewordings were authored by
  me from the findings, not pasted.
- Rule change needed: applied — see Destination. All standing-order-class and
  CLAUDE.md edits landed on the user's explicit sign-off ("proceed with codex" =
  sol's set), per §1. The agy-row edit was reverted. The ~150 MEMORY.md threshold is
  owner-set and PROSPECTIVE (new/edited lines only); legacy over-length lines are a
  separate task.
- Status: applied-on 2026-09-02.
- Destination: `CLAUDE.md` line 61 "the one syntax, everywhere"; line 95 "load the
  `operational-rigor` skill (repo-baseline) first"; line 3 dates removed.
  `10-orchestration.md` §0 "Bash cwd is reset to the project dir after every call" /
  "records which rebuild each arm inherited"; §2 "A phase boundary does not reset
  this gate"; §4 "recomputed from the cited evidence before you publish it" /
  "output, not idleness". `20-judgment-rubrics.md` §3 "a diff or review packet is
  built from that backup, never bare `HEAD`"; §5 "`tail -N` is display only"; §6
  "narrowing a claim is not correcting it". `40-maintenance.md` §1 self-row "draft
  it, ASK USER in the same turn, and leave it unapplied until approved"; §1 step 3
  "landed AT THE LOCUS the diagnosis named"; §3 "NO exemptions, \"pre-existing\"
  included"; §4 "a NEW or EDITED line is ≤150 characters"; §5 "never changes
  precedence". `41-file-registry.md` Memory files "is prospective (new/edited lines only".
  `50-letter` Handoff 2026-09-02 "advisory history, not standing rules".
  `cross-model-review/SKILL.md` §2 "never bare `HEAD`"; §5 "separately NAMED artifacts".

## 2026-09-04 — An unverified failure SIGNATURE drove four experiments down the wrong road
- What happened: the 09-02 agy review-packet harness recorded `r.stderr` but graded on
  `r.stdout.strip()` alone, and its PREREG asserted the empty-return signature was
  "rc=0, empty stdout, EMPTY stderr". Nobody ran `print(r.stderr)`. That unverified
  clause survived four experiments (09-02 sweep, 09-03 reduced sweep, 3.8-solo, `${`
  minimal-pair), one VOIDed probe, a 12-feature structural hunt, and three memory
  findings — all hunting a "transport"/"size cliff" cause. Capturing the text on
  2026-09-04 showed every failing call carried 300 bytes: `jetski: no output produced —
  a tool required the "command" permission that headless mode cannot prompt for, so it
  was auto-denied.` A no-tool preamble took the worst packet from 0/4 to 4/4 live
  (Fisher p=0.0286). Cost: ~6 hours of runs.
- Root cause: the harness DISCARDED the diagnostic channel it had already captured, and
  a prose PREREG line ("empty stderr") was then treated as a measured fact by every
  later run that imported the harness byte-for-byte — importing the code also imported
  its unexamined claim.
- Rule change needed: NONE — `20-judgment-rubrics.md` §2 and R0 already cover it
  ("reproduce before trusting", expected-before-actual). This is an instance, not a gap.
  The operational specifics are homed in the agy playbook instead.
- Status: applied-on 2026-09-04.
- Destination: `~/.claude/memory/workflow_agy_subordinate.md` READ FIRST block —
  "Diagnosis rule: `capture_output=True` then READ `r.stderr` — never test only"
  / "`r.stdout.strip()`.** A \"silent\" agy failure is almost never silent."

## 2026-09-04 — Two driver bugs produced plausible scoreboards; the soundness gate only covered the grader
- What happened: codex hard-axis drift re-probe (`experiments/codex-hardaxis-2026-09-04/`).
  (a) `run_fix(){ local task="$1" t="$2" d="$BASE/$ROOT/${task}__t$t"; ...}` — bash
  expands every `local` argument in the caller's scope before assigning, so `${task}` was
  unbound under `set -u`; H2/H3 never launched, H1 ran only because `$t` happened to exist
  as the loop's global with the right value, and every cell that existed scored perfect.
  (b) three `codex exec ... &` jobs shared the shell's stdin; codex blocked on "Reading
  additional input from stdin...", hit the 300s timeout with 0 files changed, and the
  grader scored the unmodified seed as a MODEL failure. Both graders had passed the
  dual-reference gate (good-ref/bad-ref) minutes earlier. Also (c): the July harness this
  rebuilt lived in `scratchpad/` (=/tmp) and had been wiped — same class as the 2026-09-02
  stale-`/tmp` incident above; the finding's "harness pointer" was a tmp path.
- Root cause: the soundness gate certified the GRADER (does it pass good and fail bad) and
  nothing certified the DRIVER (did each cell actually run the model), so driver faults
  surfaced as missing cells or as model failures — both shapes a scoreboard reader accepts.
- Rule change needed: applied — experiment-protocol Rule 2 (project skill) gains a driver
  gate: pre-registered rows `cell count == N` / `no latency near timeout` / `output != seed`
  checked before any score is read; one `local` per line; `</dev/null` on every backgrounded
  subordinate call. Rule 6 already says copy the harness into the repo — (c) is an instance,
  not a gap; the harness is now git-tracked (`b5b10d7`).
- Status: applied-on 2026-09-04.
- Destination: `claude code technique/.claude/skills/experiment-protocol/SKILL.md` Rule 2
  "**The DRIVER gets the same gate as the grader.**" / "check them BEFORE reading any
  score" (grepped 2026-09-04: line 23; wrapped phrase count 1).

## 2026-09-06 — Round-2 cross-model review: two dispatch faults were mine, both already documented
- What happened: dispatching codex + grok for round-2 review of the compaction-hook
  harness's StdoutTap/stdin-pump fix (`hooks/harness/`). First codex call hung: `codex
  exec` with a non-TTY stdin printed "Reading additional input from stdin..." and never
  ran. Second call errored rc=1: "Not inside a trusted directory and
  --skip-git-repo-check was not specified" (the review packet dir under scratchpad/
  is not a git repo). Grok returned 382 bytes of narration about its reading plan
  instead of the review, no verdict.
- Root cause: the codex invocation omitted `</dev/null` and `--skip-git-repo-check`;
  the grok prompt omitted an explicit "produce the review text itself, do not narrate"
  instruction. All three are pre-existing, named gotchas in the routing playbooks —
  I dispatched from memory instead of re-reading the playbook before the call.
- Rule change needed: NONE — `workflow_codex_subordinate.md` line 40 already has
  `</dev/null` in its canonical background-dispatch command and line 44 already says
  "Must be in a trusted dir OR pass `--skip-git-repo-check`"; `workflow_grok_subordinate.md`
  line 262 already documents "narrates its plan and exits" as the failure mode. This is
  an instance of not applying an existing rule, not a gap.
- Status: applied-on 2026-09-06 (no edit needed; re-verified the destinations carry
  the operative text).
- Destination: `~/.claude/memory/workflow_codex_subordinate.md:40` "`codex exec -m
  gpt-5.6-luna --skip-git-repo-check -s workspace-write "$(cat /tmp/codex-spec.txt)"
  </dev/null > /tmp/codex-out.txt 2>&1 &`" and `:44` "Must be in a trusted dir OR pass
  `--skip-git-repo-check`."; `~/.claude/memory/workflow_grok_subordinate.md:262`
  "narrates its plan and exits".
