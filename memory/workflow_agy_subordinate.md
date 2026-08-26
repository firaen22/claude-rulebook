---
name: workflow-agy-subordinate
description: "Playbook for calling the Antigravity CLI (`agy`, Gemini Flash family) as a subordinate tool from Claude sessions to offload pattern-discovery and decode-reading work. Established 2026-05-20 after empirical experiment on BF67. DEFAULT 2026-08-14: gemini-3.7-flash-medium (N=175, ties 3.6 + wins transport); review-dispatch pin stays gemini-3.6-flash-high."
metadata: 
  node_type: memory
  type: workflow
  originSessionId: d0fc7ada-52e0-4711-bae0-899ed2f8e5ae
---

# Calling `agy` (Gemini 3.5 / 3.6 Flash) as a subordinate

> **Model default (updated 2026-08-14):** pin **`--model gemini-3.7-flash-medium`**
> for general subordinate use — N=175 five-arm probe (`finding_agy_37_subordinate_2026-08-14.md`),
> agy v1.1.12. 3.7 ties 3.6 on adversary recall (24/24 both), fabrication (0), and
> contract compliance, and wins only on transport: 0 failures in 105 calls vs 3.6's
> 3 in 70. It is NOT safer on unstated edges (3.7-medium guards 0/5, same as 3.6-medium).
> Review/adversary dispatches STAY on
> `gemini-3.6-flash-high` — **the real-repo packet sweep this line used to demand has
> now been RUN (2026-08-18, agy v1.1.14, `finding_agy_review_packet_sweep_2026-08-18.md`):
> 3.7-high 23/30 vs 3.6-high 22/30 ledger defects over 6 whole-file packets mined from
> fix-commits, Fisher p=1.000 → NO SEPARATION.** The pin stays, but it now rests on a
> measured tie rather than untested inheritance. Do not re-open without a new model
> tier or a harder battery.
> **ALWAYS RETRY agy ON AN EMPTY RETURN when the prompt carries a real packet.** The
> empty-return rate scales with prompt size: 6/36 (17%) on ~8KB packets vs 3/70 (4%)
> on small probe prompts, ALL of them on the two largest packets. Signature is rc=0,
> empty stderr, fast return; immediate re-invocation succeeds. A single empty return
> is NOT "no findings" — treat it as transport and retry up to 3x. Earlier text below saying the default is
> 3.6-medium is superseded. Use
> `gemini-3.6-flash-high` for review/adversary dispatches — field-confirmed 2026-07-21
> (market-index sweep-14 head-to-head on identical packets: -high found the sweep's best
> bug, one another reviewer actively defended as correct; -medium fabricated two
> cross-file contract claims about non-inlined files; zero fake verification tags on
> either tier). Standing rule: treat any agy claim about a file NOT inlined in the
> packet as fabricated until read yourself. Older sections below were
> measured on **3.5-flash-medium** — where they conflict with the 2026-07-22 finding
> at the end, the newer finding wins. NO agy tier is edge-safe: spec every edge
> explicitly regardless of model. agy's served endpoint DRIFTS day-to-day behind a
> fixed model string, so any edge-safety *number* here has ~1-day shelf life — re-run
> the probe before reusing one, and never against a different prompt phrasing.
> **2026-08-25: `gemini-3.7-flash-low` passed its fresh-day edge-guard gate (15/20 vs
> 14/20; medium 4/20 same day) — candidate pin for edge-SENSITIVE dispatch only; see
> the 3.7-flash-low section below. Medium stays the general default.**

> GLOBAL playbook — applies to ALL projects. Concrete examples below are from the moira project,
> but agy's *behaviors* (wedge triggers, fabrication, run-to-run variance, vision, delegation
> economics) generalize. Substitute your own oracle/verifier for the moira-specific `chart-diff`.

