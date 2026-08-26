# Distilling incidents into rules — cases & A/B evidence (kernels in SKILL.md §2, §4)

Extracted 2026-07-17 from SKILL.md during the size-control extraction. The
SKILL.md kernels (the incident-vs-prescription 3-step check, the enforcement
ladder + absence-compliance policy, and the lint-one-by-one rule) are binding;
this file carries the cases and the measured evidence behind them.

## Verifying the incident does not verify the prescription — cases

A rule can cite a real incident yet prescribe a mechanism that fails on exactly
the case it targets:

- `git cherry` for squash residue on a **multi-commit** branch — wrong on the
  multi-commit squash it targets, yet right on a single-commit branch (the
  boundary the step-2 variant-flip catches).
- "ack webhooks before durably recording them" — a plausible ordering that drops
  the record on a crash between ack and write.

4/27 rules in one reviewed batch carried this defect class, all past the author's
self-review — which is why step (3) sends a different model family (or a
same-model fresh-context critic) to attack the MECHANISM, not the prose.

## The enforcement ladder — A/B evidence

(fable-method, via upstream opus-pack 2026-07-16)

A rule shipped as mid-list prose showed no transfer on a weak executor; the same
rule as a decision-point artifact (a required report line — a named search, a
quoted authorization) transferred. BUT the artifact form did NOT transfer when
compliance meant noticing an ABSENCE (a follow-up deliberately skipped), plausibly
because an artifact attaches to an action in hand. Hence the policy: never rely on
an action-bound artifact alone for absence-sensitive compliance — use a machine
gate (Stop hook) or an out-of-band check. Corollary: a rigor rule can itself
induce costume rigor — the form of thoroughness with no search behind it.

## Lint a new rule against the file's own rules — cases

Two separate additions to the skill-authoring file each passed the author's
self-review while violating three of its own rules:

1. a label-phrased trigger, a paraphrased load-bearing clause, a non-executable
   test (§5 / §3 / §1);
2. a step with no completion condition, a failure mode stated stronger than the
   record showed, and a universal drawn from one incident (§1 / §2).

None was a contradiction *between* rules — an external lens caught each, which is
why self-review is no substitute for walking the file's rules one by one.

## Campaign-continuation check — full protocol

(distills a maintainer-gated upstream rule, folded 2026-07-24; kernel in §2)

Query BOTH open and merged-after-anchor on the SAME upstream repo and target
branch (`gh pr list --repo <upstream> --base <branch> --state open`, then
`--state merged --json number,mergedAt` sorted by mergedAt, not PR number — PR
numbers don't order by merge time). Paginate every query to exhaustion (gh's
default page size is 30 and silently truncates; a date bound doesn't lift the
cap — stop only when the last page is short). Classify each candidate by
CHANGED FILES, read mechanically and repo-scoped (`gh pr view <n> --repo
<upstream> --json files`, or `gh pr diff <n> --repo <upstream> --name-only` —
an unflagged view from a fork checkout reads the wrong PR since PR numbers are
repo-local) — never by title or body; a continuation PR's title can carry no
path token. File-listing has its own caps (gh's files query returns the first
100); verify the retrieved count equals `changedFiles`, and when completeness
can't be proven, treat that PR as touching (conservative). A rename touches
when EITHER path side matches a synced surface.

Repeat the open+merged pass until it adds no new touching-or-unclassified
candidate versus the prior pass (an open PR's files mutate with new commits —
track head OIDs to skip provably-unchanged ones; each pass's merged query
re-covers whatever the prior open query lost to a merge). Still unstable
after three passes → record the sync provisional, no further queries owed.
Any touching hit → don't close the sync as final: re-anchor to the newest
touching merged state, re-diff local files against it, re-run checks; a
still-open touching round → record the sync provisional with the fold owed.
Zero touching hits on a stable pass → the anchor is safe AS OF that check,
never forever — cite the checks (commands + date + totals), not a permanent
verdict.

## Re-baselining gate — cases

(distills a maintainer-gated upstream rule, folded 2026-07-24; kernel in §4)

A maintenance log carried a "still owes an extraction pass" line across
sessions for a file that had already extracted everything extractable —
every remaining line traced to a live trigger, including one added after the
old baseline was set. The gap was that new trigger's legitimate cost;
honoring the stale number would have meant gutting a live trigger or
carrying phantom debt indefinitely. The failure mode this guards against is
the inverse: declaring a new floor on self-judgment, with no word-diff
artifact and no per-line trigger check — a maintenance entry that says
"extraction complete" without evidence is exactly as unverifiable as one that
never updates. The gate (artifact → per-line check → only then re-baseline)
exists so a floor claim is falsifiable by a fresh reader, not asserted.

## Compression and restructuring passes — the two cuts that go wrong

