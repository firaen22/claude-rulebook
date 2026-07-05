---
name: workflow-agy-subordinate
description: "Playbook for calling the Antigravity CLI (`agy`, Gemini 3.5 Flash) as a subordinate tool from Claude sessions to offload pattern-discovery and decode-reading work. Established 2026-05-20 after empirical experiment on BF67."
metadata: 
  node_type: memory
  type: workflow
  originSessionId: d0fc7ada-52e0-4711-bae0-899ed2f8e5ae
---

# Calling `agy` (Gemini 3.5 Flash) as a subordinate

> GLOBAL playbook — applies to ALL projects. Concrete examples below are from the moira project,
> but agy's *behaviors* (wedge triggers, fabrication, run-to-run variance, vision, delegation
> economics) generalize. Substitute your own oracle/verifier for the moira-specific `chart-diff`.

## Invocation
```
agy -p "<prose prompt>"
```
- Returns in ~5–7s on small prompts
- Auth: Google login via the Antigravity IDE, persists across sessions
- **To switch model/thinking level:** run `agy` in TUI (interactive) mode and type `/model` → interactive selector appears → pick "Gemini 3.5 Flash (Medium)" → setting is sticky across sessions. WARNING: `/model` sent via `-p` headless mode is interpreted by the LLM, not the binary — LLM will hallucinate "switched to medium" while nothing actually changes. Only works in TUI.
- `GEMINI_API_KEY` set in `~/.zshrc` also helps: CLI reads IDE model preference correctly when key is present. Confirmed 2026-05-21: both together switched CLI from High → Medium.
- Python SDK (`google-antigravity`) works with `GEMINI_API_KEY` + explicit `thinking_level="medium"` in `LocalAgentConfig(generation={"thinking_level": "medium"})`. No CLI hang bugs in SDK path.
- **Vision / image input (verified 2026-06-02):** agy has NO image flag, but it reads images via `--add-dir <dir>` + naming the file path in the prose prompt (e.g. "look at the image at /tmp/x/test.png and read it"). It has a vision-capable file tool — confirmed reading a controlled screenshot's random token + number + status word exactly. Use for OCR, screenshot-to-bug, chart/diagram/decode-from-image reads. (Gemini-family vision; pairs with agy's edge-hunting strength on UI screenshots.)

## Silent hang — THREE causes, same symptom

A silent hang looks identical regardless of cause: no output, no error, near-zero CPU, `--print-timeout` ignored. There are three root causes:

**Cause A — input parser wedge (CSV/TSV or numbered sections).** Three confirmed hangs on 2026-05-20: full 24-row CSV (1h+), 10-row CSV with Chinese chars, 10-row CSV ASCII-only. Numbered-section headers also trigger it (confirmed: "Question one… Question two…" prose hung 13 min). The binary is stuck parsing input, not waiting for anything external.
- Fix: reformat as prose. Inline lists ("X, Y, Z") are fine; pipes, tabs, and commas are not. No numbered-section headers of any kind.

**Cause B — permission wait (missing `--dangerously-skip-permissions`).** By default agy pauses before running any shell command or file write and waits for explicit user approval. In headless `-p` mode this approval can never arrive — agy hangs silently. Same symptom as Cause A, different root: engine is waiting for a keypress, not stuck parsing.
- Fix: always pass `--dangerously-skip-permissions` for non-interactive use.

**Cause C — open-ended hard-recall with NO escape hatch (diagnosed 2026-06-04).** agy hangs when asked an open-ended question it cannot confidently answer AND given no way to bail — it loops trying to manufacture an answer it doesn't have until timeout. Full diagnosis + probe battery in "Wedge trigger #2" below.
- Fix: append a termination escape to recall/open-ended prompts — `若不確定就只答「不確定」，切勿留白` / "if unsure, answer only 'unknown', never leave blank". Converts the hang into an instant honest answer.

**Diagnosis**: if you see a silent hang, check three things: (1) does the prompt contain CSV/TSV or "Question N / Step N" headers? (2) did you pass `--dangerously-skip-permissions`? (3) is it an open-ended recall question with no escape clause?

## Known v1.0.0 bugs

**1. Input-parser wedge (CSV/TSV + numbered section headers).** See "Silent hang" section above for causes and fix. Confirmed hang corpus: 24-row CSV (1h+), 10-row CSV with Chinese chars, 10-row CSV ASCII-only (all 2026-05-20); "Question one… Question two…" prose headers with paragraph body (13 min, 2026-05-20). Numbered headers alone are sufficient to trigger — no table needed.

