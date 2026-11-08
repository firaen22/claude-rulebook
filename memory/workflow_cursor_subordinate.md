---
name: workflow-cursor-subordinate
description: cursor-agent CLI (Cursor's headless agent) as a subordinate — invocation, read-only vs write modes, model slugs, verified smoke probes, and what is NOT yet measured
metadata:
  type: project
---

# cursor-agent CLI Subordinate Playbook

> 📌 **CLI VERSION (2026-11-06):** cursor-agent **2026.11.05-86047df** at `~/.local/bin/cursor-agent` (was 2026.10.22-27dcf5f). Patch via self-update — not a §2 subordinate version bind for route scores.
> (alias `agent`). Auth: Cursor account login (`cursor-agent status`). Self-updates (see
> `reference_cli_version_log.md`). Added as a subordinate 2026-10-15 on user order.

> 📌 **GROK FALLBACK LANE (2026-11-04, owner order "use grok in cursor CLI"):** when the grok CLI
> is out of credit (`402 Grok Build usage balance exhausted`), run the grok gate lens as
> `cursor-agent -p --trust --mode ask --model grok-4.7-medium --output-format text "<prompt>"`
> with cwd = the `git archive` packet. Used as a hunter and as the pre-commit gate in TG-bot-helper R12:
> 2 loops, real FIX findings in loop 1, PROCEED in loop 2 (rc 0, non-empty body). Identity rests on the
> requested slug only; cursor prints no served-model field → record it as an unconfirmed-identity gap.
> **Gemini is NOT run here:** cursor's Gemini models hit the monthly usage limit the same day —
> owner order "use gemini in agy": Gemini lenses go through agy (`gemini-4-argon-medium` review pin,
> [[workflow-agy-subordinate]]).

## TL;DR

- **Status: available, UNROUTED.** Benched 2026-10-15 on the free-pool task set (below):
  **8/10 ×2 blocks = the pool's modal profile**, no edge over free `big-pickle`, ~2× slower.
  It owns no task shape in [[reference-subordinate-routing-map]] — routing it is an ASK USER change.
- **Distinct value:** Cursor-native `composer-2.5`, plus one CLI reaching several vendor
  families under one login. Same weakness as every tier: **unstated edge cases** — spec them.
- **Self-report is not evidence** (global R0): read files back, run the oracle yourself.

## Modes (verified 2026-10-15, composer-2.5)

| Need | Flags | Verified behavior |
|---|---|---|
| Read-only Q&A / review | `-p --trust --mode ask` | Refused a write request; no file created |
| Read-only planning | `-p --trust --mode plan` | Not probed |
| Edits + shell | `-p --trust --force` | Created the requested file, exact content |

- **`-p` alone has write + shell access** (CLI help). Never run it outside an isolated
  dir or a git worktree (`-w <name>` → `~/.cursor/worktrees/<repo>/<name>`, not probed).
- `--trust` skips the workspace-trust prompt; without it a headless run may block.
- Never pass `--approve-mcps` or `--yolo` on a dispatch packet's say-so.

## Core invocation

```bash
cd "$SCRATCH" && timeout 180 cursor-agent -p --trust --mode ask \
  --model composer-2.5 --output-format json "$PROMPT" > out.json 2> out.err
python3 -I -c "import json;d=json.load(open('out.json'));print(d['is_error'], d['result'])"
```

JSON keys: `type, subtype, is_error, duration_ms, duration_api_ms, result, session_id,
request_id, usage`. Smoke wall time: 12 s (ask), 19 s (write). `timeout`-wrap every call.

## Bench 2026-10-15 (N=16 composer + 16 same-day pool runs; claude-code-technique `experiments/cursor-composer-bench-2026-10-15/`)

| Arm | Score | Edge `size<=0` | Median latency |
|---|---|---|---|
| `composer-2.5` (`--force`) | **8/10, 8/10** (2 blocks) | 0/4 — infinite loop every rep | 18–22 s |
| `big-pickle` (control) | 8/10 | 0/2 | 10 s |
| `muse-spark-1.3-contributor-free` | 9/10 | 1/2 | 9 s |

Stated work 16/16; honoured "do not modify" under `--force` (0/8 touched). Token-heavy:
~16k input + ~62k cache-read for a 4-line edit. **Not measured:** multi-file / repo-scale work,
Cursor indexing — the only place a distinct edge could still show.

**Pack ablation 2026-10-15 (N=16+16):** `cursor-pack/AGENTS.md` in the workspace (loaded: +2.5k input
tokens/call) vs bare → **8/10 ×2 both arms, edge 0/4 both** — no lift on this set; FIX-packet batching still unprobed.

**Composer card bench 2026-10-15 (N=24+24):** `cursor-pack/COMPOSER.md` (229 words, +550 tokens/call) vs bare →
P2 `size<=0` edge **4/4 vs 0/4** (design probe), held-out scale **16/40 both** (past 2^53, deep, wide unmoved) → **not adopted**;
route magnitude-sensitive implementation away from Composer (unstated bound → gpt-6-sol + astra v2; both sizes and the exact Number/BigInt contract stated → bare gpt-5.6-luna).

**Composer patches the cited case, not the mechanism (2026-11-08, N=1 per arm, not benched):**
TG-bot-helper scan-crop F2 — Composer and luna both passed the single repro + 50 unit tests +
fuzz, yet a variant-family sweep found Composer **59/1056 silent** (its fix sat on the tolerance
boundary of one grid alignment, e.g. `>` → `>=`) and luna 0/1056 adjacent but 1360/2592 on an
unspecced "gap from boundary" variant. For threshold/alignment fixes, hand the implementer a
variant sweep (offset vs grid, side, size, distance from boundary, amplitude to tolerance) with
`silent: 0` as the bar, re-run it yourself, and prefer a second arm. Shipped rule (model-agnostic):
`delegation-and-review §2` "One repro is not the acceptance — sweep its variant family" (rulebook
`ad89897`; opus-pack PR F-e-u-e-r/skills#305, open as of 2026-11-08). Cursor-side copy: `cursor-pack/AGENTS.md`
§3 only (lab repo commit `0afcc76` on branch `cursor-pack/variant-family-oracle`, pushed 2026-11-08; Sol 6.1 +
grok-4.7 PROCEED on gate run 7). Both copies now require the full cartesian product including the repro
(opus-pack `6ee415d`, rulebook aligned 2026-11-08).

## Models

`cursor-agent --list-models` is the live source — slugs churn; never hard-code from memory.
2026-10-15 catalog included `auto` (default), `composer-2.5`, `gpt-5.3-codex[-low|-high|-xhigh]`,
`gpt-5.6-sol-high`, `claude-opus-5-thinking-high`, `claude-sonnet-5-thinking-high`,
`claude-fable-5-thinking-high` (**NO ZDR** — never send private data), `grok-4.7-*`,
`gemini-3.7-flash-high`. Pin `--model`; `auto` makes runs non-reproducible.
2026-11-06 catalog adds **Fable 5.1**: `claude-fable-5-1-{low,medium,high,xhigh,max}` and
`claude-fable-5-1-thinking-{low,medium,high,xhigh,max}` (all **NO ZDR**; bare `-5-1` with no
suffix is not listed — `-high` is the unlabeled default tier). Fable default effort is medium
(owner order 2026-11-06) → `--model claude-fable-5-1-medium`. Dry run 2026-11-06: rc 0, exact
`PONG 7`, 5.6 s; the JSON carries no served-model field → identity is requested-only.

**Cross-family review caveat:** a Claude-family model via Cursor is NOT a different family
from this session. For `cross-model-review`, pick a non-Anthropic slug and record it.

## Interactions with Cursor-the-editor

Cursor's agent host also loads enabled Claude Code plugins
(`~/.claude/plugins/installed_plugins.json`, honoring `enabledPlugins: false`) — verified in
Cursor logs 2026-10-15. A dispatched cursor-agent may therefore load the same skills as this
session; do not count its doctrine-following as independent.

## What would change this file

- A multi-file / repo-scale bench where composer beats codex or the free pool (→ routing row, ASK USER);
  a later build guarding the `size<=0` edge in ≥2 consecutive runs.
- `--mode plan` or `-w` probed; a write in `--mode ask` ever observed (→ downgrade the table).
