# Worked examples & measured incidents (kernels in SKILL.md)

Extracted 2026-07-21 from SKILL.md during the slim pass. Each section carries
the depth behind a SKILL.md kernel; the kernel bullet in the body is binding.

## Cost asymmetry — the measured F1-masking case

(kernel: SKILL.md "Cost asymmetry")

Measured: one over-match case left macro-F1 at 0.900 (passing the 0.90 threshold)
yet the gate correctly FAILED on the false route — an F1-only gate ships that
regression.

## Adapting a TypeScript project — shim recipe

(kernel: SKILL.md "Adapting to your project" step 1)

For a TS project, either add a 5-line `.mjs` shim that imports the compiled
function, or port the ~90-line runner into your test stack — the gate logic is
the value, not the file.

## Staging review queue — what to flag for a human glance

(kernel: SKILL.md "Building the case set" step 3)

Flag for human glance: residual names that survived the anonymizer, and
likely-bot lines (status emojis, ack openers) polluting a user-intent set.

## Baseline freezes *current*, not *correct*, behavior — the enshrined bug

(kernel: SKILL.md "Replay-gate discipline" first bullet)

One committed baseline enshrined a real redaction bug this way — the bug was
frozen as ground truth until noticed. Fix the transform first, then freeze.

## Parity variant — recipe

(kernel: SKILL.md "Replay-gate discipline" parity bullet)

Keep the pre-change implementation *callable* — `git show <base>:<path>` into a
`_old` module — and run old vs new over a declared input set, asserting identical
output/exit (allow-list intended diffs). Freezing the old source *text* as a
string is NOT a parity test — it never runs the old code.

## Grep-count ratchet — full shape

(kernel: SKILL.md "Replay-gate discipline" ratchet bullet)

When an anti-pattern can't be removed wholesale (inline locale ternaries, stray
global listeners), pin its current grep count as a dated baseline with the hits
enumerated; the executable done-check on every diff is "the count did not grow"
— and nobody "fixes" the enumerated baseline hits as a side quest either.

## What this catches that unit tests miss — scenario table

(kernel: SKILL.md section of the same name)

| Scenario | Unit test | This harness |
|---|---|---|
| Regex change over-matches a real user phrase | miss (synthetic only) | catches (real corpus) |
| Two patterns interact on real compound messages | miss | catches |
| Redaction edit changes what leaks in logs | miss | catches (replay diff) |
| False route hidden by good aggregate F1 | miss (F1 averages it away) | catches (hard gate) |

## Verify-by-reconstruction — full rule (kernel: SKILL.md "Replay-gate discipline")

Moved here VERBATIM from SKILL.md on 2026-08-14 (reverse-port size offset; move
map: SKILL.md bullet at backup
`~/.claude/backups/ground-truth-gates.SKILL.md.2026-08-14-1338.bak` → this
section, disposition verbatim, no rewording; the SKILL.md kernel is a
compressed pointer and this copy wins on dispute).

To prove "exactly X was applied" to a delivered state, reconstruct across the
boundary with an INDEPENDENT prescription of X — a pinned oracle, the
pre-change implementation (the parity variant), or the spec — never the
delivering system's own producer, whose bugs reproduce on re-run and
self-confirm. Two sound forms: full-state comparison
`apply_independent(baseline) == delivered` over a DECLARED projection — and
the projection must cover the complete mutation boundary, every field X
touches AND the fields expected to stay unchanged, with only the ambient
fields the system legitimately mutates on its own (ids, timestamps, server
defaults) on a declared allow-list, exactly as the parity variant allow-lists
intended diffs. A projection cut down to "what X touches" passes a delivery
that also mutated state outside it — the nearest over-application variant;
where the full boundary genuinely cannot be enumerated, the conclusion narrows
to "exact within this projection" and every out-of-projection surface is
reported unverified, never implied proven. (Raw whole-state equality with no
allow-list false-fails on every non-pure deliver, and a false-failing gate
gets weakened or dropped.) Or a true inversion `apply⁻¹(delivered) == baseline`
ONLY where the inverse is a proven bijection — a lossy "undo"
(reset-to-default) maps an under-applied state back to baseline too and passes
exactly the case the check exists to catch. Both forms prove STATE, not
history: repeated idempotent application and duplicate side effects that leave
identical state are invisible to them — where those matter, add an
operation/event witness (an application count, an audit log), or the claim
stays state-only, said so. No independent prescription available → the re-run
is a consistency check, labelled so — never a proof.

## Downstream-observable differential — full rule (kernel: SKILL.md "Replay-gate discipline")

Ported 2026-08-14 from upstream opus-pack (PR #177, landed via consolidated
PR #197, main `c2fc127`); upstream wording kept verbatim minus the Provenance
pointer (local convention). Ships `unprobed` — contributor incident as shape.

When direct state readback is unreliable or unavailable, verify through a
downstream observable that must move under a correct application and cannot
move otherwise. A control/treatment pair — run the system once without the
change and once with it, over identical input, and assert the treatment's
downstream signal differs from the control's in the direction the change
predicts, written down BEFORE either run (P1 > P0, not merely P1 ≠ P0) —
proves the application happened even where the state it touched cannot be
read back directly (an opaque UI setting, a third-party system with no
inspectable state). The same differential form pins protocol-level bugs: diff
your own request byte-for-byte against the target system's own observed
WORKING request for the same operation — a length or byte-offset difference
the diff surfaces is often the entire defect.
✅ "state readback was unavailable; ran the flow with the setting unset (P0)
and set (P1) over identical inputs, asserted P1 > P0 before either run —
passed, proving the setting reached the downstream calculation."
✅ "diffed my request body against the app's own captured working request
byte-for-byte; length differed by 5, decoding to exactly the two JSON quotes
and `Bearer ` my construction had dropped."
❌ a single successful run with no control, read as proof the change did
anything — nothing rules out the same output with the change absent.
