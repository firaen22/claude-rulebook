# TASK — find FALSE-GREEN paths in this contract harness

You are reviewing a verification harness, not application code. Your job is to
find cases where the harness reports PASS while the hook actually violates the
contract. Read COMMON-CONTEXT.md first for the contract and the cost asymmetry.

Method — follow it, do not skip steps:
 1. For each of the 4 contract clauses, write down BEFORE you look at the code:
    "what would a violation of this clause look like at runtime, and what signal
    would reach the harness?" Then read contract.py and check whether that signal
    is actually captured and graded.
 2. Specifically interrogate these, each of which is a known false-green shape:
    a. Is stdout captured on the RIGHT file descriptor, in every spawn shape?
       Could the hook write to fd 1 in a way the harness never sees (a re-opened
       controlling terminal, /dev/tty, an inherited fd, a fork that outlives the
       measured process)?
    b. Does the elapsed-time measurement actually bound the hook, or only the
       parent? If the hook forks a child that lives on holding fd 1 open, does
       the harness notice?
    c. Does the canary snapshot detect every destruction shape — unlink, rename
       over, truncate-in-place, symlink repoint, permission strip, directory
       replaced by a file? Which of those would slip through the comparison in
       diff_snapshots?
    d. Can a case's `rc` be graded 0 when the process was actually killed or
       stopped? Look hard at the waitpid loop and at what happens when the
       process exits between two poll iterations.
    e. Are the isolated HOMEs really isolated? Could a case write to the real
       $HOME or to a shared path and have the harness still call it clean?
 3. Then RUN it. Write a mutant of your own that violates a clause in a way the
    existing mutants M1-M7 do not, run the harness against it, and report whether
    the harness caught it. A mutant the harness misses is your strongest finding.

Report each finding as: file:line + mechanism (why the harness is blind to it) +
concrete fix. Rank by severity. Tag every claim [verified: how] or [unverified].
If you find nothing, say so and show what you ran — "no findings" without
evidence of work is not an acceptable result.

End with exactly one line:
VERDICT: HARNESS-SOUND
or
VERDICT: HARNESS-LEAKY
