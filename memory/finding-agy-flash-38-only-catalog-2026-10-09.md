---
name: finding-agy-flash-38-only-catalog-2026-10-09
description: "agy Gemini Flash catalog consolidating to 3.8 only — operational pins moved; all 3.6/3.7 benchmark-backed route claims are historical until re-bench on 3.8."
metadata:
  node_type: memory
  type: finding
---

# agy Gemini Flash — 3.8-only catalog (2026-10-09)

**Verdict:** update routing pins to **`gemini-3.8-flash-{low,medium,high}`**. Treat every
measured score tied to **`gemini-3.6-flash-*` or `gemini-3.7-flash-*`** as **historical on
retired IDs**, not transferable to 3.8 without a re-bench.

## What changed

- **Owner intel (2026-10-09):** agy will keep **only the Gemini 3.8 Flash line** (3.6 / 3.7
  Flash tiers go away).
- **Same session:** `agy models` on **1.3.2** still listed 3.6, 3.7, and 3.8 — treat the
  owner note as the **forward catalog regime**; re-run `agy models` before dispatch if a call
  fails with unknown model.

## New operational pins (supersede 2026-08-14 / 2026-09-04 pins)

| Role | Old | New |
|------|-----|-----|
| Default / pre-impl adversary | `gemini-3.7-flash-medium` | **`gemini-3.8-flash-medium`** |
| Optional large-packet agy review lens | `gemini-3.6-flash-high` | **`gemini-3.8-flash-high`** |
| Unstated-edge exposure (least-bad agy arm) | `gemini-3.7-flash-low` | **`gemini-3.8-flash-low`** |

Process rules unchanged: no-tool preamble on read-only packets; `--dangerously-skip-permissions`
only for agentic work; always pass `--model`.

## What would change the conclusion

- Re-bench on 3.8 (edge battery + review sweep + transport) shows a different effort tier wins.
- Catalog still lists 3.6/3.7 with no EOL — pins stay on 3.8 but deprecation is not forced yet.
- agy removes 3.8 or renames IDs — update pins from `agy models`, not from this file.

## Retractions / supersessions

- **Supersedes** the standing default pin `gemini-3.7-flash-medium` and review pin
  `gemini-3.6-flash-high` in `reference_subordinate_routing_map.md` and
  `workflow_agy_subordinate.md` as **operational** choices.
- **Does not retract** the underlying measurements on 3.6/3.7 — they remain valid **for those
  IDs only** (including Sept 2025 partial 3.8 comparisons on v1.1.x).
