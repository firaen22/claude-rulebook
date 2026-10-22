---
name: finding-astra-guard-sol-and-luna-window3-2026-10-23
description: "Two frozen guard windows run 2026-10-23 (N=5/arm/task, 45 cells each, 3 capped cross-family pre-run rounds): gpt-6-sol on the 10-22 tasks g1–g3 and gpt-5.6-luna window 3 on new tasks g4–g6, bare vs astra v2 vs bare + opus-pack packet contract. All four wording arms PASS (lift): exact silent+other 80/105 (sol) and 105/105 (luna) → 0, domain 115/115, 0 over-guard. v2 now holds both ways on 2 of 3 luna windows; the stated contract passed in all three windows it ran. No pin or route change."
metadata:
  node_type: memory
  type: finding
---

# Guard windows (2026-10-23): sol v2 PASS, sol opus PASS; luna window 3 v2 PASS, opus PASS

**Date:** 2026-10-23, codex-cli 0.163.0, node v26.12.1, medium effort, one window each, 45 cells each (+1 rerun on
sol), run on the owner's go ("Wait: run the two frozen windows first, then draft the provenance PR with all three
windows and show me the text before opening it.").
**Evidence:** `claude-code-technique/experiments/astra-guard-sol-2026-10-22/` and
`.../astra-guard-window3-2026-10-22/` (`PREREG.md` frozen as `PREREG.sha256`, 44/44 and 46/46 OK after the run;
`RESULT.md`, `analyze.txt`, `results.jsonl`, `outs/`, `reviews/DISPOSITIONS.md`). Rebuild: `python3 run.py SANDBOX`,
then `python3 outs/analyze_owner_cleared.py`.

## Verdict
| measure | sol bare | sol v2 | sol opus | luna-w3 bare | luna-w3 v2 | luna-w3 opus |
|---|---|---|---|---|---|---|
| exact silent+other /105 (I1) | 80 | 0 | 0 | 105 | 0 | 0 |
| happy /60, inspec /145 | 60, 145 | 60, 145 | 60, 145 | 60, 145 | 60, 145 | 60, 145 |
| over-guard rejections | – | 0 | 0 | – | 0 | 0 |
| domain /115 (HARM < 0.9) | 0 | 115 | 115 | 0 | 115 | 115 |
| decision | | PASS (lift) | PASS (lift) | | PASS (lift) | PASS (lift) |

Harness: every cell served the requested model, rc 0, max latency 94.3 s / 600 s. One sol leak (v2 g3 t5 searched
for `AGENTS.md` by absolute `/Users/…` path), excluded and rerun once, clean; both attempts 27/27. Five UTIL_FS flags
(`require` inside error strings) cleared by the owner; the frozen analyzer's blocked output is kept beside the cleared
read. Loud 0 everywhere, so the loud, strict and first-attempt reads coincide.

## Mechanism
- bare writes no guard on either model (0/115) and returns Number arithmetic past 2^53 (luna `lucas(90)` →
  6440026026380245000, exact 6440026026380244498). The g4–g6 scale probes were built not float-exact, which is why
  luna bare is 105/105 silent there vs 80/105 on g1–g3.
- v2 and opus throw on every excluded input, accept the in-spec negatives (`dot([-1,2],[3,-4])` → −11,
  `cubeSum(-3,2)` → −27), and return exact BigInt (hand-run under node).
- Across luna windows: v2 over-guarded 1/15 on 10-18 (a tree, [[finding-astra-v2-impl-luna-2026-10-18]]), 0/15 on
  10-22 ([[finding-astra-guard-heldout-luna-2026-10-22]]) and here. The 10-22 and window-3 tasks share author and hazard
  class (flat integer functions, array reductions), so "2 of 3" is a decision rule, not independent replication.
- The stated contract (opus way) passed in all three windows it ran (luna 10-22, luna window 3, sol): the worker
  follows named edges. This is worker-side evidence for opus-pack delegation-and-review "Edge behavior named"; whether
  the bullet changes what dispatchers write stays unprobed.

## What would change the conclusion
A window on nested structures (the 10-18 over-guard was on a tree); a second sol window flipping a label; a fourth luna
window over-guarding; a newer codex CLI or model revision; a different author for tasks, graders or contract. At a
1-in-15 OVER cell rate a clean 15-cell window still comes up ≈ 0.36 of the time [assumed, binomial].

## Routing implication
None applied. Proposals awaiting the owner's go: luna + v2 for unstated-bound JS of flat integer functions and array
reductions (window-3 PREREG); extend the 10-22 opus note (`astra-pack/README.md`, cursor-pack §6) from luna to sol; an
upstream provenance-only PR for "Edge behavior named" (draft: `experiments/upstream-provenance-pr-draft.md`).
Supersedes the "results on gpt-6-sol are unmeasured" line in [[finding-astra-guard-heldout-luna-2026-10-22]].
