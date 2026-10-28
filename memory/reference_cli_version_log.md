---
name: reference-cli-version-log
description: "Dated one-line CLI upgrade notes — housekeeping only, not bench findings. Canonical routing stamp: ~/.cursor/rulebook/memory/reference_subordinate_routing_map.md (mirror ~/.claude/memory/ for Obsidian sync until sync script retargets)."
metadata:
  node_type: memory
  type: reference
---

# CLI version log

Append-only. Each line is `--version` unless noted. Route-to table changes only when a finding says so.

## After a fleet / CLI upgrade (Cursor migration)

Edit in **`~/.cursor/rulebook/memory/`** in this order:

1. `reference_subordinate_routing_map.md` — VERSION STAMP (patch/minor: §2 route-to usually unchanged).
2. This file — append a table row.
3. Each touched `workflow_<tool>_subordinate.md` — `CLI VERSION` line.
4. Recompile lab repo `.claude/skills/delegation-routing` + `build-and-env` (or your compile script).
5. Mirror changed files to `~/.claude/memory/` if `sync-to-obsidian.sh` still sources there.
6. Optional on material bumps: `python3 ~/.claude/lib/dispatch.py … --pong`.

| Date | Component | Change | Notes |
|---|---|---|---|
| 2026-10-28 | codex | 0.164.0 → **0.165.0** | MINOR; UNVERIFIED on 0.165.x |
| 2026-10-28 | opencode | 2.1.4 → **2.2.0** | MINOR; UNVERIFIED on 2.2.x |
| 2026-10-28 | agy | 1.4.7 → **1.4.9** | patch (via 1.4.8); UNVERIFIED on 1.4.x |
| 2026-10-28 | Claude Code (native) | 2.1.311 → **2.1.312** | not a routing-map subordinate |
| 2026-10-28 | grok / uv / node | unchanged | 1.0.70 / 0.13.6 / 26.12.1 |
| 2026-10-28 | npm (global) | vercel **65.5.0**; `npm update -g` | not subordinates |
| 2026-10-28 | brew | cmake, openjdk@17/@21/@25, simdjson, simdutf, ollama-app | not subordinates |
| 2026-10-27 | uv | 0.13.5 → **0.13.6** | not a subordinate |
| 2026-10-27 | Claude Code (native) | 2.1.310 → **2.1.311** | not a routing-map subordinate |
| 2026-10-27 | codex / grok / opencode / agy | unchanged | already latest |
| 2026-10-27 | npm (global) | `npm update -g`; vercel **65.3.1** | not subordinates |
| 2026-10-27 | brew | gh 2.103.3, python@3.14 3.14.10 | not subordinates |
| 2026-10-26 | fleet (subordinates) | unchanged | codex 0.164.0, grok 1.0.70, opencode 2.1.4, agy 1.4.7, uv 0.13.5 |
| 2026-10-26 | npm (global) | `npm update -g`; npm **12.2.1** after node bottle reset | not subordinates |
| 2026-10-26 | brew | node 26.12.1_1, openssl@4 4.1.0, harfbuzz, icu4c@78, simdutf, tesseract, z3 | not subordinates |
| 2026-10-25 | grok | 1.0.67 → **1.0.70** | patch; UNVERIFIED on 1.0.70 |
| 2026-10-25 | agy | 1.4.6 → **1.4.7** | stamp catch-up; already on disk |
| 2026-10-25 | Claude Code (native) | 2.1.309 → **2.1.310** | not a routing-map subordinate |
| 2026-10-25 | codex / opencode / uv / node | unchanged | 0.164.0 / 2.1.4 / 0.13.5 / 26.12.1 |
| 2026-10-25 | npm (global) | `npm update -g` | not subordinates |
| 2026-10-25 | brew | gh 2.103.2, openjdk 27.0.1.0.3, ollama-app 0.40.11 | not subordinates |
| 2026-10-23 | codex | 0.163.0 → **0.164.0** | MINOR; UNVERIFIED on 0.164.x |
| 2026-10-23 | opencode | 2.1.2 → **2.1.4** | patch (via 2.1.3); UNVERIFIED on 2.1.x |
| 2026-10-23 | agy | 1.4.5 → **1.4.6** | patch; UNVERIFIED on 1.4.x |
| 2026-10-23 | Claude Code (native) | 2.1.308 → **2.1.309** | not a routing-map subordinate |
| 2026-10-23 | cursor-agent | → **2026.10.22-27dcf5f** | already latest this pass |
| 2026-10-23 | npm (global) | mcpvault 0.17.1; vercel 65.2.0 | not subordinates |
| 2026-10-23 | brew | harfbuzz 15, openjdk 27.0.1, ollama-app 0.40.9 | not subordinates |
| 2026-10-23 | grok / uv / node | unchanged | 1.0.67 / 0.13.5 / 26.12.1 |
| 2026-10-22 | Claude Code (native) | 2.1.302 → **2.1.308** | security-priority; not a routing-map subordinate; past recent Claude Code CVEs |
| 2026-10-22 | agy | 1.4.3 → **1.4.5** | patch (via 1.4.4); UNVERIFIED on 1.4.x |
| 2026-10-22 | grok | 1.0.62 → **1.0.67** | patch; UNVERIFIED on 1.0.67 |
| 2026-10-22 | uv | 0.13.4 → **0.13.5** | not a subordinate |
| 2026-10-22 | opencode / codex | unchanged | 2.1.2 / 0.163.0 already latest |
| 2026-10-22 | npm (global) | npm 12.2.1; firebase-tools 15.34.1 | node brew bump had reset npm to 11.20.0 |
| 2026-10-22 | brew | gh 2.103.0, node 26.12.1, llvm, brotli, ollama-app, python@3.14 | not subordinates |
| 2026-10-22 | supply-chain check | clean | no tensorlake@0.5.144, no LiteLLM 1.107.0, no Gemini CLI |
| 2026-10-21 | opencode | 2.0.32 → **2.1.2** | MINOR; UNVERIFIED on 2.1.x |
| 2026-10-21 | agy | 1.4.2 → **1.4.3** | patch; stamp catch-up |
| 2026-10-21 | uv | 0.13.1 → **0.13.4** | not a subordinate |
| 2026-10-21 | codex / grok | unchanged | already latest |
| 2026-10-21 | npm (global) | `npm update -g` | not subordinates |
| 2026-10-21 | brew | openjdk@17/21, gh, ollama-app, ca-certificates, … | not subordinates |
| 2026-10-19 | agy | 1.4.0 → **1.4.2** | patch; stamp catch-up; UNVERIFIED on 1.4.x |
| 2026-10-19 | codex / grok / opencode / uv | unchanged | upgrade pass already latest |
| 2026-10-19 | npm (global) | `npm update -g` | not subordinates |
| 2026-10-19 | brew | sqlite, z3, coreutils, simdutf, libunistring, pkgconf, libx11, libxrender, ollama-app | not subordinates |
| 2026-10-17 | grok | 1.0.60 → **1.0.62** | patch via `grok update`; UNVERIFIED on 1.0.62 |
| 2026-10-17 | opencode | 2.0.30 → **2.0.32** | patch; 2.0.x UNVERIFIED |
| 2026-10-17 | agy | 1.3.6 → **1.4.0** | MINOR; UNVERIFIED on 1.4.x |
| 2026-10-17 | codex / uv | unchanged | already 0.163.0 / 0.13.1 |
| 2026-10-17 | npm (global) | `npm update -g` | not subordinates |
| 2026-10-17 | brew | z3, llvm, llama.cpp, hdrhistogram_c | not subordinates |
| 2026-10-15 | fleet (upgrade pass) | unchanged | subordinates already latest; `npm update -g`; brew simdjson 5.0.4→**5.0.5** |
| 2026-10-15 | opencode | 2.0.28 → **2.0.29** | patch; 2.0.x UNVERIFIED |
| 2026-10-15 | agy | 1.3.3 → **1.3.5** | patch; UNVERIFIED on 1.3.x |
| 2026-10-15 | uv | 0.13.0 → **0.13.1** | not a subordinate |
| 2026-10-14 | opencode | 2.0.27 → **2.0.28** | patch via `opencode upgrade`; 2.0.x scores still UNVERIFIED |
| 2026-10-14 | codex / grok / agy / uv | unchanged | already latest |
| 2026-10-14 | npm (global) | `npm update -g` | not subordinates |
| 2026-10-14 | brew | openssl@3 3.6.5 → **3.5.9** | bottle downgrade pin; not a subordinate |
| 2026-10-13 | grok | 1.0.50 → **1.0.52** | patch via `grok update`; claims UNVERIFIED on 1.0.52; restart Grok |
| 2026-10-13 | codex / agy / opencode / uv | unchanged | already latest after `codex update`, `uv self update`, `opencode upgrade` |
| 2026-10-13 | npm (global) | `npm update -g` | 1048 packages touched; not subordinates |
| 2026-10-13 | brew | simdjson 5.0.3 → **5.0.4** | not a subordinate |
| 2026-10-12 | agy | 1.3.2 → **1.3.3** | patch; 3.8 pins unchanged; UNVERIFIED on 1.3.x |
| 2026-10-12 | opencode | 2.0.26 → **2.0.27** | patch; first `opencode upgrade` failed, retry OK |
| 2026-10-12 | grok | 1.0.50 | unchanged |
| 2026-10-12 | uv | 0.12.24 → **0.13.0** | not a subordinate |
| 2026-10-11 | codex | 0.162.0 → **0.162.1** | patch via `codex update`; `dispatch.py --pong` luna + 6.1-sol PASS |
| 2026-10-09 | agy catalog | Gemini Flash → **3.8 only** | pins → `gemini-3.8-flash-{low,medium,high}`; [[finding-agy-flash-38-only-catalog-2026-10-09]] |
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
