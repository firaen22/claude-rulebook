# The honest limit — autonomous floor (kernel in SKILL.md "The honest limit")

Extracted 2026-07-17 from SKILL.md during the size-control extraction. The
SKILL.md kernel (the three valid outputs when criteria are uncheckable, and the
"just proceed" trigger) is binding; this file carries the autonomous-floor
mechanism.

## The provably-safe subset (when the user answers "just proceed")

If the user answers a criteria proposal with only "just proceed", the autonomous
floor is the provably-safe subset:

- changes whose behavior-preservation you can PROVE — characterization tests you
  add first, or golden before/after outputs;
- plus deletions of code with zero callers, evidenced by a repo-wide usage scan,
  listed in the report.

Anything beyond that still needs agreed criteria — say so rather than expanding
the mandate to fill the silence.
