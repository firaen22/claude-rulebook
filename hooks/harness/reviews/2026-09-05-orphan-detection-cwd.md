# 2026-09-05 — orphan detection: the `HOME=` clause does not reach platform binaries

Split out of the top-level [`README.md`](../README.md) on 2026-09-06 (the README
had reached 284 lines against a ~200 soft ceiling). The section below is the
original text, verbatim and unedited — its heading level included. Standing
rules live in the README; this file is the round's evidence trail.

Round of record: the fix, its round-2 review (codex gpt-5.6-sol + grok-4.6) and
its round-3 review. Mutant of record: **M18** (`detached_bin_sleep`).

---

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
