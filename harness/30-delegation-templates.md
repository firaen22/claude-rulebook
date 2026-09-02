# Delegation Prompt Templates

Copy the template, fill every `{{field}}`, delete nothing except clearly-marked
optional blocks. Each template already embeds the three-part package (goal+why /
acceptance criteria / reporting format) and the reporting contract from
`10-orchestration.md` §3–§4. Executor choice: `10-orchestration.md` §2.

Universal rules baked into all templates — do not remove them when filling in:
- "Report failure honestly" line: every subordinate fabricates success under
  pressure; the line measurably reduces it and costs nothing.
- Edge-case spec: unstated edges are the shared blind spot of all model tiers.
- Long output → file + path, never inline.
- Subagents do NOT inherit your scratchpad path or env — every `{{scratch path}}`
  field must be a literal absolute path you write into the prompt.
- Deliverable IS a scanner/checker/guard → acceptance criteria MUST include
  executing the deliverable against one known-positive and one known-negative
  input, with both observed outputs in the report. Measured 2026-08-24: the
  dominant failure across 18 codex runs (flat across every rule configuration)
  was shipping a scanner whose scan never executes — prose care doesn't prevent
  it; a required execution does. Corollary for red-tests: the injected failure
  must be REACHABLE (a failing line after `exit` silently reports green).

---

## T1 — SEARCH / codebase exploration
Executor: Agent `Explore`, model sonnet (haiku if single-fact).

```
GOAL: Find {{what — e.g. "every place user-facing currency amounts are formatted"}}.
WHY: {{decision this feeds — e.g. "we will change rounding; I need the blast radius"}}.

SCOPE: Search under {{paths}}. Also check {{naming variants / synonyms / conventions
to try — e.g. "format, fmt, toFixed, Intl.NumberFormat"}}. Breadth: {{"medium" |
"very thorough — multiple locations and naming conventions"}}.

ACCEPTANCE CRITERIA:
- Every match listed as file:line + one-line description of what happens there.
- Explicitly state which directories/patterns you searched and which you did NOT.
- Distinguish definite matches from possible ones.

REPORT FORMAT: A list of file:line entries grouped by {{grouping}}, then a 3-line
summary (count, clusters, surprises). No file contents. If >30 matches, write the
full list to {{scratch path}} and return the path + the summary.
If you find nothing, say "nothing found" and list what you tried — do not pad.
```

## T2 — IMPLEMENTATION (spec'd)
Executor: codex CLI (airtight spec) or Agent `general-purpose` sonnet.

```
GOAL: Implement {{feature/fix}} in {{files/module}}.
WHY: {{user-visible reason}}.

SPEC:
- Behavior: {{exact input → output pairs, at least 2 normal cases}}.
- EDGE BEHAVIOR (mandatory, be explicit): empty input → {{...}}; zero → {{...}};
  negative → {{...}}; null/undefined/NaN → {{...}}; oversized → {{...}}.
- Do NOT touch: {{files/behaviors out of bounds}}.
- Match existing conventions in {{reference file}}.

ACCEPTANCE CRITERIA:
- {{test command, e.g. "pytest tests/x_test.py"}} exits 0.
- New behavior covered by tests that FAIL without the change (state which test).
- No changes outside {{allowed paths}} (verify with git diff --stat).

REPORT FORMAT: files changed (paths only) + git diff --stat output + test command
with exit status + any criterion NOT met, stated plainly. Do not claim success you
did not observe: a truthful "blocked because X" is a good report; a fabricated
"all tests pass" is the worst possible report.
```
Dispatcher note: YOU then rerun the test command yourself and read the diff before
accepting (R0). Then fresh-context review (T5) for anything non-trivial.

## T3 — REFACTORING
Executor: Agent `general-purpose` opus (convention judgment) or codex (mechanical,
pattern proven first). Parallel agents ONLY on disjoint files.

```
GOAL: Refactor {{what}} from {{current shape}} to {{target shape}}.
WHY: {{pain it removes}}.

BEHAVIOR CONTRACT: zero observable behavior change. The proof is {{test suite /
golden output file / before-after command outputs to diff}}.
WORKED EXAMPLE: {{one instance already converted, shown before→after — mandatory
for batch refactors; do the first one yourself}}.

ACCEPTANCE CRITERIA:
- {{proof command}} identical/green before and after.
- All {{N}} instances converted; list any instance you judged different and
  SKIPPED, with reason (skip-with-reason beats forced conversion).
- git diff contains only the refactor pattern — no drive-by edits, no comment or
  formatting churn outside converted lines.

REPORT FORMAT: instance list (file:line → done/skipped+reason), proof-command
output summary (exit status + counts), git diff --stat. Full diff to a file if
>30 lines; return the path.
```
Dispatcher note: after the batch returns, spot-check ~20% of instances (minimum 2,
chosen at random) plus every instance flagged skipped/unusual — expected-before-
actual on each. Any spot-check failure → verify 100% of the batch.

## T4 — RESEARCH (web/docs)
Executor: Agent `general-purpose` sonnet.

