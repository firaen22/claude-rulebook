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
setsid-detaching interpreter vs group-KILL (the HOOK cannot reach it; the
harness now does detect such a descendant via its inherited `HOME=`, unless the
hook scrubs the environment); exit-37 probe is a skip-broken-file check, not
authentication; plain (non `-p`) invocation reads BASH_ENV; D-state self-test
holds SIGKILL until syscall return; C4 covers `$HOME`, planted canaries and the
cwd's top level — arbitrary absolute paths need OS-level fs isolation.

## Re-running
```
scripts/run_all.sh [candidate.sh] [label] [--pidhang]
```
prints one line per instrument (contract / gap / grpsig2, plus the slow
4-version pidhang differential with `--pidhang`) and exits 1 on any failure;
full logs land in `$WORK` (default `$TMPDIR/hook-harness-<label>`). This is the
token-lean entry point for an LLM session: ~4 lines instead of ~80.

`contract.py` itself prints only FAIL rows and a summary by default; the full
per-case table is always written to `TABLE-<label>.txt` in the workdir, and
`CONTRACT_VERBOSE=1` echoes it to stdout. A 4th positional argument filters
cases by substring (`python3 harness/contract.py candidate/v28.sh v28 /tmp/w D_pid`).

The legacy `scripts/run_*.sh` / `gate*.sh` still reference the original
scratchpad layout (`harness-frozen3/`) and are kept as history, not runners.
`pidhang.py` must run from the repo root (it opens `candidate/v2*.sh`).
