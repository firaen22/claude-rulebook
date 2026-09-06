# v29 breadcrumb candidate — cross-model review dispositions (2026-09-06)

Author of v29: Opus (Claude family) orchestrator agent, spec by Fable. Reviewers, round 1,
same packet (`BRIEF.md` + v29.sh + diff + soak_launch.py): codex `gpt-6-astra` medium
(`FIX F1,F2,F3,F4`), grok-4.6 staged-files recipe (`PROCEED`, with the F1 mechanism named as a
"non-blocking residual"), fresh-context Fable critic (`FIX F1,F2,F3,F4`). Each finding was
re-derived or executed by the orchestrating session before any disposition.

| Finding (reviewer ids) | Reproduction | Disposition |
|---|---|---|
| Pre-planted FIFO (or symlink→FIFO) at `$LOG_DIR/<pid>.dropped.txt` blocks the PARENT in `open()`; `set -C` only refuses regular files (codex F1, Fable F1, grok residual) | **CONFIRMED by execution**: primitive (both FIFO and symlink→FIFO block bash 3.2 for >2 s); hook-level (fork-free `os.mkfifo` for the next 60 pids, no-interpreter mutant of v29 → parent alive >5 s, killed). Dangling-symlink write-through (my own hypothesis, also grok's "create outside LOG_DIR") **NOT a defect**: bash noclobber refuses ("cannot overwrite existing file"), file not created. | **must-fix → resolved by SCOPE, not by patch**: v29 is re-labelled HARNESS INSTRUMENT ONLY — DO NOT INSTALL (header rewritten). The breadcrumb already delivered its purpose (mechanism found). Remedies declined: codex "remove the writes" (would delete the instrument's only output); Fable "`-e`/`-L` guard + `$RANDOM`" (still a parent-side `$HOME` stat/open, race residual, and adds two more stats on a possibly wedged FS — trades one D10 hazard for three). Production fix goes to **v30 = probe-budget fix only, no parent-side `$HOME` touch**. |
| Header claim "`set -C` so it can never replace an existing file" is false for non-regular targets; first parent-side `$HOME` touch not disclosed (Fable F2) | Confirmed by reading + F1 execution | **fixed**: header rewritten to state both hazards and the instrument-only status. |
| soak_launch.py: any filename counts as success → `.error.txt`/`.partial.json`-only outcomes graded clean and evidence `rmtree`'d (codex F2, Fable F3) | Confirmed by reading (`keep = drops or not names or rc != 0`); Fable executed it (S1) | **fixed** (authored): CLEAN requires exactly one `*.complete.json` parsing with `saw_eof:true, truncated:false`; anything else → ANOMALY, HOME kept; `N<=0`/missing hook → exit 2; exit 1 on any anomaly. Positive control: error-only fake → `files=[...error.txt]` ANOMALY ×2. |
| soak_launch.py: no pgid-survivor check, no stdout tap (codex F3, Fable F4) | Confirmed by reading; Fable executed (S2: two `/bin/sleep` orphans invisible) | **fixed** (authored): `killpg(pgid,0)` after wait → `pgid-survivor` ANOMALY + kill; stdout tapped to `stdout.bin`, `>0` bytes → ANOMALY; `try/finally` closes the stdin pipe. Positive controls: orphan fake → `pgid-survivor`; stdout fake → `stdout=5B`. Negative: real v29 N=40 → 0 anomalies, exit 0, 0 leftover sleeps. |
| Breadcrumbs bypass `MAX_FILES`/`MAX_BYTES` (codex F4, grok residual) | Confirmed by reading; not executed | **rejected-with-reason for v29's role**: instrument runs in a fresh HOME per launch; moot once v29 is not installed. Recorded as a design constraint for any future production breadcrumb. |
| Soak docstring over-claims "sig_pid shape" (Fable F5) | Confirmed by reading contract.py 555–700 | **fixed**: docstring now says LAUNCH shape, not stdin/signal shape. |
| "6/400 expired" not reproduced at 3 ms spin (Fable F6) | Fable: 3/400 at ~10 ms, rates scale with spin length; mechanism CONFIRMED by all three | **no change**: my spin was ~3000 builtin iterations (≈15–20 ms). The number is spin-length dependent; the finding memory already states the mechanism, not the rate as a constant. |
| v30 direction (all three, unprompted convergence) | Diagnosis confirmed ×3 | **open**: candidates are `SECONDS+2` (codex; budget (1,2] s, ceiling +1 s), iteration-count with tick (Fable; [~1,2] s), or `/bin/sleep 0.05` poll counter replacing `SECONDS` (grok; 50 ms grid). Not built — user decision. |

