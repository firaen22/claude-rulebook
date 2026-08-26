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
