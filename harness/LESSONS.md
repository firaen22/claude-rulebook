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

## 2026-08-28 — git-filter-repo hard-resets the worktree: it ate another session's uncommitted work
- What happened: ran `git-filter-repo --replace-text --force` on `~/.claude` to
  purge client PII from history. It rewrote 53 commits correctly, but also
  hard-reset the working tree — silently destroying 172 uncommitted insertions
  another session had made at 15:27 to `ground-truth-gates/SKILL.md`,
  `skill-authoring/SKILL.md`, `skill-vetting/SKILL.md`. I had SEEN those files in
  `git status` minutes earlier, correctly identified them as another session's
  work, and deliberately left them uncommitted — which is exactly what made them
  destroyable. Recovered byte-exact (172 insertions / 9 deletions, diffstat
  matched) from the Obsidian vault copy, because the sync had run at ~15:5x,
  after their edits and before the rewrite. Pure luck of timing.
- Root cause: my `git bundle --all` backup captured REFS ONLY. Uncommitted
  worktree state is not in any ref, so the backup I took specifically to make the
  rewrite safe could not have restored the thing the rewrite actually destroyed.
  I verified the backup existed; I never asked what it contained.
- Rule change needed: NONE new — this is operational-rigor §4's "verify by
  execution" and §2's baseline-before-mutation applied to backups themselves.
  Worth carrying as a concrete instance: **a backup is not a backup until you
  name what it does NOT cover.** For history rewrites specifically: `git stash`
  or copy the dirty tree FIRST, or refuse to rewrite a dirty repo at all —
  filter-repo does not warn, and `--force` suppresses the check that would have.
- Second-order lesson: **leaving another session's uncommitted work in place is
  not the safe option it looks like.** "Don't touch it" protects provenance but
  offers zero protection against a destructive operation in the same repo. The
  safe move is stash-or-copy it, act, then restore it untouched.
- Status: applied-on 2026-08-28 (recovery verified; no rules-file edit owed)

## 2026-08-28 — the brief must describe the delivery: two tiers, one mechanism
- What happened: reviewing the sub-harness, I dispatched codex with the files INLINED
  in the prompt but left the brief's line "FILES UNDER REVIEW (in `./files/`)" intact.
  codex shell-globbed `/private/tmp/files`, found nothing, and returned no review —
  three times, ~50 min, before I read the bytes instead of theorising. Identical
  mechanism to grok's 08-28 attempt 3 (brief described staged files that were never
  written; grok narrated "the workspace is empty" and exited). **Second instance, second
  tier: a brief that contradicts its own delivery sends the subordinate hunting for
  material that isn't there, and the failure looks exactly like model incapacity.**
- Also measured, unrelated to the above and NOT a model failure: codex v0.149.0's inline
  packet cliff sits just above **~30KB** (16/29.6 OK · 32/33/45 preamble-only · 51-63
  silent, rc=0, `-o` never written), against the playbook's `79KB packet verified` from
  v0.144.4. Interleaved PONG controls passed throughout, which is what separated
  "packet too big" from "quota" and from "model broken".
- Root cause: I built the packet and reused the brief without re-reading the brief
  AGAINST the packet. The dispatch checklist asked whether the fields were filled, not
  whether they were TRUE of this delivery.
- Rule change needed: none new — this is the packet-SHAPE rule the same day's grok
  retraction already established, now shown to be tier-independent. Landed as a
  dispatch-time check rather than prose.
- Status: applied-on 2026-08-28
- Destination (asymmetry + the rule): `memory/reference_subordinate_routing_map.md` §2a —
  "Review packet SHAPE — codex and grok need OPPOSITE shapes … A dispatch that returns
  nothing is a SHAPE bug until proven otherwise" (grepped 2026-08-28)
- Destination (checklist): `harness/30-delegation-templates.md` — "REVIEW dispatches to a
  CLI: the target is STAGED AS FILES the reviewer reads, never pasted into the prompt."
  (grepped 2026-08-28)
- Destination (the size cliff): `memory/workflow_codex_subordinate.md` — "The 79KB
  inline-packet ceiling is v0.144.4's and does NOT hold on v0.149.0." (grepped 2026-08-28)
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