**2. Self-introspection is unreliable.** Asking `agy` about its own quota / rate limits returns generic public Gemini limits, NOT the user's actual consumption. There is no `agy quota` / `agy usage` subcommand. To check real usage: web dashboard at aistudio.google.com.

## Where it earns its keep
1. **Empirical pattern discovery** — "here are N positives and M negatives, find the simplest discriminator." Proven on BF67: Gemini found the yang/yin day-stem split in 6.5s, matching the shipped predicate.
2. **Second-opinion Ghidra reads** — paste decompiled pseudocode (as prose), ask what the function computes. Useful when stuck on a decode.
3. **Bulk reference summarization** — long external doc → one-paragraph distillation, saves Claude's context budget.
4. **Domain knowledge lookup** — specialized knowledge questions where Claude would have to reason from first principles. Proven 2026-05-23: identified that the "generals" on the 太乙 board were 六壬 十二天將 (not 太乙 八將) in one pass — a distinction that took Claude multiple dead-end analysis loops to approach. Saves more tokens than code-gen delegation when the blocker is *naming the right concept*.

## Where NOT to use it
- **Moira-parity judgment calls.** Gemini doesn't have AGENTS.md or memory context — it'll "fix toward doctrine" exactly as AGENTS.md warns against. Never let it decide between Moira output and textbook.
- **Target selection / ship-vs-wall calls.** Picking which BF/KT/QM target to tackle, deciding when a partial decode is acceptable to ship — those need cross-session context Gemini doesn't have.
- **Self-introspection.** When asked to list its own model IDs, it hallucinated (`gemini-3.1-flash-lite-preview` etc.) — the real model is `gemini-3.5-flash`. Don't trust it for facts about itself or the API surface.

## Verification rule
Treat any Gemini output like a junior's PR: run it through `scripts/chart-diff/` against Moira.jar before trusting any predicate or decode. "Seems right" is not sufficient.

**Critical: agy fabricates "run" output.** When agy writes a script and then describes a verification run with realistic-looking output, that description is often fabricated prose — agy narrating what success would look like, not reporting an actual execution. Proven 2026-05-23: agy output included a JSON block claiming "PASS" for `extract-palaces.py` — the script happened to work, but the claimed run was not real. Always execute the script yourself and verify independently.

## Verified capability profile — 2-round controlled experiment (2026-05-30 → 06-02, vs codex + Opus)
Round 1 was single-run with asymmetric task/lens assignment (its tool-specialization conclusions
were artifacts). Round 2 fixed it: equal coverage (both tools, 5 tasks incl. a new algorithmic
expression-evaluator, × py/ts), replicated ×3, frozen pre-registered suites, symmetric lenses.
Net verified findings (artifacts: `claude-code-technique/experiments/tool-comparison/`):

