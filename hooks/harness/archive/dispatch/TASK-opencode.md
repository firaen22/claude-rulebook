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
