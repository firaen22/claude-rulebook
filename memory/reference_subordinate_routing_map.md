---
name: reference-subordinate-routing-map
description: "Which of the 5 subordinates (codex / agy / grok / opencode / NIM) to route a task to, and why. Canonical path (Cursor migration): ~/.cursor/rulebook/memory/reference_subordinate_routing_map.md — mirror here for Obsidian sync until sync script retargets. Spine: 7 same-task-set comparisons exist across the fleet (7th added 2026-08-25) — this file separates those from reasoned defaults. THE cross-fleet rule: no tier is safe on unstated edges, and no tier's self-report is evidence."
metadata:
  node_type: memory
  type: reference
---

# Subordinate routing map — 2026-10-21

Per-tool operating detail lives in the playbooks; this file is ROUTING only.
[[workflow-codex-subordinate]] [[workflow-agy-subordinate]] [[workflow-grok-subordinate]]
[[workflow-opencode-subordinate]] [[workflow-splash-qwen]] [[reference-nim-via-opencode]]
[[workflow-cursor-subordinate]]

> 📌 **VERSION STAMP — binaries checked 2026-10-21 via each `--version` (no `dispatch.py --pong` this pass):**
> `grok 1.0.62 (1474f9cbdd91)` · `codex-cli 0.163.0` · `opencode 2.1.2` · `agy 1.4.3`.
> (2026-10-21: §2 route-to rows unchanged — no re-bench. opencode 2.0.32→**2.1.2** via `opencode upgrade` — **MINOR** within 2.x; opencode/NIM scores **UNVERIFIED on 2.1.x** (still UNVERIFIED on 2.0.x). agy **1.4.2→1.4.3** stamp catch-up (patch-only). uv 0.13.1→0.13.4; codex/grok unchanged; `npm update -g` refresh; brew openjdk@17/21, gh, ollama-app, ca-certificates, etc. 2026-10-19: §2 route-to rows unchanged — no re-bench. Upgrade pass: codex/grok/opencode/uv already latest; agy **1.4.0→1.4.2** stamp catch-up (patch-only, **UNVERIFIED on 1.4.x**). `npm update -g` refresh; brew sqlite/z3/coreutils/simdutf/libunistring/pkgconf/libx11/libxrender/ollama-app. 2026-10-17: §2 route-to rows unchanged — no re-bench. grok 1.0.60→1.0.62 via `grok update` — patch-only; **UNVERIFIED on 1.0.62**. opencode 2.0.30→2.0.32 via `opencode upgrade` — patch-only. agy **1.3.6→1.4.0** — **MINOR**; agy route scores **UNVERIFIED on 1.4.x**. codex/uv unchanged; `npm update -g` refresh; brew z3/llvm/llama.cpp/hdrhistogram_c; cursor-agent **2026.10.16-e3cb207**. 2026-10-16: §2 route-to rows unchanged — no re-bench. codex 0.162.1→0.163.0 — **MINOR** bump; codex rc/ceiling claims stay **UNVERIFIED on 0.163.x**. grok 1.0.52→1.0.60 — patch-only; grok rc/edge/schema claims stay **UNVERIFIED on 1.0.60**. agy 1.3.5→1.3.6, opencode 2.0.29→2.0.30 — patch-only; 2.0.x scores stay **UNVERIFIED**. cursor-agent/uv unchanged; brew node 26.12.0, ggml 0.27.0, ollama-app; npm global vercel 64.3.1 (node upgrade reset bundled npm to 11.20.0 → reinstalled 12.2.0). 2026-10-15 late: upgrade pass — subordinates already at stamp versions; `npm update -g` refresh; brew **simdjson** 5.0.4→5.0.5. 2026-10-15: §2 route-to rows unchanged — no re-bench. opencode 2.0.28→2.0.29 via `opencode upgrade` — patch-only; 2.0.x scores stay **UNVERIFIED**. agy 1.3.3→1.3.5 (stamp catch-up; patch-only). codex/grok/cursor-agent unchanged; uv 0.13.0→0.13.1; npm 11.20.0→12.2.0; node/simdutf et al. via brew (simdutf bump broke node until `brew upgrade node`). 2026-10-14: §2 route-to rows unchanged — no re-bench. opencode 2.0.27→2.0.28 via `opencode upgrade` — patch-only; 2.0.x scores still **UNVERIFIED**. codex/grok/agy/uv unchanged; `npm update -g` refreshed globals; brew openssl@3 3.6.5→3.5.9 (bottle pin). cursor-agent self-update ran. 2026-10-13: §2 route-to rows unchanged — no re-bench. grok 1.0.50→1.0.52 via `grok update` — patch-only; grok rc/edge/schema claims stay **UNVERIFIED on 1.0.52** (was UNVERIFIED on 1.0.50). codex/agy/opencode/uv unchanged (`codex update`, `uv self update`, `opencode upgrade` already latest; first opencode check hit 503). npm global `npm update -g` refreshed packages; brew upgraded simdjson only. 2026-10-12: §2 route-to rows unchanged — no re-bench. codex 0.162.0→0.162.1, agy 1.3.2→1.3.3, opencode 2.0.26→2.0.27 — all patch-only (opencode first upgrade failed, retry OK); grok unchanged. **Edit stamp in `~/.cursor/rulebook/memory/` first** (post-migration canonical); mirror this file under `~/.claude/memory/` for `sync-to-obsidian.sh`. `dispatch.py` stays at `~/.claude/lib/` — if missing, re-clone `firaen22/claude-rulebook`. Housekeeping checklist: `reference_cli_version_log.md`. 2026-10-09: codex 0.161.0→0.162.0 — **MINOR** bump; codex rc/ceiling claims stay **UNVERIFIED on 0.162.x** (was UNVERIFIED on 0.160.x/0.161.x). grok 1.0.46→1.0.50 — patch-only; grok rc/edge/schema claims stay **UNVERIFIED on 1.0.50** (was UNVERIFIED on 1.0.41+). agy 1.3.1→1.3.2 — patch-only. opencode 2.0.24→2.0.26 — patch-only (first upgrade attempt failed, retry OK). **2026-10-09 late — agy Gemini Flash catalog:** owner intel + routing update — **only 3.8 Flash remains**; §2 agy model IDs moved to `gemini-3.8-flash-{low,medium,high}`; all 3.6/3.7 numbers below are **historical on retired IDs** until re-bench → [[finding-agy-flash-38-only-catalog-2026-10-09]]. 2026-10-07: agy 1.2.17→1.3.0 — MINOR; opencode 2.0.22→2.0.24 patch; codex 0.160.0→0.160.1 patch; grok unchanged. 2026-10-05 late: all five + TypeSafe `jev-1.13.0` passed `dispatch.py --pong` / one-call probe. Claims stay flagged against the minor versions below.)
> Every rc / ceiling / bug-status claim in this file and the linked playbooks is
> **VERSION-BOUND**. codex jumped another minor version since the last stamp
> (0.157.0→0.159.2, upgraded 2026-09-30 via `codex update`; standalone install, not brew/npm) — agy
> moved patch-only (1.2.12→1.2.13), grok/opencode unchanged. **opencode jumped a MAJOR version (1.18.31→2.0.18):** `run --dir` is gone
> (dispatch.py fixed: subprocess `cwd=` + `--standalone`), and default mode talks to a shared
> background service where a timeout-killed client's run keeps going server-side (verified
> 2026-09-27) — `--standalone` contains it. Every opencode/NIM rc/pin/parallelism/free-pool
> score below was measured on 1.x and is **UNVERIFIED on 2.0.x / 2.1.x** (installed 2.1.2 as of 2026-10-21) until re-benched; the
> opencode default model moved to `nvidia/nvidia/nemotron-3-ultra-550b-a55b` (gpt-oss-120b 410 EOL).
> Every codex rc/ceiling/bug-status claim below (the ~30KB inline-review
> ceiling §2a, `gpt-5.6-luna` default behavior, the astra-vs-luna E4 scale finding) was
> measured on 0.153.4 and is **UNVERIFIED on 0.162.x** (0.160.x/0.161.x included) until re-run — treat codex
> findings from this point forward as provisional pending a re-bench. Every agy
> rc/pin/edge claim below on **3.6/3.7 Flash IDs** was measured through 1.3.x and is
> **historical** — operational pins are **3.8 Flash** (2026-10-09 catalog regime;
> [[finding-agy-flash-38-only-catalog-2026-10-09]]). The empty-return-is-permission-deny
> finding is process, not model-ID-specific. **No 3.8 Flash route number is current** until
> re-bench. Every grok rc/edge/schema
> claim below was measured on 1.0.13 and remains **UNVERIFIED on 1.0.52** (was UNVERIFIED on 1.0.41+/1.0.50;
> no re-bench). **Re-run `--version` before trusting a number.**

