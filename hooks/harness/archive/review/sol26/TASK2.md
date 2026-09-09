# TASK — reliability review of hook-v26.sh (candidate replacing the rejected v24)

## Context
v22-installed.sh is the LIVE Claude Code PreCompact/SessionStart observability hook,
invoked as `/bin/bash --noprofile --norc -p <path> <matcher>` on macOS bash 3.2.57.
Reliability contract on EVERY path: C1 exit 0 always; C2 zero stdout bytes; C3 never
block the calling process and never leave behind a stuck or CPU-spinning child
process; C4 never delete or replace a pre-existing file. A lost measurement event is
acceptable; a hang, stray stdout byte, nonzero exit, clobbered file, or abandoned
spinning process is not.

You reviewed v24 (the process-group approach) and returned DO-NOT-APPLY with four
findings: F1 group-directed termination from the caller no longer reached the worker;
F2 a session-detaching child evades group-directed cleanup; F3 the trap's cleanup
loop mis-parses under a nonstandard IFS in the plain (non--p) invocation; F4 the test
harness's process-group scan cannot see a worker that moved groups. v24 is withdrawn.
v26 uses a different mechanism intended to answer all four — please verify that
claim rigorously and independently.

## The v26 mechanism (diff in files/DIFF-v22-to-v26.txt — verify it yourself)
1. The interpreter self-test is no longer a blocking command substitution. Each
   candidate interpreter runs as a DIRECT background child of the worker with
   stdin/stdout/stderr pinned to /dev/null; the worker polls `builtin jobs -pr`
   (the same pattern as the outer watchdog) against a SHARED 1-second budget set
   before the candidate loop, and when the budget expires it terminates the
   self-test child BY PID. The success channel moved from stdout "1337" to exit
   code 37; `wait` runs only in the already-reaped branch, never after a
   termination, to avoid blocking on an uninterruptible child.
2. NO process-group membership changes anywhere (no `set -m`). Caller-directed
   group signals keep exactly the approved v22 delivery (answers F1); a
   session-detaching candidate is still reachable because cleanup targets the
   spawned pid (answers F2).
3. `IFS=$' \t\n'` is assigned immediately after the exec redirect, before any
   word-splitting expansion (answers F3).
4. The harness gained: (a) an orphan scan that also matches processes whose
   command line references the test stub, regardless of group; (b) grpsig.py with
   two new cases — group-directed KILL mid-self-test and group-directed STOP/CONT
   mid-self-test. Validated as a discriminator: v22 fails I02 (2 leftover
   processes), v24 fails I01+I02 (your F1, reproduced), v26 passes both (F4).

## Measured so far (verify what you can)
contract.py: v22 baseline 55/56 (H01 only), v26 56/56; gap.py 6/6; grpsig.py PASS;
`bash -n` clean under both -p and plain invocation.

## Your job — find any way v26 falls short of the contract. Default DO-NOT-APPLY
unless you find no defect. Areas needing scrutiny:
 a. The inner poll loop: `case` matching of $(jobs -pr) with newline guards — a
    child pid that is a substring of another; jobs -pr contents when a previous
    candidate's terminated-but-unreaped job lingers; SECONDS integer granularity
    at both ends of the budget.
 b. `wait "$_ppid"` reachability: any path where wait runs on a stuck child and
    delays the worker past the outer deadline.
 c. The exit-37 protocol: ENOEXEC fallback semantics on macOS bash 3.2 (empty
    file, binary garbage, shebang-less text); any real /usr/bin/python3 or CLT
    python3 behavior that returns 37 spuriously or fails to.
 d. The shared 1s budget vs the outer DEADLINE=2: worst-case timing overlap, and
    whether two slow candidates plus overhead can leave a self-test child alive
    when the outer deadline fires.
 e. A self-test child left with a pending termination while stuck in an
    uninterruptible syscall: which file descriptors can it still hold, and can
    any of them block the CALLER? (Trace fd provenance: the worker is spawned
    `<&3 3<&-`; the self-test child gets `</dev/null >/dev/null 2>/dev/null`.)
 f. The IFS assignment: placement relative to every unquoted expansion in the
    file; `$'...'` support and semantics on bash 3.2.57 under -p and plain.
 g. The documented limit: a terminating signal to the PARENT while a self-test
    child is stuck fires the top-of-file trap, the worker is cleaned up, and the
    stuck child is left for up to the 1s budget. Check the bound: can that
    leftover child persist LONGER, spin the CPU, or hold the caller's stdin?
 h. Regressions on the other 55 cases and the H02/H03/H04 fixture semantics (the
    "noisy" stub now needs `exit 37` — confirm the harness change is sound
    rather than a test adjusted to pass).
Also name any construct that is safe only because of this host's configuration,
environment, or invocation form — that is a finding, not a pass.

## Method requirements
- Execute rather than only read: copy files/*.sh anywhere writable and test them;
  if your sandbox denies something, say so and label those claims [unverified].
- Write expected-before-actual for every check.
- Findings: location (file:line) + mechanism + concrete fix, severity-ranked;
  every claim tagged [verified: how] / [unverified].
- Report inability honestly.
- End with exactly one line: `VERDICT: APPLY` or `VERDICT: DO-NOT-APPLY`.