Round 2 (soak fixes + header) → codex astra + fresh Fable per the owner's pre-commit rule.

## Round 2 — soak rewrite + header (codex gpt-6-astra `FIX F1 F2 F3 F4`; fresh Fable: see below)

| Finding | Reproduction | Disposition |
|---|---|---|
| R2-F1 corrupted record (`raw` wrong, matcher wrong) grades CLEAN, evidence deleted | Confirmed by execution (fake hook writing `raw:"CORRUPTED"` → was CLEAN) | **fixed**: CLEAN now also requires `raw == STDIN payload` and `registered_matcher == "manual"` (field names verified against v29.sh:533-535). Control → `raw_ok=False` ANOMALY. |
| R2-F2 valid non-object JSON (`null`, array) crashes the soak | Confirmed: `null` initially graded CLEAN in my first fix (None was the sentinel — JSON null decodes to None); array → AttributeError | **fixed**: distinct `UNPARSED` sentinel + `isinstance(dict)` gate. Controls: `null` → `not an object: NoneType`; `[1,2]` → `list`; `{bad` → `unreadable`. |
| R2-F3 evidence reads can block on a FIFO / read unbounded files | Confirmed: a fake hook that `mkfifo`s its `.complete.json` | **fixed**: `read_small()` opens `O_RDONLY|O_NONBLOCK|O_NOFOLLOW`, requires `S_ISREG` and ≤1 MiB, else ANOMALY. Control → `record not a small regular file`. |
| R2-F4 header says "fixed in v30" (unbuilt) and implies fresh HOME excludes a wedged FS | Confirmed by reading | **fixed**: "DEFERRED to v30 (not built as of 2026-09-06)"; instrument runs REQUIRE a healthy local filesystem. |
| codex: F1 scope disposition legitimate, guard not required | — | recorded; codex notes `killpg(p.pid,0)` proves "no surviving original-group members", not an absolute leak guarantee — accepted as the instrument's stated scope. |

Negative control after all fixes: real v29 N=30 and N=20 → 0 anomalies, exit 0, no `/bin/sleep` survivors.

### Round 2 — fresh Fable: `FIX F1` (tested against the LIVE files, noting the packet's diffs were stale vs. my codex-R2 fixes)
| Finding | Reproduction | Disposition |
|---|---|---|
| R2-Fable-F1 pgid-escaping hook child (`setsid` then exec sleep) invisible to `killpg(pgid,0)` → false CLEAN | Fable executed it (lsof showed the sleep alive, pgid ≠ hook) | **recorded as a stated limitation, not fixed** (Fable's own alternative): v28/v29 never change pgid; adding a per-launch lsof-cwd sweep is a code change that would need round 3 (cap reached). Docstring now states it. Queue: port `contract.cwd_pids` into the soak before it is used on any hook that spawns pgid-changing children. |
| R2-Fable-F2 re-run into a workdir with kept HOMEs → FileExistsError exit 1 | Fable executed | **recorded** (fail-loud, not false-CLEAN) in docstring; exit-2 refinement queued with F1. |
| R2-Fable-F3 header: TERM does release the FIFO block (contract 1 holds, contract 3 does not) | Fable executed | **fixed** (comment wording only). |
| All header noclobber claims; all 13 controls incl. FIFO/symlink evidence files, TIMEOUT path, real v29 N=30 clean | Fable executed | confirms codex-R2 fixes; no change. |
| (d) dispositions | — | Fable: none overturned; the survivor-check "fixed" row is tightened to "fixed for same-pgid orphans". |

**Loop closed at round cap 2.** Every FIX item is dispositioned (fixed / recorded-limitation / rejected-with-reason). Committed to the rulebook as harness instrument + trail; nothing installed.
