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

## Start the server (this 32 GB Mac, Splash 1.3.0)

One session, 2026-10-09. Uncapped `splash serve --model incoai/Qwen3.8-27B-Splash` and
an 8k serve were both refused with `host memory reserve protected` while about 21 GB
was free. Splash printed minimum required `19217.67 MiB` and deficit `0`. After quitting
Chrome, Grok Bot, and Dropbox, with NordVPN left running (operator: do not quit it),
this command logged `Ready · context 16K`:

```bash
splash serve --model incoai/Qwen3.8-27B-Splash --offline --port 8000 \
  --max-memory 20G --max-context 16K
```

Wait until the log says `Ready` before any client call. Those quits were enough in
that session; they are not a guarantee for a later start. A separate 8k server, once
it was running, rejected the golden's 12,411-token prompt with HTTP 400
`context_length_exceeded`. The 16k server completed that prompt
(`prompt_tokens` 12411, `completion_tokens` 256). `./run_bench.sh` then printed
`GOLDEN PASS` (exit 0). The long rows were `cache=hit/8192` with TTFT about 11 s,
against the frozen golden's about 33 s cold TTFT, so this pass is not a cold-prefill
match. It does not add a throughput session to the N=3 finding, and it does **not**
promote the coding lane (N=10 has not run).

## Preconditions

```bash
python3 "/Users/yauch/Documents/claude code technique/experiments/qwen-splash-local-2026-10-07/check_server.py"
```

Exit **2** on connection failure, or when `choices[].message.content` is not a string
(see `check_server.py`). The ping sends `reasoning_effort: none` and `max_tokens: 4`
(commit `2592a91`). On 2026-10-09 a live probe without that field returned `content`
null and the 4 tokens in `reasoning_content`; with the field, `content` was a string
and `check_server.py` printed `SERVER OK`.
Other API errors may raise — treat any non-zero exit as **fail closed** (do not grade
review files).

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
