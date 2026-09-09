# TASK — name the unstated edges this test suite is missing

Read COMMON-CONTEXT.md first.

You are an adversarial edge-finder. Read harness/contract.py's case table and
hook.sh. Do not fix anything. Produce a list of INPUT / ENVIRONMENT / TIMING
conditions under which this hook runs in the real world that the 50-case table
does not exercise.

For each one give:
  - the condition, concretely enough to turn into a test case
  - which contract clause (C1/C2/C3/C4) it would threaten
  - why you believe the current cases do not already cover it

Rank by how likely the condition is to occur in normal use on a developer's Mac.
Aim for conditions that are REAL, not theoretical: this hook runs on macOS, on a
laptop, invoked by a CLI tool, many times a day, sometimes while the machine is
under memory pressure, sometimes during sleep/wake, sometimes with the user
hitting Ctrl-C.

Do not speculate about what the code does — quote the line you are reasoning
from. If you cannot find the line, say so.
