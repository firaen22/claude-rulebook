# Task contract — GRILL PASS depth (kernel in SKILL.md §1)

Extracted 2026-07-17 from SKILL.md §1 during the size-control extraction. The
SKILL.md kernel (classify-the-ask, GOAL/ACCEPTANCE/OUT-OF-BOUNDS/ASSUMPTIONS,
and the GRILL PASS trigger) is binding; this file carries the rationale, the
edge rules, and the GOOD/BAD example (moved here 2026-07-21).

## GRILL PASS — GOOD/BAD

GOOD: "Before I spec this: (1) concurrent editors — how many? (2) offline edits
— queue or reject? (3) same-line conflict — last-write-wins ok?" BAD: "I'll
assume single-user and online-only" for a feature whose whole value is
collaboration — a plausible assumption stated confidently is how a wrong spec
gets locked.

## Why pointed questions beat stated ASSUMPTIONS

Stating your own ASSUMPTIONS is not a substitute for the GRILL PASS —
assumptions test what you imagined, questions surface what the user knows and
never said. The ACCEPTANCE blind-spot rule (unstated edges are the shared blind
spot of every model tier — spec them or lose them) is why this matters: the edge
you never thought to assume is exactly the one a question extracts.

## The "don't know" rule

An answer of "don't know" converts that question to a stated ASSUMPTION and work
proceeds — a GRILL PASS is not a blocker waiting on certainty, it is a
one-batch attempt to replace guesses with facts where the user has them.