## Invocation
```
agy --model gemini-3.7-flash-medium --dangerously-skip-permissions -p "<prose prompt>"
```
- Returns in ~5–7s on small prompts
- Auth: Google login via the Antigravity IDE, persists across sessions
- **Model selection (v1.1.5) — use the `--model` flag.** `agy --model <id> -p "..."` works
  headlessly and is the correct way to pin a model per call. `agy models` lists what is
  callable. Verified 2026-07-21 across 60 headless calls; the flag demonstrably takes
  effect (3.5 vs 3.6 produced systematically different code under byte-identical prompts —
  see the 3.6 regression section — so it is not being silently ignored).
  ```
  agy --model gemini-3.7-flash-medium -p "<prose prompt>"
  agy models          # list callable models
  ```
  `agy --effort low|medium|high` also appears in `--help` @v1.1.5 but is **UNVERIFIED** — it
  was never exercised; only `--model` has evidence behind it. Unknown whether `--effort`
  interacts with the `-low/-medium/-high` suffix already baked into the model ID, or is
  independent. Do not assume it works; test before relying on it.
- **Lineup snapshot 2026-07-22** (`agy models`, volatile fact — re-run before relying):
  `gemini-3.6-flash-{high,medium,low}`, `gemini-3.5-flash-{medium,high,low}`,
  `gemini-3.1-pro-{low,high}`, `claude-sonnet-4-6`, `claude-opus-4-6-thinking`,
  `gpt-oss-120b-medium`. Measured tiers: **3.5-flash-medium** (the playbook baseline)
  and **3.6-flash-medium** (2026-07-21 N=60 probe — see regression section). Everything
  else was unmeasured as of 07-21; 3.6-low/medium/high were later measured N=140
  (2026-07-22, see below) and 3.6-flash-high is the standing review-dispatch pin.
  The claude-* / gpt-oss entries route non-Gemini models through agy — untested on this
  path; first-party Claude delegation stays on native subagents, not agy.
- **STALE (pre-v1.1.5, corrected 2026-07-21):** the old rule "model switching only works in
  TUI via `/model`; there is no flag" is **no longer true** — `--model` is a real binary flag.
  What remains true: typing `/model` *inside a `-p` prompt string* is interpreted by the LLM,
  not the binary, and it will hallucinate "switched to medium" while nothing changes. Pass the
  flag, never the slash-command.
- `GEMINI_API_KEY` set in `~/.zshrc` also helps: CLI reads IDE model preference correctly when key is present. Confirmed 2026-05-21: both together switched CLI from High → Medium. **Likely superseded by `--model` at v1.1.5 (untested) — prefer the explicit flag; do not rely on this env-var path for model pinning.**
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

**Diagnosis**: if you see a silent hang or 0-byte output, check four things: (1) does the prompt contain CSV/TSV or "Question N / Step N" headers? (2) did you pass `--dangerously-skip-permissions`? (3) is it an open-ended recall question with no escape clause? (4) is this a **sandboxed session**? antigravity-cli must bind a localhost port; under sandbox it fails "operation not permitted" with 0-byte output — that's NOT a wedge, agy is simply unavailable, so plan fleet composition around sandbox status.

