---
name: workflow-codex-subordinate
description: "How to use Codex CLI (gpt-5.5) as a coding subordinate — invocation, division of labor, verified capability profile, co-work patterns"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 909ab1a7-504d-490d-976b-c8b1450aec01
---

Codex CLI (`/Users/yauch/.local/bin/codex`, v0.144.1 as of 2026-07-10, config default gpt-5.5) as a coding subordinate.

> **GPT 5.6 IS AVAILABLE (verified live 2026-07-10) — but ONLY under codenames**: `-m gpt-5.6-luna`, `-m gpt-5.6-sol`, `-m gpt-5.6-terra` all answer (PONG probe, ~10K tok each). Plain `gpt-5.6` / `gpt-5.6-codex` are REJECTED with a *generic* 400 ("not supported when using Codex with a ChatGPT account") — same error a nonsense model name gets, so that error carries zero existence signal. Codenames found via `strings` on the binary. Required CLI ≥0.144.1 (`codex update` — the standalone install at ~/.local/bin, NOT npm/brew).
>
> **BENCHED 2026-07-10 (4-probe × 2 reps × 4 models incl. same-day gpt-5.5 control, 32/32 runs, deterministic grading): KEEP gpt-5.5 AS DEFAULT.** Core probes fully saturated — all 4 models 2/2 on file-edit, chunk-basic, maxVal bug-catch (concrete counterexample), bsearch no-false-positive; zero separation. The only differentiator was the unstated `chunk(arr,0)` edge, and **gpt-5.5 WON it**: 5.5 = 2/2 safe (one `size<=0 → []` guard, one explicit `RangeError` throw — hand-verified), luna 1/2, sol 0/2, terra 0/2 (both infinite-loop, no guard at all — hand-verified). Latency same class for all (22–97s/probe; luna occasionally slow, 84–86s twice). If forced to pick a 5.6: **luna** (only one that ever guarded the edge). Would change conclusion: a harder-than-saturation task set, or an OpenAI statement on what luna/sol/terra actually are (A/B of the same model vs a size ladder — if A/B, the luna-vs-sol/terra edge split is noise at N=2). Grader gotcha logged: accept BOTH `module.exports = fn` and `{fn}` export shapes — all 4 models chose the direct-function export and an early destructure-only grader scored a false 0/16 on P2. **No 5.6-specific prompt tailoring needed (verified 2026-07-10)**: re-ran P2 on the two 0/2 edge-failers (sol, terra) with the edge spelled out ("if size is 0, negative, or not finite, return []") — 4/4 perfect on ALL three specified edges (size=0/negative/NaN, node-verified). The standing codex rule (airtight spec, edges explicit) fully cures 5.6's blind spot; same playbook applies unchanged.
>
> **HARD-AXIS FOLLOW-UP (2026-07-10, 12/12 runs): sol offers NOTHING over 5.5 even at max reasoning — MIX MODE DEAD.** Arms 5.5-med / sol-med / sol-max × the two non-saturated frontier axes (H1: LRU cache impl incl. unstated capacity-0/negative edges, hang-detected; H2: localize a planted `arr.sort()` lexicographic bug in `median()` among 5 functions) × 2 reps. ALL arms 12/12 perfect — every LRU survived cap-0/negative (the edge that hung even claude 2/3 in the frontier bench, on free-tier models), every localization named median + mechanism + verified failing input (hand-checked: 5.5 ran the code itself as evidence). **sol-max costs 2–4× wall time (194–248s vs 51–107s) for zero gain.** VERDICT: codex default stays gpt-5.5, no tier routing within codex, no mix mode. Codex-class saturates these axes — the frontier-bench failure rates were a free-model phenomenon. Would change conclusion: a probe set that de-saturates at codex tier (multi-file integration bugs, adversarial specs), or a real-work miss by 5.5 that sol catches. Sibling to [[workflow-agy-subordinate]] — Codex is a strong code writer; delegate implementation, not just lookups. (It TIES agy on implementation of well-specified tasks per the 2-round experiment — its edge is low run-to-run variance + tighter typing, not raw "stronger." See capability profile.)

> GLOBAL playbook — applies to ALL projects. Examples are illustrative; the codex *behaviors*
> (ambiguity blind spot, JS/TS NaN under-defense, low variance, calibrated review, Cloud workflow)
> generalize to any project. Substitute your own verifier for the moira-specific oracle/sweeps.

## Invocation
- Read-only probe / Q&A:
  `codex exec --skip-git-repo-check "<prose prompt>"`
- Code-writing (autonomous file edits — approval mode is `never`):
  `cd <dir> && codex exec --skip-git-repo-check -s workspace-write "$(cat /tmp/codex-spec.txt)" > /tmp/codex-out.txt 2>&1 &`
- Sandbox modes: `read-only` (default) | `workspace-write` (workdir + /tmp + $TMPDIR writable) | `danger-full-access`.
- **Vision / image input:** `-i, --image <FILE>...` attaches images. **GOTCHA (verified 2026-06-02):** the flag is greedy (`<FILE>...`), so a positional prompt placed AFTER `-i` is consumed as a second image path → codex falls back to reading the prompt from stdin and errors "No prompt provided via stdin." Fix: pipe the prompt via stdin — `echo "<prompt>" | codex exec --skip-git-repo-check -i img.png` (or put the prompt before `-i`). Confirmed reading a controlled screenshot (random token + number + status) exactly. Use for OCR, screenshot-to-bug, diagram/chart reads.
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
- Run: `codex cloud exec "<task>"` (submit) · `codex cloud list` · `codex cloud status <id>`.
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