## 0. Two rules that override every row below

**R-A — No tier defends unstated edges. Spec them, always.** This is the only property
measured on all five and it fails on all five: codex drifty (sol/terra 0/2 on `chunk(arr,0)`
→ family 36/36 twelve days later, same model strings); agy K1 FALSE at every tier both years
(1/5, 0/5, 2/5 at 3.6; 3/5, 0/5, 0/5 at 3.7, N=315 combined); grok 0/16 deterministic, same
naive loop every run; free pool — ⛔ **the two standing exceptions are RETRACTED 2026-08-28**:
on a one-build N=2x4x6 re-bench `muse-spark-1.2-contributor-free` fell 2/2 → **1/2** and
`nemotron-3-ultra-free` holds **1/2**, and by this file's own standing rule (guards it one rep
and not the next ⇒ not an edge-guarding model) **the free pool now has ZERO reliable edge
defenders — best in pool is 1/2**. [[finding-zen-pool-rebench-2026-08-28]]. Spelling the edge
out costs one line and grok then guards 11/11.
**Corollary: the "spec the edges" rule has been over-generalized and retracted TWICE**
(08-04, 08-15) — say "no tier is reliable", never "no model can".
**R-A stands as of 2026-08-28, and is now UNCONDITIONAL for the free pool** (above).
Partial exception (historical ID): `agy 3.7-flash-low` at 15/20 — best
NON-FREE edge behavior measured on any tier **on 3.7-low**; operational unstated-edge pick is
`gemini-3.8-flash-low` (**UNVERIFIED** — Sept 2025 partial bench had 3.8-low 14/20 vs 3.7-low 12/20,
p=0.74). Still below the K1 ≥4/5-per-paraphrase bar
(P1_terse 1/4 even for `-low` — [[workflow-agy-subordinate]]), exempts nothing. Measurement rule: **never
compare an edge-guard number against a prior measured on a different prompt phrasing**
(`-medium`, same model, same day: 9/10 on a new phrasing vs 4/20 on the frozen set,
p=0.0004 — those numbers are -medium's, NOT -low's) — same-instrument
or no comparison. Numbers: [[finding-geminimd-and-fleet-probe-2026-08-25]] Result 5.

