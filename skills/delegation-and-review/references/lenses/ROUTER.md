# Lens router — load only what the artifact can actually reach

Created 2026-08-29. Governs the lens files in this same directory.

**How to use.** Before writing a review dispatch packet, match the ARTIFACT against
the table below and paste the matched lens files verbatim into the packet — they
extend field 2 (ACCEPTANCE CRITERIA) of the dispatch packet spec in SKILL.md §3.
Load **at most 2** (~80 lines). Loading everything defeats the point: a lens exists
to make the packet SMALLER and the reviewer DIFFERENT, not to bolt a generic
checklist onto every dispatch.

**Run `bash check-lenses.sh` after editing any lens.** It enforces the 40-line cap,
prose density, and that the table and the files on disk name each other. The earlier
"≤30 lines" line here was an unmeasured number, violated by 5 of 6 files on the day
it was written — hence a gate instead of a rule.

**Match on what the artifact IS, not on what you suspect is wrong with it.** Router
rows are decidable by looking at the file; if a row needs you to already know the
defect, it is a bad row — fix the row.

| Load when the artifact … | Lens |
|---|---|
| has a shebang, hook registration, cron/workflow entry, or is otherwise EXECUTED by the harness rather than imported | `shell-and-hooks.md` |
| is itself a runnable guard, gate, test, assertion, or fixture with a PASS path (not prose that merely describes one) | `false-green.md` |
| claims to implement a spec, proposal, doc, or rule written elsewhere — caches, ports, extracted ledgers; NOT a hook whose comment cites the rule it enforces | `contract-drift.md` |
| is prose that instructs a future session (harness, SKILL.md, memory, CLAUDE.md, session recap or handoff) | `rules-text.md` |
| opens, creates, renames, removes, or appends to a path outside an invocation-local temp dir | `state-and-concurrency.md` |
| is itself a review, finding list, audit, or verdict produced by someone else | `packet-premise.md` |

**More than 2 rows match?** Drop in this order until 2 remain: (1) `contract-drift`
when the external spec is only cited in a comment rather than being the artifact's
reason for existing; (2) `state-and-concurrency` when the only shared path is an
append-only log. **Never** drop `false-green` from a gate, or `shell-and-hooks` from
a hook. Record the dropped matches in the packet — a silent drop makes every
dispatch a different, unstated experiment.

**No row matches?** Dispatch without a lens and say so in the packet. Do NOT stretch
a lens to fit — a mismatched lens sends the reviewer hunting the wrong failure class,
which is worse than no lens. A recurring no-match is the signal to write a new lens,
and a new lens needs a measured incident behind it, not a hunch.

## Assigning lenses across families (measured profiles, not public benchmarks)

Give different families DIFFERENT lenses on the same artifact — that is where
cross-family value comes from. Agreement between two reviewers running the SAME lens
is not corroboration (measured 2026-08-29: codex and grok independently ranked the
same FALSE claim their #1 CRITICAL).

| Family | Best-fitting lenses | Why (measured) |
|---|---|---|
| codex | `contract-drift`, `packet-premise` | finds MECHANISMS; spec-review-first framing works. INLINE the target; inline cliff ~30KB **measured on v0.149.0 only** — VERSION-BOUND, re-probe on upgrade (installed 2026-08-29: v0.150.1, cliff unmeasured) |
| grok | `state-and-concurrency`, `shell-and-hooks` | finds the CORPUS PATH that fires a mechanism. STAGE files in `--cwd`; never inline |
| agy | `false-green`, `rules-text` | adversary/edge-finder, high recall. INLINE; its `[verified:]` tags are NOT evidence; retry empties up to 3x |

Unstated edge cases are the shared blind spot of every family — no lens substitutes
for spelling the edge out in ACCEPTANCE.
