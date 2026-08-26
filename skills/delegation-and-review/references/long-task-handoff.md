# Long-task handoff — full detail (kernels in SKILL.md §6)

Extracted 2026-07-21 (size control). Kernels in SKILL.md §6 are binding; this
file carries the full text.

## Handoff notes and final summaries — reader guidance

Handoff notes and final summaries are written for a reader who watched none of
the work: outcome first, every mid-task codename/shorthand expanded, and
shorten by dropping low-impact items — never by compressing sentences into
fragments.

## Background agent + fallback wakeup — full pattern

After launching a background Agent whose result gates an approved action, also
`ScheduleWakeup` with the FULL contingent plan in the prompt ("if verdict=SHIP
do X as approved, else report") — so a missed notification doesn't drop the
work; a wakeup firing after completion validates ground truth FIRST and
no-ops (never re-execute a stale prompt). Block synchronously on a fan-out
with `Monitor`, not polling.

## Spawned-session harvest — details

Spawned sessions can't be transcript-harvested headless: have them WRITE a
findings file to a known path (e.g. `~/.claude/findings/<task>.json`), or
harvest by ground truth (files/git). Their prompt must be self-contained,
with an explicit confirm-before-live gate for anything outward-facing.

## Handoff compression — the three full rules (kernel: SKILL.md §6)

Moved here VERBATIM from SKILL.md §6 on 2026-08-14 (reverse-port size offset;
move map: three bullets at backup
`~/.claude/backups/delegation-and-review.SKILL.md.2026-08-14-1338.bak` → this
section, disposition verbatim, no rewording; the SKILL.md kernel is a
compressed pointer and this copy wins on dispute).

- **Compress a handoff by re-derivability, not by success/failure.** What the
  next reader can re-derive alone — file contents still on disk, listings a
  command re-produces — compresses hardest, and compressed never means erased:
  at minimum a one-line pointer survives. What exists only in this run's
  history — error output, external responses, one-shot logs — is what a
  reader can least afford to lose, whether or not the step succeeded (secrets
  inside it still fall under the removed-for-cause label below). The
  handoff-note rules in SKILL.md §6 decide what is worth SAYING; this one
  decides what is safe to LOSE — a low-impact line may leave the summary, but its
  class stays recoverable. Thin summaries do not fail gracefully: an
  under-informative handoff sends the reader hunting — many probes to recover
  what one retained line would have said — so over-trimming costs more
  downstream than the lines it saved, paid by a reader with less context than
  you have now.
- **Collapsing repetition may reduce volume, never variety.** Merge repeated
  failed attempts into one line only when they are CONSECUTIVE repeats of the
  SAME operation failing the SAME way — same operation and target AND same
  error: identical error text on different operations is coincidence, not
  repetition; distinct errors under one repeated command never merge; and an
  intervening success, a different operation, or any event rendered in the
  SOURCE record between attempts breaks the group (consecutiveness is judged
  on the record being compressed, never on the compressor's own output) — two
  matching failures either side of a success are two stories, not one.
  Distinct failures each keep their own line; the merged line carries the
  count and a reference to the final attempt (the end state the retries
  landed on); and when in doubt, keep the lines separate.
- **Every elision is labelled; a recoverable one names its retrieval, a
  deliberate removal names its reason.** An omission marker names what was
  dropped, of what kind, and how much, and includes a retrieval step you have
  run once as printed. Two labelled exceptions: content removed for cause (a
  secret, personal data, material a retention policy deletes) gets
  `redacted — <reason>` and no retrieval step — recoverability serves lossy
  compression, it never undoes deliberate removal — and content whose source
  is already gone (an expired transcript, a one-shot response) gets
  `not retrievable — <why>`, never a step you cannot stand behind. Spot-check
  your own cut before shipping it — a sample can reveal category-level loss,
  never rule it out, so treat any load-bearing hit as reason to re-cut, and
  never present the sample as proof of losslessness.