**R-B — No tier's self-report is evidence. Grade on disk.** grok returned schema-valid
`{file_created: true}` with `num_turns:1` and zero tool calls (3/10); opencode agents narrate
a file and write nothing; agy fabricates claims about files not inlined in the packet; codex
quota exhaustion surfaces as a silent `no-change`, not an error. Read the file back.
**The REVIEW-side corollary (2026-08-27): a reviewer's all-clear is a self-report too.**
grok returned a schema-valid `findings: []` / all-claims-survived verdict on a diff carrying
a defect that two independent lenses (Claude + codex) found and reproduced the same hour.
A clean review verdict counts only when a second lens agrees or you reproduce the pass —
same rule as a green test count, [[finding-test-validity-failure-modes]].
**The MIRROR corollary (2026-08-27): grade your grader before you grade the tier.** A harness
that validated the response ENVELOPE instead of `.structuredOutput` logged grok at 0/16 schema
adherence — a "catastrophic model failure" that regraded to 16/16 once the parser was fixed.
Before recording any tier's catastrophic score, re-parse one raw response by hand;
a 0/N is far more often your instrument than the model, [[finding-schema-battery-parser-2026-08-27]].

**R-C — Deliverable-is-a-scanner ⇒ the dispatch must require executing it.** Measured on
codex only (2026-08-24, decisive force-load probe): dominant failure 5/18 runs shipped a
scanner whose scan never executes, FLAT across every rule/skill configuration — ambient
doctrine (skills, AGENTS.md prose) did not move it. The countermeasure is in the acceptance
criteria: run the deliverable on one known-positive + one known-negative input, both outputs
in the report (now baked into `30-delegation-templates.md` universal rules). Extension to
the other four tiers is REASONED, not measured — but it composes with R-B, so it costs
nothing to require. Red-test corollary: injected failures must be reachable; a failing line
after `exit` reports green.

**R-D — A read-only BRIEF is not a control, and the flag that looks like one fails
open.** grok holds `write`/`search_replace`/`run_terminal_command` and, under
`--always-approve`, wrote OUTSIDE its `--cwd` on first ask in 5/5 uncontained configs
(2026-08-27). An isolated cwd is a default directory, not a boundary. `--disallowed-tools`
did not bite; neither `--sandbox` name tried confined it. **Only the positive `--tools`
allowlist worked (2/2) — and ONE unrecognised name in that list silently voids the whole
allowlist and restores write+shell, rc=0, no warning.** The verified-working list, copy it
verbatim and never retype from memory: **`--tools read_file,grep,list_dir`** (re-verified
2026-08-28: contained, 15KB review delivered, post-run dir diff clean). Under it grok has no
write tool, so ask for findings on **stdout** — a recipe that asks for `FINDINGS.md` is
telling you it is uncontained. Confirm containment the R-D way, by diffing the work dir
afterwards; never by having read the flag. Adjacent flags fail in opposite
directions: `--sandbox` refuses to start on a bad name, `--tools` fails open on one. This
is the fleet-wide "read-only instruction is not a control" lesson (`delegation-and-review/SKILL.md` — "Classify an agent by the TOOLS IT HOLDS, never by what its brief asks for", :429 at the 2026-08-29 re-grep)
landing on a THIRD tier — verify the boundary by attempting an escape, never by reading the
flag name. [[workflow-grok-subordinate]] §CONTAINMENT.

## 1. The FIRST routing question: WHETHER vs WHAT

The sharpest measured separation in the whole corpus, and it is not about capability.
On N=12 probes containing an insecure pattern (API key → localStorage), **only codex and
Opus refused; every free model complied blindly.** Execution parity is real; judgment parity
is not.

> **Delegate the WHAT, never the WHETHER.** "Is this sound / safe / the right approach?"
> → codex or Opus. "Build this specified thing" → cheapest tier that clears the bar.

## 2. Route-to table

> **Cross-family REVIEW dispatches are gated by the `cross-model-review` skill — load
> it before using any row below.** This table picks the reviewer; the skill owns the
> packet, the exit-0≠verdict check, and the merge condition. A 2026-09-02 sampled
> transcript pass found genuine review occasions where a reviewer bullet/row here
> fired the dispatch and the skill never loaded — including the literal ask "review
> with codex and grok" (2026-08-25). Exact hit/miss counts are unverified (sample,
> not exhaustive) — see [[finding-cross-model-review-trigger-2026-09-02]].

