---
name: workflow-codex-subordinate
description: "How to use Codex CLI as a coding subordinate — invocation, division of labor, verified capability profile, co-work patterns. DEFAULT MODEL 2026-07-23: gpt-5.6-luna (promoted over gpt-5.5 on the hard-axis gate: ties on LRU-edge + multi-file localization, cheaper tokens; drift caveat — re-probe monthly)"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 909ab1a7-504d-490d-976b-c8b1450aec01
---

Codex CLI (`/Users/yauch/.local/bin/codex`, v0.153.4 as of 2026-09-06; playbook default `-m gpt-5.6-luna` — always pass it, the bare config default is NOT the measured model) as a coding subordinate.

> **0.144.4 RE-VERIFIED (2026-07-11, 7 deterministic probes, 1 rep each per the low-variance rule, pre-registered expected-before-actual): ALL PASS — playbook applies unchanged.** P0 invocation+config-load (PONG, `codex`/`tokens used` stdout markers intact so the `sed -n '/^codex$/,/^tokens used$/p'` extraction still works) · P1 workspace-write in-place edit (node-verified, no stray files) · P2 unstated `chunk(arr,0)` edge → explicit `RangeError` guard (matches 5.5's 2/2 safe record) · P3 inline-file review recipe: synthesis survived to stdout, caught the `let max=0` all-negative bug with concrete counterexample · P4 no-false-positive on correct bsearch ("CORRECT") · P5 `-o` captured the short verdict · P6 `-m gpt-5.6-luna` still answers; plain `gpt-5.6` still 400-rejected. NEW in 0.144.x: a warning "Skill descriptions were shortened to fit the 2% skills context budget" — codex now loads skills/plugins into context; harmless so far, but if codex output ever degrades unexplainably, check what skills it's ingesting. NOTE: npm has a SEPARATE `@openai/codex` install at /opt/homebrew that is NOT on PATH — always update via `codex update` (standalone), never npm. Would change conclusion: any probe failing on a future version, or the flaky long-answer stdout loss (P3 recipe exists because of it) recurring despite inlining.

> **GPT 5.6 IS AVAILABLE (verified live 2026-07-10) — but ONLY under codenames**: `-m gpt-5.6-luna`, `-m gpt-5.6-sol`, `-m gpt-5.6-terra` all answer (PONG probe, ~10K tok each). Plain `gpt-5.6` / `gpt-5.6-codex` are REJECTED with a *generic* 400 ("not supported when using Codex with a ChatGPT account") — same error a nonsense model name gets, so that error carries zero existence signal. Codenames found via `strings` on the binary. Required CLI ≥0.144.1 (`codex update` — the standalone install at ~/.local/bin, NOT npm/brew).
>
> **⤷ SUPERSEDED 2026-07-23 (default is now gpt-5.6-luna — see the PROMOTED block above; this block is provenance, its "KEEP gpt-5.5" verdict is NO LONGER the order).** **BENCHED 2026-07-10 (4-probe × 2 reps × 4 models incl. same-day gpt-5.5 control, 32/32 runs, deterministic grading): KEEP gpt-5.5 AS DEFAULT.** Core probes fully saturated — all 4 models 2/2 on file-edit, chunk-basic, maxVal bug-catch (concrete counterexample), bsearch no-false-positive; zero separation. The only differentiator was the unstated `chunk(arr,0)` edge, and **gpt-5.5 WON it**: 5.5 = 2/2 safe (one `size<=0 → []` guard, one explicit `RangeError` throw — hand-verified), luna 1/2, sol 0/2, terra 0/2 (both infinite-loop, no guard at all — hand-verified). Latency same class for all (22–97s/probe; luna occasionally slow, 84–86s twice). If forced to pick a 5.6: **luna** (only one that ever guarded the edge). Would change conclusion: a harder-than-saturation task set, or an OpenAI statement on what luna/sol/terra actually are (A/B of the same model vs a size ladder — if A/B, the luna-vs-sol/terra edge split is noise at N=2). Grader gotcha logged: accept BOTH `module.exports = fn` and `{fn}` export shapes — all 4 models chose the direct-function export and an early destructure-only grader scored a false 0/16 on P2. **No 5.6-specific prompt tailoring needed (verified 2026-07-10)**: re-ran P2 on the two 0/2 edge-failers (sol, terra) with the edge spelled out ("if size is 0, negative, or not finite, return []") — 4/4 perfect on ALL three specified edges (size=0/negative/NaN, node-verified). The standing codex rule (airtight spec, edges explicit) fully cures 5.6's blind spot; same playbook applies unchanged.
>
> **UPDATED 2026-07-23 — luna PROMOTED to default for single-repo coding delegation** (supersedes the 2026-07-22 "5.5 default, luna routed" line and the 2026-07-10 "5.5 default, no tier routing" verdict below; those are kept for provenance, not as current orders). Hard-axis gate ([[finding-codex-56-family-2026-07-22]] Test 3): the exact axes 5.5 was proven on and luna wasn't — LRU + adversarial capacity=0/-1 (hang-detected) and multi-file median-bug localization+fix (graded by execution) — **luna tied 5.5 EXACTLY, H1 6/6 ×3 and H2 8/8 ×3, effort=medium, verified genuine** (luna guards cap via `Math.max(0,Math.floor(capacity))`+`===0` early-return → returns -1 not hang; H2 fix a byte-identical one-line `sort((a,b)=>a-b)`, siblings untouched). Tokens luna ~20.4K < 5.5 ~24.0K. **No measured axis left where 5.5 beats luna** (small utils, algo-traps, LRU edges, multi-file localization, cost — luna ties-or-beats all). → **Default coding delegation: `-m gpt-5.6-luna`.** Keep verifying luna's output yourself regardless (codex-class). "No mix mode / sol offers nothing" STANDS — now HARD-BACKED by Test 5 (2026-07-23): sol+terra run through the SAME H1/H2/H3 hard-axis harness (18 runs, effort=medium) both tie luna/5.5 EXACTLY (6/6·8/8·13/13 ×3, verified genuine — both guard cap 0/-1, both changed only discount.js in H3), so the whole family saturates and NO model separates; **sol is strictly DOMINATED** (~31.5K tok = MOST expensive of all four for byte-identical output), terra is co-cheapest with luna (~18K) but luna keeps default on track record. Corollary: heavy adaptive-routing INFRA is NOT worth building — no crossover task-shape where a non-luna model wins, so "adaptive model" collapses to the constant luna. The only axis that actually adapts is EFFORT; use the lightweight ladder below (a decision rule, not infra). ⚠️ **Drift flag (why this is not permanent):** luna GUARDED the exact capacity edge that sol+terra INFINITE-LOOPED on 2026-07-10 (hand-verified then) — same model strings, opposite behavior, 13 days apart. The endpoint drifts like agy's; any codex edge-safety/parity number has ~days shelf life → re-run the hardaxis H1/H2 probes before relying on luna a month out, don't reuse today's numbers. **Caveats CLOSED 2026-07-23 (Test 4):** effort=LOW re-ran H1+H2, luna 6/6 & 8/8 ×3 (still guards cap 0/-1 at low, direct-probed) — effort tier does NOT degrade luna; 6-FILE cross-module root-cause task (H3: trace index→cart→discount past a correct tax distractor), luna 13/13 ×3, changed ONLY the buggy file. luna cheaper on both. → luna-default is robust to effort tier AND file count, NOT limited to small/medium tasks. **Only reasons left to reconsider:** DRIFT (the monthly re-probe, above) and true multi-REPO / long-horizon agentic work (separate repos, tool-use loops, 10+ files — H3 was 6 files in one dir, untested beyond that). Everything up to ~6-file single-dir coding is RETIRED as a luna-vs-5.5 separator (four test sessions, zero axes where 5.5 wins). Harness: scratchpad/codex-5.6-bench/hardaxis (PREREG.md + h1/h2/h3 validated graders).

> **⤷ COST NOTE 2026-09-04:** the "sol = +55% tokens" figure above is STALE. Same H1/H2/H3 battery, effort=medium, n=9: sol 17.4K (14.6–19.8K) — now the CHEAPEST and tightest of the four; terra 22.1K, 5.5 21.6K, luna 21.1K. Correctness still 27/27 tie. luna STAYS default (track record; one cost snapshot on a drifting endpoint is not grounds to swap). Cost ordering within the family is itself a drifting quantity. → [[finding-codex-56-family-2026-07-22]] "part 2".

> **ADAPTIVE codex routing — model + effort (2026-07-23).** Goal = efficiency without losing outcome. On H1/H2/H3 outcome is at ceiling (family saturates), so there this rule only SAVES tokens. Model adapts on exactly TWO measured axes (both 2026-09-06, N=3, provisional): unstated-scale implementation and post-implementation review → `gpt-6-astra` (blocks below); otherwise it is the constant `gpt-5.6-luna` (ties on every other measured axis; sol/terra offer no correctness gain and family cost-ordering DRIFTS — see COST NOTE above — so don't pick on one token snapshot; terra/sol only if luna is quota-blocked). EFFORT adapts:
> | Task shape | Effort | Why (evidence) |
> |---|---|---|
> | single-file / well-specced util / mechanical edit | `low` | Test 4: low ties medium on H1+H2 (6/6 & 8/8 ×3), still guards cap 0/-1, ~15% cheaper. No correctness cost. |
> | **DEFAULT** — multi-file in one dir, bug localization, anything not obviously trivial | `medium` | Every hard-axis result (Tests 3–5) established here; luna 6/6·8/8·13/13. |
> | multi-REPO / long-horizon agentic / tool-use loops / 10+ files | `high` | UNMEASURED axis — no data says medium suffices, so pay up. This rung is precautionary, not proven. |
> Command: `codex exec -m gpt-5.6-luna -c model_reasoning_effort=<low\|medium\|high> --sandbox workspace-write --skip-git-repo-check "<prompt>"`. When unsure of task size, use `medium` (it straddles both — safe on hard tasks, negligibly dearer on easy ones). Model is luna unless one of the two exception blocks below names astra. Still verify luna's output yourself (codex-class). Re-check the low↔medium equivalence if the drift re-probe (above) ever shows luna degrading.

> **MODEL ROUTING EXCEPTION — `gpt-6-astra` for UNSTATED-SCALE work (2026-09-06, Test 6 after self-review).** One of two measured axes where codex models differ (the other is the review role, next block). E4 probe (write hasDuplicate/flatten/sumTo from a happy-path spec, graded on UNSTATED scale in timeout-guarded children): **luna scale 4/9 — `sumTo(1e9)` as a loop 3/3 (returns 500000000067109000, silently off; correct 500000000500000000), deep `flatten` recursive 2/3 (stack overflow); astra 9/9 — closed form, iterative.** Direct re-execution, N=3. Everything else (H1/H2/H3, effort tier, E1 beyond-the-brief) SATURATES for astra exactly as for luna.
> **Rule:** when codex is the chosen tool, use `-m gpt-6-astra -c model_reasoning_effort=medium` when implementing numeric-accumulation or deep-traversal code from a spec that states no magnitude/depth bound (the measured shape: sumTo → closed form vs loop, flatten → iterative vs recursive; `hasDuplicate` at 200k TIED — "large collections" is precautionary, not measured) **AND the bound is not known to you at delegation time** — "touches a number" is not the trigger; an unstated bound on accumulation/recursion is. If you DO know the bound, **spec it in the luna prompt and verify at that bound** ("n up to 1e9", "nesting up to 1e5") — stating the edge fixed the `chunk(arr,0)` class 4/4 on 07-10 (different edge class, N=2×2; a requirement is not a guarantee) and is the cheaper fix; astra earns its place only for the edge you couldn't think to state. Default stays luna. This does NOT rank astra against agy for unstated-edge work (never compared) — the routing map's agy-low row still owns the cross-tool choice.
> **Do NOT cite as reasons to switch:** (1) tokens — astra uses ~19–24% fewer than luna on identical tasks, but codex exposes NO pricing and astra is the top-billed model, so dollars are unmeasured (token≠money); (2) E1 — luna found 3/3 latent defects ×3, same as astra (an earlier "mild edge" was a grader artifact, retracted); (3) astra's parity-form `sumTo` — the plain closed form is also exact at 1e9, so it did NOT demonstrate deeper reasoning. astra default effort=low (adds xhigh/max/ultra); low tied medium on H1/H2/H3 ONLY — E4 and R1 were run at `medium` (drive_edge.sh, drive_review.sh), so pass `-c model_reasoning_effort=medium` when invoking either evidence-backed exception; astra@low is unmeasured there.
> Would change this rule: astra pricing ≤ luna's (→ RECONSIDER the implementation default after replication at N≥5 — price alone does not cure N=3/drift); luna passing E4 on a later drift re-probe (→ retire the exception); a real-work miss by luna astra catches. Harness: `experiments/codex-hardaxis-2026-09-04/e4/` (graders validated: safe-ref 6/6, naive-ref 3/6). ⚠️ Same drift shelf-life as everything above — re-probe E4 with H1/H2/H3 monthly.

> **REVIEW-ROLE MODEL (2026-09-06, Test 7, corrected by hand-count): post-implementation code review → `-m gpt-6-astra -c model_reasoning_effort=medium`; not luna.** PROVISIONAL preference, not a prohibition: N=3/model, one JS subject, medium effort, unstated-hazard design — spec review, rules-file review, security review and large real-repo diffs were NOT measured. R1 probe (review spec-correct code carrying 10 execution-verified unstated defects): distinct-defect coverage **astra 9/10 in every run, 0 nits**; sol 8/10 ×3 but pads 2–3 validation/reversed-bounds nits per run and takes ~2× wall time (113–182s) — its apparent breadth was bullet inflation; luna 5/8/6, high variance, weakest. astra also fastest (76–85s) and fewest tokens (17–19K). sol's only residual: it surfaced 2 oddball true finds in 3 runs (ß→SS in initials; sparse-array holes in hasDuplicate) that astra never did → **sol = optional ADDITIONAL codex pass only when a miss is catastrophic and time is free**, not a primary reviewer and not a replacement for grok as the second-family lens (routing map §2). astra never found ß; sol never found flatten's quadratic copy. luna stays the IMPLEMENTATION default (R1 measures review only; luna's one implementation weakness is the separate E4 exception above). The cross-model-review skill owns packet + verdict check; this line only picks the model. N=3, one subject, token≠money, drift shelf-life — replicate at N≥5 on a second subject before treating as permanent. Harness: `experiments/codex-hardaxis-2026-09-04/r1/`.
>
> **⤷ PARTIALLY SUPERSEDED 2026-07-23: the "MIX MODE DEAD / sol offers nothing" half STANDS for implementation (sol's only measured residual is the optional review second pass, 2026-09-06); the "codex default stays gpt-5.5" half is REPLACED by luna-default (see PROMOTED block above — luna was re-tested on these same H1/H2 axes and tied 5.5); the "no tier routing within codex" half is REPLACED 2026-09-06 by luna-default + the two astra exceptions (E4 unstated scale, R1 review) above.** **HARD-AXIS FOLLOW-UP (2026-07-10, 12/12 runs): sol offers NOTHING over 5.5 even at max reasoning — MIX MODE DEAD.** Arms 5.5-med / sol-med / sol-max × the two non-saturated frontier axes (H1: LRU cache impl incl. unstated capacity-0/negative edges, hang-detected; H2: localize a planted `arr.sort()` lexicographic bug in `median()` among 5 functions) × 2 reps. ALL arms 12/12 perfect — every LRU survived cap-0/negative (the edge that hung even claude 2/3 in the frontier bench, on free-tier models), every localization named median + mechanism + verified failing input (hand-checked: 5.5 ran the code itself as evidence). **sol-max costs 2–4× wall time (194–248s vs 51–107s) for zero gain.** VERDICT: codex default stays gpt-5.5, no tier routing within codex, no mix mode. Codex-class saturates these axes — the frontier-bench failure rates were a free-model phenomenon. Would change conclusion: a probe set that de-saturates at codex tier (multi-file integration bugs, adversarial specs), or a real-work miss by 5.5 that sol catches. Sibling to [[workflow-agy-subordinate]] — Codex is a strong code writer; delegate implementation, not just lookups. (It TIES agy on implementation of well-specified tasks per the 2-round experiment — its edge is low run-to-run variance + tighter typing, not raw "stronger." See capability profile.)

> GLOBAL playbook — applies to ALL projects. Examples are illustrative; the codex *behaviors*
> (ambiguity blind spot, JS/TS NaN under-defense, low variance, calibrated review, Cloud workflow)
> generalize to any project. Substitute your own verifier for the moira-specific oracle/sweeps.

## Invocation
- Read-only probe / Q&A:
  `codex exec -m gpt-5.6-luna --skip-git-repo-check "<prose prompt>"`
- Code-writing (autonomous file edits — approval mode is `never`):
  `cd <dir> && codex exec -m gpt-5.6-luna --skip-git-repo-check -s workspace-write "$(cat /tmp/codex-spec.txt)" </dev/null > /tmp/codex-out.txt 2>&1 &`
- Sandbox modes: `read-only` (default) | `workspace-write` (workdir + /tmp + $TMPDIR writable) | `danger-full-access`.
- **Vision / image input:** `-i, --image <FILE>...` attaches images. **GOTCHA (verified 2026-06-02):** the flag is greedy (`<FILE>...`), so a positional prompt placed AFTER `-i` is consumed as a second image path → codex falls back to reading the prompt from stdin and errors "No prompt provided via stdin." Fix: pipe the prompt via stdin — `echo "<prompt>" | codex exec -m gpt-5.6-luna --skip-git-repo-check -i img.png` (or put the prompt before `-i`). Confirmed reading a controlled screenshot (random token + number + status) exactly. Use for OCR, screenshot-to-bug, diagram/chart reads. Multiple `-i` flags work for A/B comparison (`... -i img1 -i img2 -`, prompt via stdin) — a viable vision-REVIEW mode, but codex's vision has blind spots (it missed edge arcs agy caught); adjudicate any vision disagreement against a pixel crop, never on one model's read.
- Cross-model code review: `codex exec review` / `codex review`.
- Must be in a trusted dir OR pass `--skip-git-repo-check`.

## Failure mode: ONE broken MCP entry kills EVERY `codex exec` (verified 2026-06-07)
codex's config loader is **all-or-nothing**: if any `[mcp_servers.X]` block in `~/.codex/config.toml`
is malformed, codex aborts the WHOLE config load with `Error loading config.toml: invalid transport
in mcp_servers.X` and every `codex exec` fails — not just that one server. Seen: a stub block with
only `startup_timeout_sec` and **no `command` (stdio) or `url` (http/sse)** → "invalid transport".
- **Why it appears out of nowhere:** nothing in YOUR prompt changed — Codex.app rewrites
  `config.toml` on launch and can leave a half-removed server stub. This is the most likely cause of
  "codex suddenly always fails."
- **Diagnose:** run `codex exec --skip-git-repo-check "PONG"`; if it errors at load, `grep -n
  '\[mcp_servers\.' ~/.codex/config.toml` and check each block has a `command` OR a `url`.
- **Fix:** back up (`cp ~/.codex/config.toml{,.bak}`), then comment out / delete the malformed block.
  Caveat: Codex.app may re-add it on next launch → re-remove if codex breaks again.
- Note: `-c key=value` overrides LAYER on top but don't rescue a base file that fails to parse —
  you must fix the file.
- **You do NOT need Codex.app for `codex exec` (verified 2026-06-07).** The CLI is a standalone
  binary (`~/.local/bin/codex` → `~/.codex/packages/standalone/.../bin/codex`), auths via
  `~/.codex/auth.json`, and runs with ALL MCP servers off (`codex exec -c 'mcp_servers={}' "PONG"`
  → works). The MCP servers (`node_repl`, `notebooklm-mcp`, `codex_apps`) are optional and
  **app-injected** — launching Codex.app rewrites `config.toml` and adds them (incl. the stub that
  broke parsing). So: never start the app for delegation; if you keep it installed, expect it to
  re-touch config on launch. Quickest immunization for a flaky config: `-c 'mcp_servers={}'` to run
  with MCP off (works only if the file still PARSES — a malformed block must be fixed in-file first).

## Capability — early single probe (2026-05-30, merge_intervals); superseded by the 2-round profile below
Kept for the clean ambiguity-blind-spot demo. (Authoritative findings are in the next section.)
- **Correctness: strong.** Passed all 9 independent adversarial cases (nested, negatives, duplicates, zero-width, deep non-mutation) that were NOT in its own test file.
- **Scope discipline: excellent.** 14 lines, no `__main__`, no extra modules, did exactly what was asked.
- **Ambiguity handling: the weakness.** It does NOT surface ambiguity — silently resolves gaps with sensible-but-unstated assumptions (merged touching intervals without flagging). Opposite of CLAUDE.md Rule 1 — the trait the 2-round NaN finding later confirmed at idiom level.

## Verified capability profile — 2-round controlled experiment (2026-05-30 → 06-02, vs agy + Opus)
Round 2 was the sound version: equal coverage (5 tasks incl. a new algorithmic expression-evaluator
× py/ts), replicated ×3, frozen pre-registered suites, symmetric review lenses. Net findings
(artifacts: `experiments/tool-comparison/`):

- **Implementation: clean, and ties agy on well-specified tasks.** 60 Round-2 runs → codex 57/60,
  every failure being one stable edge bug (below). Strong scope discipline; tightest typing of the
  cohort (`readonly`/`unknown`).
- **Stable JS/TS unspecified-input blind spot — the one durable defect.** Its TS rate-limiter used a
  fail-path guard `if (n > cap || tokens < n) return false`; `tryAcquire(NaN)` slips through
  (`tokens < NaN` is false), runs `tokens -= NaN`, corrupts the bucket permanently. Reproduced 3/3.
  The PYTHON port of the same spec was safe. → **For JS/TS hand-offs, spec NaN/undefined/null/
  non-finite explicitly, or verify those yourself — codex defends exactly what the spec names,
  nothing more.** The concrete face of its "fills gaps silently" trait.
- **LOW-VARIANCE run-to-run — a single codex run is representative.** Across 30 replicated
  implementations its outputs AND its one bug reproduced consistently. (Contrast agy: higher-
  variance, its Round-1 LRU bug did not recur in 3 trials → sample agy ≥2×; codex once is enough.)
- **Strong, calibrated reviewer.** Correctness lens: 5/5 and 6/6 planted defects, line-cited, no
  false positives. Architecture lens: thorough (caught the `__len__`/expired-count ambiguity,
  proposed a predicate-based `retryable` API). Skeptical doc critique: careful "supported vs
  over-generalized" split. → Use codex for contract-correctness review and calibrated critique.
  NOTE: this is NOT evidence codex > agy at review — under matched lenses they TIE; Round-1's
  "codex=correctness specialist" split was a lens artifact.

## Division of labor (plays to its shape)
- **I own the spec, and make it airtight.** Every gap I leave, Codex fills silently — it won't ask. Eliminate ambiguity before hand-off.
- **Codex executes** — fast, clean, in-scope implementation against a tight spec.
- **I verify against ground truth** — my own adversarial tests, NOT its claims. Never chain Codex → ship without my own check.

## Co-work patterns (Codex backgrounds; harness notifies on completion — true parallelism)
1. **Spec→implement→verify→fix loop** (best). My failing tests = the unambiguous spec; neutralizes its blind spot.
2. **Parallel fan-out.** Disjoint files only (else edit conflicts) — use git worktrees if they must overlap. Cross-model firefire.
3. **Cross-model adversarial review.** It implements, I red-team, or vice versa. Different model catches different bugs.
4. **Tie-break / second opinion** on competing approaches.
- HARD LIMIT: no shared mutable state mid-flight. Parallel on separate things, or sequential hand-offs on the same thing.

## Codex Cloud (remote execution + sync) — distinct from `codex exec`
`codex exec` runs LOCALLY on a directory. Codex Cloud runs REMOTELY on OpenAI infra against an IMPORTED GitHub repo, you sync diffs down. Auth: logged in via ChatGPT (Cloud available).
- Import (one-time, web UI): connect a GitHub *repo* to Codex Cloud. It's a repo connection, NOT a local-folder upload.
- Run: `codex cloud exec --env <ENV_ID> "<task>"` (submit; `--env` is REQUIRED, verified via `codex cloud exec --help`) · `codex cloud list` · `codex cloud status <id>`.
- Sync down: `codex cloud diff <id>` (preview) → `codex cloud apply <id>` (git apply to local working tree).
- TWO HARD REQUIREMENTS: (1) GitHub-repo-based — local folder w/o remote can't be imported; (2) sync needs a local git working tree (`apply` = `git apply`).
- Fit: the diff→apply gate matches verify-before-trust — nothing lands until I've seen the diff. Good for long autonomous tasks vs. `codex exec` for fast inline hand-offs.
- Cloud caveat: a plain local folder without a GitHub remote can't use Cloud — it needs a GitHub-linked repo + a local git working tree (the two requirements above). Check `git remote -v` before reaching for Cloud.

## When NOT to delegate
- Cross-cutting refactors where convention-judgment is the whole task.
- Specs that cost more to write than to just do myself.
- Decisions between competing approaches (judgment — mine + user's).
- Anything needing project conventions / prior-decision context Codex lacks.

## Pattern: bounded native-decode + port (verified 2026-05-31, Liu Ren KT33)

Codex CAN own a byte-level decode-and-port when the task is bounded AND has a
cheap unfakeable verifier. KT33 亂首 (matchUnit case 23) is the worked example:
Codex resolved the matchUnit jump-table from the case number, body-traced to find
the predicate shape (getRelationship(wx(getUpValue), wx(getChkZhiValue)) == a3),
ported it, threaded a3 through all 3 callers, and left a clean note. Net result
was correct (KT33 53/20 → 0/0, KT34/BF85 no regression).

When to delegate this shape:
- A single function/case to decode, the surrounding call sites are already mapped,
  AND there is a ground-truth oracle that is cheap to run (here: the on-device
  matchUnit mu-tuples probe + the decade sweep + 3804 fixtures).
- The spec is airtight: give Codex the exact symbol/address, the dispatch mechanics,
  the consumer call sites, and the verifier command. Its blind spot (silently filling
  gaps) is neutralized when the oracle is the spec.

What I MUST still do myself (do not delegate, do not trust Codex's word on):
- **Reproduce every disasm address claim.** Codex's note cited case 23 @0x660a14 vs
  the old 0x660da8; I could NOT independently confirm the address (display glitch),
  so I treated it as UNVERIFIED and grounded acceptance entirely on device parity.
  Codex fabricates disasm/run-output the same as agy — its note's "0/0 sweep" and
  address are claims, not evidence.
- **Re-verify EVERY consumer of a shared helper, not just the headline target.**
  case 23 is shared by KT33, KT34, BF85; Codex's note only proved KT33. I captured a
  device term-bank over all 3653 charts for all consumer (a1,a3) tuples (incl
  MU(2,23,2) KT34, MU(5,23,3) BF85) → 0 mismatches, then confirmed the sweep showed
  no other code's ts_only increased.
- **Run the verifier myself** (sweep + fixtures + tsc). Never accept Codex's pasted
  pass output.

Division that worked: Codex = decode+port+note; me = airtight spec + exhaustive
device/sweep/fixture verification + the commit. Same loop as the spec→implement→
verify pattern, with the device oracle as the unambiguous spec.

## Pattern: ported-numeric-series mismatch — COEFFICIENT-DIFF FIRST (verified 2026-06-09, QiMen 節氣 engine)
The web port's 節氣 cusp differed from the Moira APK by a clean year-flat +0.58·sin(2L) min residual
that whole-hour-floored flipped a 局 bucket at a rare straddle. Root cause = a ONE-coefficient
transcription bug: the semi-annual (2·L_sun, rate 1256.66393) term in the ported solar-longitude
series had its amplitude written as +1.3375 — which is actually the PHASE of the ADJACENT term —
instead of the real -132.0 (byte-decoded from `SolarTerm::S_aLon @0x4dd5ec`; canonical sxwnl coeff).
- **COEFFICIENT-DIFF FIRST.** When a PORTED numeric series (trig / VSOP / polynomial) disagrees with
  the binary, the FIRST codex task is a coefficient-by-coefficient diff of the series function vs the
  port — NOT a structural/convergence question. Here the first codex call chased the solver's
  convergence (`S_t`) and returned a byte-accurate but IRRELEVANT finding (a chord-method `E_v`-reuse,
  ~0.01 min effect); the real bug was a coefficient in a DIFFERENT function (`S_aLon`). codex answers
  exactly what you ask — point it at the coefficient table, not your pet hypothesis.
- **ADJACENT-VALUE TRANSCRIPTION is a named failure class.** When one ported coefficient looks ~100×
  off, ask codex explicitly: "does any amplitude equal an ADJACENT term's phase or rate?" Here +1.3375
  was literally the next term's phase. Neighbor-swap between amplitude/phase/rate columns is a
  recurring hand-port slip.
- **SELF-CORRECTION IS A TRUST SIGNAL.** codex mid-stream "Wait, correction… phase is 3.5069" and its
  unsolicited note that `SolarTerm::nutation(double) @0x4dd544` is a one-instruction `ret` no-op both
  prove it was reading bytes, not pattern-matching. Treat the ABSENCE of any self-correction on a hard
  decode as mild suspicion. (Reinforces: always demand a terse structured OUTPUT block and grep only
  for it — the raw first-call output was 36k lines incl. unrelated repo greps.)
- Division: agy named the concept → codex byte-decoded the -132.0 literal → my own OLS harmonic fit
  (leftover sd = 1/√12 = pure minute-truncation floor) + an env-var ground-truth probe VALIDATED the
  fix sign/amplitude against a 504-cusp captured fixture BEFORE shipping. Neither agent's output
  shipped directly. Fix = `1.3375 → -132.0`.

## Pattern: `codex exec` HEADLESS OUTPUT is flaky — INLINE the code, grep the synthesis (verified 2026-06-30, TG-bot PDF-toolbox review)
Ran `codex exec --skip-git-repo-check "<prompt>" < /dev/null > out 2>&1 &` for a code review ~5× and got NO findings — only the echoed prompt. Diagnosis + the recipe that finally worked:
- **Don't over-restrict shell.** "NO shell / NO execution" makes codex REFUSE to read the files at all (it reads via rg/sed/cat) — it then refuses out loud or emits nothing. Allow read-only file commands; forbid ONLY code *execution* (node/tsx/npm/build) — that eval path is the broken part (its repro scripts crash on top-level-await/CJS via esbuild).
- **The real failure mode: a LONG final answer after many tool calls does not flush to captured stdout** (exit 0, file = prompt echo + grep traces only, synthesis gone). A SHORT immediate reply (a refusal, or a one-word "none") DOES survive. Non-deterministic run-to-run.
- **FIX (worked every time): INLINE the target files into the prompt** (`{ cat hdr; nl -ba f1; nl -ba f2; } > prompt.txt`) so codex makes ZERO tool calls and goes straight to synthesis. The findings then render at the END of stdout — extract with `sed -n '/^codex$/,/^tokens used$/p' out`.
- **`-o, --output-last-message <file>` reliably captures SHORT verdicts** (it caught a lone "none") but was NOT written on the lost-long-answer runs. Backup, not primary.
- **Still earns its keep on REVIEW.** Across rounds it found 4 real Firestore concurrency bugs in a Telegram album→PDF collector: concurrent webhooks (album photos arrive as parallel updates → serverless runs them concurrently) → read-modify-write lost-update; and a non-atomic read-then-delete "claim" → double-tap duplicate + item acked-to-user-then-dropped. Fix = transactions on the SAME session doc (append-tx and claim-tx serialise). One [high] (`deleteMessage` "awaited outside try, can throw → stuck session") was a FALSE POSITIVE — that fn swallows all errors and never throws. Verify-before-acting (read the cited fn) caught the false flag and confirmed the real ones; the verification round then returned "none" = converged.

## Failure mode: background call hangs to `timeout`, no output file — open-pipe-on-fd0 (verified 2026-08-25)
Two background `codex exec` calls (part of a multi-tool-call parallel launch) died silently: no
output file, exit via `timeout`'s kill. Root cause CONFIRMED by direct reproduction, not just
codex's own account of itself:
- **Mechanism (execution-verified):** codex always attempts to read fd0 as a `<stdin>` block when
  fd0 is a pipe — true even with a prompt argument (documented in `codex exec --help`: "If stdin
  is piped and a prompt is also provided, stdin is appended as a `<stdin>` block"). If the pipe's
  write end doesn't close, codex blocks on that read until `timeout` kills it — no output file is
  ever created. Reproduced directly: `sleep 30 | timeout 10 codex exec ... "OK"` → hangs, rc=124,
  no file. Control: `echo | codex exec ... "OK"` → EOF arrives immediately, succeeds normally,
  rc=0. The differentiator is NOT "is stdin a pipe" — it's whether that pipe's write end closes
  before codex's read (or the timeout) does.
- **UNRESOLVED, do not overclaim:** why the harness sometimes leaves fd0 as an open (non-EOF) pipe
  on a background `codex exec` call and sometimes doesn't, on ostensibly identical command shapes
  in the same session — this needs harness-internals instrumentation, not shell-side probing (a
  `&`-backgrounded same-shell experiment can't replicate two-separate-tool-call topology and gave
  an inconclusive negative result). Two independent AI lenses (codex self-review + grok, isolated
  HOME) both ranked "harness/parallel-launch descriptor topology" as the top candidate cause, but
  neither is confirmed. Do NOT treat "two background tool calls in one turn" as a proven trigger.
- **Mitigation (execution-backed, not proven to be what fixed the ORIGINAL failures — that specific
  causal claim was tested directly and REFUTED, see below):** `</dev/null` on the codex invocation
  guarantees fd0 is never a pipe, so this specific hang class cannot occur. Safe to add
  defensively to background `codex exec` calls.
- **REFUTED, logged so it isn't retried:** hypothesized "`</dev/null` is *the* fix for background
  codex hangs" — tested with paired controls (identical trivial-prompt background call, with and
  without `</dev/null`); BOTH succeeded, meaning presence/absence of the redirect made no
  observable difference in that controlled pair. The redirect prevents ONE real mechanism (open
  pipe on fd0) but is not established as the explanation for any specific past failure — apply it
  as a hardening default, not as a diagnosis of what already happened.
- Also confirmed as a real, separate bug: `codex ... | tail -N; echo "EXIT=$?"` reports `tail`'s
  exit status, not codex's — masks a real timeout/hang as `EXIT=0`. Use `${pipestatus[1]}` (zsh)
  or `set -o pipefail` to read codex's actual exit code through a pipe.

## v0.144.4 invocation traps: double-backgrounding orphans; stdin `-`; -o long verdicts OK; workspace-write blast radius (2026-07-14/16)
- **Never double-background.** `nohup codex exec ... &` inside an already-backgrounded harness
  call → parent shell exits 0 immediately, codex orphaned mid-run, harness reports success.
  Cheap diagnostic BEFORE blaming the prompt: output has the echoed prompt + `user` marker but
  NO `codex` assistant-turn marker and NO `tokens used` line. Fix: ONE backgrounding mechanism.
- **A codex "no changes" report is not evidence — in EITHER direction.** Edits can land on
  disk while the terminal report is lost mid-flight; and a later self-report can falsely
  claim a file was untouched that it DID edit. Verify end-state against disk/`git status`,
  never against codex narration — including its narrations of *failure*.
- **Big prompts (>~10KB) via stdin `-`, not argv**: `cat prompt.txt | codex exec
  -m gpt-5.6-luna --skip-git-repo-check -s read-only -o last.txt - > out.txt 2>&1`.
  `-s read-only` for reviews, `-s workspace-write` for implementation.
- 🔴 **The 79KB inline-packet ceiling is v0.144.4's and does NOT hold on v0.149.0.**
  Measured 2026-08-28 on v0.149.0, same flags, `reasoning_effort=high`: **63KB and 55KB
  and 54KB each produced NO assistant turn at all** — stdout ends at the echoed prompt,
  no `codex` marker, no `tokens used`, `-o` never written, rc=0. Interleaved controls the
  same minutes: a PONG answered normally, **16KB → 4.4KB answer, 29.6KB → 6.8KB answer**.
  Between those: **32KB and 33KB returned only a ~370-byte contract statement and then
  stopped**; 45KB the same; 51KB+ nothing at all. So the cliff is just above **~30KB**,
  and it degrades gracefully-looking (a confident preamble, no findings) before it goes
  fully silent. **Keep an inline review packet under 30KB** — measured points are
  16/29.6 OK, 32/33/45 preamble-only, 51/54/55/63 silent. ⚠️ The failure is SILENT and looks exactly like the model having nothing to
  say — check for the `codex` marker, never assume an empty answer is a verdict.
  Re-measure this boundary on any version bump; it moved once already.
- 🔴 **A chunk must be SELF-SUFFICIENT.** Splitting by file and then asking cross-file
  questions gets an honest refusal, not findings: fed one file of a 15-file corpus, codex
  correctly reported "cannot verify without inventing evidence" and returned only
  dangling-pointer noise about the files it wasn't given (2026-08-28). Put the ground
  truth a chunk is checked against INSIDE that chunk.
- **`-o` captured a 10.5KB verdict** — the older "short verdicts only" caveat did NOT
  reproduce on v0.144.4; -o fails only when the run itself dies (see orphan trap above).
- **workspace-write blast radius = the whole repo.** Enforcing its "only these N files"
  constraint, codex restored NON-listed files to HEAD mid-run — silently wiping a fix I had
  landed in the same tree (2026-07-14). While codex holds write access to a tree, land
  nothing in it yourself: stage in scratch, merge after it exits, then audit for double-edits.
  **`.git` is outside the sandbox** — codex can't commit its own work, so the orchestrator
  commits after codex exits; treat workspace-write as a write LOCK on the tree until exit.

## Gotcha: the inlined packet IS codex's argv -- your own `pkill -f` can kill it (verified 2026-09-05)
Two `codex exec -m gpt-5.6-sol` reviews died RC 143 within minutes, 0 tool calls, no verdict. Not
the `timeout` cap: the 98KB prompt (passed as one argv per the inline recipe) contained the literal
`/bin/sleep 25` from an evidence file, and a harness cleanup `pkill -f '/bin/sleep 25'` running in
the same session matched codex's command line. `pgrep -f` with the same pattern then counted the
codex processes as "leaked sleeps" (pid chain zsh→timeout→codex, cwd = packet dir). Rule: while a
codex review runs, no `pkill -f`/`pgrep -f` with any string that could be in the packet -- match on
`pkill -x`, pgid, or cwd instead. RC 143 far short of the cap with 0 exec lines = external SIGTERM.
Also seen the same day: codex loaded an installed plugin skill (`agent-skills` 6-phase lifecycle
from `~/.codex/plugins/cache/`) and began following it instead of reviewing -- the "check what
skills it's ingesting" warning above, live. Mitigation under test: `--ignore-user-config` plus a
seeded `CODEX_HOME` holding only `auth.json` (isolate state, never credentials).
→ [[feedback-pkill-pattern-matches-subordinate-argv]]
