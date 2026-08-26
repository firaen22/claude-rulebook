# Completion protocol — depth + examples (kernel in SKILL.md §5–6)

Extracted 2026-07-21 during the size-control extraction. The SKILL.md kernel
(the §5 checklist, DONE definition, decisions-note trigger, artifact-gate
re-derive) is binding; this file carries the examples and long-form clauses.

## §5 quality floor — GOOD/BAD

GOOD: after writing a guide that references `codex exec --skip-git-repo-check`, run
that exact command once to confirm the flag exists in the installed version. BAD:
declaring a 6-file documentation system complete because you remember writing all 6
files, without an `ls` — Write calls can be interrupted mid-session.

## DONE: the litter clause, in full

Own temp files and debug scaffolding removed or explicitly named: git status
clean of untracked litter outside the scratchpad — look at each file before
deleting, §2 gates apply to your own litter too; leftover debris reads as
abandoned work to the next agent and as a fraud signal to an auditor.

## Decisions-and-why note — GOOD/BAD

GOOD: "Decision: shim at the adapter, not an API change; rejected: breaking mobile
clients; why: latency cost measured acceptable" → written to memory/decisions.md,
path cited in the report. BAD: the choice explained only in the final chat message
— gone by the next session.

## Deferring measured work — the defer-record (added 2026-08-04)

One record, two forms. The decisions-note above stays the ≤5-line default.
Deferring work that was MEASURED, tuned, or adversarially reviewed escalates
that same record — same home (the repo's decision record, else project memory),
reported through the same "Decisions note: <path>" line — into a defer-record
carrying:

- the evidence gathered;
- each claim's review verdict;
- every rejected alternative WITH the measurement that killed it;
- what remains unproven;
- pre-registered revisit triggers.

The point is that the next attempt starts from the evidence instead of
re-deriving it — a "not now" on measured work throws away the measurement
unless the measurement is what gets written down.

**Companion gate: instrument before you tune.** Never ship a change whose
target metric is not yet observable. If that change is the one being deferred,
its defer-record states how the metric becomes observable first.

## Artifact gate — the no-papering clause, in full

For each missing owed line, first confirm the underlying work actually happened:
if it did, add the line; if it did not, do the work now or report the gap
honestly. Writing a line for work not performed is fabrication, and an outward
action with no grant to cite is reported as a finding, never papered over with a
constructed `AUTH:` line. The re-derive always runs; a clean report needs no
edits, so the gate costs nothing on ordinary tasks.

## No idle waits — the long form

The turn-level rule applied to latency: while a background job or subordinate
runs, do the next in-scope unit (dig the next suspect, write the next spec,
smoke-test on the partial output). Block synchronously (`Monitor`) only when no
in-scope work remains — waiting is the last resort.

## Completion report — GOOD/BAD

GOOD: "Done: 5/5 criteria pass. Ran `pytest tests/test_parse.py` (exit 0, 14
passed). Read back config.yaml — key present at line 12. Empty input → [] as specced.
Reviewer confirmed, one nit fixed. Skipped: perf criterion — no benchmark exists;
flagging instead of claiming." BAD: "Done — implemented the parser and it works."
