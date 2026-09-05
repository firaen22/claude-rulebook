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
- `mutants/` — M1–M22 seeded-defect hooks used to mutation-validate the
  harness (all 10 original harness defects showed as false GREENS before fix;
  M16/M17 were added by the 2026-09-01/02 cross-model review, see `reviews/`;
  M18 detached `/bin/sleep` 2026-09-05; M19 stdin stall, M20/M21 stdout-then-
  ftruncate, M22 chdir-away fd-1 holder 2026-09-06 — see "Other findings").
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
setsid-detaching interpreter vs group-KILL (the HOOK cannot reach it; the
harness detects it by pgid, stub path, `HOME=`, or cwd — see the orphan
detection section below for the reach and the one known residual); exit-37
probe is a skip-broken-file check, not
authentication; plain (non `-p`) invocation reads BASH_ENV; D-state self-test
holds SIGKILL until syscall return; C4 covers `$HOME`, planted canaries and the
cwd's top level — arbitrary absolute paths need OS-level fs isolation.

### Orphan detection: the `HOME=` clause does not reach platform binaries (FIXED 2026-09-05)
Out-of-group survivors (a descendant that `setsid`'d or double-forked away from
the hook's group) were attributed by matching the inherited `HOME=` in
`ps -axwwEo command=` output. macOS emits no environment text for platform
binaries — measured: a `/bin/sleep` row is 18 chars with no `HOME=`, a
CommandLineTools `python3` row is 5018 chars with it — so that clause was
**inert** for any descendant that is, or execs, `/bin/sleep`, `/bin/sh`,
`/bin/bash`. No environment scrubbing by the hook was needed. M17 was caught
only because its grandchild stays a python process. Reproduced: v28 plus a
double-fork + `setsid` + `execv("/bin/sleep")` scored `contract 1/1 pass,
orph=0` while a live `/bin/sleep 25` sat reparented to ppid 1; the reporting
agent measured the whole runner green with 21 orphans left behind.

**Fix:** `contract.cwd_pids(workdir)` — `lsof -a -d cwd -u <uid> -Fpn`, the set
of this user's pids whose cwd realpath is the workdir. cwd survives `execve` and
fd-closing, every instrument spawns the hook with `cwd=workdir` (gap.py now
`cwd=home`, unique per probe), and the workdir is unique to the run. Each
instrument samples before `Popen` and at scan time; `now − pre − {hook}` are
survivors, unioned with the pgid / stub-path / `HOME=` clauses — the fix only
ADDS detection. Cost: ~0.15s per sample. **Mutant M18** (`detached_bin_sleep`)
keeps it red: after the fix, contract `FAIL orph=1`, gap `+SURV1` on all six
probes, grpsig2 names the `/bin/sleep 25` per trial, pidhang target
`runs_with_orphan=10/10`; v28 unchanged (57/57, same md5, all PASS, exit 0).
Side effect, verified: B07_no_home and B08_home_missing — which strip the
`HOME` marker the old clause needed — now catch M18 too (`FAIL orph=1` each).

**Round-2 review of the fix (codex gpt-5.6-sol + grok-4.6, 2026-09-05), each
item reproduced by execution before it was acted on:**
- *Shared workdir = false GREEN (codex, critical).* Two concurrent runs in one
  workdir: run A attributed everything in it (`orph=5`) and SIGKILLed it, so run
  B's leaked descendant was dead before B scanned and B scored `1/1 pass` on a
  leaking hook. Fixed twice over: `run_all.sh`'s default `WORK` is now unique
  per run (`mktemp -d .../hook-harness-<label>.XXXXXX`), and every instrument
  calls `contract.require_exclusive_workdir()` at entry — before any `rmtree` —
  which exits 2 with a `FAIL <instrument>: workdir … occupied by pid(s) …` line
  if any process other than the harness's own ancestor chain has its cwd there.
  Verified: second concurrent run refuses, first grades normally; a foreign
  occupant refuses; launching the harness from inside its own workdir passes.
- *`cwd_pids` unknown-as-empty (codex + grok).* Now: lsof exit status outside
  {0,1} → None; a listing that does not contain the harness's own pid (which
  always has a cwd) → None; lsof runs with `cwd="/"` so its own row can never
  match — before that, launching the harness from inside the workdir scored v28
  `orph=1` (false red, measured). Unit-verified on all six shapes.
- *grpsig2 unknown-is-clean (codex + grok, both high).* Measured: lsof broken →
  `PASS 5/5` on M18 with 10 live survivors in the workdir. `real_survivors()` is
  now tri-state — cwd attribution unknown → None → VOID trial → INCONCLUSIVE —
  and the entry gate refuses outright when lsof is unusable. `sweep()` stays
  best-effort. `members()` also UNIONs cwd-attributed pids absent from the ps
  sample (grok), as gap.survivors now does and pidhang.scan already did.