Moved here VERBATIM from SKILL.md §5 step 2 on 2026-07-27 to make room for
§2's verify-capability-before-shipping rule. Move map: SKILL.md lines 306-329
at backup `~/.claude/backups/skill-authoring.SKILL.md.2026-07-27-*.bak` →
this section, disposition **verbatim, both bullets, no rewording** (these are
adapted from probe-tuned external text via PR #75, and §5's own move-map rule
forbids paraphrasing tuned prose while relocating it). SKILL.md §5 step 2
keeps a pointer. Trigger for opening this section: you are running a condense,
extraction, split, or re-home pass on a rules file.

- **A compression cut is a falsifiable bet, not just a word-count win.**
  The word-diff shows what TEXT disappeared; it can't prove retained or
  reworded text preserves the dropped words' behavioral force —
  argument/rebuttal prose can be load-bearing under exactly the pressure
  it rebuts (one external measurement found a compression that kept
  every rule but deleted its "why" and lost 3-in-10 pressure-case
  compliance). When a cut removes argument, rebuttal, or persuasion
  text, fold the rebuttal into the rule line where the excuse fires
  rather than deleting it, and where probe infra exists, probe the cut
  under pressure framing at the decision point the prose guarded — a
  cut that degrades the probe gets reworked, not shipped. ❌ "the rule
  survived, only the justification went" — the justification was the
  pressure armor.
- **Restructuring probe-tuned text needs a move map, not a rewrite.**
  When a doc whose sentences were probe- or eval-tuned gets split,
  merged, or re-homed, move tuned sentences VERBATIM and enumerate every
  rewording in a map: source line-range at a named revision → new
  location, per-row disposition (verbatim / reworded-with-both-versions-
  shown + probe status). Documenting a rewording doesn't validate it —
  a reworded tuned rule gets re-probed, or its marker downgrades to
  `unprobed` with the debt queued. Paraphrase drift on tuned prose is
  otherwise invisible to review: the reviewer sees fluent text, not the
  tuned sentence it silently replaced. ❌ "improved the wording while
  moving it" — an untested regression on a tuned sentence.

## Install-time citation retargets — probe evidence (kernel: SKILL.md §2)

Trigger for opening this section: you are folding, re-probing, or arguing
about §2's retargeted-citation rule.

