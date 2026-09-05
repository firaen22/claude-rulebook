# Exhaustive discovery — the sweep protocol

Load this for **miss-is-costly audits** (security, money paths, data-leaving-the-machine)
and any **"find ALL of X"** task where a single missed instance is expensive. For an
ordinary "does this work / find the bug" pass, the standard single-round T5 review is
enough — do NOT pay for this machinery on cheap-miss tasks.

**Honest ceiling first.** This protocol raises audit COVERAGE — it makes a weaker
orchestrator search more of the space and quit less early. It does NOT manufacture the
ability to spot an unbriefed, off-spec defect that no finder was pointed at; that is a
model-tier property, not a rule (measured: beyond-the-brief defect discovery does not
come back at any retry count — see `feedback_adopt_fable_habits.md`, EXP-6). The
second-independent-reviewer and ceiling-honesty rules in the main skill remain the
backstop for the defects this sweep won't surface. Route the genuinely miss-is-costly
audit to the top tier AND run this sweep; don't let the sweep talk you out of the tier.

## The loop

1. **Inline scout builds the work-list first.** Before any fan-out, do one cheap
   in-context pass to enumerate the search space (the files, the channels, the entities,
   the call sites). Fan out over a known list, not a guess — a fan-out over an
   imagined work-list inherits the imagination's blind spots.

2. **Axis-diverse parallel finders — each searches a DIFFERENT way.** Redundant finders
   that all search the same way find the same things and miss the same things. Give each
   finder a distinct axis so their blind spots don't line up:
   - by-container (dir / module / package)
   - by-content (grep the pattern / the dangerous call / the string)
   - by-entity (per user-input source, per external boundary, per credential)
   - by-time (recent diffs, the migration window, the last N commits)
   One axis per finder; the union covers what any single angle misses.

3. **Dedup against SEEN, not against CONFIRMED.** Keep a `seen` set keyed by
   file+line+claim. Deduplicate each new round against everything ever surfaced —
   including findings the verifier already REJECTED. Dedup against only the confirmed
   set makes rejected-then-rediscovered findings churn forever; the loop never
   converges.

4. **Stop only after K=2 consecutive empty rounds.** One clean round is not convergence
   — the tail is exactly where the rare instance hides. Keep spawning finders until two
   rounds in a row surface nothing new (after dedup). A simple `while (found < N)` stops
   too early and silently.

5. **One completeness-critic pass feeds the next round.** After a round, a single agent
   asks: what modality did we NOT run, what claim is still unverified, what source went
   unread, what axis has no finder? Whatever it names becomes the next round's work —
   this is what turns "I found some" into "I can state what's left".

6. **No silent caps.** If you bound the sweep (top-N per finder, sampling, a hard round
   cap), SAY what was dropped in the report. A bounded sweep reported as exhaustive
   reads as "covered everything" when it didn't — the exact failure this protocol exists
   to prevent.

## Verification framing inside the sweep

Every surfaced finding is verified by an agent prompted to **refute** it (see main skill
§4): "try to refute this; report NOT CONFIRMED unless you can reproduce it." When a
finding can fail in more than one way, give the verifiers **distinct lenses**
(correctness / security / does-it-reproduce) rather than N identical checkers — diverse
lenses catch failure modes redundancy can't. This is the same anti-confirmation-bias
rule as the main dual-review section, applied per finding.

## Workflow-tool shape

This maps directly onto the Workflow tool's loop-until-dry + parallel-barrier patterns
(the tool description documents the stage topology — barrier only where a stage consumes
ALL of the prior stage's output; per-item pipeline otherwise). Force `schema` returns on
every finder and verifier so `seen`-dedup and the empty-round check run on structured
data, not parsed prose. Validate fan-out array lengths before any synth/critic stage —
a critic fed empty arrays invents plausible completeness (see
`finding_workflow_synth_confabulates.md`).

## Accepting a sweep/completeness claim (moved from SKILL.md §4, 2026-07-21)

A sweep/completeness claim is accepted only by re-running its named search AND
challenging coverage with one differently-shaped query (broader/structural or
class-aware) — a narrow pattern reproduces its hits AND its misses.

## Scoping a token/pattern sweep (added 2026-07-21)

A 53-file styling sweep + three review rounds + a merged PR all missed the
defect: it lived in a global CSS utility class, not in component files. Each
follow-up round found a category the previous round's grep pattern structurally
excluded (saturated color families at other tiers, class-emitting helper
functions), surfacing as successive user "still broken?" re-asks.

- Before sweeping, enumerate EVERY surface that can generate the pattern:
  component literals, global CSS utility classes, CSS modules, helper functions
  returning class strings — and the full family/tier matrix of the token space.
- Acceptance for a styling sweep is rendering (drive the real page/theme), not
  grep-zero: grep proves absence of one spelling, not absence of the effect.

## A failed grep is not evidence of absence (added 2026-08-29)

Verifying that a cited rule/order/symbol still lives at its claimed destination,
a zero-hit grep has TWO causes — the text is gone, or your pattern missed it —
and the second is the common one. Measured 2026-08-29 during a LESSONS
compression: 3 of 10 destination greps returned nothing; all 3 rules were live.
The patterns had been built from the CITATION's paraphrase, not the file's
wording (`classify by tools held` vs the live `Classify an agent by the TOOLS IT
HOLDS`). Recording those as rot would have re-added three orders on top of live
text — the duplicate-then-contradict failure the caches are built to avoid.

- Before recording any destination as missing: re-search on a DISTINCTIVE
  content word from the rule rather than its cited phrasing, case-insensitively,
  across the whole tree — not just the cited file.
- A hit in a `.bak`/backup copy but not the live file is a real signal, but read
  the diff before calling it a deletion: the live text may have been REPLACED by
  a stronger rule. (Same sweep: one "missing" quote had been superseded by a
  per-executor rule that INVERTS it for two executors — the citation was stale,
  the rule was not, and re-adding the old sentence would have restored a wrong
  order.)
- Cite destinations in `40-maintenance.md` §3's form — `<file:line> "<operative
  sentence, pasted from the grep hit>"` — and treat the SENTENCE as the durable
  key, the line as a dated stamp of when the grep hit. Never cite a line alone,
  and never cite a paraphrase: lines drift on every edit above them, and a
  paraphrase never matched to begin with. Off-by-one is the specific trap — a
  line number derived by ARITHMETIC from a known drift is not a grep hit; re-open
  the file and confirm the sentence sits on the line you are about to write.
- **Done-state — "missing" may be recorded only when all four are true, and the
  record must show them:** (1) the tree-wide content-word query is written down
  verbatim, (2) it returns zero hits in live files, (3) backup/`.bak` hits were
  either absent or opened and diffed against live, and (4) the rule's own
  destination file was opened and read, not just grepped. Fewer than four → the
  status is UNRESOLVED, never missing. Absent that record, a later reader cannot
  tell a real deletion from a bad pattern — which is the whole failure this
  section exists to stop.