- *C3 elapsed charged with the scan (codex).* `elapsed` is now taken at hook
  completion (`t_done`), before ps/lsof/fd-drain, so ~0.15s of harness overhead
  can no longer push a conforming hook over the 11.5s threshold.
- *Rejected with reason — gap `cwd=home` "changes hook semantics" (codex).* The
  pre-change cwd was the harness's own cwd, an accident of invocation; the other
  three instruments already ran the hook in a temp workdir; v28 has no cwd
  dependence (`grep -E '\$PWD|\bcd |\./'` → none); and C4 gets STRONGER (a
  cwd-relative delete now lands in the snapshotted tree). Kept.
- *Accepted residual — bare-pid baseline / pid reuse (codex, grok).* `pre` is
  empty in a fresh workdir (nothing can have that cwd yet), so reuse cannot hide
  a pid; a non-empty `pre` only arises from an earlier case's leftover, which
  already failed that case. Not fixed; would need (pid, start-time) identities.

**Round-3 review of the round-2 fixes (codex gpt-5.6-sol + grok-4.6):**
- *Occupancy snapshot is not a lock (codex, high).* Two runs could both pass the
  gate before either spawned; and gap's probes run in CHILD dirs, so an exact
  cwd match on the parent never saw a running gap. Now: an atomic lock file
  (`O_CREAT|O_EXCL`, keyed by the workdir's realpath, in `$TMPDIR`, held for the
  process lifetime, stale-from-dead-pid reclaimed) PLUS occupancy matched at or
  UNDER the workdir. Verified: second concurrent gap refuses; second concurrent
  contract refuses (LOCKED); child-dir occupant refuses; freed dir passes; lock
  removed at exit. The first cut used `open(O_EXCL)` then `write(pid)` — not
  atomic: under load a second gap run read the lock EMPTY, judged it stale,
  unlinked it and acquired (both graded the same dir; hit once). Now the pid is
  written to a private temp file and `link()`ed into place, so the lock file can
  never be observed without its holder. Verified: 8 simultaneous takers → exactly
  1 acquires, 7 refuse, no temp leftovers; dead-holder lock is reclaimed. `run_all.sh` runs the occupancy check (no lock) on an explicit
  `WORK` before `rm -rf`. Residual: the pre-`rm -rf` check in run_all is itself a
  snapshot — a run that starts in that same instant is not caught.
- *lsof exit 1 trusted (codex, high).* Measured 30/30 exit 0 under concurrent
  process churn, so `rc != 0` → unknown now. Nothing partial is ever a set.
- *I02 running-state probe graded with unresolved cwd state (codex, high).* It
  now resolves `cwd_extra()` itself; unknown → VOID.
- *Slash in the label broke `mktemp` (codex, medium).* Reproduced (`release/28`
  → "mkdtemp failed", exit 2). The pathname now uses a `tr`-sanitised label.
- *`_ancestors()` capped at 64 / silent stop (codex, low, fail-closed).* Walks to
  pid 1 with a visited set.
- *grok round-2 verdict: PROCEED.* Its two mediums were the gap child-dir gate
  (fixed above) and a chain needing lsof to fail at the second `real_survivors`
  sample AND at the following `sweep()`, then recover: the un-killed leftover
  lands in the next trial's `pre` and is hidden. Accepted residual — lsof failed
  0/30 under churn, and a total lsof failure is caught at the entry gate. Also
  accepted: `if not s1: return []` trusts a complete-but-empty first sample
  (only wrong if lsof omits a live process while exiting 0).