| Task | Route to | Basis |
|---|---|---|
| "Should we?" / safety / soundness / accepting a design | **codex** (or Opus) | MEASURED N=12, only tier that refuses |
| Airtight-spec implementation, single file | **free pool** — `muse-spark-1.3-contributor-free` **=** `nemotron-3-ultra-free` (09-23 ×2 on 1.18.31: 10/10, 9/10; 2026-10-15 on 2.0.29: 9/10 edge 1/2; 1.2 delisted 2026-10-15) → `big-pickle` = `hy3-free` = `mimo-v2.5-free` (8/10). ⛔ `nemotron-3.5-lightning-free` is **NOT SERVING** (hangs 90s rc=124, and is STILL LISTED — listing is not liveness) | MEASURED — Zen whole-pool re-bench 2026-08-28, N=2x4x6 on ONE build, [[finding-zen-pool-rebench-2026-08-28]]. Supersedes the 08-21/08-23 order: muse-spark's debut 10/10 did NOT hold. **Re-list before every chain run — the pool churns within hours, and a `-free` id and its bare twin are different products.** (The N=57 battery is the NIM direct-curl line, not these Zen ids) |
| Tight-spec pure function, no file edit needed | **NIM direct curl** | fan-out at 40rpm×3 keys; opencode wrapper is ~6/min. ⚠️ **2026-10-16:** NIM parity re-check VOID — both fixed controls are HTTP 410 (`deepseek-ai/deepseek-v4-pro` EOL 08-07, `openai/gpt-oss-120b` EOL 09-03), and `nimroute.py` still has 410 `mistral-nemotron` as PARITY[0]/FAST (`nimroute.py:97,134`; owner fix pending). Unbanded liveness: `nemotron-3-super-120b-a12b` strict 30/30 ×2; `laguna-xs-2.1` 30/30 then 20/30 (transport flake); `nemotron-3-ultra-550b-a55b` empty content ×2 → `claude-code-technique/experiments/sub-rebench-2026-10-16/RESULT.md` |
| Same, but needs the file actually edited | **opencode** (only free tier with an agent layer) | 4/4 clean on simple single-file |
| Enumerating ambiguities in a spec BEFORE building | **codex as spec-reviewer** | MEASURED N=1016; run this pass first. Model slug unmeasured astra-vs-luna here — the R1 "not luna for review" line (§3) does NOT apply to spec review |
| Adversarial edge-hunting, PRE-implementation | **agy** `gemini-3.8-flash-medium` | **historical on 3.7-medium:** 24/24 recall, 0/32 fabrication w/ escape clause — **UNVERIFIED on 3.8** |
| **IF** agy reviews a large real-repo packet (e.g. as an extra lens), which agy model | **agy** `gemini-3.8-flash-medium` (review pin, 2026-10-16) + no-tool preamble + wall ≥ 300 s | **MEASURED 2026-10-16 on agy 1.4.0** (N=8 per arm, one window): medium 1/8 dead at 240 s, 0/8 at 600 s; high 3/8 at 240 s, 2/8 at 600 s → high not used for review. Recall not ranked at N=8 → [[finding-agy-38-rebench-and-dead-cell-diag-2026-10-16]]. Historical: 3.6-high N=30 sweeps. This row picks the agy MODEL; whether agy reviews post-impl at all is the "NOT agy" row below (reworded 2026-09-06 to remove the apparent conflict both cross-model reviewers flagged) |
| Structured/JSON-schema fan-out, N verdicts parsed | **grok** | 16/16 (08-23 regraded) + 15/16 (08-27 fresh) adherence + free cost telemetry (SINGLE-ARM). **Re-measured 2026-10-16 (grok 1.0.60): `grok-4.7` 16/16 valid, 0 null `structuredOutput` (4.6 same window 16/16)** → `claude-code-technique/experiments/sub-rebench-2026-10-16/RESULT.md`. Read `.structuredOutput` from the WHOLE buffer; a null `structuredOutput` is a failed rep — drop it, never rescue from `.text` |
| Third review lens after codex (diff/rules-file review) | **grok — pick the shape by the MATERIAL: reviewing FILES ⇒ STAGE them in `--cwd` and tell it to read them (🔴 never inline a review target); judgement on already-inline material ⇒ keep it inline + `--json-schema`. Isolated HOME either way** | ⛔ the "always inline" form of this row is RETRACTED 2026-08-28. Three INLINED-code review packets gave schema-valid-empty / 0 bytes / narration; attempt 4 on the staged-files recipe gave 5.4KB, 5 findings, 3 real. The 0/3 "idle" was MY packet error — grok was hunting for files never written. [[finding-misroutewatch-grok-review-2026-08-28]]. Its finds are real; its all-clears are void (R-B corollary) |
| Second reviewer AFTER codex on the same artifact | **grok on the staged-files recipe — they are COMPLEMENTARY, not redundant** | MEASURED 2026-08-28, byte-identical brief + same pre-fix file: **zero overlap on 3 real defects.** codex finds mechanism/contract bugs via contrived inputs; grok finds the realistic corpus path that actually fires them. codex missed both of grok's; grok missed codex's. n=1 file, 2 reviewers. Neither alone was sufficient |
| Ordinary spec'd implementation, want to spare codex quota | **free pool first** (`muse-spark-1.3-contributor-free`; 1.2 delisted 2026-10-15), grok if the free pool is unavailable | MEASURED 08-23 same-window five-way: free 10/10 > grok-default 9/10 > grok-isolated/NIM/big-pickle 8/10. ⚠️ **The 10/10 is retracted** (08-28 re-bench: 9/10, edge 1/2) — the ROUTING order survives, the margin does not. **2026-10-16 re-run of the 08-23 harness VOID:** its opencode control calls `opencode run --dir`, which opencode 2.0.x dropped (control 0/10, rc 1). grok 4.7 scored 8/10 (P2 edge 0/2) but is unbanded; grok rows from this harness are UNMEASURED on current CLIs until the control argv is fixed → `claude-code-technique/experiments/sub-rebench-2026-10-16/RESULT.md` |
| **Live X / social retrieval** (what was posted, by whom, when) | **grok — the only tier with it** | NEW 2026-08-27. Native `x_keyword_search`/`x_semantic_search`/`x_user_search`/`x_thread_fetch`; keyword search VERIFIED live against a known account. On by default, survives `--disable-web-search`. A RETRIEVAL lane only — it does nothing for grok's judgement weaknesses. 🔴 Cannot be run contained (see R-D) |
| Anything with a loop / iteration / termination edge | codex or agy — or grok WITH the edge stated | PROVISIONAL, n=3, p=0.17 pooled |
| Same, but the edge CANNOT be stated (unstated-edge exposure is the risk) | **agy `gemini-3.8-flash-low`** — then verify by execution regardless | **historical on 3.7-low:** 15/20 fresh-day repeat; `-medium` 4/20 same day. NOT safe, just least-bad — **UNVERIFIED on 3.8-low** |
| Post-implementation code review on a real repo | **NOT agy** | adoption 0/5, 0/5, 1/5, 3/8 across 4 sweeps. Scope note 2026-08-25: on a SMALL single-file seeded-defect review, codex and agy TIED 8/8 vs 8/8 (saturated instrument) — this row does not generalize down to small single-file review, stays scoped to large real-repo packets → [[finding-step4-seeded-review-2026-08-25]] |
| Pre-commit / post-impl review of SMALL code with unstated hazards (the R1 shape) | **codex `-m gpt-6.1-sol -c model_reasoning_effort=medium` WITH the astra pack prefixed** (pack text, then `\n\n---\n\n`, then the brief — recipe in `workflow_codex_subordinate.md`; default since 2026-09-30). Alternate: `-m gpt-5.6-luna` medium + pack (sol quota-blocked, or a second pass when a miss is catastrophic). Not bare luna (held-out r2 4/15). **JS only** — other languages unmeasured: there use `gpt-6.1-sol` medium. ⛔ `gpt-6-astra` only on the owner's explicit command for that task (owner 2026-09-29; drains the codex limit) | Owner-approved 2026-09-25 on astra-pack bench stage 1 (N=5, PREREG D4), corrected the same day after a five-lens cross-model review + re-grade: 5.6-luna+pack r1 15/15, r2 15/15; sol+pack 15/15 on both too (the first-reported "sol no lift 12→11" was a grader keyword miss, 'nested…RangeError'). astra ran in that bench on r2 only: **tied astra on r2 only**, at the score ceiling, so "equals astra" is not shown; r1/e4 astra numbers are other benches. 0 grader-flagged fp on r2 (r1: 1 flag). PROVISIONAL: two tiny JS subjects, one held out, pack as prompt prefix only. Supersedes the 2026-09-23 sol-routine/astra-gate split. Same scope limits as before (not large real-repo packets, not spec review) → [[finding-astra-pack-stage1-2026-09-24]]. **2026-09-30 (codex 0.159.2):** review slots that named `gpt-6-sol` moved to `gpt-6.1-sol` (owner go) — bare R1 6.1 15/15 vs 6-sol 12/15; with pack (r1+r2, N=5) 6.1+pack, bare 6.1 and 6-sol+pack all 30/30 by hand (ceiling), 6.1+pack ~41 % fewer r1 tokens and ~1.6× faster than 6-sol+pack; luna+pack default and the JS scale-implementation slot NOT re-measured, unchanged → [[finding-codex-gpt61-sol-bench-2026-09-30]]. **2026-09-30 addendum 2 (owner go):** JS review default moved to `gpt-6.1-sol`+pack, luna+pack now alternate — r1+r2 N=5: 6.1+pack 30/30 vs luna+pack 28/30 (+2 = the registered bar exactly; luna misses are r1 sumTo; crediting one borderline cell would tie); ~47 % fewer r1 tokens, ~30 % slower. JS scale slot re-measured and STAYS `gpt-6-sol`+pack: 50/50 vs 6.1+pack 36/50 with 14 silent wrong (6.1 returns `Number(exact BigInt)`) → [[finding-codex-gpt61-sol-bench-2026-09-30]]. **2026-10-16 rebench (codex 0.163.0, pack `bec8c00a`; pack and CLI confounded):** JS review 6.1+pack 30/30 vs luna+pack 26/30 (+4, bar ≥ +2 held) → default re-confirmed. JS scale slot `gpt-6-sol`+pack **45/50, 5 silent wrong** (DOWN from 50/50: `sumSquares` returns `Number(exact BigInt)`) — still ahead of 6.1+pack 38/50 normalized, so it STAYS; a frozen-pack arm would attribute the drop → `claude-code-technique/experiments/sub-rebench-2026-10-16/RESULT.md` |
| Multi-file / long-horizon agentic work | **none of them — do it yourself** | UNMEASURED on all five; opencode 0 edits on 20/20 hard |
| Typed probability / choice over short text (urgency, department, yes-no with a graded P) | **TypeSafe `jev-latest`** when you need GRADED probabilities to threshold. No live NIM substitute is measured: the NIM arm was `mistralai/mistral-nemotron`, **HTTP 410 EOL since 2026-09-28** ([[reference-nim-via-opencode]]) — re-bench before routing a NIM arm | MEASURED N=100 synthetic tickets, one run/arm (2026-09-20): accuracy competitive (urg 94% vs NIM 93%), "better calibrated" claim UNSUPPORTED (ECE 0.121 vs NIM 0.046) — but Jev spreads 55 distinct probs vs NIM's 7. Not an agent, not a reviewer → [[finding-typesafe-jev-bench-2026-09-20]]. Ladder follow-up **CLOSED 2026-09-25, SUPPORTED** (corrected 09-29): Jev ranks a specified rung order better than NIM, 0.973 vs 0.775, 55 scenarios × 5 rungs × 2 runs/arm; target-informed set, ranking only (not calibration), NIM served model unverified → [[project-typesafe-ladder-2026-09-24]] |
| TypeSafe as a REVIEW lens | **don't** — scores only, never a finding source | Used in 3 multi-lens reviews (2026-09-22 ×2, 09-25): "priority corroboration only, no finding of its own"; once scored a FABRICATED control finding as P0 (no signal). Its scores count toward nothing on their own (R-B) |

