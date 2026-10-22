---
name: finding-astra-v2-impl-luna-2026-10-18
description: "luna (gpt-5.6-luna) implementation, bare vs astra v2, JS exact-integer probes past 2^53 with unstated sizes (2026-10-18, N=5/arm/task, PREREG frozen, 3 cross-family pre-run rounds): KEEP bare (HARM: I3). v2 took silent wrong answers from 38/40 to 0/40 (I1 −38) and scale from 46 to 110/110, but one v2 cell's input guard rejected a negative tree value (happy 54/55 vs 55/55), and I3 has zero tolerance. No routing change."
metadata:
  node_type: memory
  type: finding
---

# luna implementation, bare vs astra v2 (2026-10-18): KEEP bare (HARM: I3)

**Date:** 2026-10-18, codex-cli 0.163.0, node v26.12.0, `gpt-5.6-luna` medium, one window, 30 cells.
**Evidence:** `claude-code-technique/experiments/astra-v2-impl-luna-2026-10-18/`:
- `PREREG.md`, frozen as `PREREG.sha256` (18 files, checked OK before the run)
- `RESULT.md`, `analyze.txt`, `results.jsonl`, `outs/`
- `reviews/`: three pre-run cross-family rounds (gpt-6.1-sol medium in all three; grok-4.7 in all three, served model
  unconfirmed; agy gemini-3.8-flash-medium in round 3, unconfirmed), plus a TypeSafe premise gate. Every disposition
  is in `reviews/DISPOSITIONS.md`.

**Status:** decision of record = KEEP bare. No pin or routing change.

## Verdict
| measure | bare | v2 | label |
|---|---|---|---|
| exact silent+other /40 (I1) | 38 | 0 | LIFT (−38) |
| scale /110 (I2) | 46 | 110 | LIFT |
| size /55 (I2b) | 39 | 55 | – |
| happy (I3) | 55/55 | 54/55 | **HARM** |
| e6 domain /25 (I4) | 0 | 25 | – |

Harness: 30/30 cells clean (rc 0, served luna, no quota, leak, escape or UTIL_FS hit). The run digest was stable. No
exact-probe THROW/CRASH, so there was nothing to hand-read and the default mode is the decision of record.

## Mechanism
- **v2's lift:** exact BigInt arithmetic with a safe-range `Number` return, the same as on gpt-6-sol
  ([[finding-astra-v2-bigint-gpt6sol-2026-10-17]]). Bare luna is silent on 38 of 40 probes. Example:
  `sumSquares(1e6)` → …127550 against …500000.
- **v2's harm:** in e6 rep 1, a shared `integerBigInt` guard demanded non-negative values, and `treeSum({value:-4})`
  threw. The spec allows any integer. This was reproduced by hand: it is a model defect, not the grader. The other 4
  v2 e6 cells passed.

## What would change the conclusion
A new pre-registered window, with the owner's go, in which v2 on luna keeps the I1 lift with happy 55/55. For
example, a v2 revision whose guard clause says "guard only what the spec excludes". Re-scoring this window, or
loosening I3 after the fact, would not count.
Follow-up run the same day: [[finding-astra-v21-impl-luna-2026-10-18]], which tested that exact wording. It ended
KEEP bare (HARM: DOM), so this conclusion stands.

Held-out window 2026-10-22 ([[finding-astra-guard-heldout-luna-2026-10-22]]): v2 PASS on new tasks, 0 of 15 cells
over-guarded, domain 115/115. The two windows disagree on the guard clause; neither re-scores this one.

## Routing implication
None. Keep "state the bound for luna", and send unstated-bound JS to gpt-6-sol + v2. The size of the I1 gap (38 → 0)
says the pack's exact-result rule transfers to luna. The guard clause is what failed, in 1 of 15 v2 cells.