## Known bugs — found at v1.0.0, NOT retested at v1.1.5
Treat all of these as still-open: none was re-probed after the CLI moved to v1.1.5
(2026-07-21), so absence of recent reports is not evidence they were fixed.

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
- **Self-introspection.** When asked to list its own model IDs, it hallucinated (`gemini-3.1-flash-lite-preview` etc.). Don't trust it for facts about itself or the API surface — use `agy models` (the binary), never the model's self-report. Reconfirmed 2026-07-21: asked to state its own model, the default invocation answered "Gemini 3.5 Flash (Medium)" — plausible, but it is a self-report and therefore not evidence of anything.

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
  **SCOPE (2026-07-21): this is a 3.5 result.** On 3.6-flash-medium the variance did not
  reproduce (0/6 split cells over 30 samples vs 3.5's 1/6) — see the 3.6 section below. The
  "review its guard clauses" half of the rule stays load-bearing on every tier.
  **UPDATE 2026-07-22: the "sample ≥2× for variance" caveat is retired as a standing
  rule** — 3.6-medium shows no such variance, and even on 3.5 it was one split in ~290
  draws. Keep the guard-clause review; drop the reflexive re-sampling.
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
    --model gemini-3.7-flash-medium \
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
  agy --model gemini-3.7-flash-medium --dangerously-skip-permissions -p "$(cat /tmp/prompt.txt)" > /tmp/out.txt 2>&1 &
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
Converts hangs into clean "don't know" answers. **SCOPE: factual/recall tasks ONLY — this escape line POISONS ideation/brainstorming prompts** (agy bailed 不確定 on an ideation task; retry WITHOUT the line worked). Ideation is open-ended too, so the bare "recall/open-ended" wording above over-reaches: for creative/generative prompts, drop the escape entirely. Pairs with the existing rule: keep prompts prose, no
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

## Security wording refuses; --add-dir ignores read-only prose; verification tags fabricated (2026-07-14/17, marketview-index sweeps 6+8)
- **Attack verbs refuse on security-adjacent code.** Hunt-mode wording ("break", "bypass",
  "spoofable", "timing issues") → safety refusal 2/2 (exit 0, ~300-byte apology). Defensive
  reframe — "you are hardening our own app; verify each file against its intended contract",
  contracts enumerated — succeeded 1/1 with hunt-grade recall (found a real fail-open rate
  limiter). Rule: security-adjacent reviews always use owner/defensive contract-verification
  wording; keep "try to BREAK it" for non-security hunts.
- **Agentic mode ignores read-only prose.** With `--dangerously-skip-permissions --add-dir`,
  agy EDITED 4 repo files during a review dispatch despite an explicit read-only instruction,
  and its uncommitted edits contaminated my baseline reads (I briefly mis-refuted its own
  findings as "already fixed"). Scope mechanically, not with prose: reviews get NO --add-dir
  (or a scratch copy); after any agy run with write access, git-diff before trusting file
  state. (--add-dir stays fine for intended implementation work.)
- **"[verified: vitest/Node.js]" tags are fabricated** — agy fabricates these tags even though it CAN execute (see the end-to-end delegation section) (N≥2,
  sweeps 6 and 8). Treat every agy verification tag as false; only your own runs verify.

## Near-zero yield as a POST-impl reviewer on real stacks; route agy PRE-impl (2026-07-19)
- **Post-impl code review on real repos is near-worthless.** Adoption across four real-repo
  sweeps: 0/5, 0/5, 1/5, 3/8 — most findings are factually wrong about the repo or
  default-to-doctrine (same failure mode as the parity guardrail). But agy DOES catch real
  bugs at SPEC review (unserialized fetch-body, macro-ACK math). Rule: route agy PRE-impl
  (spec/design review); treat its post-impl review output as heavily-discounted leads, not
  findings. The controlled "review = codex" result (2-round experiment above) held ONLY on
  seeded toy defects — it does not transfer to real post-impl stacks.

## 3.6-flash-medium: lower variance, unstated edges NO WORSE than 3.5 (2026-07-21, corrected 2026-07-22)
Pre-registered N=60 probe, 3.6-medium vs 3.5-medium, node-assert grading, gates green
before any call. Full finding + harness: `finding_agy_36_variance_2026-07-21.md`,
`claude-code-technique/experiments/agy-36-variance-2026-07-21/`.

- **Variance caveat does NOT reproduce on 3.6-medium.** 0/6 split cells across 30 samples
  (3.5 baseline: 1/6). Tight-spec accuracy identical: both 15/15.
- **~~3.6 REGRESSES on the unstated-edge blind spot~~ — RETRACTED 2026-07-22, did not
  replicate.** 2026-07-21 measured 3.6 guarding the unstated `size=0` edge 0/5 vs 3.5's
  4/5 and called it a regression. The N=140 re-run one day later (same harness, same
  prompt, agy v1.1.5) got **3.5-medium = 1/5**, not 4/5 — the gap was a one-day endpoint
  artifact. Corrected truth: **all** agy tiers miss this edge most of the time
  (3.6-low 1/5, 3.6-medium 0/5, 3.6-high 2/5, 3.5-medium 1/5), and **effort tier does
  not fix it** (K1 falsified). Standing lesson: agy edge-safety numbers have ~1-day
  shelf life; the only durable rule is spec edges explicitly + timeout-wrap execution.
- **THE UNFLAGGED DEFAULT IS ALREADY THE WORSE ONE (verified 2026-07-21, N=5).** Plain
  `agy -p ...` with no `--model` scored guard **0/5** on the fingerprint above — behaviorally
  indistinguishable from 3.6-medium (0/5) and clearly distinct from 3.5-medium (4/5). So
  every existing unflagged agy call in every project is *already* getting the worse-on-edges
  behavior. (Asked directly, it self-reports "Gemini 3.5 Flash (Medium)" — false, exactly as
  the self-introspection rule warns. Fingerprint by behavior, never by asking.)
  Strength: this proves the default is **not 3.5-medium**; it does not prove *which* newer
  tier it is — 0/5 is consistent with 3.6-medium and with any other non-guarding variant.
- **Rules:**
  1. **Always pass `--model` explicitly on correctness-bearing work.** Never rely on the
     default — it is not what the older sections of this playbook were measured on, and it
     silently changed under a CLI update.
  2. ~~Prefer 3.5 for unstated-edge safety~~ — RETRACTED 2026-07-22: 3.5 is not safer
     (1/5 guard on re-run). Default was `--model gemini-3.6-flash-medium` at the time (superseded 2026-08-14 by 3.7-flash-medium — see banner); no tier is edge-safe.
  3. The pool-wide **spec edges explicitly** rule is now load-bearing for agy, not optional.
     Spec NaN/undefined/empty/zero/negative in every agy hand-off.
- **Timeout-wrap every execution of agy-written code, on ANY model tier** (3.5 missed the
  guard 1/5 too). A missing edge guard surfaces as a hang or an OOM, not a wrong answer, so
  an ungraded run can burn a machine instead of failing. Concretely: run it as
  `timeout 15 node cand.js` (or the equivalent for the language), never bare.
- **Do not quote "0/6 split" alone.** One of those clean cells is clean-by-consistently-
  FAILING (`[0,0,0,0,0]`); a split-cell metric cannot tell that from consistent success.
- **Scope:** `-medium` only (`-low`/`-high` untested here — but covered by the 2026-07-22
  finding below); 3 JS pure-function tasks, N=5 — coarse variance only, says nothing about
  multi-file/debugging/agentic work.

## 3.6 as a subordinate — the N=140 four-arm probe (2026-07-22)
Pre-registered, all 5 gates green pre-run, hand-adjudicated (Rule 3). Full finding +
harness: `finding_agy_36_subordinate_2026-07-22.md`,
`claude-code-technique/experiments/agy-36-subordinate-2026-07-22/`. 3.6-low/-medium/-high
+ 3.5-medium comparator.
- **K1 FALSIFIED — effort tier does NOT fix unstated edges.** Guard rate on `chunk(arr,0)`
  by execution: 3.6-low 1/5, 3.6-medium 0/5, 3.6-high 2/5, 3.5-medium 1/5. No tier reaches
  the ≥4/5 bar. Spec edges explicitly on every tier.
- **Adversary/edge-finder role: 24/24 recall, ALL four arms** (after hand-fixing 6 regex
  false-negatives). Saturated — agy keeps the slot, but this battery can't rank tiers.
  Every arm also found real defects beyond the ledger (EXP-6 "false positives are usually
  real" pattern again).
- **Fabrication: 0/32** with the "if unsure, answer only 'unknown'" clause. Reporting
  contract (conclusions + file:line, no code blocks): 8/8 PASS all arms.
- **C2 "hangs on structured INPUT" — FALSIFIED at every tier:** 8/8 JSON-blob prompts
  completed. A single JSON object + a prose instruction does not wedge. (The CSV/TSV/
  numbered-header wedge is a different shape and still assumed live; not retested.)
- **Transport reliability is the real per-tier difference:** timeouts per 35 calls —
  3.6-medium 1, 3.6-high 2, 3.6-low 3, **3.5-medium 6** (+1 empty). 3.6 is more reliable.

## 3.7-flash-low: fresh-day edge-guard replication PASSED — candidate pin for edge-sensitive dispatch (2026-08-25)
The 2026-08-14 N=175 probe found `-low` guarding the unstated `chunk(arr,0)` edge
14/20 vs `-medium` 2/20, and named ONE remaining gate before pinning it: a fresh-day
repeat of `probe_lowguard.py` unchanged. That gate is now PASSED.
Harness: `claude-code-technique/experiments/agy-oldprompt-replication-2026-08-25/`
(probe byte-identical to the 08-14 original, md5 `7152b5fba2bec0893e92880c390c2f0c`);
finding: `finding_geminimd_and_fleet_probe_2026-08-25.md` Result 5, which survived a
fresh-context adversarial review (YES-WITH-CAVEATS, all counts/p-values reproduced).
- **`-low` 15/20 today vs 14/20 on 08-14 (p=1.000)** — clean replication, 11 days and
  a CLI bump (1.1.12→1.1.19) apart. Same day, same frozen prompt set:
  **`-low` 15/20 vs `-medium` 4/20.** Effort is non-monotonic on edges, consistent
  with K1's falsification.
- **Routing:** `-low` is the **candidate pin for edge-sensitive implementation
  dispatch** (the specific use the 08-14 finding scoped it to). `-medium` STAYS the
  general default — its justification is transport, and `-low` had the worst
  transport of the 3.6 arms; nothing here re-tests 3.7-low transport at scale.
- **NOT edge-SAFE:** 15/20 = 75%, still under the original K1 ≥4/5 bar per
  paraphrase (P1_terse was 1/4 even for `-low`). Spec edges explicitly on every
  tier, `-low` included; keep the timeout-wrap.
- **Instrument lesson (the reason Result 5 exists):** a same-day 9/10 guard score
  for `-medium` on a NEW prompt phrasing turned out to be a PROMPT-DIFFICULTY
  artifact — the frozen old prompts still score `-medium` 4/20 (vs 2/20 on 08-14,
  p=0.661, no model change). **Never compare an agy edge-guard number against a
  prior measured on different prompt phrasing**; the ~1-day-shelf-life rule above
  now has a second leg: same-instrument or no comparison.

## 3.6-flash as post-impl REVIEWER: high > medium; format discipline good; cross-file fabrication persists (2026-07-22, marketview sweep 14)
First review-dispatch use of 3.6 (one `-medium` + one `-high` sample, same ~42KB packet:
5 inlined React/TS files with `nl -ba` line numbers, callee contracts enumerated, defensive
framing, escape hatch appended). Both compared against codex + big-pickle + NIM on
overlapping surface, every finding adjudicated by execution/read-back.
- **No hang on inlined `nl -ba` code + `===== FILE =====` separators** (n=2). The CSV/
  numbered-header wedge did not fire on this shape; both returned in ~1 min.
- **Format discipline is a real 3.6 improvement**: both samples followed the exact
  file:line/MECHANISM/FIX/SEVERITY/tag contract, no filler, honest per-file "no bugs found"
  sections, no fabricated verification tags (first sweep with zero fake "[verified]" from agy).
- **Yield — HIGH beat MEDIUM decisively.** `-high`: 5 findings → 2 real (incl. the best bug
  of the sweep: a stale-`useState`-initializer modal bug every other reviewer missed and
  big-pickle explicitly defended as correct), 1 adopted-defensive, 1 design-nit, 1 refuted.
  `-medium`: 4 findings → 1 real (shared w/ high), 1 adopted-defensive, **2 fabricated
  cross-file contract claims** (invented a callee's lookup key; claimed a locale key missing
  that exists — both about files NOT in the packet, despite instructions not to speculate).
- **Rules:** for agy review dispatches prefer `--model gemini-3.6-flash-high`. Treat ANY
  agy claim about a file not inlined in the packet as fabricated until read yourself —
  3.6 did not fix this. The 2026-07-19 "route agy PRE-impl" discount stands for medium;
  high earned a partial exception (2/5 adopted) but still below codex precision.