### 2b. Optional local Splash cross-lens (not a route target)

**Not a sixth subordinate** — not `dispatch.py`, not for implementation. Harness artifact:
`claude-code-technique` `experiments/qwen-splash-local-2026-10-07/` on `main`.

| Task | Optional lens (not dispatch.py) | Basis |
|---|---|---|
| Harness / methods packet when Splash is already up | **Local Splash cross-lens only** — `http://127.0.0.1:8000/v1`, model `incoai/Qwen3.8-27B-Splash`; [[workflow-splash-qwen]] | MEASURED 2026-10-07: golden selftest + TypeSafe PASS validate **bench state**, not Qwen review quality. Qwen r2 printed PROCEED (R-B: void alone). **Weak lens** in that harness — missed 3 sol-found mutation defects. Require grok/codex agreement or author reproduction before acting on Qwen text; never single-source ship. Server down ⇒ fail closed → [[finding-splash-qwen-routing-2026-10-07]] |

Implementation or multi-file agentic work via Splash Qwen: **not routed** — use §2 rows
(free pool / opencode / codex / **none of them — do it yourself** for multi-file); coding
quality unmeasured.

### 2c. Optional local Strata implementer (available, not routed)

**Not a sixth subordinate**: it is not in `dispatch.py` and is never a default route. Added 2026-10-16 on the
owner's order. Harness artifact: `claude-code-technique` `experiments/strata-local-bench-2026-10-16/`.

