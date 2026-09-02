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
| F3 | survivor scan can miss a `setsid`'d worker whose cmdline lacks the `interp_` marker | ~~rejected-with-reason~~ → **FIXED in the grok round** (grok F2/F3 below reproduced it with mutant M17) | the 09-01 rejection was wrong: attribution by the case's unique `HOME=` in `ps -E` output needs no supervisor. Two reviewers converging on the same class raised its priority; the mutant, not the convergence, changed the disposition |
| F4 | `within_ceiling` uses `WALL_CEIL-0.5`, false RED for an 11.7s run | **rejected-with-reason** | deliberate overhead margin; fails in the CHEAP direction per the brief's asymmetry; an 11.7s hook is not a hook we want green |
| F5 | signal cases grade `alive_at_signal=None` as failure instead of VOID/retry | **rejected-with-reason** | sig cases hold stdin open until delivery (`hold_open`), so a compliant hook cannot exit early; grading a never-landed signal as a loud FAIL is the intended fail-closed behaviour |
| F6 | `pidhang.py` imports from a non-existent `harness-frozen3/` | **FIXED** (stale path removed) | reproduced: import still WORKED (script dir is on `sys.path[0]`), so not a crash as claimed — but the path was dead code from the old layout |
| F7 | `gap.py` blind 1.0s sleep; kill `OSError` swallowed; a target gone before delivery grades `exit0` = PASS | **FIXED** — `p.poll()` before delivery → `VOID-exited-before-signal`; kill error → `VOID-kill-*`; neither equals `exit0` | reproduced by reading; v28 still 6/6 `exit0` after fix |
| F8 | `grpsig2.py` I02: `ps_rows()` returning `None` skips the running-while-STOPPED check and the trial still counts landed-clean | **FIXED** — `None` sample → CONT, drain, `VOID` (retried) | reproduced by reading (`if rr is not None:` fell through); v28 still PASS after fix |

## grok — VERDICT: FIX F1,F2,F3,F4,F5,F6,F9,F11 (run 2026-09-02)

First dispatch (9-file packet, ~62K input tokens) died with `inference idle timeout after
600s with no chunks` (grok-err.txt) after 317 bytes of plan narration. Retry with only the
four core `harness/*.py` files (v28.sh, grpsig.py, exectext.py, refcheck.py dropped as
out-of-scope by the brief itself) and `--no-plan` produced the full 11.4KB report below in
~13 min. Identity: requested `-m grok-4.6`, rc=0, non-empty body, verdict line quoted.
Grok reviewed the tree AFTER the codex-round fixes (`692e4a0`), so its "prior … look fixed"
notes on gap.py refer to that round.

