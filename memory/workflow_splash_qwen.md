---
name: workflow-splash-qwen
description: "Local Qwen3.8-27B-Splash via Splash OpenAI-compatible API — optional cross-lens review only. Not dispatch.py; not an implementation subordinate. Harness lives in claude-code-technique."
metadata:
  node_type: memory
  type: reference
---

# Local Qwen3.8-27B-Splash (Splash API) — workflow

**Role:** optional **methods / harness review** lens when the Splash server is running on this
machine. **Not** a replacement for codex, agy, grok, opencode, or NIM.

> **THE ONE RULE.** Same model that ran the bench is judging the bench — confounded.
> Use only as an extra lens; never single-source PROCEED. R-B: a Qwen `PROCEED` line is not
> evidence — accept only when an **independent family** (grok/codex) agrees on the same
> artifact **or** you reproduced the pass (read files back, run the grader). Unrelated
> golden/TypeSafe PASS does not validate Qwen's review. R-A: spec applicable edges in every
> packet (empty / zero / negative / null / undefined / NaN / boundary / oversized) — same
> fleet rule as codex/agy/grok; metrics and failure-mode subjects need explicit cases.

## Preconditions

```bash
python3 "/Users/yauch/Documents/claude code technique/experiments/qwen-splash-local-2026-10-07/check_server.py"
```

Exit **2** on connection failure or empty `choices` (see `check_server.py`). Other API
errors may raise — treat any non-zero exit as **fail closed** (do not grade review files).

## Review invocation (mandatory chain)

Use the wrapper — server check **first**, then stage packet, remove stale output, run
Qwen, require non-empty output, then grade:

```bash
cd "/Users/yauch/Documents/claude code technique/experiments/qwen-splash-local-2026-10-07"
zsh review/run_qwen.sh
```

Equivalent explicit chain (do not skip steps):

```bash
set -euo pipefail
python3 check_server.py || exit 2
zsh review/stage_packet.sh
OUT=review/verdicts/qwen-cross.txt
rm -f "$OUT"
python3 ask_splash.py --prompt-file review/packet-built.md --out "$OUT" \
  --max-tokens 4096 --effort none
test -s "$OUT"
python3 grade_verdict.py --require-proceed "$OUT"
```

System prompt in `ask_splash.py` is **review-shaped** (last line `PROCEED` or `FIX F1, …`).
There is **no** measured agentic coding recipe on this endpoint in rulebook.

## TypeSafe arm (bench states)

From the experiment directory:

```bash
zsh run_typesafe.sh   # set -euo pipefail; removes stale preds before run
```

Accuracy gate: `grade_typesafe_metrics.py` (driver faults and wrong labels both fail).

## What not to do

- Do not route "implement this feature" or multi-file edits here (unmeasured; see
  [[reference-subordinate-routing-map]] §2).
- Do not skip server check and reuse an old `qwen-*.txt` verdict.
- Do not treat TypeSafe scores as review findings ([[reference-subordinate-routing-map]] TypeSafe row).

## Evidence pointer

[[finding-splash-qwen-routing-2026-10-07]] — N=3 sessions, 2026-10-07 harness merge.
