---
name: finding-strata-local-bench-2026-10-16
description: "Local Strata (Qwen3.8-Flash-Next Q2_0, ~/Strata, :8080) passed the pre-registered sub gate as a single-shot, tight-spec, single-file lane; effectively N=1 (greedy); edge/scale same as bare Composer. Available, NOT routed."
metadata:
  node_type: memory
  type: finding
---

# Local Strata Q2_0 — subordinate bench finding (2026-10-16)

**Verdict:** candidate local sub, **available, not routed** (a §2 routing-map row needs the owner's order).
Lane: private or offline, single-shot, tight-spec, single-file implementation, plus short "is this correct?"
checks. Not for unstated edges, magnitude-sensitive work, multi-file or agent work, or more than ~6k tokens of
context.

- Evidence: `claude-code-technique/experiments/strata-local-bench-2026-10-16/` (PREREG 70de4aa, RESULT.md,
  score.json). Date 2026-10-16. N = 24 runs (6 tasks × 4 reps), `reasoning_effort=medium`.
- S1 P1/P2cap/P3/P4 4/4 each · S2 happy 24/24 · S3 0 discipline runs · S4 median 25.6 s, 0 timeouts.
- **Effectively N=1 per task:** greedy decoding; all reps were byte-identical.
- Edge and scale are the same as bare composer-2.5: P2 `size<=0` 0/4, scale 16/40, the same six cases.
- Throughput ~12 tok/s; context 8,192.
- Invocation: `POST http://127.0.0.1:8080/v1/chat/completions` with `model: qwen3.8-flash-next-q2_0`. Server:
  `cd ~/Strata && ./.venv/bin/python serve/server.py --engine strata --config strata-q2_0.json --port 8080`.
  Files come back as `FILE: name` plus a fence, and the caller applies them (harness `bench_strata.py`
  `apply_files`).
- The comparator is NOT like-for-like: Composer ran as an agent with tools, and Strata ran single-shot.
- TypeSafe claim gate: headline claims scored 0.76–0.98 and the fabricated controls 0.02–0.03 (scores only).

**What would change it:** a sampled arm (temperature > 0) under 3/4 on any S1 task; longer or multi-file tasks;
an agent-mode arm (opencode or codex over `/v1`); a different quant, effort or fine-tune.
**Supersedes:** nothing. This is the first Strata measurement. Related: [[finding-splash-qwen-routing-2026-10-07]]
(the other local model, a methods cross-lens only).
