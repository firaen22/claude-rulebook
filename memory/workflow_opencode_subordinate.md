---
name: workflow-opencode-subordinate
description: opencode CLI (native OpenCode Zen free models) as a coding subordinate — invocation, model selection, session management, gotchas, and the delegate-WHAT-not-WHETHER boundary
metadata:
  type: project
---

# opencode CLI Subordinate Playbook

## TL;DR — the delegation decision (benchmarked, 3 rounds, 2026-06-11)

Free opencode models tested at PARITY with codex/opus on EXECUTION (code-from-spec, bug-fix,
reasoning, convention-match, edge-defense, trap-avoidance). They diverge on ONE axis only:
**judgment-to-refuse** — recognizing when the instruction itself is unwise (only codex/opus
flagged a security anti-pattern; all free models executed it blindly).

- ✅ **Delegate the WHAT (execution) freely** → cheapest reliable model, isolated dir, verify output.
- 🚫 **Never delegate the WHETHER** ("is this safe / a good idea / architecturally sound?") →
  keep codex/opus/you as the judgment layer. Free models execute footguns without blinking.

Operational guardrails (non-negotiable, see Benchmark findings below):
1. Run opencode models SEQUENTIALLY (shared SQLite db → lock under parallel).
2. Run in an ISOLATED scratch dir (`--dangerously-skip-permissions` = full read+write; it roams).
3. `timeout 180`-wrap every call (free models hang).
4. Prefer native `opencode/*` (Zen) over `openrouter/*:free` (rate-limits + hangs).
5. Verify output yourself; parse BOTH inline code blocks AND files the agent wrote.

## Install & Auth
- Installed to: `~/.opencode/bin/opencode` (PATH set in `~/.zshrc`)
- Auth: OpenCode Zen + OpenRouter creds in `~/.local/share/opencode/auth.json` (`opencode providers list`)
- Version check: `opencode --version`
- Upgrade: `opencode upgrade`

## Core Invocation

**Read-only / lookup:**
```bash
opencode run --dangerously-skip-permissions -m opencode/big-pickle "<prompt>"
```

**Code-writing (backgrounded, isolated + timeout-wrapped):**
```bash
SCRATCH=$(mktemp -d) && cd "$SCRATCH" && timeout 180 opencode run --dangerously-skip-permissions -m opencode/big-pickle "$(cat /tmp/opencode-prompt.txt)" > /tmp/opencode-out.txt 2>&1 &
```

**With file attachments:**
```bash
opencode run --dangerously-skip-permissions -m <model> -f path/to/file.ts -f path/to/other.ts "<prompt>"
```

**JSON output (for parsing):**
```bash
opencode run --dangerously-skip-permissions -m <model> --format json "<prompt>" | jq .
```

## Model Selection (FREE ONLY — do not use paid models)

Use NATIVE `opencode/*` (OpenCode Zen) free models — they are far more reliable than
`openrouter/*:free` (which rate-limits + hangs). Benchmarked 2026-06-11 (see below).

Re-verified 2026-06-27 @ opencode v1.17.8 (4 probes × 5 models × 2 reps, deterministic grading — see section below). Scores are x/2 unless noted.

| Use case | Model | Notes (✅=re-verified 2026-06-27 @v1.17.8) |
|---|---|---|
| Default / general (headless) | `opencode/big-pickle` | ✅ best overall 9/10, **0 fabrications**, 8.2s. Real on-disk edits matched narration. Roams cwd. (Refutes the old "0/20 file-edits" — see Conflict note.) |
| Fastest / latency-critical fan-out | `opencode/deepseek-v4-flash-free` | ✅ tied-best 9/10, **FASTEST 7.6s** (tightest spread). Rate-limit caveat still stands. Roams cwd. |
| Clean all-rounder | `opencode/mimo-v2.5-free` | ✅ 9/10, clean, 9.4s; self-tests via `node`; roams+writes+EXECUTES cwd. Solid alt to deepseek. |
| Write-from-spec + review/diagnosis | `opencode/north-mini-code-free` | ✅ good IMPL **and** solid diagnosis (P3 2/2 caught real bug, P4 2/2 no false-positive) — **"bad at bug-diagnosis" caveat RETIRED for v1.17.8**. Knocks: slowest (14s) + one missing-file run. |
| Edge-defense / self-verify (FLAKY) | `opencode/nemotron-3-ultra-free` | ✅ ONLY model to guard `size<=0`; self-tests. BUT infra-flaky on the NIM backend (exit-1 no-edit + Nvidia `ResourceExhausted` this run) — **never a default**; always timeout-wrap + revert-on-failure. |
| AVOID (headless) | `openrouter/qwen/qwen3-coder:free` | 429 rate-limit / silent hang |
| AVOID (any tier) | `openrouter/nousresearch/hermes-3-llama-3.1-405b:free` | verified 2026-07-03: agent path hard-fails ("No endpoints found that support tool use") AND one-shot direct-curl 429'd — no viable tier. Revisit only with paid Hermes-4 or own OR key (tool-use blocker would still cap it at one-shot) |
| List all free | `opencode models \| grep -E '\-free$\|big-pickle' \| grep '^opencode/'` | as of 2026-06-27 the free pool is exactly these 5 |