```
GOAL: Answer: {{specific question(s) — numbered}}.
WHY: {{decision this feeds}} — so prioritize {{what matters: recency / official
sources / real-world reports}}.

ACCEPTANCE CRITERIA:
- Each numbered question gets a direct answer, or "not determinable" with what
  was tried.
- Every factual claim has a source URL and a date.
- Each claim tagged with confidence: [confirmed — 2+ independent sources] /
  [single-source] / [inference].
- Prefer official docs > maintainer statements > blog posts > forums. Note when
  sources CONFLICT rather than averaging them.

REPORT FORMAT: per question — answer (≤3 sentences), then sources. Then one
"caveats" block: what's stale, what conflicts, what you'd verify by running code.
Anything long (comparison tables, quotes) → file, return path.
Do not fill gaps with your own knowledge silently — training-data claims get
tagged [inference] like any other unverified claim.
```

## T5 — REVIEW / acceptance verification
Executor: FRESH-context agent that did not produce the work. `agent-skills:
code-reviewer` sonnet for briefed scope; opus (+ second opinion from codex/agy)
for miss-is-costly surfaces. Give it the spec and the location of the work —
NEVER the producer's claims or self-assessment. **A second opinion from a
DIFFERENT model family (codex/agy/grok) is a cross-model-review skill dispatch
— load that skill first; it owns the packet/verdict/merge gate, this template
only picks WHO.** (2026-09-02, [[finding-cross-model-review-trigger-2026-09-02]])

```
ROLE: Independent acceptance reviewer. The work is at {{paths/diff/branch}}.
The spec it must satisfy is below. You did not write this; assume nothing.

SPEC + ACCEPTANCE CRITERIA: {{paste the original dispatch criteria verbatim}}.

REAL INPUT DISTRIBUTION (mandatory — describe what the code actually receives in
production): {{shape of real inputs, the weird-but-common cases, volumes — e.g.
"transcript lines: 4,325 of them start with a `<command-name>` tag; 24,897 are
tool_result payloads"}}. Measured 2026-08-28: two silent misses a 12-finding review
had passed were found by the reviewer whose brief described the corpus shape — a
reviewer given only the code reasons from CONTRIVED inputs and finds mechanism bugs;
one given the real distribution finds the path that actually fires them. If you cannot
describe the distribution, say so — do not invent one.

METHOD (follow exactly, in this order):
1. For each criterion, WRITE DOWN the input and the output you EXPECT if the work
   is correct — before looking at the actual code/output.
2. Then check actual against expected. Run {{test/build/run commands}} yourself;
   do not trust reported results.
3. Probe edges NOT in the criteria: empty/zero/negative/huge/malformed input,
   concurrent/repeated calls — whichever apply.
4. Check the diff for out-of-scope changes (git diff --stat vs allowed paths).

REPORT FORMAT: verdict first — ACCEPT / REJECT / ACCEPT-WITH-FIXES. Then findings,
severity-ranked, each as location (file:line) + mechanism (why it's wrong, with
the expected-vs-actual you observed) + suggested fix. Then: criteria checklist
with pass/fail each. "No findings" requires listing what you executed and probed —
an empty report with no evidence of work is a REJECT of the review itself.
```

---

## Dispatch checklist (30 seconds, every time)
- [ ] All {{fields}} filled — no template braces left.
- [ ] Edge behavior specced (T2/T3) or edge-probing required (T5).
- [ ] Every interface/signature/path in the spec was READ from source this
      session (quote file:line), not recalled — an imagined interface is how a
      plausible-but-wrong spec reaches the executor, which then fills the gap.
- [ ] Reporting contract present (conclusions + paths, long output → file).
- [ ] I know exactly what command I will run to verify the result myself.
- [ ] Executor per routing table; escalation state noted if this is a retry
      (attempt #, prior failure trail attached).
- [ ] REVIEW dispatches to a CLI: pick the packet SHAPE by executor — they are
      OPPOSITE, and getting it backwards costs the whole run while looking like the
      model is useless. **grok / opencode: STAGE the target as files in `--cwd`** and
      tell it to read them (an inlined target gave schema-valid EMPTY reviews that
      passed every existing guard, 2026-08-28). **codex: INLINE the target** (`nl -ba`)
      so it makes ZERO tool calls — staged files make it read everything, announce the
      report, then the final answer never reaches stdout and `-o` is never written.
      **agy: INLINE** too — it fabricates claims about files not inlined — and ALWAYS
      retry an empty return, whose rate scales with packet size. **Any executor not
      named here: STAGE, and verify the shape on one throwaway packet first** — staging
      degrades to a slow read, inlining degrades to silence.
      Size the codex packet under ~30KB and make each chunk SELF-SUFFICIENT (v0.149.0,
      measured 2026-08-29: 16/29.6KB fine, **32-45KB returns a confident preamble and
      no findings — the false-green band** — 51KB+ silent at rc=0). That number is
      VERSION-BOUND: on any codex upgrade, re-probe with one oversized packet before
      trusting the inline route. If you chunk, EVERY chunk must be dispatched and the
      verdicts accepted JOINTLY — a per-chunk verdict is blind to cross-chunk defects,
      and a review reported on a subset is a review of the subset.
      Whichever shape you pick, the BRIEF must describe that delivery — a brief that
      says "files in ./files/" beside an inlined packet sends the reviewer hunting for
      material that isn't there, in both tiers. (Distinct from "long output → file"
      above: that governs what comes BACK, this governs what goes IN.)
- [ ] Schema/structured returns: check ENGAGEMENT, not just validity — compare
      `usage.reasoning_tokens` against input size. 43 reasoning tokens on a 15k-token
      input is a non-review that parses perfectly.