- **Implementation: ties codex on well-specified tasks.** 60 Round-2 runs → agy 60/60 (both
  languages, every trial, including the new algorithmic task). No quality gap on anything the spec
  states. (agy uses looser typing — `any` — vs codex's `readonly`/`unknown`.)
- **Review: equal to codex under the SAME lens — no correctness blind spot.** Correctness lens →
  agy caught 5/5 (seeded LRU) and 6/6 (seeded retry) planted defects, including the TTL `>=`
  boundary, the backoff-exponent off-by-one, and `maxAttempts<1`. Architecture lens → strong design
  findings (O(n)/`OrderedDict`, FIFO-vs-LRU, separation of concerns). Round 1's "agy is weak at
  correctness" was purely the architecture lens it had been handed.
- **Precision depends on FRAMING, not capability.** Told to *verify against a contract* → precise,
  zero false positives. Told to *try to BREAK it* (adversarial) → HIGH RECALL / LOW PRECISION: it
  surfaces real edge cases others miss (found a `tryAcquire(NaN)` corruption bug my own tests
  missed — its standout strength) but also flags out-of-scope or even correct behaviour as "FAIL".
  → Choose the framing for the job; triage hunt-mode output by reproducing each finding.
- **Higher variance than codex, run-to-run.** A bug agy wrote once (TS LRU `undefined`-key leak via
  an over-clever `!== undefined` guard) did NOT reproduce in 3 later trials (it used the correct
  guard). Its idioms vary between generations. → A single agy run is NOT representative: **sample
  ≥2× when correctness matters, and review its guard clauses**, not just the happy path.
- **Fabricates run AND review output** — narrates "PASS"/"FAIL" that never executed. Always verify
  by execution; reproduce every agy-claimed defect.
- **Cross-family check beats self-review.** What agy (and my own tests) missed was caught by a
  different-family reviewer (Opus). When a result matters, cross-check across model families.

## Auth notes
- Shared with Antigravity IDE — no API key needed for `agy`.
- The Python SDK (`pip install google-antigravity`) requires `GEMINI_API_KEY` explicitly. Cannot reuse the agy Google-login cred cache (unverified, but no SDK example shows OAuth).

## End-to-end delegation with tool access (added 2026-05-21)

`agy` has tools — bash, file edit/write, `adb` (confirmed at `/opt/homebrew/bin/adb`), `--add-dir` for workspace access. With `--dangerously-skip-permissions`, it runs commands and edits files non-interactively in `-p` (print) mode. Proven this session: agy shipped QM year plate port end-to-end (commit `361b431`) — read plan + source, applied 3 edits, ran tsc + vitest, reported pass.

**Invocation pattern for code-writing delegation:**
```bash
# Prompt in a file (avoid HEREDOC + zsh-eval escaping issues)
agy --add-dir /Users/yauch/Documents/moira/moira-web \
    --dangerously-skip-permissions \
    -p "$(cat /tmp/agy-prompt.txt)" \
    > /tmp/agy-output.txt 2>&1 &
```
- Background it; harness emits `task-notification` on completion (~minutes for multi-step).
- Check progress: `ls -la <output-file>` (size growing?), `ps -ef | grep "agy "`, `git status --short`.

**Refined delegation contract:**

Delegate to agy:
- Oracle captures — write capture-X.sh, `adb shell ./oracle ...`, dump JSON.
- Bipartite analysis — load N-row sweep, find discriminator, output formula.
- Single-file ports following an explicit plan + acceptance criteria.
- Disasm reading with given address anchors.
- Sweep test harnesses, fixture generators.
- Routine TS implementations when the algorithm is spelled out in prose.

Keep for claude:
- Moira-parity judgment (above).
- Target selection / ship-vs-wall calls.
- Hypothesis design + falsification probes — esp. resisting doctrinal pattern-matches.
- Wall analysis (why is this cascade-dependent; what's the next layer).
- Reviewing agy's diff before commit (the "junior PR" check).

**Cost of NOT delegating** — confirmed 2026-05-21 by the QM 3yDay misfire. Claude pattern-matched 3 fixtures to "拆補 against day pillar," shipped, tests failed, reverted, then did the empirical-first sweep that should have been step 1. ~15 min of context burned on the doctrinal prior. agy would have done the sweep cold without the bias.

**Late delegation tax** — confirmed 2026-05-23 (太乙 八將 Phase B). Claude burned ~1,500 tokens on manual formula analysis before delegating; agy then resolved the question in one pass. The pattern: Claude starts trying to "just quickly check" a hypothesis, runs 3–4 manual iterations, then delegates. The manual iterations were wasted. **Rule: if you catch yourself running a second formula hypothesis, stop and brief agy instead.** The briefing cost is always less than the second dead-end.

**Heuristic** — if about to write a capture script, sweep harness, or routine port: pause, brief agy. Briefing cost is small. Context-burn from direct execution is real (CLAUDE.md rule 6).

## Sync vs async delegation

- **Analysis tasks** (read-only, expected < 60s): run sync with a `until` poll loop:
  ```bash
  agy --dangerously-skip-permissions -p "$(cat /tmp/prompt.txt)" > /tmp/out.txt 2>&1 &
  PID=$!
  until ! ps -p $PID > /dev/null 2>&1; do sleep 5; done
  cat /tmp/out.txt
  ```
  No need to background and resume — the wait is short enough to stay in the same turn.

- **Code-writing tasks** (file edits, multi-step, expected > 60s): background with `&`, harness notifies on completion. Check `git status` and output file size on wake.

- **No `--add-dir` needed** for analysis tasks where data is pasted inline. Only needed when agy must read project files itself.

## Inline data format for analysis prompts

The wedge bug triggers on CSV/TSV and numbered section headers. For data tables, use this safe inline format:
```
C26 陰 太乙=P4: P2:勾陳 青龍  P3:朱雀 騰蛇  P6:太常 白虎
C27 陰 太乙=P4: P2:六合 勾陳  P3:騰蛇 貴人  P6:白虎 天空
```
Space-separated, colon-keyed, no pipes, no tabs, no commas. Confirmed safe on 2026-05-23 with 29-row dataset.

## Wedge trigger #2 — open-ended hard-recall WITHOUT an escape hatch (diagnosed 2026-06-04)

Distinct from the CSV/numbered-section wedge. agy hangs (returns EMPTY / "timed out waiting for
response", exit 0) when asked an open-ended domain question it cannot confidently answer AND given
no way to bail. It loops trying to manufacture an answer it doesn't have until the harness times out.

Isolated by probe battery (all reproducible, agy itself confirmed alive via "PONG"):
- OK instantly: trivial prompts, neutral facts, KNOWN terms (奇門 三奇→乙丙丁), confident yes/no even
  in-domain ("太乙 大游 冬至後是否逆行？只答是或否"→是), long neutral prompts (~400c → NOT length-driven).
- TIMEOUT (3×, reproducible): "太乙 大游冬至逆行 有專門名稱嗎？" — short, single-focus, but open-ended
  recall of an esoteric term it lacks. Hangs with NO output.
- The SAME question + escape "若不確定就只答「不確定」，切勿留白" → returns "不確定" in 9 chars instantly.

ROOT CAUSE: agy can't admit ignorance unprompted on hard-recall — it wedges instead of saying "don't know".
FIX (always do this for recall/open-ended prompts): append an explicit termination escape, e.g.
  「若不確定就只答X，切勿留白」 / "if unsure, answer only X; do not leave blank".
Converts hangs into clean "don't know" answers. Pairs with the existing rule: keep prompts prose, no
CSV/TSV/numbered headers. Corollary: a clean "不確定" means agy genuinely lacks the knowledge — stop
asking and find another source (here: 太乙 大游 冬至-reflection doctrine name — agy does NOT know it;
derived empirically from 易匠 captures instead, which is the project oracle anyway).

**CAVEAT — the escape hatch is NOT a guaranteed fix (n=1 counter-example, 2026-06-13).** On a 六壬
月神 神煞 orthodoxy question (which of two 12-value branch sequences is canonical), agy hung with
0 output until killed (exit 144) **even though all three known causes were ruled out**: no CSV/
numbered headers, `--dangerously-skip-permissions` present, and the `若不確定就只答「不確定」，切勿留白`
escape clause appended. A retry that ALSO inlined the table values (dropping `--add-dir`, to test the
file-read-wedge hypothesis) hung identically — so the wedge was the **question content**, not the
file-read or the missing escape. Takeaways: (1) the escape hatch *reduces* but does not *eliminate*
hang risk on hard-recall/judgment prompts — it is not load-bearing. (2) For a **must-deliver**
cross-check, do NOT route a recall/judgment question to agy at all; codex (read-only) answered the
exact same investigation cleanly with file:line provenance while agy AND opencode-free both produced
nothing across retries. Reserve agy for cheap lookups where a hang costs only a `pkill` — never put it
on the critical path. (3) Same session: opencode free models (big-pickle, nemotron) returned 0 bytes
×3 on a tool-use file-review prompt while a trivial no-tool PONG worked — symmetric lesson, see the
opencode playbook.

## CONCEPT ≠ MECHANISM — agy names what to look for, never what's there (2026-06-09, QiMen 節氣 engine)
A web-port 節氣 cusp differed from the APK by a clean +0.58·sin(2L) min residual; real bug was a
one-coefficient transcription slip in the solar-longitude series (a 2L term's amplitude written as the
adjacent term's phase). Two findings from agy's role in the fix:
- **agy's QUANTITATIVE physics prediction was accurate** — it predicted a 0.54·sin(2L) min effect;
  measured 0.581. Its "domain-knowledge lookup" use case EXTENDS to order-of-magnitude prediction that
  doubles as a ground-truth cross-check. Worth the ~6s call. (It also correctly ruled out solver
  under-convergence and NAMED the concept: a 2·L_sun nutation-in-longitude term.)
- **CONCEPT ≠ MECHANISM (parity guardrail held).** agy named the concept right but its MECHANISTIC
  prescription — "you're MISSING the term, ADD -1.32″·sin(2L)" — would have been a doctrinal fudge.
  The truth was the OPPOSITE: the term was already PRESENT with a wrong amplitude. NEVER ship agy's
  prescription. agy names what to LOOK FOR; the binary (via codex byte-decode) says what's ACTUALLY
  there; your own ground-truth harness decides. Same shape as the existing "fix toward doctrine"
  warning — agy defaults to "add the missing canonical term," not "audit the existing one." The
  escape-phrase habit worked (no hang).
