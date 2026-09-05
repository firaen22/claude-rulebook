# compaction-hook-harness

Reliability harness and version history for the macOS Claude Code
PreCompact/SessionStart observability hook shipped as
[`../observe-compaction-events.sh`](../observe-compaction-events.sh) (== `candidate/v28.sh`
plus a header comment) and installed at `~/.claude/hooks/observe-compaction-events.sh`
(invoked as `/bin/bash --noprofile --norc -p <path> <matcher>` on bash 3.2.57).

Curated from the round-23 working tree (session scratchpad, 2026-09-01).
Working directories, per-run homes, and raw run outputs were excluded;
review stderr/stdout logs are kept as evidence.

Cross-model reviewed (codex luna/sol + grok, 2026-09-01/02): 57/57 contract
cases, gap 6/6, grpsig2 5/5 x2, pidhang discriminated; mutants M14/M16/M17
fail as intended. Full trail in `reviews/2026-09-01-cross-model-harness-review.md`.

## Contract (every path)
- C1 exit status 0 always
- C2 zero bytes on stdout
- C3 never block the caller; never leave a stuck/spinning child
- C4 never delete or replace a pre-existing file

A lost measurement event is cheap; a hang, stray stdout byte, nonzero exit,
clobbered file, or abandoned spinning process is expensive.

## Layout
- `harness/` — frozen, mutation-validated harness (harness-frozen3):
  `contract.py` (57 single-shot cases), `pidhang.py` (pid-directed SIGTERM
  during a hung interpreter self-test), `grpsig2.py` (group KILL / STOP-CONT
  with ready-handshake + double-sampled survivors; replaces the racy
  `grpsig.py`, kept for comparison), `gap.py` (launcher startup-window stop
  signals), `exectext.py`, `refcheck.py`.
- `candidate/` — hook versions v22 (previously live) … v28 (INSTALLED live
  2026-09-01, md5 4472d36b, verified identical to
  `~/.claude/hooks/observe-compaction-events.sh` at repo creation).
- `mutants/` — M1–M17 seeded-defect hooks used to mutation-validate the
  harness (all 10 original harness defects showed as false GREENS before fix;
  M16/M17 were added by the 2026-09-01/02 cross-model review, see `reviews/`).
- `scripts/` — runners (`run_full.sh`, `run_grpsig2.sh`, …), builders/patches,
  standalone repros (`repro_h1*.py`, `setsid_f2_repro.py`), v22→v27 diff.
- `dispatch/` — subordinate dispatch packets (sol/grok/agy/nim/opencode/luna).
- `review/` — per-reviewer packets, verdicts, and raw logs; `review/v27/TASK.md`
  is the fullest statement of contract, history, and known limits.

## Headline results (2026-09-01)
- v28: contract 57/57, pidhang 0 orphans, grpsig2 5/5 both cases, gap 6/6.
- Live v22 reproducibly FAILS grpsig2 I02 (orphaned spinning probe grandchild).
- v26 returned DO-NOT-APPLY (grandchild orphan Critical); v27/v28 fix it.
- Dual independent APPLY (sol + grok) before install.

## Known accepted limits (identical in v22, out of single-file scope)
setsid-detaching interpreter vs group-KILL (the HOOK cannot reach it; see the
ORPHAN DETECTION HOLE below for how far the harness's own detection actually
reaches); exit-37 probe is a skip-broken-file check, not
authentication; plain (non `-p`) invocation reads BASH_ENV; D-state self-test
holds SIGKILL until syscall return; C4 covers `$HOME`, planted canaries and the
cwd's top level — arbitrary absolute paths need OS-level fs isolation.

### ORPHAN DETECTION HOLE — open, unfixed (2026-09-05)
**Do not read a clean `orph=0` as "no orphans".** Out-of-group survivors are
attributed by matching the inherited `HOME=` in the `ps -axwwEo command=` output
(`contract.py` clause 3, `grpsig2.members()`, `pidhang.scan()` loop 2). macOS
does not emit environment text for platform binaries, so that clause is **inert**
for any descendant that is, or execs, a `/bin` binary — no environment scrubbing
by the hook is required. Measured 2026-09-05: `/bin/sleep` ps row is 18 chars
with no `HOME=`; a CommandLineTools `python3` row is 5018 chars with it. M17
is caught only because its grandchild stays a python process.

Reproduced end-to-end: v28 plus a double-fork + `setsid` + `execv("/bin/sleep")`
scored `contract 1/1 pass, 0 FAIL` with `orph=0` while leaving a live
`/bin/sleep 25` reparented to ppid 1; the reporting agent measured the full
runner green (contract 57/57, gap, grpsig2, pidhang all PASS, exit 0) with 21
live orphans left behind. All three instruments share the defect, so this is a
C3 hole, not a single-instrument bug.

