---
name: finding-astra-v2-review-gpt61sol-2026-10-17
description: "astra pack v2 vs the v1 route pin on the JS REVIEW route (gpt-6.1-sol medium, 2026-10-17, N=5/arm × 3 subjects, PREREG r2 hash-frozen, 3 pre-run review rounds): v2 NON-INFERIOR — both 75/75 recall, 65/65 found, 0 FP/scope/escape by blind hand read (ceiling; no lift claimable). Removes the 'review route unmeasured' blocker on a shared pin move to v2. Pin NOT moved."
metadata:
  node_type: memory
  type: finding
---

# astra v2 vs v1 pin on the JS review route (gpt-6.1-sol) — non-inferiority (2026-10-17)

**Date:** 2026-10-17. codex-cli 0.163.0, node v26.12.0, `gpt-6.1-sol` medium, pack as prompt prefix, one window,
N=5 per arm on 3 subjects (r1 09-04, r2 09-24, r3 09-30), 30 runs.
**Evidence:** `claude-code-technique/experiments/astra-v2-review-2026-10-17/` — `PREREG.md` (r2, frozen in
`PREREG.sha256`), `RESULT.md`, `analyze.txt`, `results.jsonl`, `outs/`, `handread/` (+ `NOTES.md`), `void-run1/`
(void, unscored), `reviews/` (gpt-6.1-sol ×3, grok-4.7 ×3 with served identity UNCONFIRMED, TypeSafe; every finding
in `DISPOSITIONS.md`).
**Status:** decision of record = v2 NON-INFERIOR. **Proposed only:** no pin, pack or routing-map change without the
owner's go.

## Verdict
| arm (pack sha) | recall /75 | found /65 | other /10 | FP | scope | escape |
|---|---|---|---|---|---|---|
| v1 route pin `55941cca` (`67eb3ce`) | 75 | 65 | 10 | 0 | 0 | 0 |
| v2 candidate `fab42e11` | 75 | 65 | 10 | 0 | 0 | 0 |
All labels `-` (REC/FND/OTH/FP/SCOPE/ESC). Harness 30/30 clean: served gpt-6.1-sol ×30; 0 quota, timeout, leak,
escape or scope; run digest stable. The machine grader gives v2 74/75 from one grader false miss (`sumTo/precision`,
v2 r1 t4); the hand read gives 75.

## Caveats
- Ceiling on both arms: this shows **no harm**, not equality of skill, and no lift. Undetected band: ≤2 extra misses.
- Two FP rulings rest on the in-domain rule: `last` with an `arr[-1]` property (v1 1, v2 2) and `padNum(1e21)` (5/5).
  Counting them all gives FP +1, under the +3 threshold.
- The reader is the author (single reader, blind shuffle). JS only, small seeded subjects, medium effort.
- Void run 1: the r1 leak rule flagged codex's own `~/.codex/plugins/…/SKILL.md` read in every run. **Lesson:** a
  leak or containment rule must be replayed on a real CLI transcript before freezing, not only on a fake.

## Effect on the pin decision
[[finding-astra-v2-bigint-gpt6sol-2026-10-17]] RECOMMENDed v2 for the JS scale slot but held the shared pin because
the review route was unmeasured. That route is now measured: v2 is non-inferior there. A shared pin move to v2 is no
longer blocked by the review route. It still needs the owner's go.

## What would change this
A HARM label in a second window; a new codex CLI or gpt-6.1-sol revision; a non-saturated review subject; other
languages.
