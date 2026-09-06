# compaction-hook-harness

Reliability harness and version history for the macOS Claude Code
PreCompact/SessionStart observability hook shipped as
[`../observe-compaction-events.sh`](../observe-compaction-events.sh) (== `candidate/v28.sh`
plus a header comment) and installed at `~/.claude/hooks/observe-compaction-events.sh`
(invoked as `/bin/bash --noprofile --norc -p <path> <matcher>` on bash 3.2.57).

Curated from the round-23 working tree (session scratchpad, 2026-09-01).
Working directories, per-run homes, and raw run outputs were excluded;
review stderr/stdout logs are kept as evidence.

Cross-model reviewed across three dates, four rounds — codex (luna/sol) and grok
throughout, plus gemini 3.6 on the first 2026-09-06 round. Current results,
re-run 2026-09-06: 57/57 contract cases, gap 6/6, grpsig2 5/5 x2, pidhang
discriminated, `run_all --pidhang` rc 0.
- 2026-09-06 (later, installed hook `51bf9e4`, code = v28): three `run_all` passes.
  Two were 57/57; one graded `D_pid_INT` FAIL `VOID signal never landed (alive=None)`:
  the hook exited 0 at 0.026s with NO observed file, before the 0.35s signal —
  i.e. it took a pre-worker exit-0 path (line 604 OBS_CODE check, line 752 no
  interpreter, or a trap). 1 in ~400 hook launches that day; 30 isolated
  `D_pid_INT` repeats + 60 boundary-timed launches did not reproduce it. The
  "whole-second `SECONDS` budget collapses near a wall-clock boundary" theory
  was TESTED and REJECTED (bash 3.2 here does not tick at the boundary; 0/45
  primitive probes expired). Mechanism UNIDENTIFIED — the hook's exit-0 paths are
  silent by design, so the harness cannot tell a hook-side drop from a VOID.
  A single `D_pid_*` VOID in an otherwise-green run is a re-run, not a regression;
  a repeat in the same run, or any case other than a `sig_*` kind, is a finding.
- 2026-09-01/02 — the review this tree was curated from; mutants M14/M16/M17
  fail as intended. Trail: `reviews/2026-09-01-cross-model-harness-review.md`.
- 2026-09-05 — the `HOME=` orphan clause does not reach platform binaries;
  fixed by cwd attribution, then re-reviewed (M18).
  Trail: `reviews/2026-09-05-orphan-detection-cwd.md`.
- 2026-09-06 — the last two documented holes closed: A06 could not enforce
  `WALL_CEIL`, and C2 was graded from a file the hook could `ftruncate`
  (M19–M22). Trail: `reviews/2026-09-06-stdout-tap-stdin-pump.md`.

**Read the dated sections, not this summary, before trusting any single number** —
each round restates what its predecessor got wrong.

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
- `mutants/` — M1–M22 seeded-defect hooks used to mutation-validate the
  harness (all 10 original harness defects showed as false GREENS before fix;
  M16/M17 were added by the 2026-09-01/02 cross-model review, see `reviews/`;
  M18 detached `/bin/sleep` 2026-09-05; M19 stdin stall, M20/M21 stdout-then-
  ftruncate, M22 chdir-away fd-1 holder 2026-09-06 — see the dated trails).
- `scripts/` — runners (`run_full.sh`, `run_grpsig2.sh`, …), builders/patches,
  standalone repros (`repro_h1*.py`, `setsid_f2_repro.py`), v22→v27 diff.
- `dispatch/` — subordinate dispatch packets (sol/grok/agy/nim/opencode/luna).
- `review/` — per-reviewer packets, verdicts, and raw logs; `review/v27/TASK.md`
  is the fullest statement of contract, history, and known limits.

## Why v28 is the installed version (decided 2026-09-01)
The install decision, not a current measurement — the harness has gained
detection twice since (M18 cwd attribution 09-05, M19–M22 stdin/stdout 09-06),
so read the header's re-run line for where v28 stands today.
- v28 was green on the harness AS IT STOOD: contract 57/57, pidhang 0 orphans,
  grpsig2 5/5 both cases, gap 6/6. Still green on the strengthened harness
  (header, re-run 2026-09-06) — v28 has never needed a code change.
- Live v22 reproducibly FAILS grpsig2 I02 (orphaned spinning probe grandchild).
- v26 returned DO-NOT-APPLY (grandchild orphan Critical); v27/v28 fix it.
- Dual independent APPLY (sol + grok) before install.

## Known accepted limits (identical in v22, out of single-file scope)
setsid-detaching interpreter vs group-KILL (the HOOK cannot reach it; the
harness detects it by pgid, stub path, `HOME=`, or cwd — see the 2026-09-05
review trail below for the reach and the one known residual); exit-37
probe is a skip-broken-file check, not
authentication; plain (non `-p`) invocation reads BASH_ENV; D-state self-test
holds SIGKILL until syscall return; C4 covers `$HOME`, planted canaries and the
cwd's top level — arbitrary absolute paths need OS-level fs isolation.

### Dated review trails (split out 2026-09-06 to keep this file under the ceiling)
The two rounds that changed what the harness can DETECT have their own files.
Both are verbatim; nothing was summarised away. Read them before trusting any
claim about detection reach:
- [`reviews/2026-09-05-orphan-detection-cwd.md`](reviews/2026-09-05-orphan-detection-cwd.md)
  — the `HOME=` clause is inert for platform binaries, fixed by `cwd_pids`
  attribution; the exclusive-workdir lock; rounds 2 and 3 (M18). Ends with the
  standing "unknown is never clean" rule and the residuals that still evade
  every clause.
- [`reviews/2026-09-06-stdout-tap-stdin-pump.md`](reviews/2026-09-06-stdout-tap-stdin-pump.md)
  — A06's blocking stdin write (M19), C2 graded from a truncatable file
  (M20/M21), and `StdoutTap`'s EOF requirement turning the chdir-away residual
  into a detection (M22).
- [`reviews/2026-09-01-cross-model-harness-review.md`](reviews/2026-09-01-cross-model-harness-review.md)
  — the round this tree was curated from (M14/M16/M17).

**Two residuals stated here because they bound every number above:** a
descendant that closes fd 1 *and* `chdir()`s away is unreachable by any clause
(the 09-06 EOF net catches it only while it keeps fd 1); and unknown is never
graded clean — an unusable `lsof` fails or VOIDs each instrument rather than
passing it.

### Known limit: the harness's own bookkeeping is excluded from C4 (not fixed)
The harness keeps its own bookkeeping (`TABLE-*`, `RESULT-*`, the `o_*.out`/`.err`
capture files) *inside* the directory it hands the hook, so those paths must be
excluded from the C4 snapshot — the harness rewrites them itself during the run.
Every exclusion is a blind spot: a hook that specifically targets one of those
names (deleting `TABLE-<label>.txt`, or unlinking `o_*.out` by path — it no longer
holds that file as fd 1, so truncating it no longer erases C2 evidence) is not
graded on it. The realistic classes are covered by
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