| Task | Optional lane (not dispatch.py) | Basis |
|---|---|---|
| **Private / offline** single-file implementation with a tight spec, or a short "is this code correct?" check, when Strata is already up | **Local Strata, single-shot**: `POST http://127.0.0.1:8080/v1/chat/completions`, model `qwen3.8-flash-next-q2_0`, `reasoning_effort=medium`. Inline the seed files and ask for `FILE: name` plus a fence. You apply the files (`bench_strata.py` `apply_files`) and run the tests yourself. | MEASURED 2026-10-16: S1 P1–P4 4/4, happy 24/24, 0 stray files or protocol violations, median 25.6 s. **Effectively N=1** (greedy, byte-identical reps). Edge 0/4 and scale 16/40 = bare Composer: spec every edge and magnitude bound. ~12 tok/s, 8k context, no tools. Server down ⇒ fail closed → [[finding-strata-local-bench-2026-10-16]] |

Unstated edges, magnitude-sensitive work, multi-file or agent work, or more than ~6k tokens of context through
Strata: **not routed**. Use the §2 rows.

### 2a. Review packet SHAPE — codex and grok need OPPOSITE shapes

Measured, both directions, one task family. Getting it backwards costs a whole run and
the failure does NOT look like a packet problem — it looks like the model being useless.

| Reviewer | Shape that WORKS | What the wrong shape looks like |
|---|---|---|
| **grok** (measured on v1.0.13, now UNVERIFIED on 1.0.24) | **STAGE the files in `--cwd`**, tell it to read them; findings on stdout | inlined target ⇒ schema-valid `findings: []` (43 reasoning tokens on 15k input), or 0 bytes, or 259 bytes of narration. 3/3 (2026-08-28) |
| **codex** | **INLINE the files** into the prompt (`nl -ba`) so it makes ZERO tool calls | staged files ⇒ it reads them all, announces the report, then the long final answer **vanishes from stdout and `-o` is never written**. 1/1 (2026-08-28, this map's own review) |

So the same review dispatched to both needs two differently-built packets. Keep each
under codex's inline ceiling — **~30KB measured on v0.149.0** (32-45KB returns a confident
preamble and NO findings: the false-green band; 51KB+ silent at rc=0). The older
~79KB figure was v0.144.4's and is RETRACTED for current builds; it is
VERSION-BOUND, so re-probe on upgrade. Split into passes rather than growing one.
⚠️ **UNVERIFIED ON THE INSTALLED BUILD (2026-08-31): codex is now `0.150.1`, not
0.149.0.** The ceiling has NOT been re-probed since the bump — treat ~30KB as a prior,
not a measurement, and stay well under it until someone re-runs the band.
A dispatch that returns nothing is a SHAPE bug until proven otherwise: **re-shape, never
retry** (tightening the output contract made grok's case strictly worse — schema-valid
bad answer became 0 bytes).

## 3. Per-tool one-liners

