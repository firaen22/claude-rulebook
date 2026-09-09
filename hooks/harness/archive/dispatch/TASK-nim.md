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
