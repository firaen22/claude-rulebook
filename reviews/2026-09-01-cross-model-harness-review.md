# Cross-model review of the HARNESS — 2026-09-01

Reviewers: codex `gpt-5.6-luna` (read-only, files staged in cwd) and grok `grok-4.6`
(read-only `--tools read_file,grep,list_dir`, isolated seeded HOME). Both received the
same packet: `harness/*.py` + `candidate/v28.sh` + a brief naming the cost asymmetry
(false GREEN expensive, false RED cheap). Dispatcher: Claude (Fable 5.1) — a third family,
so the family-diversity invariant holds.

Every finding below is a claim reproduced (or refuted) by the dispatcher before
disposition; reviewer agreement never substituted for reproduction.

Baseline before any fix: v28 contract 57/57, gap 6/6, grpsig2 PASS (both cases).

## codex — VERDICT: FIX F1..F8

| id | claim | disposition | evidence |
|---|---|---|---|
| F1 | C4 only graded `$HOME`, planted canaries and `EXPECTED-*.json`; a hook destroying a REAL cwd file (`payload.sh`) scores `destroyed=[]` | **FIXED** — `shallow_snapshot(workdir)` graded as `CWDFILE/…` | mutant `mutants/M16_deletes_cwd_payload.sh`: OLD harness 1/1 pass (false GREEN), NEW harness `FAIL … C4 CWDFILE/DELETED payload.sh`; v28 control still passes |
| F2 | transient rename-away-and-back within the run is invisible to before/after snapshots | **rejected-with-reason** (accepted limit) | true, but closing it needs fs auditing / OS isolation, outside a userland harness; inode+md5+mtime already catch delete-and-recreate. Recorded as a limit in README |
| F3 | survivor scan can miss a `setsid`'d worker whose cmdline lacks the `interp_` marker | **rejected-with-reason** (pre-existing documented limit) | README "Known accepted limits"; needs a supervisor outside the caller's group; harness already fails closed (`orphans=-1`) when ps itself fails |
| F4 | `within_ceiling` uses `WALL_CEIL-0.5`, false RED for an 11.7s run | **rejected-with-reason** | deliberate overhead margin; fails in the CHEAP direction per the brief's asymmetry; an 11.7s hook is not a hook we want green |
| F5 | signal cases grade `alive_at_signal=None` as failure instead of VOID/retry | **rejected-with-reason** | sig cases hold stdin open until delivery (`hold_open`), so a compliant hook cannot exit early; grading a never-landed signal as a loud FAIL is the intended fail-closed behaviour |
| F6 | `pidhang.py` imports from a non-existent `harness-frozen3/` | **FIXED** (stale path removed) | reproduced: import still WORKED (script dir is on `sys.path[0]`), so not a crash as claimed — but the path was dead code from the old layout |
| F7 | `gap.py` blind 1.0s sleep; kill `OSError` swallowed; a target gone before delivery grades `exit0` = PASS | **FIXED** — `p.poll()` before delivery → `VOID-exited-before-signal`; kill error → `VOID-kill-*`; neither equals `exit0` | reproduced by reading; v28 still 6/6 `exit0` after fix |
| F8 | `grpsig2.py` I02: `ps_rows()` returning `None` skips the running-while-STOPPED check and the trial still counts landed-clean | **FIXED** — `None` sample → CONT, drain, `VOID` (retried) | reproduced by reading (`if rr is not None:` fell through); v28 still PASS after fix |

## grok
(pending at time of writing — appended below when the run completes)
