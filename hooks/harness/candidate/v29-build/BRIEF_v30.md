# Review packet — v30 probe-budget fix (compaction hook)

You are reviewing ONE change to a macOS PreCompact hook. You cannot see the repo;
everything you need is inlined below. Return a structured verdict (last line
`PROCEED` or `FIX <ids>`).

## What the hook is (context)
`observe-compaction-events.sh` (bash 3.2, `#!/bin/bash -p`) records one file per
compaction event under `$LOG_DIR/observed/`. Before spawning its python worker it
runs a **probe loop**: for each candidate python3 it forks a subshell that closes
inherited fds and `exit 37` iff python>=3.7, polls it with a builtin `jobs -pr`
loop ticking every `/bin/sleep 0.05`, and KILLS it if a shared budget expires. The
first candidate that exits 37 becomes the worker interpreter. If none passes, the
event is silently lost (contract prices this "cheap"). bash 3.2 has NO sub-second
clock builtin; `SECONDS` is whole-second.

## The bug being fixed (reproduced, not theorized)
The probe budget was `_pend=$(( SECONDS + 1 ))`. `SECONDS` increments on integer
wall-clock ticks, so `SECONDS+1` expires between (0,1]s after assignment depending
on sub-second phase — at a boundary phase it collapses toward 0 ms. When it does,
the watchdog kills the FIRST python probe before it can reach exit 37, no worker
spawns, and the event is lost with rc 0 and no file: the `D_pid_INT` VOID seen
once in ~400 live harness launches.

Evidence (all executed 2026-09-06):
- v29 breadcrumb instrument, 1500-launch soak: 1 hit at 16 ms showing
  `drop=NO_INTERPRETER secs=1 pend=1 ... rc137,killed=yes ... budget-spent-before-spawn`.
- Pure-builtin `SECONDS+1` spin at random phases: ~1.5% expired <20 ms.
- Positive control replicating the EXACT probe loop (kill-at-tick, 0.05 poll)
  around a 0.05 s "startup", 150 trials each:
  `+1 → KILLED(dropped)=5/150 (3.3%)`, `+2 → KILLED(dropped)=0/150`.

## The fix (the entire executable change)
`_pend=$(( SECONDS + 1 ))` → `_pend=$(( SECONDS + 2 ))`. Nothing else executable
changed (comments only). Budget is now (1,2]s: minimum >1 s regardless of phase,
so a ~30–100 ms python startup can never be clipped. Worst-case probe phase grows
~1s→~2s; C3 total hook bound ~3s→~4s (well under the 10 s ceiling). Same whole-
second source, same kill-at-tick mechanism — only the WIDTH changed.

Rejected alternatives (state if you disagree): a poll-iteration counter (a
fast-returning `/bin/sleep`, e.g. signal-interrupted, would burn ticks with no
wall-clock and re-introduce the clip); a new sub-second clock (bash 3.2 has none;
forking `date`/`perl` per tick adds the fork surface the loop spent rounds 9–27
removing). The worker watchdog is a SEPARATE `SECONDS + DEADLINE` (DEADLINE=2),
floor already >1 s, never implicated in a VOID — left UNCHANGED on scope.

## Full diff (v28 → v30)
<<<DIFF>>>

## Verification already run (reproduce/challenge as you see fit)
- `bash -n candidate/v30.sh` → OK. Non-comment diff vs v28 = the single line above.
- run_all.sh v30 --pidhang: contract **57/57**, gap PASS, grpsig2 5/5+5/5,
  pidhang **DISCRIMINATED** (v26 control leaks 10/10, v30 clean 10/10).
- Positive control above.
- soak_launch.py v30, 1500 launches: <<<SOAK>>>

## Rubric — answer each
1. Does `+2` actually eliminate the boundary collapse, or is there a phase/edge
   where the budget still floors below a python startup? Show the arithmetic.
2. Does widening the probe budget to (1,2]s break any C-bound or watchdog
   invariant (total hook lifetime, worker watchdog independence, the abandoned-
   orphan bound)? The loop body is unchanged — is that safe with the wider budget?
3. Is leaving the worker watchdog (DEADLINE=2) unchanged correct, or does the same
   class of boundary bug live there too and warrant inclusion in THIS fix?
4. Any regression the one-token change introduces that the green suites above
   would NOT catch?
5. Cost asymmetry: a budget too SHORT drops events silently (the bug); a budget
   too LONG only delays a rare wedged-probe host by up to ~1 extra second. Probe
   the short/silent side hardest.

Report each finding as: location + mechanism + concrete fix, severity-ranked.
Tag claims [verified: how] / [reasoned]. Last line: `PROCEED` or `FIX <ids>`.
