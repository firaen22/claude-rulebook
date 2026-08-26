# Extracted examples, cases, and templates (kernels in SKILL.md)

Extracted 2026-07-21 during the size-control slim of SKILL.md. The SKILL.md
rules these support are binding; this file carries the moved GOOD/BAD example
pairs, incident narrations, boundary examples, and copyable templates. Each
header names the SKILL.md section it belongs to.

## §1 — Eligibility gates precede the first artifact-producing step

Incident (source-measured): a weak-tier executor blew past a mid-procedure
scope check and escaped its sandbox; the identical check moved before
generation produced a correct early exit.

❌ "Stage 4: before finalizing, confirm the change was needed at all" — by
Stage 4 the artifact exists and the check reads as waste.
✅ the same sentence as Stage 1's first bullet.

## §1 — What makes the strongest BAD example

The strongest BAD example quotes a rationalization actually observed ("tests
are probably fine — the change is small") and names why it fails.

## §1 — Rule-format GOOD/BAD pair (retry cap)

GOOD: "Hard cap: 2 retry rounds of the same approach at the same tier. Third
attempt must change tier, decomposition, or approach."
BAD: "Avoid excessive retries; know when to try a different strategy." (No
trigger, no threshold, no verdict — a weak model retries forever.)

## §2 — Variant-flip examples (incident-vs-prescription check, step 1)

Flip one property of the motivating scenario: multi-commit → single-commit,
crash → no-crash, concurrent → one worker.

## §2 — Gap-test GOOD/BAD pair

GOOD: a fresh consumer-tier agent given only the rubrics file plus a
"reviewer contradicts itself" scenario fails to reject the review → add the
self-contradicting-reviewer rule (a measured gap).
BAD: adding "watch out for race conditions" to a playbook because it sounds
prudent — no probe ever surfaced that gap; it's line-weight, not a rule.

## §2 — Capability-negative rot incident

One playbook's "no flag for model switching; interactive only" was actively
wrong at the tool's current version (a flag existed) and had been routing
sessions into a degraded, more expensive path for weeks — nothing ever
re-exercised the claim to expose the drift, since a negative gives no
occasion to retest itself.

## §2 — Recorded-environment-remedy — full upstream text

Ported 2026-08-14 from upstream opus-pack (PR #176, landed via consolidated
PR #196, main `c2fc127`); kept verbatim minus the Provenance pointer (local
convention), the SKILL.md §2 bullet is a lightly compressed kernel and this
copy wins on dispute. Ships `unprobed` — contributor incident as shape (a
service restart recorded in memory as "the fix" cleared once, was reused
across several later sessions, then directly falsified).

A recorded environment remedy is a hypothesis on reuse, not a fact — verify
it fired this time, and retract it in place when it doesn't. A fix for an
environment quirk (a process restart, a service bounce, a config toggle)
gets written to memory once it worked, then reused across sessions on the
strength of that one success — but the underlying cause can be a different
bug next time the same symptom appears, or the environment can have moved
out from under the remedy entirely. Applying a recorded remedy without
confirming the symptom actually cleared repeats the capability-negative
failure in the opposite direction: a false negative fails silent, a false
remedy fails LOUD the first time someone trusts it and it doesn't work — but
only if the session checks; skipped, it just re-applies the broken fix next
time too. Before writing "X fixes Y" into a durable file: confirm Y actually
cleared, not merely that X ran without erroring. Before reapplying a
recorded remedy: confirm it fixed THIS occurrence before moving on, and when
it doesn't, correct the rule in place rather than leaving the disproven fix
for the next reader.
❌ "restart the service — that's the documented fix" written once, applied
unverified in three later sessions, until a session that checked found the
symptom persisted and the note was stale.

## §3 — "A cross-reference is not a load" — A/B evidence

External A/B evidence (fable-method, via upstream opus-pack 2026-07-16):
in-skill pointers went essentially unpicked-up by a weak executor across
rewordings.

## §3 — Supersede-explicitly GOOD/BAD pair

GOOD: "big-pickle reclaimed as default (supersedes the 0/20 finding — that
result was task-complexity-bound, re-verified)" — one current truth, the
history explains itself in place.
BAD: appending "NOTE: actually big-pickle works now" below an untouched
"0/20 — never use" line — the next session obeys whichever sentence it reads
first.

## §3 — Flip-default verdict-sweep GOOD/BAD pair

Moved here from SKILL.md §3 on 2026-08-14 (reverse-port size offset; the
SKILL.md bullet keeps the rule, this section carries the examples and the
alias-grep why — move map at backup
`~/.claude/backups/skill-authoring.SKILL.md.2026-08-14-1338.bak`).

Why alias-grep: an empty grep isn't a clean sweep — a stale verdict can
phrase the incumbent without the exact term.
✅ "grepped the old model's name, found two 'KEEP AS DEFAULT' blocks,
rewrote both verdict lines in place as SUPERSEDED."
❌ "updated the top summary; the old write-up below is just history" (a
weaker executor reads that far).

## §3 — Red-line boundary examples

Not red-line: general work that merely touches money or health (a budgeting
spreadsheet, fitness logging) is not red-line; the line is substituting for
the professional's individualized call. Adjacent-to-red-line examples:
tooling FOR practitioners, compliance research.

## §4 — LESSONS.md entry template (copy verbatim)

```
## YYYY-MM-DD — <one-line title>
- What happened: <2–3 lines, concrete — commands, files, error text>
- Root cause: <one sentence with a MECHANISM, not "it failed">
- Rule change needed: NONE | <proposed edit + which file>
- Status: noted | user-approved | applied-on <date>
```

## §5 — Condense-pass structural checks (why they are not enough)

Structural checks (grepping that anchors, pointers, headers, and examples
survived) verify structure, not clauses.
