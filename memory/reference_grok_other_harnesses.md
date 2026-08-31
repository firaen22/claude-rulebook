---
name: reference-grok-other-harnesses
description: "Verified recipes for running grok OUTSIDE the grok CLI — opencode, codex, Claude Code — with the TOML-placement and non-TTY gotchas that produced two false BLOCKED verdicts. Extracted verbatim from workflow_grok_subordinate.md 2026-08-27 (soft-ceiling enforcement). The STANDING DECISION lives in the playbook, not here: grok CLI is the default lane; these paths bill metered OpenRouter credits and buy no capability."
metadata:
  node_type: memory
  type: reference
---

Extracted VERBATIM from `workflow_grok_subordinate.md` §"Grok inside OTHER
harnesses" on 2026-08-27 when that file hit ~39% over its ~200-line soft ceiling.
All four recipes were verified empirically 2026-08-25; nothing here is restated
from memory.

**Nothing in this file is an order.** It is a recipe book you open when grok must
run inside another harness, or when a bench must exclude the CLI scaffold. The
routing decision — CLI first, always — is in the playbook, and the playbook wins
on any disagreement.


**Standing decision (user, 2026-08-25): grok CLI is the default grok lane** — it is the
only path the SuperGrok subscription covers. The opencode/codex/Claude Code recipes below
all WORK but bill metered OpenRouter credits, and buy no capability (edge-blindness is a
model property, identical in all four harnesses). Reach for them only when grok must run
inside another harness or a bench must exclude the CLI scaffold.

- **opencode**: works via `openrouter/x-ai/grok-4.6` (metered OpenRouter credits; edge
  profile identical to CLI, [[finding-openrouter-grok-p2-2026-08-25]]). Zen's
  `opencode/grok-4.6` is billing-blocked (exits 0 with an Error on stdout).
- **codex (verified on 0.149.0, 2026-08-25; installed build is now `0.150.1` — UNVERIFIED since the bump): WORKS** — smoke test + file-write
  task both clean, direct to OpenRouter, no proxy. Recipe (isolated CODEX_HOME):
  top-level `model = "x-ai/grok-4.6"`, `model_reasoning_effort = "low"`, and
  `[model_providers.openrouter]` with `base_url = "https://openrouter.ai/api/v1"`,
  `env_key = "OPENROUTER_API_KEY"`, `wire_api = "responses"` (`"chat"` was removed in
  this codex version). TWO GOTCHAS found on the way: (1) `model_reasoning_effort` MUST
  be top-level — appended after a `[model_providers.*]` table it silently becomes a
  table key, codex then disables reasoning and xAI 400s "Reasoning is mandatory"; an
  earlier BLOCKED verdict here was exactly this TOML-placement error. (2) `codex exec`
  under a non-TTY needs `</dev/null` or it waits on "Reading additional input from
  stdin". Incidental: the file task emitted the same naive unguarded chunk loop — third
  harness, same edge-blindness ([[finding-openrouter-grok-p2-2026-08-25]]).
- **Claude Code: WORKS, verified empirically 2026-08-25** — no proxy needed: OpenRouter
  exposes an Anthropic-compatible `/api/v1/messages` (verified by raw curl first). Recipe:
  `ANTHROPIC_BASE_URL="https://openrouter.ai/api" ANTHROPIC_AUTH_TOKEN=$OPENROUTER_API_KEY
  ANTHROPIC_MODEL="x-ai/grok-4.6" claude -p ...` (isolated `CLAUDE_CONFIG_DIR` for tests).
  Chat AND tool use both clean: headless file-write task wrote a working `chunk.js`
  (executed, correct). Caveats: unrecognized-model warning caps assumed context at 200k
  (map it in `modelOverrides` or set `CLAUDE_CODE_MAX_CONTEXT_TOKENS` to fix); metered
  OpenRouter billing; and the emitted chunk was AGAIN the naive unguarded loop — fourth
  harness, same edge-blindness.
- **SuperGrok subscription transfers to NONE of these** — OAuth consumer login, not an
  API key; every non-CLI path is separately metered.