> ⚠️ **Pool-wide edge blind spot (re-verified):** free models nail the happy path but do NOT defend *unstated* degenerate inputs. P2 probe: 9/10 wrote a `chunk()` that **infinite-loops on `size=0`** (no guard), *even though an example was given*. Only nemotron guarded it (1/2). → **Spec `size<=0` / negative / NaN / empty explicitly, or put those cases in your own verification** — same defensive-spec discipline already required for [[workflow-codex-subordinate]] / agy. This is the WHAT-vs-WHETHER rule's sharper edge: they execute the happy path, they won't *judge* what a degenerate input should do.
>
> 🔀 **Conflict reconciled (Rule 7):** the prior frontier-bench finding ([[finding-delegation-frontier-bench]]) recorded "big-pickle 0/20 headless file-edits + 14 fabrications → route to north-mini, NOT big-pickle." It **did not reproduce** here: big-pickle did 4/4 real on-disk file ops (P1 2/2 + P2-cap 2/2), 0 fabrications. Reconciliation is **task-complexity, not a version fix** — same v1.17.8 (Jun-18) build both times; the 0/20 was on the frontier's *harder multi-file dir-mode* tasks (A1/A2/A3), this is a *simple single-file* in-place edit. → **big-pickle is reclaimed as a viable default for simple/medium headless edits**; for **complex multi-file** edits keep the caution and verify on disk. **`north-mini-code-free` remains your proven at-scale headless choice** (your own ground-truth — frontier finding line 35). Both are viable; pick big-pickle/deepseek for speed on bounded tasks, north-mini for sustained/complex headless work.

## Benchmark findings (2026-06-11) — opencode free models vs codex/agy

4-probe battery (impl-from-spec / bug-hunt / reasoning / ambiguity). Raw capability was
near-ceiling for ALL models — the real differentiation was OPERATIONAL:

1. **Run opencode models SEQUENTIALLY, never in parallel.** All `opencode run` instances
   share one SQLite db (`~/.local/share/opencode/opencode.db`) → "database is locked"
   failures when fanned out. codex/agy have independent stores (parallel-safe).
2. **`--dangerously-skip-permissions` = full file READ + WRITE in cwd.** opencode agent-models
   roam the working dir (read sibling files, other outputs, secrets) and write arbitrary
   files. ALWAYS run in an isolated scratch dir; never in a repo with secrets. Contrast:
   codex's `read-only` sandbox BLOCKS writes — safer for untrusted tasks.
3. **`north-mini-code-free` hallucinates on code REVIEW** — diagnosed a non-existent "integer
   overflow" in a JS binary search (2/2 reproducible), pattern-matching the C/Java textbook
   lesson. Fine for WRITING code from an explicit spec; do NOT trust for bug-diagnosis.
   → ⚠️ **SUPERSEDED 2026-06-27 (@v1.17.8):** directly re-tested this exact case (review a correct JS
   binary search) — north-mini answered `CORRECT` 2/2 (no hallucination) and caught a real bug 2/2.
   Caveat retired; see the Re-verification section. (Original behavior was real on the older build/session.)
4. **`openrouter/*:free` is operationally broken headless** — qwen3-coder:free 429'd then hung
   for ~1hr, stalling the runner's `wait`. Native `opencode/*` Zen models did not.
5. **Delivery format varies** — some emit a fenced block (codex/agy/big-pickle/deepseek),
   nemotron writes a file + self-tests. When scoring/extracting code, check BOTH inline
   blocks AND files the agent wrote.
6. **Always `timeout`-wrap free-model calls** (`timeout 180 opencode run ...`) so a hang can't
   stall a batch.
7. With an AIRTIGHT spec (edge cases listed), every model produced correct edge-defended code —
   the codex/agy "edge blind spot" only fires on gaps you leave. See [[workflow-codex-subordinate]].
8. **Capability is NOT the differentiator.** Rounds 2–3 used trap-laden + judgment probes:
   - Trap probes (lexicographic-sort, dropped-remainder, climbing-well, semver) caught NOBODY —
     all 6 models perfect. Convention-fit from one example — all 6 perfect.
   - The ONLY discriminator in 12 probes: **push-back on a bad instruction.** Asked to store an
     API key in localStorage, only codex flagged the XSS risk + offered an HttpOnly alternative;
     every free model + agy complied blindly. → This is the WHAT-vs-WHETHER rule in the TL;DR.
   Full detail: [[finding-model-benchmark-2026-06-11]].

