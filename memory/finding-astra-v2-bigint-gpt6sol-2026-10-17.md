---
name: finding-astra-v2-bigint-gpt6sol-2026-10-17
description: "astra pack v2 vs the v1 route pin on gpt-6-sol, JS exact-integer probes past 2^53 (2026-10-17, N=5/arm/task, PREREG r3 hash-frozen, 3 review rounds): v2 RECOMMEND — silent wrong 0/40 vs v1 7/40 (I1 −7, threshold −5), exact passes 40 vs 33, no HARM on scale/size/happy/domain/escape. Thin margin: 6 of v1's 7 on e5 sumSquares (Number(exact BigInt)). Pin moved to v2 2026-10-17 (owner go) after the review route measured NON-INFERIOR."
metadata:
  node_type: memory
  type: finding
---

# astra v2 vs v1 pin on gpt-6-sol — silent-wrong BigInt answers (2026-10-17)

**Date:** 2026-10-17, codex-cli 0.163.0, node v26.12.0, `gpt-6-sol` medium, one window.
**Evidence:** `claude-code-technique/experiments/astra-v2-bigint-2026-10-17/` — `PREREG.md` (r3, frozen as
`PREREG.sha256` sha256 `1da4e7c5…`), `RESULT.md`, `analyze.txt`, `results.jsonl`, `outs/`, `reviews/`
(gpt-6.1-sol ×3 rounds, grok-4.7 ×2 rounds with served identity UNCONFIRMED, TypeSafe jev-1.13.0 premise scores;
every finding's disposition in `reviews/DISPOSITIONS.md`).
**Status:** decision of record = RECOMMEND v2. **Pin moved to v2 2026-10-17 (owner go)** for both pack slots, after
[[finding-astra-v2-review-gpt61sol-2026-10-17]]; recipe and rollback pin in `workflow_codex_subordinate.md`.

## Verdict
| arm (pack sha) | exact silent+other /40 | exact pass /40 | scale /110 | domain /25 |
|---|---|---|---|---|
| v1 = route pin `55941cca` (`67eb3ce`) | 7 (all silent) | 33 | 103 | 0 |
| v2 candidate `fab42e11` | **0** | **40** | 110 | 25 |
| wk = working file `bec8c00a` (report-only) | 9 | 31 | 101 | 0 |

I1 −7 (LIFT ≤ −5), I2 +7, I2b 0, I3 0, I4 +25, no escape → RECOMMEND. The lift is all extra passes, not refusals.
Harness: 45/45 cells, rc 0, served gpt-6-sol ×45, 0 quota/escape/extra files, latency ≤ 88 s, run digest stable,
0 exact-probe THROW/CRASH (hand read empty). Re-grading all 45 util.js reproduced every exact result.

## Mechanism
v1's silent answers: e5 `sumSquares` in 3 of 5 reps (both probes) + e4x `sumTo-1e9+1` once. Code: exact BigInt
arithmetic, then `return Number(...)` (off by 32/64/1). v2's bullet ("return the exact BigInt: never Number() it")
produced `<= MAX_SAFE_INTEGER ? Number(x) : x` in every e5 rep. Grader gotcha: a wrong double prints in shortest
round-trip form, so `got 333333833333500000` looks equal to the expected value (it is …500032).

## Caveats
- Thin: one fewer silent v1 rep on e5 and I1 would be −5 → still LIFT; two fewer → KEEP v1. 6 of 7 points on one
  function.
- **Scope of any pin move:** `astra-pack/AGENTS.md` is also the prefix of the JS REVIEW route (`gpt-6.1-sol`+pack).
  This bench measures only the scale-implementation slot on `gpt-6-sol`. Moving the shared pin to v2 would change
  the review route unmeasured; a scoped option is a v2 pin for the scale slot only, review stays on `55941cca`
  until an R1-style review rerun. (Resolved 2026-10-17: the review rerun read NON-INFERIOR; shared pin moved.)
- v2 domain 25/25 is the designed guard (it says so), not an independent finding.

## Supersedes / corrects
- 10-16 rebench A2 ("JS scale slot 45/50, 5 silent", pack `bec8c00a`) measured the working file, not the pin. The
  pin is now measured: 7/40 silent on the exact probes in this window. The routing map's "a frozen-pack arm would
  attribute the drop": in this window the pin is also silent (7 vs wk 9), so "the drop came from the working-file
  edits" is not supported — but there is no crossed pack-by-window design, so the drop stays unattributed.

## What would change this
A second window where v1's e5 silent count falls (I1 > −5 → KEEP v1); a new codex CLI or gpt-6-sol revision;
float-valued subjects; any claim about the review route (untested here).
