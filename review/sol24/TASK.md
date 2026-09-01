# TASK — adversarial review of hook-v24.sh (a 4-executable-line fix to the approved v22)

## Context
v22-installed.sh is LIVE as a Claude Code PreCompact/SessionStart hook, invoked as
`/bin/bash --noprofile --norc -p <path> <matcher>` on macOS bash 3.2.57. It carries a
three-way APPLY (you approved v22). Contract, non-negotiable on EVERY path:
  C1 exit 0 always; C2 zero bytes to stdout; C3 never block the caller and never
  leave anything behind that blocks or burns the host; C4 never delete/replace a
  pre-existing file. A lost measurement event is CHEAP. A hang, stray stdout byte,
  nonzero exit, destroyed file, or abandoned 100%-CPU process is EXPENSIVE.

## The defect v24 fixes (reproduced, live on this host)
The deadline `kill -KILL "$wid"` is PID-directed. When an interpreter candidate's
probe never returns, $wid (the worker subshell) dies but its command-substitution
child and the hung interpreter survive, reparent to init, spin at 100% CPU forever,
and hold the `<&3` dup of the caller's stdin. Reproduced: 6 prior harness runs left
6 such processes on this machine. Contract case H01_interp_hangs: v22 FAILS
(orphans=2), v24 PASSES (orphans=0), all 56/56, stop-signal instrument 6/6.

## The change (diff v22 -> v24, executable lines only — verify this claim yourself)
1. `builtin set -m` immediately before the worker spawn; `builtin set +m`
   immediately after `wid=$!`. Purpose: worker becomes leader of its own pgid.
2. Deadline branch: `builtin kill -KILL -- "-$wid"` added BEFORE the existing
   pid-directed kill (which is kept as the floor).
3. The ERR/signal trap's job sweep rewritten from
   `kill -KILL $(jobs -pr)` to a for-loop doing group-then-pid kill per job,
   pure builtins.

## Pre-authoring probes already run on this host (bash 3.2.57 arm64, non-interactive)
P1 set -m => bg subshell pgid == its pid (own group). P2 after set +m, a SIGSTOP'd
worker STAYS in `jobs -pr` (so the watchdog still reaches its deadline; no wait-hang).
P3 `kill -KILL -- -$wid` swept a stopped leader + descendants, 0 survivors.
P4 `set -m; set +m` in a script emits 0 stderr bytes.

## Your job — try to REFUTE the fix. Default to DO-NOT-APPLY unless you cannot break it.
Hunt specifically:
 a. Any path where `set -m` changes behavior BEYOND pgid assignment: job-completion
    notifications reaching stdout/stderr in the window before/after `exec >/dev/null`
    (note the exec redirect runs at line ~176, long before the spawn); SIGCHLD/trap
    interactions; `wait` semantics in the gone-branch on a STOPPED job; terminal
    signal delivery differences given the hook may have no controlling tty OR may
    inherit one from Claude.
 b. The window between `set -m` and `set +m`: if a signal lands there, the trap
    runs with job control ON — any hazard?
 c. The new trap body: for-loop word-splitting of $(jobs -pr) under a hostile IFS
    inherited from the caller? (Check what the file does about IFS.) Quoting, `--`
    placement, a job pid that is gone by kill time, recursion via ERR inside a trap.
 d. Group-directed signals FROM the caller (killpg at the hook's group) now no
    longer reach the worker directly (different group). Trace whether any contract
    clause depends on the worker receiving group signals firsthand.
 e. The kept pid-kill floor: any way the group kill SUCCEEDS but leaves survivors
    the pid kill also misses?
 f. `builtin set -m` under `-p` and under plain `bash <path>` (no -p): exported
    function named `set`? (builtin-forced — but verify the prefix is actually there.)
 g. Anything in the 4-clause contract the edit regresses on the OTHER 55 cases.
Name the config-dependent safety class explicitly: a construct safe only because of
this host's config/env/invocation is a finding, not a pass.

## Method requirements
- Execute, do not just read: run hook probes yourself (you may copy files/*.sh
  anywhere writable; if your sandbox denies writes, say so and fall back to
  source-trace clearly labelled [unverified]).
- expected-before-actual on every probe.
- Report each finding: location (file:line) + mechanism + concrete fix, severity-ranked,
  each claim tagged [verified: how] / [unverified].
- Report failure honestly; an inability to run is a report, not a guess.
- End with exactly one line: `VERDICT: APPLY` or `VERDICT: DO-NOT-APPLY`.
