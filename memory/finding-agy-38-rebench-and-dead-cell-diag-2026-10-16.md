---
name: finding-agy-38-rebench-and-dead-cell-diag-2026-10-16
description: "agy 1.4.0 / Gemini 3.8 Flash re-bench + review dead-cell diagnosis (2026-10-16): empty returns are still the headless permission deny (preamble fixes it, 0/32 empty); with the preamble, 3.8-high review is NOT USABLE at 240 s and INCONCLUSIVE at 600 s, 3.8-medium USABLE at 240 s and 600 s; 3.8-medium edge-hunt QUALIFIES 24/24; 3.8-low unstated-edge 19/20."
metadata:
  node_type: memory
  type: finding
---

# agy 3.8 re-bench + review dead-cell diagnosis (2026-10-16)

**Date:** 2026-10-16, agy CLI **1.4.0** (auto-updated from 1.3.6 at 15:15 the same day, partway through B1).
**Evidence:** `claude-code-technique/experiments/sub-rebench-2026-10-16/RESULT.md` (Lane B, PREREG r4) and
`claude-code-technique/experiments/agy-timeout-diag-2026-10-16/RESULT.md` (PREREG hash-frozen, re-checked after the run).
All labels are proposed; the routing map and playbook are unchanged pending the owner's go.

## Verdicts

1. **"agy returned nothing" is still the headless permission deny on 1.4.0.** rc 0, 0 B stdout, and 1.4.0 now
   explains it on stderr ("a tool required the "command" permission that headless mode cannot prompt for, so it
   was auto-denied"). With the no-tool preamble: **0/32 empty, 0 empty-retries** across four arms. (N=1 mechanism
   call; N=32 grid.)
2. **Review dispatch with the preamble (P1/P2/P3/P6 × 2 reps, N=8 per arm, one window):**
   | arm | dead | label |
   |---|---|---|
   | 3.8-high, 240 s | 3/8 (all timeout) | NOT USABLE |
   | 3.8-high, 600 s | 2/8 (both P2, timed out at 600 s) | INCONCLUSIVE |
   | 3.8-medium, 240 s | 1/8 (P2) | USABLE (slowest answer 232 s: thin margin) |
   | 3.8-medium, 600 s | 0/8 | USABLE |
   Rule: dead ≤ 1/8 USABLE, ≥ 3/8 NOT USABLE. High's timeouts are partly budget (2 answers took 314 s and 534 s) and
   partly not (P2 unanswered at 600 s). 5 of 6 grid timeouts are packet P2.
3. **Edge-hunt (B1, 3.8-medium):** hand recall **24/24**, axis-C FABRICATED **0/8** → QUALIFIES, equal to the
   retired 3.7-medium comparator. Thin: 10 of 12 fabrication probes (all arms) returned EMPTY, i.e. unmeasured.
   B1 ran without the preamble and spans both CLI versions.
4. **Unstated edge (B3, 3.8-low):** GUARD **19/20** (baseline 14, margin 2) → UP. Only 5 of 20 outputs distinct.
5. **No-preamble replays (B2, B4)** measured the old invocation, not today's dispatch: B2 3.8-high 18/20 dead;
   B4 case-cell deaths high 8/8, medium 5/8, low 0/8. Their empties are verdict 1; their timeouts are verdict 2's mode.

## Retractions / supersessions
- Supersedes the playbook's "3 remaining deaths are `__TIMEOUT__`… still-undiagnosed" (09-04) to the extent above:
  the mode is now characterised (budget-sensitive for high, packet-concentrated on P2, not cured by 600 s) but its
  root cause (slow generation vs stall) is still open: a killed process leaves no stderr.
- Today's 1.4.0 changelog item ("Eligibility check failed" lockouts) is unrelated: no attempt in the grid wrote stderr.
- The playbook cited `finding_agy_empty_return_is_permission_deny_2026-09-04.md` and
  `finding_agy_review_preamble_sweep_2026-09-04.md`; neither file existed (checked 2026-10-16). **Fixed in
  `7449ea0`:** the playbook now points at `experiments/agy-review-preamble-2026-09-04/`, where the 09-04 data lives.

## What would change this
- A second window where 3.8-high/600 s dies on ≥ 3/8 (or ≤ 1/8).
- A P2-only run with `--log-file` at ≥ 900 s, separating slow generation from a stall.
- Any agy CLI release after 1.4.0 (it auto-updates; re-check `agy --version` before relying on these numbers).
- A medium/240 s run where answers cross 240 s more often (today's margin was 8 s).

## Applied (owner's go, 2026-10-16, rulebook `7449ea0`)
- Review-dispatch pin: `gemini-3.8-flash-high` → `gemini-3.8-flash-medium` with the preamble and wall ≥ 300 s.
- The two dangling 09-04 links in `workflow_agy_subordinate.md` (see Retractions).

## Still proposed (not applied)
- Edge-hunt row: 3.8-medium re-confirmed on 3.8 (with the fabrication caveat); the routing-map row still reads
  "UNVERIFIED on 3.8".
