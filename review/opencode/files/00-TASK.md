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
# TASK — audit the harness's grading logic for silent passes

Read COMMON-CONTEXT.md first.

Read harness/contract.py and answer these specific questions. Quote the exact
lines you reason from; do not summarise the file.

 1. In `grade()`, four conditions are checked. For each, describe an ACTUAL
    runtime situation where the contract is violated but that condition is still
    satisfied.
 2. `run_case` computes `rc`. Enumerate every distinct value `rc` can take and
    say, for each, whether it is graded correctly. Pay attention to the branch
    where `os.waitpid` raises ChildProcessError — what does `rc` become there,
    and is that correct?
 3. `within_ceiling` is computed as `elapsed < WALL_CEIL - 0.5 and rc != "TIMEOUT"`.
    Under what circumstances is this True while the hook actually blocked?
 4. `diff_snapshots` reports only destruction, ignoring new files. Is there a
    destruction shape that presents as "a new file appeared" and is therefore
    missed?
 5. The EXPECTED table is written to disk before any run, then reloaded. Does the
    grading actually use the reloaded copy, or could it silently fall back to the
    in-memory constant? Trace it.

Answer each numbered question separately. If the answer is "no problem here",
say so and say what you checked. Do not invent findings.
