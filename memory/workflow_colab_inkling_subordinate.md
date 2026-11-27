---
name: workflow-colab-inkling-subordinate
description: "Playbook for Colab CLI + Inkling 2 Mini Q3 GGUF (Unsloth llama-server) as an optional single-file implementer — not dispatch.py, not NIM thinkingmachines/inkling (410 EOL). Owner-routed only; burns Colab compute units."
metadata:
  node_type: memory
  type: workflow
---

# Colab CLI + Inkling 2 Mini (Q3 GGUF)

> ⛔ **Not the same as NIM `thinkingmachines/inkling`** — that API id is **410 EOL** (`reference_nim_via_opencode.md`). This workflow is a **Colab VM** running Unsloth **Inkling 2 Mini** Q3 GGUF behind `llama-server` on **127.0.0.1** (loopback).

> 📌 **CLI (2026-11-27):** `colab` at `~/.local/bin/colab` (**0.8.0** observed). Skill: `colab-operator` (`~/.cursor/skills/colab-operator/SKILL.md`).

> **Naming:** Server `--alias` / API model id is `inkling-2.5-mini`; weights are still **Inkling 2 Mini** GGUF from Unsloth.

## When to use

- Owner asks for **Inkling on Colab**, or a session is **already up** and pinged.
- **Single-file Python or TypeScript** with a **tight spec** and edges named (other languages: **unmeasured** — not this lane).
- You **apply** the returned diff and **run tests yourself** — Inkling output is a claim (R0).

**Not routed:** review gates, multi-file agentic work, unstated edges, harness authorship, anything when server/session is down (fail closed).

## Routing basis

**UNMEASURED as configured** (Q3, Unsloth fork, T4, 8k context). Nearest evidence: **Inkling 2 Mini GGUF Q8** on A100, N=12, **0.917** → pre-registered **TIE** with Colab Flash-Next NVFP4 — Python + TypeScript tasks only — see routing map §2c and `finding-flashnext-vs-27bfp8-coding-2026-11-22`. **OWNER ORDER 2026-11-27:** optional lane, not measured superiority.

## Provision (explicit go — spends CU)

Default session: **`inkling-25mini`**, GPU **`T4`**. **`colab new` only runs when `INKLING_ALLOW_NEW=1`.**

```bash
INKLING_ALLOW_NEW=1 ~/.cursor/rulebook/scripts/colab_put_inkling_25_mini.sh
```

Do **not** rely on raw `colab exec` exit codes (CLI 0.8.0 returns 0 on VM `SystemExit`). Always use **`colab_put_inkling_25_mini.sh`** (sentinel greps) unless you replicate the same checks.

Cold start: llama.cpp tarball + GGUF download — **15–25 min** on a fresh VM when binaries and weights are absent; **~2 min** when the Q3 GGUF and pinned tarball are already on disk (observed 2026-11-27, T4). Use `colab exec --timeout 0` for the start script (default CLI timeout is too short).

VM env overrides (**not** forwarded from local shell by the bash wrappers — use `colab exec --env KEY=VALUE` if needed): `INKLING_BASE_URL`, `INKLING_MODEL`, `INKLING_MAX_COMPLETION`, `INKLING_CTX`, `INKLING_LLAMA_TAG`. Legacy `ELKO_INKLING_*` on the start script aliases the same knobs where noted in source.

## Coding packet

1. Write a spec markdown (task, acceptance, one output format: plan + one fence).
2. Run:

```bash
~/.cursor/rulebook/scripts/colab_inkling_code_help.sh -f /path/to/spec.md
```

3. Read the printed path; extract diff; apply; run project tests.

`max_tokens` on the VM is capped under server **8192** context (`INKLING_MAX_COMPLETION` default 6144).

## Teardown

```bash
colab stop -s inkling-25mini
```

Idle VMs burn compute units.

## Scripts (tracked in rulebook repo)

| File | Role |
|------|------|
| `scripts/colab_put_inkling_25_mini.sh` | list session / optional new + start + ping |
| `scripts/colab_vm_start_inkling_25_mini.py` | VM: Unsloth llama-server + GGUF |
| `scripts/colab_vm_ping_inkling.py` | VM: health check (`content` + `finish_reason=stop`) |
| `scripts/colab_vm_inkling_code_help.py` | VM: spec → completion |
| `scripts/colab_inkling_code_help.sh` | Local: upload / exec / download |

Paths: **`~/.cursor/rulebook/`** (`firaen22/claude-rulebook`); mirror to `~/.claude/` when syncing.

## Gate sentinels (not `colab exec` exit codes)

**Verified 2026-11-27:** `colab exec` (CLI **0.8.0**) returns **0** even when the VM script raises `SystemExit` or tracebacks — only timeouts and dead connections exit non-zero. Wrappers therefore **`grep` stdout** for:

- Start: line beginning with `READY`
- Ping: exact lines `inkling-ok` **and** `INKLING_PING_OK` (reply must be exactly `inkling-ok`, not a substring)
- Code help: exact line `INKLING_CODE_HELP_OK:<request_id>` matching the upload (one packet per session via `flock`)

Specs are scanned locally with **`dispatch.scan_secrets`** before upload; **`lib/dispatch.py` must exist** (wrapper refuses otherwise).