# Project-skill category templates

The canonical project-skill taxonomy (moved here from skill-authoring §3,
2026-07-16 size control) and how to write each category. Load it when
authoring or reviewing any project skill or a library's
entry/manifest/uncertainty files.

**Categories that earn a file**: debugging-playbook (symptom→triage from
real incidents), failure-archaeology (dead ends, reverts, why),
architecture-contract (invariants, load-bearing decisions),
extension-point / adapter contract (how to add a new plugin/provider/route
safely), parity-map / oracle-map (ported codebases where the shipped
artifact is the spec), config-and-flags, build-and-env (rebuild from zero +
pitfalls), run-and-operate, diagnostics-and-tooling, validation-and-qa
(evidence standards, thresholds).

## The universal rule (every category)

A category earns a file, and an entry earns its place, only with a **real incident
or an explicit recorded decision behind it**. Every entry states an **observable
trigger** (the state that means "you are about to touch this"), not a topic label.
An entry with no incident, no decision, and no observable trigger is a "be
careful" — cut it. The one exception: a preventive invariant for a well-understood
catastrophic mode (data corruption, money loss) may exist without a past incident
— say so in the entry ("preventive; not observed here") so a reader doesn't hunt
for a commit that isn't there.

## failure-archaeology (the strongest template)

Purpose: stop a future agent re-walking a dead end. "We tried that" only works if
you can say *why it died* and *what rule it left*.

Reconstruct it right: dead ends don't always appear as `revert` commits — where a
review pipeline catches failures pre-merge, the evidence lives in stalled/unmerged
branches, rejected-experiment reports, in-code rationales, and deferred-by-design
markers. Search whichever of git history, issues, PRs, comments, and branches the
repo actually has.

Entry shape (each field load-bearing):

- **Disposition tag** in the title — `dead` (tried, failed) / `rejected` (design
  considered and declined) / `recurring-trap` / `burned` (a fixture/secret/asset
  spoiled) / `mooted` (was real, made irrelevant by an environment change).
- **What was tried** — with the commit/PR/branch id, so it's checkable.
- **Why it died** — the *mechanism*, not "it didn't work". If a fix introduced a
  new bug, record the whole chain (A broke, fix B regressed C).
- **The standing rule it produced** — bolded, transferable.
- **Where the residue is now** — the branch, worktree, tmp dir, or closed PR the
  dead end left, tagged **"residue, not in-progress work"**. For a `burned`
  secret, record only its revocation status + an incident id — never the material.
- **The tripwire** — the observable proposal-keyword that should re-load this entry
  ("any 'a bridge page is faster' proposal"); enumerate tripwires in the skill's
  frontmatter description so it loads when someone reaches for a buried idea.

Two required sub-lists:

- **Deliberately-not-done** — things intentionally left unbuilt, each with the ❌
  rationalization a future agent will use to "helpfully" finish them.
- **Rejected options + the evidence that killed each** — distinguish "lost" from
  "never earned entry" (untested ≠ beaten).

