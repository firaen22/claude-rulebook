# 2026-09-06 — the last three documented holes closed (stdin pump + StdoutTap)

Split out of the top-level [`README.md`](../README.md) on 2026-09-06 (the README
had reached 284 lines against a ~200 soft ceiling). The section below is the
original text, verbatim and unedited — its heading level included. Standing
rules live in the README; this file is the round's evidence trail.

Holes closed: A06 could not enforce `WALL_CEIL` (blocking stdin write), B07/B08
disabled the descendant detector, and C2 was graded from a file the hook could
`ftruncate`. Mutants of record: **M19** (stdin stall), **M20**/**M21**
(stdout-then-ftruncate), **M22** (chdir-away fd-1 holder). Reviewed over two
rounds by codex sol, grok-4.6 and gemini 3.6.

---

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