## Re-verification 2026-06-27 @ opencode v1.17.8 (deterministic-graded)

Triggered by "check the opencode zen free mode again." Free pool unchanged (5 models: big-pickle,
deepseek-v4-flash-free, mimo-v2.5-free, north-mini-code-free, nemotron-3-ultra-free). 4 probes ×
5 models × 2 reps = 40 runs, **sequential** (SQLite lock), `timeout`-wrapped, isolated dir per run,
graded by `node` test harness on disk (not narration). Probes targeted the *real* discriminators
(raw capability is saturated): P1 = file-EDIT gate (modify existing file in place), P2 = unstated-edge
robustness (`chunk(arr,size)` with `size=0` → infinite-loop trap), P3 = catch a real bug (`maxVal`
`max=0` init), P4 = do NOT hallucinate a bug in VERIFIED-CORRECT code (a real binary search; the
exact class north-mini was previously flagged on).

Scorecard (x/2):

| Model | P1 edit | P2 cap | P2 edge | P3 catch | P4 no-FP | avg lat |
|---|---|---|---|---|---|---|
| big-pickle | 2/2 | 2/2 | 0/2 | 2/2 | 2/2 | 8.2s |
| deepseek-v4-flash-free | 2/2 | 2/2 | 0/2 | 2/2 | 2/2 | **7.6s** |
| mimo-v2.5-free | 2/2 | 2/2 | 0/2 | 2/2 | 2/2 | 9.4s |
| north-mini-code-free | 2/2 | 1/2 | 0/2 | 2/2 | 2/2 | 14.1s |
| nemotron-3-ultra-free | 1/2 | 2/2 | **1/2** | 2/2 | 1/2+err | 11.0s |

Findings:
1. **big-pickle file-edits work on simple tasks** (4/4 real on-disk ops, 0 fabrications) → the old "0/20"
   did not reproduce on a simple single-file edit (see Conflict note — it's task-complexity, not a version fix;
   the 0/20 was harder multi-file dir-mode). Reclaimed as a viable default for simple/medium headless edits.
2. **north-mini did NOT hallucinate** → P4 2/2 said exactly `CORRECT` on the binary-search class it
   previously false-positived on; P3 2/2 caught the real bug with a counterexample. Diagnosis caveat retired.
3. **Edge robustness is the universal pool weakness** → 9/10 `chunk` impls infinite-loop on `size=0`
   (identical unguarded `for(i;i<len;i+=size)`). Only nemotron guarded it, once. Spec edges or verify them.
4. **nemotron is now the flaky one** → exit-1 on 3/8 runs + 1 Nvidia `ResourceExhausted` (it's NIM-backed,
   see [[reference-nim-via-opencode]]). Capable (only edge-guarder, caught every bug) but unreliable headless.
5. **gotcha #6 (0-byte empty file-review) did NOT reproduce** @ v1.17.8 — all 20 P3/P4 file-review runs
   returned substantive output. Likely version-fixed or stochastic; kept the gotcha but watch for it.
6. **Latency order** (fast→slow): deepseek 7.6 < big-pickle 8.2 < mimo 9.4 < nemotron 11.0 < north-mini 14.1.

Method caveats (kept honest): n=2/probe; probes are *single-file* tasks. **The judging-Workflow silently
self-sabotaged and I only caught it by cross-checking — the lesson matters more than the bench.** Root cause
(verified with an echo-workflow): the Workflow tool delivers the `args` global to the script as a **raw JSON
STRING, not a parsed object** (`typeof args === 'string'`). My script did `args.p3` directly → `undefined` →
`(args.p3 || [])` defaulted to `[]` → ZERO judge agents spawned → the synth received `detSummary: undefined`,
`p3: []`, `p4: []` and **confabulated the ENTIRE report — all 4 probes, with confident specifics (latencies,
on-disk counts, the `[-5,-3,-10]` counterexample) — from nothing**, yet mostly correct because these are
well-known models and the probe design telegraphs outcomes. The only reason the numbers here are trustworthy is
that I re-graded every raw output *deterministically* myself (P4 = literal `CORRECT`/error-string match; P3 =
phrasing-robust signal). Lessons for workflow authoring (see [[finding_workflow_synth_confabulates]]):
(1) **`JSON.parse(args)` at the top of every script** (`const A = typeof args==='string'?JSON.parse(args):args`);
(2) a synth agent FAILS QUIET — it invents a plausible authoritative report from missing input rather than
erroring; (3) **never `|| []`-default a critical input** — it masks non-arrival; assert/`log()` it early, throw
if absent; (4) ground the final answer in deterministic checks you ran yourself, never the agent's narration.

