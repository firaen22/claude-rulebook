---
name: workflow-cursor-subordinate
description: cursor-agent CLI (Cursor's headless agent) as a subordinate — invocation, read-only vs write modes, model slugs, verified smoke probes, and what is NOT yet measured
metadata:
  type: project
---

# cursor-agent CLI Subordinate Playbook

> 📌 **CLI VERSION (2026-10-15):** cursor-agent **2026.10.14-941492e** at `~/.local/bin/cursor-agent`
> (alias `agent`). Auth: Cursor account login (`cursor-agent status`). Self-updates (see
> `reference_cli_version_log.md`). Added as a subordinate 2026-10-15 on user order.

## TL;DR

- **Status: available, UNROUTED.** Smoke-probed only; no task-set comparison against
  codex/agy/grok/opencode exists. It owns no task shape in
  [[reference-subordinate-routing-map]] until one is measured — routing it is an ASK USER change.
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

## Models

`cursor-agent --list-models` is the live source — slugs churn; never hard-code from memory.
2026-10-15 catalog included `auto` (default), `composer-2.5`, `gpt-5.3-codex[-low|-high|-xhigh]`,
`gpt-5.6-sol-high`, `claude-opus-5-thinking-high`, `claude-sonnet-5-thinking-high`,
`claude-fable-5-thinking-high` (**NO ZDR** — never send private data), `grok-4.7-*`,
`gemini-3.7-flash-high`. Pin `--model`; `auto` makes runs non-reproducible.

**Cross-family review caveat:** a Claude-family model via Cursor is NOT a different family
from this session. For `cross-model-review`, pick a non-Anthropic slug and record it.

## Interactions with Cursor-the-editor

Cursor's agent host also loads enabled Claude Code plugins
(`~/.claude/plugins/installed_plugins.json`, honoring `enabledPlugins: false`) — verified in
Cursor logs 2026-10-15. A dispatched cursor-agent may therefore load the same skills as this
session; do not count its doctrine-following as independent.

## What would change this file

- A same-task-set comparison vs the other subs (→ routing map row, ASK USER).
- `--mode plan` or `-w` probed; a write in `--mode ask` ever observed (→ downgrade the table).