2026-07-28 probe, two rounds. Fixture: skill `beta` cites a sibling `alpha` at
two section numbers — one correct in the destination library, one stale
(`§4` timeouts, but the destination's `§4` is Reporting and timeouts are `§2`).
The one-correct/one-wrong split separates *re-resolving* from *renumbering*:
an arm that rewrites both has cargo-culted.

Round 1 graded DETECTION and returned 4/4 pass — a non-result. Detection was
never the point; the rule exists to leave a correct library and a record.
Round 2 graded the artifact on two axes frozen in advance, and gave arms
standing authority to finish so "ask the user" was not an escape hatch:

| Axis | bare (N=3) | ruled (N=1) |
|---|---|---|
| library correct (`§4`→`§2`, `§1` untouched) | 3/3 pass | pass |
| retarget durably recorded | **0/3** | pass |

Every bare arm found and fixed the stale pointer unprompted — one volunteered
that section-number coupling is fragile and suggested named anchors. None
recorded the change anywhere but the chat. That reads as "the re-resolve half
is redundant with model capability", and a fresh-context reviewer had already
refused to let the kernel say so: phrasing it as a prediction ("you will
re-resolve without being told") bakes an N=3 observation into text addressed
to the weakest model that will ever load the file, and where the prediction is
false the clause would affirmatively REMOVE the instruction.

**Round 3 proved the prediction false.** Same fixture, same task, axis 1 only,
three bare arms at haiku (criteria and outcome-licensing registered before the
run; the pre-reg file itself was lost with the session scratch directory —
transcript and evidence status in `finding_probe_BC_2026-07-28.md`):

| Axis 1 — library correct | session tier | haiku |
|---|---|---|
| bare | 3/3 pass | **0/3** |

All three haiku arms copied the skill byte-for-byte with the stale `§4` intact;
two reported they had "verified the content transferred intact" — byte-fidelity
of the copy, the one check that cannot catch an already-wrong citation. **So
both halves of the kernel earn their line: the record clause at every tier, the
re-resolve imperative at the tier §0 actually writes for.** Do not trim it.

The transferable lesson is about the ledger, not this rule: a bare-arm verdict
inherits the TIER of the arm that produced it. "Redundant" measured on a strong
arm is a claim about strong readers, and §0 does not write for them. Record the
tier next to every verdict; re-probe at the weakest tier before any trim.

Two method notes from the same pass:

- **The "bare" arm was not bare.** A diagnostic confirmed every arm carried
  global `CLAUDE.md` R0-R8 and the MEMORY.md index despite an explicit
  disregard-recalled-rules instruction. Injected context is not neutralized by
  disregard framing. Every bare ✓ in this project therefore reads "redundant
  GIVEN R0-R8", never "redundant everywhere" — record the baseline next to the
  verdict.
- **A substring grader over prose needs a token the prose cannot contain.**
  The first axis-2 script keyed on `drift`, which appears in the fixture's own
  body text ("a batch that drifts model mid-run"), and returned pass for all
  four arms including the three that recorded nothing. Regraded on a port-note
  *heading* plus extra files. Same class as the term-grep miss in the
  2026-07-25 cache-staleness audit.

Companion result, candidate C (stage by explicit pathspec): killed as redundant
with global R3 across two scenarios, the second one forcing creation of a new
untracked file so `git add -A` was the path of least resistance. Bare still
staged narrowly. Revival condition is registered in `40-maintenance.md` §1
rather than here, so it fires if R3 is ever narrowed.

## Probe methodology — full tuned text (kernel in SKILL.md §4)

Moved here VERBATIM from SKILL.md §4 on 2026-08-12 (extraction pass; the
overdue order recorded in 40-maintenance §1). Move map: SKILL.md lines
314-375 at backup ~/.claude/backups/skill-authoring.SKILL.md.2026-08-12-0710.bak
→ this section, disposition **verbatim, both bullets, no rewording** (both
are probe-tuned: the fold rule via opus-pack #82 + the #90 re-sync, the
scenario rule via the #102-lineage fold gates). SKILL.md §4 keeps an
unprobed checklist kernel; THIS COPY WINS on any dispute between them.

- **Probe a candidate rule against the bare executor before folding it in.**
  Correct + non-duplicate is the bar for TRUTH, not for inclusion. Run the
  candidate's scenario twice as independent fresh invocations — once with no
  rule, once with it — and read the PAIR: both arms produce the intended
  outcome → non-discriminating, it costs a line and buys nothing (reference
  file or nowhere); only ruled → it earns its line; NEITHER → ineffective as
  written, rewrite or drop, never fold on truth alone; only bare → harmful,
  drop it. Score against the rule's INTENDED outcome (for a preventive rule
  that is the abstention — a bare arm that commits the act FAILS). An arm
  counts only if the SCENARIO presented the guarded situation; "the answer
  handled it badly" is a FAIL, not a not-armed exclusion — conflating those
  builds a change detector into the gate. Two traps, both hit in-house
  2026-07-27: a scenario that names the distinction the rule teaches inflates
  the bare arm (say `src/config/timeouts.ts`, never "the generated config");
  and a subagent bare arm is NOT bare — session memory reaches it, so frame
  BOTH arms away from recall (the candidate rule stays their only
  difference), say "disregard memory", and check the output for citations;
  that check bounds only QUOTED recall, so a surprising bare-pass from a
  memory-bearing arm stays suspect, not license. Run both arms at the tier
  the file is written for, and record that tier and what the baseline
  carried next to the verdict — a bare ✓ argues redundancy in that
  environment at that tier, never everywhere, and no bare-pass from an arm
  stronger than the audience licenses removing a line. n=1/arm screens large
  effects only. Measured: of 8 rules folded
  in one week, 3 reproduced with no rules file at all.
  ❌ "it's correct and not a duplicate, so it earns a line."
- **The probe scenario must not do the candidate rule's work.** A second
  controls failure, distinct from contamination: contamination is
  finding-content reaching an arm, while this is the shared task prompt
  instructing the behavior the candidate prescribes, so both arms reach the
  intended outcome from the prompt alone. A scenario can be perfectly
  generic and carry no phrasing from the finding — satisfying the rule
  above — and still hand over the method. The existing guards do not catch
  it either: the arm DID meet the rule's trigger, so the not-armed exclusion
  does not apply, and re-running a surprising call on the same scenario
  reproduces the same result. Nor does it announce itself as a broken
  probe; its symptom is a both-arms pass, which the bullet above reads as
  non-discriminating — demoting to a reference file, or dropping, a rule
  that was never actually tested. Before running, re-read the scenario and
  ask whether its text STATES OR DIRECTS the move the rule prescribes —
  names the operation, instructs it, or makes acceptance contingent on it.
  If so a run would measure the prompt, not the rule: discard the scenario,
  rewrite, and run (or re-run) both arms — a discarded round is not a
  verdict and licenses no fold, demotion, or drop. (Inferability is not the
  bar: a bare arm INFERRING the move unaided on a scenario whose text
  nowhere directs it is real non-discrimination, scored by the bullet
  above, never a reason to discard.) Name the situation and the task the
  executor is asked to perform, never the outcome the rule exists to
  produce — where a preventive rule's intended response is the abstention
  or refusal, a task written as "avoid X" has already handed it over. This
  strips the method from the SCENARIO, not from the world: whatever the
  executor's baseline already carries stays, and is recorded per the tier
  clause above. Record the check where baseline and tier are recorded —
  the probe record carries the scenario verbatim and the line "scenario
  names situation and task only; method absent", because a skipped re-read
  is otherwise invisible. Done when that line sits beside the verdict and
  the scenario text nowhere states, directs, or conditions acceptance on
  the move the rule prescribes.
  ❌ "the scenario only scopes the task — naming what counts as
  out-of-scope isn't handing over the method" — scoping that names the
  operation the rule prescribes IS the method; scope by naming the
  situation, not the move.