Fix shape (not yet applied — a cross-cutting change to three instruments):
stop attributing by environment text. Take a pid set before `Popen` and again at
scan time, and treat as a survivor any pid absent from the pre-sample that is
still alive, non-zombie, and reparented to ppid 1, excluding the harness's own
children. Until that lands, add a mutant of this shape so the blind spot is red
rather than silent.

### Other open findings (2026-09-05, each verified by execution, none fixed)
- **`contract.py` A06_oversize cannot enforce WALL_CEIL.** The 300,008-byte
  payload is pushed with one blocking `p.stdin.write` *before* the deadline loop,
  against a 64KB pipe buffer. A candidate that stops draining stdin while alive
  blocks the grader until it exits on its own: measured 40.04s elapsed for a
  `sleep 40` mutant (ceiling is 12.0s, and `rc=0` proves the deadline branch never
  ran), and a never-exiting mutant left the grader still sleeping past a 45s outer
  timeout with no verdict. `run_all.sh` has no timeout of its own. Fix: feed stdin
  inside the deadline loop as `drip_stdin` already does, or off the main thread.
- **`contract.py` B07/B08 disable the descendant detector.** `B07_no_home` pops
  `HOME` and `B08_home_missing` sets it to `/nonexistent/nope`, so the `HOME=`
  clause has nothing to match — the harness hands the hook the blind spot for 2
  of 57 cases. Compounds with the orphan hole above. Fix: key detection on a
  dedicated env marker no case override touches.
- **`grpsig2` C2 is graded from point-samples of a shrinkable file.** stdout is a
  regular file the hook holds as fd 1, so `ftruncate(1,0)` before exit makes every
  sample read 0 and the grade comes back clean. Grading both samples (done) closes
  the settle-window case, not this one. Fix: give the hook a pipe for fd 1 and
  count drained bytes, or grade a high-water mark and treat any shrink as a
  violation in its own right.

The harness keeps its own bookkeeping (`TABLE-*`, `RESULT-*`, the `o_*.out`/`.err`
capture files) *inside* the directory it hands the hook, so those paths must be
excluded from the C4 snapshot — the harness rewrites them itself during the run.
Every exclusion is a blind spot: a hook that specifically targets one of those
names (deleting `TABLE-<label>.txt`, or truncating its own `o_*.out` after
writing to stdout) is not graded on it. The realistic classes are covered by
mutants (M1/M7/M12 stdout, M15/M16 cwd destruction, M17 detached grandchild);
closing the residue properly means moving harness output out of the hook's cwd,
which is a layout change across contract/gap/grpsig2/pidhang, not a patch.
Raised by codex 2026-09-05 (F4/F5/F6), accepted as a known limit, not fixed.

## Re-running
```
scripts/run_all.sh [candidate.sh] [label] [--pidhang]
```
prints one line per instrument (contract / gap / grpsig2, plus the slow pidhang
differential with `--pidhang`) and exits 1 on any failure; full logs land in
`$WORK` (default `$TMPDIR/hook-harness-<label>`). This is the token-lean entry
point for an LLM session: ~4 lines instead of ~80. `--pidhang` is a flag and is
accepted in any position; an unknown option, a missing candidate, or more than
two positional arguments is a usage error (exit 2) rather than a silent skip.

An instrument is graded PASS only if it exits 0 AND prints a recognised summary
AND that log contains no `FAIL`/`INCONCLUSIVE` line and no nonzero FAIL count.
Exiting 0 is not by itself evidence that an instrument ran, or passed.

`contract.py` itself prints only FAIL rows and a summary by default; the full
per-case table is always written to `TABLE-<label>.txt` in the workdir, and
`CONTRACT_VERBOSE=1` echoes it to stdout. A 4th positional argument filters
cases by substring (`python3 harness/contract.py candidate/v28.sh v28 /tmp/w D_pid`);
a filter matching no case is a usage error (exit 2), not a `0/0 pass` green.

The legacy `scripts/run_*.sh` / `gate*.sh` still reference the original
scratchpad layout (`harness-frozen3/`) and are kept as history, not runners.
`scripts/funct_test.sh` is NOT in that set — it is a live single-shot smoke check
(`funct_test.sh <hook> <tag>`, prints rc / stdout bytes / record file), nothing
invokes it automatically, and it is not a substitute for `contract.py`.
`pidhang.py` takes the candidate as `argv[1]` (default `candidate/v28.sh`) and
must run from the repo root: it opens `candidate/v26.sh` as its positive control,
which has to keep leaking for a clean result on the target to mean anything.