- **codex** `gpt-5.6-luna` (implementation default; R-shape review of JS WITH the astra pack = alternate since 2026-09-30, default is `gpt-6.1-sol`+pack) / **`gpt-6-sol`**
  medium (review pick outside JS → **`gpt-6.1-sol`** since 2026-09-30; and WITHIN codex, once codex is already the chosen tool — implementation where a
  numeric-magnitude / recursion-depth bound can't be spec'd up front: JS with the astra pack, owner pick 2026-09-25,
  scale bench N=5: 45/50 vs astra 35/50; recipe + evidence in workflow_codex_subordinate.md). ⛔ **`gpt-6-astra` is
  never routed**: owner 2026-09-29, "astra will only be used on my command" (it drains the codex limit) — one command
  covers that task only. The measured astra numbers below stay as evidence, not as a route;
  this is a model pick, not a family route: astra was never benched against agy, so the §2
  agy `3.8-flash-low` row still owns unstated-edge routing — UNVERIFIED on 3.8) — the only judgment tier. 5.5/5.6/astra all saturate H1/H2/H3 (36/36 + 27/27, 2026-09-05/06),
  so for ordinary coding pick on cost not capability — BUT bare astra SEPARATES from bare luna/sol on two measured
  axes (with the astra pack, luna and sol tie astra's review score at the ceiling on JS, 2026-09-25, §2) (2026-09-06, N=3, [[finding-codex-56-family-2026-07-22]] Tests 6–7): unstated-scale
  edges (E4 astra 9/9 vs luna 4/9 — luna's `sumTo(1e9)` loop MATCHES the happy-path spec and is
  silently off only at the unstated grader scale; if you can state the bound, spec it for luna — MEASURED 2026-10-01 (owner go): JS impl
  with sizes + the exact Number/BigInt contract stated → bare `gpt-5.6-luna` 50/50, 0 silent (unstated 20/50, 19 silent; 6-sol+pack
  stated 50/50 = tie) → [[finding-luna-stated-magnitude-2026-10-01]])
  and review coverage (R1 astra 9/10 ×3, 0 nits; sol 8/10 + 2–3 nits, ~2× slower; luna 5/8/6
  avg 6.3, only recall miss). Family cost-ordering drifts (sol "most expensive" → cheapest in 6 weeks), token≠money,
  astra unpriced. Both astra rules are PROVISIONAL (N=3, one subject/task family; E4 and R1
  ran at `medium` — pass it). Run-to-run variance was low on H1/H2/H3 (every cell identical across
  3 trials, four models) — that does NOT make one run representative elsewhere: luna varied
  4/6·5/6·4/6 on E4 (recursive flatten failed 2/3) and 5/8/6 on R1. Replicate outside H1–H3.
  *Weakness:* silently fills spec gaps — never hand it an ambiguous brief; quota strands
  mid-batch with no error; long final answers can vanish from captured stdout.
- **agy** `3.8-flash-medium` (review: `3.8-flash-medium` + preamble, wall ≥ 300 s; **unstated-edge exposure:
  `3.8-flash-low` — UNVERIFIED; historical 3.7-low 15/20 vs medium's 4/20 same day**)
  — free, fast, PRE-impl adversary lane; **24/24 recall etc. measured on 3.7-medium only**.
  *Weakness:* useless post-impl on real repos; empty stdout is usually permission auto-deny
  (prepend no-tool preamble — do not retry blindly); bare `agy -p` is not the pinned model —
  always pass `--model`. Catalog: Gemini **3.8 Flash only** going forward
  ([[finding-agy-flash-38-only-catalog-2026-10-09]]).
- **grok** `grok-4.7` (pin moved from `grok-4.6` 2026-09-22: review-task 9/9 vs 4/9 N=3, impl parity, faster — PROVISIONAL; numbers in this entry were measured on 4.6) — third option at ceiling, best structured output, SUBSCRIPTION-billed
  (SuperGrok flat plan — the ~$0.005/run telemetry is reported, not billed; the metered path
  is `openrouter/x-ai/grok-4.6`, a separate product), effort tiers are FLAT (don't build effort routing). *Weakness:* slowest of
  the three (16.1s vs 8.5/9.2); provisional HANG-class miss; **ingests `~/.claude` by
  default → not an independent review lens, and any benchmark without an isolated HOME is void**;
  HOLDS write+shell and an isolated `--cwd` does NOT contain it (only a `--tools`
  allowlist does, and that flag fails OPEN on a typo — R-D);
  ⛔ the "IDLES on read-then-analyze packets ⇒ re-shape inline" rule is RETRACTED
  2026-08-28 — the idling cause was an EMPTY workspace, not the read step: staged files +
  "read them" + NO schema is the shape that delivered. **Never inline a review target.**
  Idling still happens when it has nothing to read, and the fix is still SHAPE, never retry;
  its review all-clears are void per R-B;
  `structuredOutput` comes back NULL with a complete draft stranded in `text` ~1/16 (08-27) —
  drop the rep, and never fall back to `.text` (the one observed orphan was a confident false
  alarm that passed every shape check).
- **opencode** — the free agent layer: the only free path that edits files. 2.x: use
  `opencode run --standalone` with `</dev/null` (shared background service otherwise; `run --dir` is gone — see `build-and-env` / `workflow_opencode_subordinate`). Isolated scratch
  dir + `timeout` + sequential by default (parallel OK with isolated `XDG_DATA_HOME` + copied auth.json). *Weakness:* no judgment-to-refuse; reliability (not
  reasoning) ceiling on multi-file; `$PWD`-not-cwd bug last CONFIRMED live at 1.18.19 — on 2.0.x
  **UNVERIFIED**; keep `env["PWD"]` aligned with dispatch's subprocess `cwd=` (harmless if fixed).
  ⚠️ **Installed build is `2.0.26` (2026-10-09).** Every free-pool/rc score in §2 was measured on 1.x.
  🔴 Also measured 2026-08-31: opencode hangs in TIME-VARYING windows (8/8 hang → 4/4 pass →
  0/6 hang → 10/10 pass, same command). Gate any bench on a stability check and treat a
  control timeout as stop-and-re-probe, NEVER as a model score.
  → [[finding-zen-pool-rebench-2026-08-28]]
- **NIM** — a model backend, not an agent; `nvidia/<vendor>/<model>`. Direct curl for
  parallel fan-out; opencode-NIM only when file edits are needed. *Weakness:* catalog lies
  (listed ≠ callable); non-streaming gateway kills at ~60s and has produced FOUR false death
  certificates — always smoke with `stream:true`.
- **TypeSafe** (`jev-latest`, served `jev-1.13.0`) — NOT one of the five subordinates: a typed
  classifier API, no agent, no files, not in `dispatch.py`. `POST https://api.typesafe.ai/v1/systemone`,
  `Authorization: Bearer $TYPESAFE_API_KEY` (`~/.zshenv`), body `{state, model:"jev-latest",
  questions:{name:{type:"noul"|"choice", instructions, criteria?}}}` → `answers.name.noul` (P) /
  `.choice`; read `model` from the response for the served version. Working caller:
  `claude-code-technique/experiments/typesafe-ladder-2026-09-23/run_arm.py` (`_body`, `_real_transport`).
  ~0.4 s per call (probe 2026-10-05). *Weakness:* conservative on ambiguous items (all 6 urgency
  misses on the `ambig` tier); review-lens output is noise. Cursor's auto-review blocks the raw
  call (key → third-party API) — expect an approval prompt.
- **cursor-agent** (`2026.10.14-941492e`, added 2026-10-15 on user order) — available,
  **UNROUTED**: owns no §2 row until a same-task-set comparison exists (routing it = ASK USER).
  Smoke-verified: `-p --trust --mode ask` read-only (refused a write), `--force` edits.
  Pin `--model` (e.g. `composer-2.5`); its Claude slugs are NOT a second family. → [[workflow-cursor-subordinate]]

## 4. Compose them: routing beats any single tool

**Routing > best-single is the most replicated result in the corpus** — 2024/2024 enumerated
triples (mean +4.5, never negative) and 97% vs 93% at N=1016. **Runtime voting is a wash
(54.9%) — do not build voting infra** ([[finding-voting-vs-single-verification]]).

Default chain for a non-trivial build:
1. **codex** spec-review → enumerate ambiguities (kills R-A and codex's own gap-filling).
2. **agy** pre-impl adversary → edge list, before code exists.
3. Cheapest tier that clears the bar implements, edges now STATED.
4. Fresh-context acceptance review (R1) — never the implementer, never self.

**Steps 1-3 MEASURED** — CHAIN 5/5 vs BASELINE 0/5 GUARD, same implementer/grader, only
the upstream edge-list differs; the chain manufactures the missing spec. N=5/arm,
single task shape, PROVISIONAL. → [[finding-chain-vs-direct-2026-08-25]]

**Step 4 MEASURED THREE TIMES, all saturated across three domains, densities and an
independent author — seeded recall is ROBUST and step 4 earns its place.** Zero tier
differentiation on seeded recall — weak evidence of reviewer equivalence, never an
equivalence claim (it retracts §2's "NOT agy post-impl" as a blanket rule — see that
row's scope note) — and the pre-registered unseeded-defect replication
REFUTED the codex discovery edge (gap 0.2 vs frozen 0.5; the earlier 6.2/4.2/4.0 split
is withdrawn — do not cite it). **Route step 4 on cost.** Three findings:
[[finding-step4-seeded-review-2026-08-25]], [[finding-step4-sparse-density-2026-08-25]],
[[finding-step4-independent-ledger-2026-08-25]].

## 5. What is NOT established (do not claim these)

- No step-4 tier ranking, in either direction (see §4). Re-opening it needs an instrument
  with ≥4 unseeded defects independent of each other, authored hypothesis-blind by
  someone else — the run-3 instrument had ONE, so it cannot distinguish "no edge" from
  "no resolving power".
- **Rule 3 applies per CLAIM, not per topic** — execute the review's own cited example;
  topic-crediting alone flipped run 3's verdict (5/5 → 3/5, INDETERMINATE → FAILS).
  → [[finding-step4-independent-ledger-2026-08-25]]
- **A seeded ledger is not the defect count.** Three experiments had the author's ground
  truth turn out incomplete with reviewer "false positives" verifying as real — Rule 3
  (execute every extra before scoring it false) is load-bearing, and padding tests bound
  nothing because missed defects live off the tested surface.
  → [[finding-step4-sparse-density-2026-08-25]]
- Only SEVEN same-task-set comparisons exist; everything else is single-arm plus
  reasoning. The 7th is cross-TIER valid only (ranking agy > NIM > opencode > grok holds;
  every stored-prior comparison in it is retracted per the R-A instrument rule) and
  established 0 fabrication in 54/54 honesty reps WITH the escape clause — that measures
  "takes the out when offered"; never cite it as baseline honesty
  ([[finding-geminimd-and-fleet-probe-2026-08-25]]). The six older: 3-way head-to-head
  (N=12/arm, [[finding-grok-cli-bench-2026-08-23]]); codex-vs-agy Round 2 (N=60, TIE —
  Round 1's correctness/architecture split RETRACTED as a lens artifact,
  [[finding-agy-vs-codex-aspects]]); free-NIM tight-spec parity (N=57);
  judgment-to-refuse (N=12); routing-vs-single (N=1016); one-window five-way (N=2/arm,
  [[finding-fiveway-bench-2026-08-23]]).
- Free pool won the 08-23 five-way (muse-spark 10/10 over both grok configs — **that 10/10
  is retracted, 9/10 on the 08-28 one-build re-bench; the win stands, the margin does not**); the same
  run's grok default-config 1/2 "lift" is ⛔ RETRACTED (0/6 on the N=6 repeat), and
  NIM-served `nemotron-3-ultra-550b` scored the OPPOSITE of its Zen-free namesake — never
  carry a Zen-free score onto a same-named NIM id. [[finding-fiveway-bench-2026-08-23]],
  [[finding-grok-defaultconfig-p2-2026-08-25]].
- No tool has been measured on multi-file, long-horizon, or ambiguous-spec work. The
  parity claims explicitly do NOT extend there.
- Free-pool scores are point-in-time SERVING facts, not model properties (big-pickle's edge
  guard regressed 2/2→0/2 across two days). Re-probe; never reuse a stale number.
  **Sharpened 2026-08-25: before blaming serving drift, check the INSTRUMENT.** An apparent
  agy 5/30→9/10 jump looked like drift and was pure prompt phrasing — the frozen old prompts
  still scored 4/20 vs 2/20 eleven days earlier (p=0.661). Two consequences: (a)
  `muse-spark`'s 4/4 "standing exception" above scored 5/10 on the 08-25 prompt — flagged,
  NOT overwritten at the time, because that comparison was instrument-crossed. **Settled
  2026-08-28 by a same-instrument re-bench: edge 1/2, exception withdrawn** (R-A); (b) a re-probe only
  supersedes a prior if it reuses that prior's prompt set byte-for-byte.
- **PAID ≠ DEAD ≠ INCAPABLE.** Before any death certificate: match on the
  `Error:`/`No payment method` STRING never on rc (two billing shapes: rc=1 stderr-only,
  and Zen-paid grok's rc=0 with the error on stdout); retry ≥3× with backoff (NIM
  529/503/`RemoteDisconnected` are all transient — the test is persistence across ≥2
  attempts, not the shape); treat NIM catalog-404 as don't-route; and an id ending
  `-free` vs its bare twin are DIFFERENT PRODUCTS. Case log: [[finding-pool-reprobe-2026-08-23]], [[reference-nim-via-opencode]] FULL
  CATALOG SWEEP; the Zen-paid rc=0 shape: [[reference-grok-other-harnesses]].
- Cost comparisons are inferred, not measured — NOTHING is CLI-metered in dollars any more
  (grok CLI moved to the SuperGrok subscription 2026-08-25; the metered grok is the separate
  `openrouter/x-ai/grok-4.6` product).
