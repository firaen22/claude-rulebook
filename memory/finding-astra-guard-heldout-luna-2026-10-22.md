---
name: finding-astra-guard-heldout-luna-2026-10-22
description: "luna (gpt-5.6-luna) on three held-out integer tasks, bare vs astra v2 vs astra v2.1 vs bare + an opus-pack packet contract naming every edge (2026-10-22, N=5/arm/task, PREREG frozen, 3 cross-family pre-run rounds): v2 PASS, opus PASS, v2.1 FAIL (UNDER, 89/115). Every arm removes bare's silent wrong answers past 2^53 (80 → 0 /105) with no over-guard; v2.1 again drops whole guards in some cells (3 of 15). No pin or route change."
metadata:
  node_type: memory
  type: finding
---

# luna guard held-out bench (2026-10-22): v2 PASS, opus PASS, v2.1 FAIL (UNDER)

**Date:** 2026-10-22, codex-cli 0.163.0, node v26.12.0 (hand re-reads on v26.12.1), `gpt-5.6-luna` medium, one window, 60 cells (+1 rerun), run on
the owner's go.
**Evidence:** `claude-code-technique/experiments/astra-guard-heldout-2026-10-22/` (`PREREG.md` frozen as
`PREREG.sha256`, 45 files OK after the run; `RESULT.md`, `analyze.txt`, `results.jsonl`, `outs/`, `OWNER-NOTE.md`,
`reviews/DISPOSITIONS.md`). Rebuild: `python3 run.py SANDBOX`, then `python3 outs/analyze_owner_cleared.py`.

## Verdict
| measure | bare | v2 | v2.1 | opus |
|---|---|---|---|---|
| exact silent+other /105 (I1) | 80 | 0 | 0 | 0 |
| happy /60, inspec /145 | 60, 145 | 60, 145 | 60, 145 | 60, 145 |
| over-guard rejections | – | 0 | 0 | 0 |
| domain /115 (HARM < 0.9) | 0 | 115 | **89** | 115 |

Harness: 60/60 served luna, no quota/escape/timeout; one leak (opus g1 t3) excluded and rerun clean; three UTIL_FS
flags (`require` in error strings) cleared by the owner, applied without editing the frozen analyzer.

## Mechanism
- v2.1 g1 t4, g1 t5, g3 t1 contain no `throw` at all; g3 t4 misses `gcdAll([])`. 14 of the 26 misses are silent
  values (`factorial(-1)` → 1, `sumRange(3,1)` → −2), so v2.1 fails even if engine crashes counted as rejections
  (101/115 = 0.878).
- Across windows: v2.1 under-guarded on 10-18 ([[finding-astra-v21-impl-luna-2026-10-18]]) and here; v2 over-guarded
  1/15 on 10-18 ([[finding-astra-v2-impl-luna-2026-10-18]]) and 0/15 here. v2's guard clause is unresolved across two
  windows; v2.1's narrowing reproducibly drops guards.
- opus is the only arm whose prompt names each excluded input; its PASS measures a stated contract, matching the
  upstream position that the packet author states edges (delegation-and-review "Edge behavior named").

## What would change the conclusion
A third pre-registered window on new tasks: v2 over-guarding there returns it to unresolved; v2 holding both ways makes
two of three windows. Results on gpt-6-sol (v2's actual implementation route) are unmeasured; this is luna-only.

## Routing implication
None from this window. Keep "state the bound and edges for luna" and gpt-6-sol + v2 for unstated-bound JS. Do not
adopt v2.1.
