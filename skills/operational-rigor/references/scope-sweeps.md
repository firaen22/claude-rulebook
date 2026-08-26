# Scope sweeps — full rules (kernel in SKILL.md §3)

Extracted 2026-07-16 from SKILL.md §3 during the Phase A–D reverse-port
(size control). The SKILL.md kernel is binding; this file carries the full
mechanism and cases.

## Documented decisions are load-bearing

A documented decision is not a defect to fix. Before removing an
inconsistency or hardening a limitation, check whether it is a recorded
decision (ADR, changelog, inline rationale comment): if so, changing it
*reverses a decision* (the owner's call), and a re-proposal ("adding X is
easy now") is already-adjudicated, not new, information. Conversely, when
you write odd-looking-but-correct code, carry its rationale +
reproducing-test name inline, or a later agent "helpfully" reverts it.

## Interface changes: exhaustive call-site sweep FIRST

Changing a schema, enum, status value, or interface: grep every touchpoint
before editing, leave no site on the old shape, and report sibling sites of
the same bug — a partial sweep ships a half-migrated shape.

**Interfaces include observable output text and names** — error-message
strings, test-assertion copy, output filenames, upstream column names (even
a misspelled one), route/command names — each has hidden downstream
consumers, so changing one is an interface change to sweep, not cleanup to
tidy.

**Changing WHO performs an action** (a token, service account, bot
identity) is a behavior change with no code diff — after any
credential/identity swap, enumerate what keys off that identity (triggers,
permissions, rate-limit buckets) and verify each.

## "You created it" is a provenance claim (added 2026-08-04)

Removing state — your own cleanup at completion, a retry sweeping up a failed
prior attempt, a rollback — is licensed by attribution, and attribution has
two halves that must BOTH hold:

- **By record.** The task's own write log, or a run-scoped name/tag. Run-scoped
  means this authorized task across its turns and resumptions, not one
  wall-clock invocation — otherwise a resumed session cannot clean up its own
  earlier debris.
- **By current identity.** The recorded path must still hold the recorded
  content: hash it, plus the platform's object/generation identity where it has
  one. Byte-identical content re-created by the user is still the user's.

Where no generation identity exists, a content match alone cannot rule that
re-creation out. Deletion on record+content alone is licensed only inside a
namespace reserved to this run — your own scratch directory, a run-tagged path
no human edits. OUTSIDE such a namespace, content-only attribution is
non-probative: the state is retained and reported, not removed.

Never attribute by pattern-match on what LOOKS like automation output — a
matching-looking file may be the user's. State failing either check defaults to
human-owned and stays: reported, not removed.

## Fixed a defect? Presume twins until searched

Name the exact wrong construct, then search the whole project for the
defect CLASS — including the same operation written other ways, which a
single literal pattern misses (a probe's named search missed a
differently-written twin that a class-aware check caught in one command;
upstream opus-pack provenance, 2026-07-16). Report the search itself: the
pattern run and what it found (files, or "none"). Fix or explicitly list
every hit. A completeness claim without a named, re-runnable search behind
it is fabrication-shaped — and a reviewer accepting the claim re-runs the
named search, then challenges its coverage with one differently-shaped
query (broader/structural pattern, or a class-aware check): re-running a
narrow pattern reproduces its hits AND its misses.