| id | claim | disposition | evidence |
|---|---|---|---|
| F1 | `_proc_state()==None` (ps timeout/empty) graded as live; kill `OSError` swallowed with `delivered=True` | **FIXED** — `None` → `STATE-UNREADABLE`, kill error → `KILL-<Exc>`; both grade VOID (never `True`) | reproduced by reading `contract.py` (`if _proc_state(p.pid)=="Z" … else True`); D_pid_TERM still passes |
| F2 | survivor scan (pgid clause + `interp_` marker) misses a descendant that left the group | **FIXED** — third clause: any live process whose `ps -E` environment carries this case's unique `HOME=<home>` | mutant `mutants/M17_detached_grandchild_late_writer.sh` (double-fork + `setsid`, sleeps 3s, writes `LEAK` on inherited fd 1): OLD harness `ok … orph=0` 1/1 pass; NEW harness `FAIL … C3 1 process(es) abandoned` |
| F3 | out-of-group child writes to stdout after the 1.5s SETTLE → C2 graded 0 bytes | **FIXED via F2** (a live descendant at scan time is now C3 FAIL, so the late write cannot be the only evidence) | same mutant: after the OLD harness graded `out=0`, the capture file read `LEAK` 3s later (`cat o_A01_happy_manual.out` → `LEAK`) |
| F4 | G01/G02 pass pipes through at the PARENT's fd numbers; child fd 3 / 3..12 never held the pipes the labels promise | **FIXED** — write ends `dup2`'d onto exactly 3..3+n-1 in `preexec_fn`, harness keeps the read ends and grades them for EOF after exit (`fd_held` → `C3 inherited fd(s) … still held`) | probe target `ls /dev/fd >&2`: G01 child sees `0 1 2 3 (+2 of ls's own)`, G02 sees `3..12`; first cut false-RED'd because the PARENT still held the write ends — fixed by closing them right after `Popen`; v28 G01+G02 2/2 pass |
| F5 | `pidhang.py` counted a trial "landed" whenever the hook was alive, not when its hung PROBE was; no handshake; kill error swallowed | **FIXED** — `pidhang.py` rewritten on `grpsig2.wait_probe_landed`/`probe_alive`: deliver only after the probe is observed alive in-group (+0/0.1/0.2s phase offset, re-checked), else VOID and retry; kill error → not landed | grok's stated mechanism ("hook reads stdin before the interpreter loop") is FALSE for v28 — the probe runs in the parent (`v28.sh:664-730`) before the worker reads stdin — but the absence of a probe-alive handshake was real: a signal after the ≤1s probe budget expired counted as landed |
| F6 | 6s cap → `killpg(SIGKILL)` → then scan: in-group evidence destroyed before it is counted; trial still "landed clean" | **FIXED** — a hook still running at the cap is `BLOCKED` (counted separately, fails the differential); survivors scanned BEFORE the group is killed | reproduced by reading (`if now-t0>6: killpg(...); break` preceded `scan()`) |
| F7 | contract.py scans survivors immediately, no double sample → a child mid-teardown is a false RED | **rejected-with-reason** (S3, not in FIX list) | cheap direction per the brief; v28 57/57 with zero flakes across every run this week; double-sampling would add 0.45s × 57 to every run |
| F8 | signal cases VOID-FAIL a hook that legitimately exits before 0.35s | **rejected-with-reason** (S3, not in FIX list) — same as codex F5 | `hold_open` keeps stdin open so a compliant hook cannot finish early; VOID = loud FAIL is the intended fail-closed shape |
| F9 | `assert m` on the interpreter-list regex crashes the run | **FIXED** (minimal) — explicit `RuntimeError` with the target path, so `python -O` cannot strip it | loud crash was already the cheap direction; not folded into per-case FAIL |
| F10 | gap.py anchor miss scored `pass: False` instead of INCONCLUSIVE | **rejected-with-reason** (S3, not in FIX list) | fail-closed by design; the row carries `note: NO-EARLY-TRAP-ANCHOR` |
| F11 | gap.py blind `sleep(1.0)`: an oversleep past the widened window lands the signal after `trap '' TSTP` and grades a vulnerable hook `exit0` | **FIXED** — busy-wait writes `$HOME/.gap_ready` (builtin redirection, no fork); prober waits for the marker, delivers, records `late`; `>1.5s` or no marker → `VOID-…` | reproduced by reading; v28 6/6 `exit0`, mutant M14 still `exit0+C2LEAK1B` ×6 after the change |

### Verdict on the dual gate (round 1+2)
Both families produced confirmed, non-empty verdicts. Every FIX item is reproduced-and-fixed
or rejected-with-reason above; no item is deferred. Post-fix re-verification (this round):
v28 contract 57/57, gap 6/6, grpsig2 5/5 both cases, pidhang DISCRIMINATED; mutants M14,
M16, M17 all FAIL as intended. Dual-lens **PROCEED** on the harness at commit `4cf965b`.

## codex `gpt-5.6-sol` (effort high) — round 3 on `4cf965b` — VERDICT: FIX F1..F10 (2026-09-02)

Packet: the four `harness/*.py`, `ROUND2-DIFF.patch` (692e4a0..4cf965b), v28.sh + M17 for
context, brief with a round-2 addendum listing the already-rejected classes so they would
not be re-litigated (none were). rc=0, 10.9KB body, model confirmed in the codex log.

