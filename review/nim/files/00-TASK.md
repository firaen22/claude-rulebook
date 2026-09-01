# What is under review

`hook.sh` is a Claude Code PreCompact/SessionStart hook. It is measurement-only:
it records that a compaction happened. It runs on every compaction and every
session start, invoked as:

    /bin/bash --noprofile --norc -p <path> <matcher>

It must satisfy a HARD CONTRACT on EVERY code path:
  C1  exit status is always 0
  C2  zero bytes written to stdout
  C3  never blocks indefinitely
  C4  never deletes or replaces any pre-existing file

COST ASYMMETRY — this decides where to spend your effort:
  A LOST measurement event is CHEAP. Nobody is harmed.
  A false PASS is EXPENSIVE: a hang wedges the user's session, a nonzero exit or
  a stray stdout byte corrupts the host tool's hook protocol, and a destroyed
  file is unrecoverable.
  Therefore: hunt for ways the harness could report PASS while the contract is
  actually violated. A finding that the harness is too STRICT is nearly
  worthless. A finding that it is too LENIENT is the whole point.

# The harness under review

  harness/contract.py  — 50-case contract suite. For each case it freezes
                         EXPECTED to disk BEFORE running anything, then runs the
                         hook under an isolated HOME containing canary files, and
                         grades rc / stdout bytes / elapsed / canary destruction.
  harness/gap.py       — widens the microsecond window between the early exit-0
                         trap and the `trap '' TSTP TTIN TTOU` line using a pure
                         shell-builtin busy-wait, then delivers stop signals into
                         that window. Uses a NON-ORPHANED process group on
                         purpose: in an orphaned group the kernel discards stop
                         signals and every variant would falsely pass.
  harness/mutants.py   — generates mutants that each break exactly one clause.
  harness/exectext.py  — proves an edit is comment-only by comparing the
                         executable text (non-blank, non-comment lines + shebang).
  harness/refcheck.py  — flags `line NNN` comment references that no longer point
                         at an executable line.

# One harness bug already found and fixed (do not re-report it)

The first version delivered signals 0.35s after spawn, but the hook exits in
0.12s. Every signal case was therefore a no-op and a mutant with ALL TRAPS
REMOVED passed. Fixed by holding stdin open so the target is alive at delivery,
and by recording a liveness probe immediately before delivery — a signal case
where the target was already dead now grades VOID, never PASS.
# TASK — independently re-derive the mutant matrix

Read COMMON-CONTEXT.md first.

harness/mutants.py generates 7 mutants of hook.sh. Each is DECLARED to break
exactly one contract clause. Your job is to check that declaration independently,
by reading the generated files in mutants/ — not by trusting the generator's
comments.

For each of M1..M7:
 1. Read the mutant .sh and diff it mentally against hook.sh.
 2. State which contract clause you believe it actually breaks, and on WHICH
    code paths. Some mutants break a clause only on some paths — for example a
    mutated final `exit` is never reached on a path that exits through a signal
    trap instead.
 3. State whether the declared clause matches your derivation. If a mutant does
    NOT break its declared clause, that is a defect in the harness's evidence and
    is the most valuable thing you can report.
 4. Say whether the mutant is a good test of the clause, or whether it could pass
    for the wrong reason.

Also answer: is there a contract clause for which NO mutant provides a real test?
If so, describe the mutant that should exist.

Report as a table: mutant | declared | your derivation | agrees? | notes.
Tag every claim [verified: how] or [unverified].