## Session Management

- Continue last session: `opencode run -c --dangerously-skip-permissions -m <model> "<next-prompt>"`
- Continue specific session: `opencode run -s <session-id> ...`
- Fork session (branch without overwriting): add `--fork` to `-c` or `-s`
- Export session: `opencode export <sessionID>`
- List sessions: `opencode session list`

Use session resume for iterative tasks — opencode retains full context (file edits, tool calls, prior messages) within a session.

## Key Differences from agy / codex

- **opencode IS a full coding agent** — it calls tools, reads/writes files, runs shell commands. It will mutate your working directory.
- **No sandbox levels** (unlike codex's `read-only` / `workspace-write`) — it operates at full access by default.
- **Session state persists** across `run` calls — more stateful than one-shot agy/codex invocations.
- **OpenRouter routing** — slight latency overhead vs direct API; model availability depends on OpenRouter.

## Gotchas

1. **`--dangerously-skip-permissions` is mandatory headless** — omitting it causes a silent hang waiting for interactive approval.
2. **Always `cd` to project dir** — opencode resolves file paths from cwd; running from wrong dir causes incorrect edits.
3. **Verify with `git diff`** — opencode narrates success; always check actual file changes before acting on them.
4. **PATH not auto-loaded in non-login shells** — use full path `~/.opencode/bin/opencode` in Bash tool calls, or source `~/.zshrc` first.
5. **Session resume caution** — `-c` appends to the last session regardless of project; always verify you're in the right project dir before resuming.
6. **0-byte empty completion on tool-use file-review** — ⚠️ **NOT reproduced @ v1.17.8 (2026-06-27): all 20 P3/P4 file-review runs returned substantive output. Likely version-fixed or stochastic; kept as a watch-item.** Original report (2026-06-13, both big-pickle AND nemotron-3-ultra-free, exit 0 ×3): Asked to read 3 files in the cwd and confirm/refute two suspected bugs, both free models returned an EMPTY file every time — while a trivial no-tool prompt (`Reply with exactly: PONG`) on the same model in the same dir returned fine. So the CLI/model are alive; the failure is specific to prompts that require tool-use to read files and synthesize. Symptom is silent: exit 0, 0 bytes, NOT a `timeout`-catchable hang. Diagnosis ruled out redirect-vs-pipe (failed under both `>` and `| tee`). Operational rule: for a **must-deliver** file-review/investigation, do NOT route it to an opencode free model — codex (read-only) did the same investigation cleanly with file:line provenance. Symmetric to agy's hard-recall hang the same session (see the agy playbook's Wedge-trigger-#2 caveat): both cheap subordinates fail on non-trivial cross-checks; keep them off the critical path and verify every delivery is non-empty before relying on it.

7. **Upstream 429 masquerades as a silent stall (NIM-backed models)** — verified 2026-07-03 on `nvidia/z-ai/glm-5.2`: when the backend rate-limits, opencode retry-loops quietly and the run either (a) produces a banner-only out.txt (~34 bytes, zero work) until `timeout` kills it (exit 124), or (b) **completes the file edit then hangs instead of exiting** (work is on disk, exit still 124). So exit 124 ≠ model failure and ≠ task failure — **diagnose with a direct-curl PONG on the same model+key** (429 = throttled, not broken) **and grade on-disk state, never exit codes**. GLM 5.2 specifically has a per-account per-model throttle (~30-40 req → 429 for >25 min, other models on the same key unaffected); rotate keys via `NVIDIA_NIM_API_KEY=<poolkey> opencode run ...`. Full detail: [[reference-nim-via-opencode]].

## Division of Labor vs agy / codex (benchmark-backed)

- **agy**: fast lookup, domain knowledge, OCR/vision reads, sweep harnesses — read-only, high
  variance, doesn't roam files (safe in dirty dirs). Complies blindly — no judgment layer.
- **codex**: tight-spec implementation, low variance, strong scope discipline, read-only sandbox
  (safe for untrusted tasks). **The only subordinate that pushes back on bad/unsafe instructions.**
  Use it (or opus) as the judgment gate. Won't surface ambiguity unless it's a safety issue.
- **opencode free models**: execution workhorses at codex-parity for bounded checkable tasks —
  multi-turn sessions, refactors, tool use + file edits. Cheapest reliable option. BUT: roam+write
  cwd (isolate it), run sequentially, and have NO judgment-to-refuse — never hand them the
  "should we even do this?" call. Per-model quirks in the Model Selection table above.