| id | claim | disposition | evidence |
|---|---|---|---|
| F1 | fd EOF check: a single `os.read(r,1)` that returns a byte scores the fd clean while a descendant still holds it | **FIXED** — drain until EOF; `EAGAIN` = held; other `OSError` = unknown (`3?Exc`), never clean | probe hook (detached child writes 1 byte to fd 3, holds 4s): OLD harness scored the fd clean (child caught only via HOME attribution); NEW adds `C3 inherited fd(s) [3] still held`. The false GREEN needs F2 evasion as well — this is now an independent second detector |
| F2 | HOME attribution is removable (`env -i`); grpsig2 lacked it entirely; proposes pre-spawn PID baseline + fail-closed on unattributed survivors | **PARTIAL** — grpsig2 now attributes by HOME too (`ps -E`, `HOMEMARK`); the env-scrub gap stays a documented limit (README); the PID-baseline remedy **rejected-with-reason** | a same-UID pid-set diff on a live macOS host catches launchd user agents spawning during a 7-minute run → nondeterministic false REDs; an attribution the hook must actively defeat is the deterministic option available in userland |
| F3 | pidhang graded only survivors: rc, stdout bytes, canary tree discarded | **FIXED** — stdout captured, `rc!=0`, bytes, `diff_snapshots(home)` → `DIRTY` landed trial, fails the differential | reproduced by reading (`stdout=DEVNULL`, `returncode` never read) |
| F4 | `shallow_snapshot` graded only the cwd's top level; nested pre-existing files invisible to C4 | **FIXED** — recursive `cwd_snapshot(workdir)` excluding this case's home, canary tree, capture files and run-level TABLE/RESULT | probe hook `rm -f ./hostilebin/python3`: OLD harness `1/1 pass` (false GREEN), NEW `FAIL … C4 CWDFILE/DELETED hostilebin/python3` |
| F5 | gap.py `killpg` before any survivor scan; no C4 | **FIXED** — `survivors()` (pgid + HOME) scanned before cleanup → `+SURVn` / `+SURV?`; home built with canaries and diffed → `+C4:` | same class as grok F6 (pidhang); v28 still 6/6 `exit0`, M14 still `+C2LEAK1B` ×6 |
| F6 | grpsig2 I01 never read its stdout capture; neither case graded C4 | **FIXED** — I01 grades bytes; both cases diff against a per-target `HOME_BEFORE` snapshot | reproduced by reading |
| F7 | `ps` rc≠0 with empty stdout parsed as an empty process table → 0 survivors | **FIXED** in all three instruments — rc≠0 or empty → `RuntimeError`/`None`, which every caller already treats as unknown/VOID | confirmed: `/bin/ps -p <bad>` exits 1 with empty stdout |
| F8 | fixed temp fd 300 exceeds a 256 soft `RLIMIT_NOFILE` → `dup2` fails in `preexec_fn`, no case result | **FIXED** — temps at `max(max(ws), 3+n)+1` | confirmed: `launchctl limit maxfiles` soft = 256 on this Mac (this session ran at 1048576, which is why the bug did not surface) |
| F9 | pidhang `rmtree(ignore_errors)` then `makedirs` → `FileExistsError` on a mode-000 leftover | **FIXED** — `contract._rmtree` (chmods on error) | reproduced by reading; the same fixture class (observed/ at 0o500) already bit contract.py once |
| F10 | gap.py `exists()` then `stat()` on the ready marker, unhandled `OSError` | **FIXED** — `VOID-ready-marker-vanished` | reproduced by reading |

Post-fix: see the run block appended below.

Post-fix run (2026-09-02, after the sol round): v28 contract 57/57, gap 6/6 `exit0`,
grpsig2 I01 5/5 + I02 5/5 landed clean, pidhang DISCRIMINATED (v22 10/10 leak, v26 10/10
leak, v27 0, v28 0; blocked=0 dirty=0); mutants M14 (`+C2LEAK1B` ×6), M16 (`C4 CWDFILE/
DELETED payload.sh`), M17 (`C3 1 process abandoned`) all FAIL as intended; probe hooks for
sol F1 and F4 FAIL under the new harness and passed (F4) / were fd-clean (F1) under `4cf965b`.
Three families (codex luna, grok, codex sol) have now produced confirmed verdicts on this
tree; every item is fixed, partial-with-documented-limit (sol F2), or rejected-with-reason.