Meta-rule: a check that looks redundant or paranoid is guilty-until-proven — it
often encodes a demonstrated attack or a paid-for lesson. Find the incident before
relaxing it; to loosen it, supply an equivalent guard (Chesterton's fence).

## debugging-playbook

Purpose: a zero-context agent matches on *what it literally sees* — a log line, an
exit code, an error string — not on subsystem names.

Entry shape:

- **Trigger = the observed symptom, keyed on a stable verbatim substring** (an
  exact log fragment / exit code / the user's own words) plus a normalized pattern
  for the dynamic parts (IDs, paths, timestamps vary — match the invariant
  substring, redact the sensitive bits). A wholly paraphrased trigger won't match.
- **Evidence first, always** — the first step captures evidence, never edits code.
- **Each triage branch terminates at a named observable** — a specific field or
  log line that explains the symptom — then decide. "Seems better" is not a
  terminated branch.
- **Fork known-limitation from regression** — split "expected/known limitation,
  tracked as X — do NOT fix" from "real regression".
- **Done** = the observable green, plus the real incident and the fix-version.
- **Recurrence signature** (optional, high-value) — what a re-occurrence would
  specifically implicate ("if this returns, X stopped going through path Y").

Structure: group by the project's own layers, bisect to the layer first, then
reproduce at the authoritative layer. One entry per *failure direction* of a guard
(fired-wrongly AND stayed-silent-wrongly are separate symptoms).

## architecture-contract

Purpose: capture the invariants whose violation "breaks users you cannot see".

- **Orientation line** — what this repo fundamentally is / what it protects.
- **Boundary map** — a small table (path | published/private | role) before the
  invariants.
- **Per-invariant block:**
  - **Trigger = the tempting change that violates it** ("any 'support external
    URLs' / 'this check looks redundant' thought").
  - **The invariant.**
  - **Executable done-check** — a *command*, not prose.
  - **Cited incident or ADR** proving the cost.
  - **"Don't simplify back to ___"** — name the naive implementation it forbids.
  - **✅ correct pattern / ❌ the rationalization** (quote a real one).
- **Known-doc-defects** — where docs and behavior conflict, state which is
  authoritative *for this project* (often code wins, but a published spec, pinned
  test, or owner decision can outrank buggy code — record the authority order).
- **Re-verify command** at the end.

Additive-compatibility default (not absolute): adding an optional flag/field is
*usually* safe for consumers that ignore unknowns — but can still break a strict
`additionalProperties:false` validator, a snapshot over serialized bytes, an
ordering assumption, or an exhaustive decoder; add it on both sides together.
Renaming/re-meaning/deleting is breaking unless an alias, shim, version
negotiation, or private-only surface covers it. Confirm against declared consumers.

## extension-point / adapter contract

Purpose: "how to add a new plugin / adapter / provider / route / model safely" is
a recurring high-value skill. Record the project's actual invariants — these are
the common ones:

1. **Verify the real external shape first** — a clue is a map, not a schema
   (operational-rigor §4): sample the actual field shape on a real instance and
   record it before writing the adapter.
2. **Change only the declared extension surface** — where consumers eat a
   normalized snapshot, adding an adapter leaves the normalized/UI/report layers
   diff-free; an explicit registration point (registry, factory, route table) is
   *expected* to change. Invariant: no provider-specific field escapes past the
   adapter boundary.
3. **Extend the canonical conformance suite** — don't copy a sibling's tests
   wholesale (drags in its old bugs).
4. **Honest-capability posture** — unknown → `—`, never a fabricated value.
5. **Structural privacy** — decode into a narrow type omitting fields you don't
   need, guarded by a sentinel test.
6. **Done** = conformance suite green + real-instance end-to-end + no
   provider-specific leak past the boundary.

## parity-map / oracle-map (ported or reverse-engineered codebases)

Purpose: when a codebase's spec is another artifact's *observed behavior* (a
port of a closed binary, a re-implementation matched to a shipped app, a
byte-parity migration), the most dangerous contributor is one who "fixes" the
code toward doctrine, docs, or the historically-correct answer. This file
stops that.

- **The prime rule, stated first: the shipped artifact is the spec.** Where the
  reference artifact and textbook/doctrine/docs disagree, parity wins — a "more
  correct" change is a regression here (a real epoch "correction" toward the
  historically-accurate constant was reverted for exactly this; the snapshot
  gate caught it). **The one carve-out:** never replicate a security, privacy,
  or legal defect for parity's sake — diverge there, and record the deliberate
  divergence in the map.
- **Subsystem → oracle → gate map** — per subsystem: its ground truth (the
  binary, a capture corpus, a lookup table) and which executable gate pins it.
- **The deliberately-NOT-pinned list** — subsystems with no oracle, named
  explicitly, so nobody hunts for an oracle that doesn't exist and no
  parity-free feature justifies touching a pinned engine.
- **Tables outrank formulas** — a lookup table captured from the artifact
  outranks an inferred formula until the formula reproduces the *entire* corpus
  exactly; keep the table as the gate even after the formula lands.
- **Tripwire** — any proposal containing "the correct value is", "per the
  standard", or "the original is wrong here" re-loads this file.

## Library packaging — the entry/manifest/uncertainty trio

Recommended packaging for a multi-skill library (not a mandate for every doc):

- **START-HERE / router** — orients by the engineering core, not the domain; a
  canonical-source map (what | source-of-truth | don't-touch caveat); a
  current-state triage of the dirty/red worktree so a fresh agent doesn't misread
  pre-existing breakage as its own; the top disciplines; a reading order. Keep it
  short — it's a router, not content.
- **MANIFEST** — one line per skill: what it is → what evidence backs it (exact
  PRs/files/incidents). A maintainer can re-verify each claim and knows what would
  falsify it. Prefer "read the directory" over a hand-kept list; pin any
  unavoidable list with a rule.
- **UNCERTAINTY register** — everything deliberately NOT settled, quarantined from
  the confident content, in labeled buckets (confirmed-contradiction-awaiting-owner
  / not-yours-to-decide / env-dependent-or-user-must-provide /
  will-go-stale-reverify / locally-unverifiable / do-not-commit-residue). **Every
  item ends in a safe default**, so a zero-context reader can act.
