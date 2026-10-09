---
name: reference-cli-version-log
description: "Dated one-line CLI upgrade notes — housekeeping only, not bench findings. Canonical routing stamp lives in reference_subordinate_routing_map.md."
metadata:
  node_type: memory
  type: reference
---

# CLI version log

Append-only. Each line is `--version` unless noted. Route-to table changes only when a finding says so.

| Date | Component | Change | Notes |
|---|---|---|---|
| 2026-10-09 | codex | 0.161.0 → **0.162.0** | MINOR; claims UNVERIFIED on 0.162.x; restart Codex |
| 2026-10-09 | grok | 1.0.46 → **1.0.50** | patch; claims UNVERIFIED on 1.0.50; restart Grok |
| 2026-10-09 | agy | 1.3.1 → **1.3.2** | patch; still UNVERIFIED on 1.3.x |
| 2026-10-09 | opencode | 2.0.24 → **2.0.26** | patch; first `opencode upgrade` failed, retry OK |
| 2026-10-09 | node (brew) | 26.10.0 → **26.11.0** | not a subordinate |
| 2026-10-09 | uv | 0.12.23 → **0.12.24** | |
| 2026-10-09 | vercel (npm) | 62.7.0 → **63.1.0** | unrelated to delegation |
| 2026-10-09 | firebase-tools | 15.32.1 → **15.33.0** | unrelated to delegation |
| 2026-10-07 | agy | 1.2.17 → **1.3.0** | MINOR; pins unchanged; all agy metrics UNVERIFIED on 1.3.x; restart CLI if session open |
| 2026-10-07 | opencode | 2.0.22 → **2.0.24** | patch; 2.0.x scores still UNVERIFIED vs 1.x benches |
| 2026-10-07 | codex | 0.160.0 → **0.160.1** | patch; codex claims still UNVERIFIED on 0.160.x |
| 2026-10-07 | grok | 1.0.46 | unchanged |
| 2026-10-07 | claude-code (npm global) | 2.1.290 → **2.1.292** | not a subordinate in routing map |
| 2026-10-07 | vercel (npm global) | 62.4.0 → **62.5.0** | unrelated to delegation |
| 2026-10-07 | uv | 0.12.23 | already latest after prior self-update |
| 2026-10-05 | fleet | `dispatch.py --pong` | all five + TypeSafe one-call probe (see routing map stamp) |