Unknown is never clean: lsof unusable → contract `orph=-1` (FAIL, verified with
`LSOF=/nonexistent`), pidhang.scan and gap.survivors return None (not-clean),
grpsig2 trials go VOID, and every instrument's entry gate refuses. Residuals
that still evade every clause (grok's list, plainly): a descendant that
`chdir()`s away — the classic `chdir("/")` daemonize — or is spawned with an
explicit cwd elsewhere; a setuid/other-uid child (`-u uid`, and `ps -E` is
same-user too); a cwd that is unlinked so lsof's path no longer equals
`realpath(workdir)`. The environment scrub alone no longer suffices. Since
2026-09-06 one more net catches the first class *when it keeps fd 1*: the
stdout pipe must reach EOF after the sweep (M22, below). A holder that also
closes fd 1 remains unreachable by any clause here.

### Other findings (2026-09-05, each verified by execution; all three CLOSED 2026-09-06)
- ~~**`contract.py` A06_oversize cannot enforce WALL_CEIL.**~~ CLOSED 2026-09-06.
  The 300,008-byte payload was pushed with one blocking `p.stdin.write` *before*
  the deadline loop, against a 64KB pipe buffer, so a candidate that stopped
  draining stdin while alive held the grader for as long as it lived: mutant
  **M19** (`stdin_stall`, `sleep 40` before the read) measured `40.13s` against
  the 12.0s ceiling (red only because the sleep ended; a never-exiting stall left
  no verdict at all). Now `run_case` sets the stdin pipe non-blocking and
  `_pump_stdin()` writes one burst before the loop and one per 20ms tick inside
  it; the deadline owns the whole wait. Verified: M19 A06 → `FAIL rc=TIMEOUT
  12.03s`, whole invocation 14.0s; v28 57/57 unchanged.
- ~~**`contract.py` B07/B08 disable the descendant detector.**~~ CLOSED by the
  cwd clause above (2026-09-05): `B07_no_home` pops `HOME` and `B08_home_missing`
  sets it to `/nonexistent/nope`, so the `HOME=` clause had nothing to match for
  2 of 57 cases; cwd attribution does not depend on `HOME`. Verified: M18 now
  `FAIL orph=1` on both cases, v28 still `ok`.
- ~~**C2 is graded from point-samples of a shrinkable file.**~~ CLOSED 2026-09-06,
  and it was not grpsig2-only: every instrument handed the hook a regular capture
  file as fd 1 and graded `os.path.getsize()` of it, so `ftruncate(1,0)` before
  exit made every sample read 0. Mutant **M20** (`stdout_then_ftruncate`, 5 bytes
  then truncate before the hook's own `exec >/dev/null`) graded CLEAN in contract
  (`A01 out=0`), grpsig2 (`5/5 landed clean` ×2) and pidhang; mutant **M21**
  (`gap_window_stdout_then_ftruncate`, the same leak inside the early exit-0 trap
  that gap's signal lands in) graded `exit0` ×6 in gap. Now `contract.StdoutTap`
  gives the hook a *pipe* for fd 1, drains it on a harness thread started after
  `Popen` (post-fork, so `preexec_fn` never runs in a child of a threaded parent),
  and grades the bytes **drained** — a count the hook cannot shrink — teed to the
  old capture path for the sample. Verified: M20 → contract `C2 stdout=5B
  b'LEAK5'`, grpsig2 `['5B stdout']` on 10/10 landed trials, pidhang `dirty=10`;
  M21 → gap `exit0+C2LEAK5B` ×6 (HEAD version: PASS); M14 control still red;
  v28 green on all four instruments (`run_all.sh --pidhang` rc 0). A pipe is also
  what Claude Code gives a hook's fd 1, so this is the more faithful stdout.
  Round-1 review (codex sol + agy, both FIX; all reproduced by reading, fixed):
  the first `count()` was a 50ms `join` heuristic → now select-driven and exact
  under a lock; a drain-thread or tee error was never graded → `tap.error` fails
  C2 at all four sites (count is taken before the tee, so a tee failure hides no
  bytes); the "post-fork thread" claim was false whenever a previous case's
  thread outlived it → every `StdoutTap()` first `quiesce()`s all live taps
  (stop flag + join; refuses to fork if one will not stop), so `preexec_fn`
  always forks single-threaded; `finalize()` after the sweep now REQUIRES EOF —
  fd 1 still open once every found survivor is dead means a holder no clause
  found. That last one turns a documented residual into a detection: mutant
  **M22** (`chdir_away_holds_stdout`: setsid + `chdir('/')` + exec `/bin/sleep`
  keeping fd 1 — invisible to pgid, `HOME=` and cwd alike) graded `ok orph=0` on
  HEAD and now `FAIL C3 stdout pipe still held after sweep`. Also from codex:
  the stdin pump treated every `OSError` as "hook closed its end" → only `EPIPE`
  is normal now, `EINTR`/`EAGAIN` retry, anything else grades `HARNESS stdin
  feed …`; and M19 was not a true regression guard (the old blocking feed also
  went red, just 28s late) → `run_case` now grades its OWN wall time against
  `GRADER_STALL`, so a re-introduced blocking feed reads `HARNESS grader
  stalled 40.1s` regardless of the hook's rc. Round 2 (codex sol FIX, grok
  PROCEED): that clock had wrapped the whole case including three `ps`/`lsof`
  calls with 10s timeouts — a slow-but-successful `lsof` could false-red a
  conforming case — so it now times only the pump→reap segment (`GRADER_STALL`
  = ceiling + 5s reap + 3s = 20s); and a failed `set_blocking` left `p.stdin`
  set, so the pump would have written A06's 300KB on a blocking fd (the M19
  hang back) → it now closes stdin and grades `stdin_feed_error`. Rejected as
  nit: a `Popen` that raises leaks the unattached tap's pipe — uncaught at all
  four sites, the instrument aborts and the kernel reclaims the fds.

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
