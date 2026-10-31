---
name: finding-agy-gemini4-argon-review-pin-2026-10-31
description: "agy review slot: gemini-4-argon-medium beat the review pin gemini-3.8-flash-medium in two separate windows (2026-10-24 agy 1.4.6, D +10 [+5,+15]; 2026-10-31 agy 1.4.12, D +18 [+13,+24]; /50, N=120 cells each, 0 dead) → review pin moved to argon-medium with a 3.8-flash-medium fallback on RATE_LIMIT. Auto-only D +6 [+3,+10] both windows."
metadata:
  node_type: memory
  type: finding
---

# Gemini 4 Argon in the agy review slot (2026-10-24 / 2026-10-31)

**Dates and N:**
- Window 1: 2026-10-23/24, agy 1.4.6.
- Window 2: 2026-10-24, VOID (Argon quota 429, 155 h reset).
- Window 3: 2026-10-31, agy 1.4.12.
- Each scored window: 120 cells = 4 arms × 6 packets × 5 reps, /50 per arm.

**Evidence:** `claude-code-technique/experiments/agy-gemini4-edge-2026-10-23/RESULT.md`,
`…/agy-gemini4-edge-w2-2026-10-24/REPLICATION_RESULT.md` and `…/agy-gemini4-edge-w3-2026-10-31/REPLICATION_RESULT.md`.

## Result
Final /50 (90 % paired-bootstrap CI vs control):

| arm | window 1 | window 3 |
|---|---|---|
| `gemini-3.8-flash-medium` (control, previous review pin) | 29 | 25 |
| `gemini-4-argon-low` | 44, +15 [+10, +21] | 43, +18 [+14, +22] |
| `gemini-4-argon-medium` (keystone) | 39, +10 [+5, +15] | 43, +18 [+13, +24] |
| `gemini-4-argon-high` | 43, +14 [+8, +21] | 44, +19 [+14, +25] |

- **Labels:** all three Argon arms are BETTER in both windows, with 0 dead cells.
- **Replication:** the window-3 replication criterion was pre-registered and hashed before window 2, and gives REPLICATED.
- **Where the gap is:** in the hard packets.
  - P4 (single-token hallucination gate): control 0/5 in both windows.
  - P5 (async submit, detached node, detector/submitter disagreement).
  - P6 (a value flag swallowing the next flag).
  - P5-b (detached submit node) is never found by the control; Argon finds it 2–3 times per arm per window.
- **Latency:** argon-medium median 32–37 s vs 171–189 s for the control.

## Robustness
- **Auto-only:** with no human adjudication, argon-medium is D +6 [+3, +10] in both windows. The direction
  holds without judgment. The BETTER label (gap ≥ 8) rests on the blind adjudication's revokes, which are
  committed by sha256 before unsealing. The control lost the most revokes in both windows (13 and 17): it
  names the right vocabulary without the mechanism.
- **New precedent in window 3:** 4 P1-b revokes. Reversing them leaves medium at +14 [+9, +20], still BETTER.
- **Window 3 amendment, declared before any call:** the `dispatch.py` hash was re-pinned to a live file whose
  uncommitted edit touched only the codex branch.

## Routing consequence
- **Review pin:** `gemini-4-argon-medium` + no-tool preamble + wall ≥ 300 s.
- **Fallback:** on `RATE_LIMIT`, re-dispatch once on `gemini-3.8-flash-medium`. This account's Argon quota has
  locked out for 67–155 h when used up. Window 3 fit 93 Argon calls without hitting it; the 10-27 screen hit
  it after 5 long calls.
- **Not changed:** default dispatch, the PRE-impl edge-hunt row and the unstated-edge pick stay on 3.8 Flash.
  This bench did not measure them. The sibling bench `agy-gemini4-bench-2026-10-23` saturated the edge-hunt
  axis at 24/24 on both arms, and its L2 unstated-edge result was argon-low 19/20 vs 3.8-low 20/20, HOLD.
- **Secondary arms:** argon-low ties medium in window 3 and is the fastest, but it is a secondary arm with no
  multiplicity correction, so it is not promoted.

## What would change it
- A further window where argon-medium's CI low is ≤ 0.
- Evidence that the client label "Gemini 4 Argon (Medium)" maps to a different backend model. Identity is the
  client-log label only.
- An agy release that changes either family.
- A second reader reversing the P4-a/P5-c revokes, which would move the keystone toward auto-only +6:
  NON-INFERIOR, not BETTER.
- Quota that makes the fallback the common path. Then the pin is in name only, and 3.8 should be re-pinned.

**Supersedes:** the 2026-10-16 review pin `gemini-3.8-flash-medium` ([[finding-agy-38-rebench-and-dead-cell-diag-2026-10-16]]).
Its dead-cell timing evidence still governs the fallback's wall. Nothing retracted.

Related: [[workflow-agy-subordinate]], [[reference-subordinate-routing-map]], [[finding-agy-flash-38-only-catalog-2026-10-09]]
