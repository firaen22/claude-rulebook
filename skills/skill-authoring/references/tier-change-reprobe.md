# Tier-change re-probe — the three-bucket triage

Kernel: `SKILL.md` §4, "The tier the file is written for has changed". Load
this when that bullet has fired and you are about to triage the file's rules.
A file whose audience tier moved while its verdicts did not can carry the
quirks of every executor it has instructed; this triage clears that.

## The three buckets

Before any verdict is cited again, put every rule in the file into exactly one:

- **(1) Context the executor cannot derive** — paths, live tool names,
  environment facts: keep, not probed.
- **(2) Workflow control** — "do it this way / in this order / check these N
  things", which a more capable executor may do unaided: the re-probe set.
- **(3) Load-bearing by content** — safety, verification, fail-closed,
  authorization-boundary, and any gate on destructive, spending, or publishing
  actions: keep, and never probed by letting a live executor cross one to see
  whether it would — that run IS the incident. A sandboxed probe of a
  bucket-(3) rule is the user's call, asked before the run (the whole class,
  not only the destructive / spending / publishing subset). Cannot tell
  whether a rule is load-bearing on one of these axes → treat it as
  load-bearing.

This partitions by necessity, not truth — §2's staleness rules for world facts
still apply to bucket (1) unchanged.

## The incident-backing fence

A rule is in bucket (3) by its CONTENT, and a rule in that class by content
**never leaves (3)**, incident or not. Only a rule whose SOLE claim to (3) is a
dated incident backing it — one that meets none of the load-bearing axes by
content — may move to (2), and only if that incident was the old executor's own
quirk rather than a standing hazard. Cannot tell whether the rule meets an axis
by content, or whether the incident was a quirk → it stays in (3); the triage
fails closed.

This closes the demotion path a weaker executor would otherwise open: a rule
that is BOTH fail-closed / verification by content AND incident-backed — e.g.
"ack the webhook before durably recording it," backed by a post-2xx-crash
incident — stays in (3) on its content and cannot be reclassified to (2) by
judging its incident "a quirk." Bucket (2) is the re-probe set and a bare pass
there makes a delete candidate; a content-load-bearing rule must reach neither.
❌ "the crash was just the old model's quirk, so this ack-before-record rule is
workflow control now — re-probe it" — it is fail-closed by content; the
incident is not its only claim to (3), so it never leaves (3).

## Re-probe bucket (2)

Re-probe by SKILL.md §4's bare-vs-ruled pair (method:
`distilling-rules.md` §Probe methodology), at the new audience tier (for a
multi-tier audience, the weakest tier it must protect), rules already carrying
a verdict first — they survived one measurement; find out whether they survive
this one — and read each pair by the same table. A bare pass makes a delete
candidate, never a deletion: deletion is its own edit, one rule per commit,
after the evidence is read, asking the user first.

## Bind the result, and Done

Bind the result where the next pass reads it — the file's change record
carries the line

> bucket triage at tier `<T>`, `<date>`; bucket-(3) rules probed live: `<each one named, or none>`

and a bucket-(2) rule with no verdict at the current tier is listed there as
queued.

Done when that line exists, every rule is bucketed, and every bucket-(2) rule
carries a current-tier verdict or a queue entry.
