---
name: finding-astra-v21-impl-luna-2026-10-18
description: "luna (gpt-5.6-luna) implementation, bare vs astra v2.1 (v2 with the rule-1 input-guard bullet narrowed to 'guard only what the spec excludes'), same BigInt harness as the 10-18 v2 run (2026-10-18, N=5/arm/task, PREREG frozen, 4 cross-family pre-run rounds): KEEP bare (HARM: DOM). The over-guard is gone (TGT clean, happy 55/55) and I1 holds (39 → 0 silent), but 3 of 5 e6 cells dropped every input guard (domain 10/25, DOM needs > 22). No routing change; stop fitting the clause on this harness."
metadata:
  node_type: memory
  type: finding
---

# luna implementation, bare vs astra v2.1 (2026-10-18): KEEP bare (HARM: DOM)

**Date:** 2026-10-18, codex-cli 0.163.0, node v26.12.0, `gpt-5.6-luna` medium, one window, 30 cells, run on the owner's
go ("Go: run the v2.1 luna impl bench as frozen").
**Evidence:** `claude-code-technique/experiments/astra-v21-impl-luna-2026-10-18/` (lab PR #35):
- `PREREG.md`, frozen as `PREREG.sha256` (24 files, OK after the run)
- `RESULT.md`, `analyze.txt`, `results.jsonl`, `outs/`, `OWNER-NOTE.md`
- `reviews/`: four capped pre-run rounds (gpt-6.1-sol medium, served model confirmed; grok-4.7, served model
  unconfirmed) plus a TypeSafe premise gate. Every disposition is in `reviews/DISPOSITIONS.md`.
- Re-checked from a second session: `analyze.py` re-run output is identical to `analyze.txt`; `fib(-1)` and
  `lcm(-4,6)` re-run by hand on all five v2.1 e6 cells (t1, t5 throw; t2–t4 unguarded).

**Status:** decision of record = KEEP bare. No pin or routing change. The live v2 pin (`fab42e11` at `46537d5`) stays.

## Verdict
| measure | bare | v2.1 | label |
|---|---|---|---|
| exact silent+other /40 (I1) | 39 | 0 | LIFT (−39) |
| scale /110 (I2) | 44 | 109 | LIFT |
| happy (I3) | 55/55 | 55/55 | – |
| e6 domain /25 (DOM: HARM if ≤ 22) | 0 | 10 | **HARM** |
| TGT (e6 cell rejects an in-spec negative) | – | 0 of 5 | – |

Harness: 30/30 cells clean (rc 0, served luna, no quota, leak, escape, exclusion or UTIL_FS hit), digest stable, no
hand-read cases.

## Mechanism
- **What the narrowing fixed:** the 10-18 v2 defect ([[finding-astra-v2-impl-luna-2026-10-18]], a shared guard
  rejecting `treeSum({value:-4})`) did not recur in any v2.1 cell.
- **What it broke:** e6 t2, t3 and t4 contain no `throw` at all. `lcm(-4,6)` → −12, `fib(-1)` → 0 or a stack
  overflow, out-of-spec where the spec says "integer n >= 0" and "two positive integers". v2 scored 25/25 domain on
  the same probes on 10-18 (no v2 arm in this window, so not a head-to-head claim).
- **Reading [assumed]:** luna reads "guard only what the spec excludes" as "guard less". t5 also kept a shared
  `Number.isSafeInteger` helper that rejects in-spec values above 2^53, the exact pattern the clause forbids, on an
  input class no probe scores.

## What would change the conclusion
A third wording tested here would be in-sample tuning: the clause is already fitted to one 10-18 defect on these
tasks. Only a new pre-registered window on a different task set (owner's go), where a revised v2 keeps I1, happy
55/55 and full required-guard coverage, would reopen luna + v2.x. Re-scoring this window or relaxing DOM would not.

Held-out window 2026-10-22 ([[finding-astra-guard-heldout-luna-2026-10-22]]): v2.1 FAIL (UNDER) again, domain 89/115,
3 of 15 cells with no guard. Two windows agree; this conclusion stands.

## Routing implication
None. Keep "state the bound for luna", and send unstated-bound JS to gpt-6-sol + v2. Across both 10-18 windows the
exact-result rule transfers to luna (I1 38 → 0, 39 → 0); the input-guard bullet is the unstable part on luna, too
strict in one wording and dropped in the other.
