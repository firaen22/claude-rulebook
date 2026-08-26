---
name: ground-truth-gates
description: Build a deterministic regression gate (golden / replay / project — three gates) around any judgment-bearing function before changing it — classifiers, intent routers, regex matchers, redaction/PII scrubbing, text normalization, prompt-driven routing. Ships a runnable, already-run-verified template (node, zero deps). Use whenever the user asks for a test harness, golden set, eval, or regression gate; whenever you are about to edit a classifier/regex/redaction/prompt that routes real actions; whenever you are designing a runtime guard (a hook, validator, or auth check) and its fail direction; whenever an experiment needs a grading harness; and whenever you catch yourself (or a subordinate) saying "sounds right" or "should work" about behavior only real data can prove.
---

# Ground-Truth Gates

**The rule: no gate → no change to judgment-bearing behavior.** Behavioral
prompting ("be careful with this regex") does nothing measurable. A harness that
runs the REAL function over labeled REAL data converts "sounds right" into a
falsifiable pass/fail — the highest-ROI artifact in any project; build it BEFORE
tuning prompts, regexes, or classifier logic, not after the regression.

If this skill ever conflicts with `~/.claude/harness/`, the harness wins (R8).

## The three gates

| Gate | Locks | Mechanism |
|---|---|---|
| **Golden** | a classifier's decisions | labeled real cases run through the real function (no mocks), scored cost-asymmetrically |
| **Replay** | a pure transform's output | frozen baseline, diffed on every run; any drifted line fails |
| **Project** | everything at once | one command (`run-all.sh`) = typecheck + golden + replay; run it before claiming "done" |

## Quick start — bundled runnable template

The template lives in this skill's `scripts/` directory and is **run-verified**
(all pass AND fail paths executed 2026-07-07; the commands below are the exact
ones that ran). Zero dependencies beyond `node` ≥18.

```bash
cd ~/.claude/skills/ground-truth-gates/scripts

# whole project gate (typecheck optional: export TYPECHECK_CMD="npx tsc --noEmit")
bash run-all.sh                                  # → ALL GATES PASS, exit 0

# golden gate alone
node golden-gate.mjs --module ./example/classifier.mjs --cases ./example/cases.jsonl

# replay gate alone (freeze once with --update, eyeball, then run frozen)
node replay-gate.mjs --module ./example/redact.mjs --corpus ./example/corpus.jsonl \
  --baseline ./example/baseline.json
```

### Adapting to your project — change exactly three things

1. **Your function.** Point `--module` at a `.mjs` exporting your real
   `(text) => label | null` classifier (golden) or `(text) => text` transform
   (replay). Named exports: `--export <name>`. Async functions work. TS
   project: shim recipe in `references/worked-examples.md`.
2. **Your data.** `cases.jsonl`: one `{"input":"…","intent":"…"}` per line.
   `corpus.jsonl`: one JSON string per line. Real logged messages, anonymized
   (rules below) — synthetic cases never reach where regressions hide.
3. **Your fallback label.** `--no-match "(fallback)"` = whatever your system calls
   "defer to the expensive fallback" (LLM, human queue). Label hard negatives with it.

Copy `scripts/` into your project's `checks/` and rewire the five path
arguments in `run-all.sh` (golden: module + cases; replay: module + corpus +
baseline). Hook it to CI or a pre-commit once it's green.

## Cost asymmetry — the part that makes the gate worth having

A **false route** (classifier fires the wrong concrete action) is far worse than
a **defer miss** (falls through to the fallback — safe). Aggregate F1 averages
false routes away; the gate hard-fails on `falseRoutes > 0` regardless of F1 —
a run can pass the 0.90 macro-F1 threshold while a false route hides (measured
case: `references/worked-examples.md`).

Picking the hard-fail class in a new domain: ask "which wrong output triggers a
concrete action a human didn't confirm?" (sends the message, books the order) —
that's the false route. "Which wrong output just costs a fallback call?" — the warn.

## Building the case set from real data

The gate has teeth only if cases come from real logs. Export flow:

1. **Pull** a sample from the real source (Firestore/Postgres/S3 — you own the
   prod-read decision; ask the user if unclear).
2. **Anonymize structure-preserving** — replace PII VALUES, keep the SHAPE the
   classifier keys on (same-shape map per PII class + why:
   `references/anonymization-map.md`).
3. **Stage** to a gitignored `candidates.jsonl` review queue. Eyeball, fix
   labels, promote good lines into `cases.jsonl`. Never auto-promote (what to
   flag for a human glance: `references/worked-examples.md`).
4. **Include hard negatives** — real messages that LOOK like a command but must
   fall through (e.g. `我想睇下今個月嘅業績` when `睇下 <name>` is a command).
   These are where regressions hide and where synthetic cases never go.
5. **Live misfires are seed cases** — when the guarded function misfires on a real
   input mid-session, copy that input VERBATIM (never paraphrased) into the case set
   with its declared expected outcome, and after the fix re-run the
   originally-failing command as the final acceptance check. A suite grown this way
   keeps catching what synthetic cases never do.
6. **Validate the capture instrument, then taint on defect.** Cases minted through
   a lossy reader (OCR, screenshot, scraping): validate the reader against
   known-answer inputs first; keep a per-row capture artifact (anonymized per step
   2). A reader defect taints every conclusion derived from its output. Access
   control + the misread-screenshot case: `references/fake-pass-patterns.md`.
7. **Every row records how it was captured.** A hand-written "plausible" row
   converts the gate into a mirror of your own guess — corruption, not coverage.
   Rig unavailable → the honest state is BLOCKED naming the exact rig and recipe
   to unblock, never synthesis as a row in this case set. (A guard's labeled
   validation plant is a narrower, corpus-scoped carve-out for a different
   failure — see "Designing the guard itself" below — not an exception to this
   rule for the golden/replay case set itself.)
8. **Hold out a distribution-disjoint slice as the ship decider.** A corpus
   consulted during development can only warn of overfit; the deciding gate is a
   slice disjoint on a real dimension (date range, source, tenant) never seen in dev.
9. **Pattern ORDER in a first-match or sequential-replace chain is a load-bearing
   invariant** — more-specific must precede broader; a broad pattern placed first
   shadows the specific one silently (both incidents:
   `references/fake-pass-patterns.md`). Pin every ordering constraint with a case
   in this set before touching the chain.
10. **A green suite names the artifact it exercised.** A suite reaches its
    subject by name (import, `PATH` lookup, package entry), and that name can
    resolve to a copy other than the one you edited — a stale location, a
    shadowing install, a one-step-stale build. The code runs to completion and
    the scorecard is real; it's evidence about the wrong copy. Assert identity
    canonicalized on both sides, with a freshness/revision witness, and run
    any deployed-path claim through the production lookup — not just the one
    shadow you suspected (full rule + Done bar: `references/fake-pass-patterns.md`).
11. **A self-benefit metric ships the tests that keep it honest.** Where a tool
    measures its own benefit (a compression ratio, cost savings, "N
    duplicates removed"), the suite guards overstatement from both
    directions: the no-benefit case reads its independently expected value
    on the metric's OWN scale, at or beyond the declared no-benefit point in
    the harm direction; at least one known-benefit calibration anchor per
    supported input class reads within a PREDECLARED tolerance of its
    independently computed value; and a comparison is admitted only when the
    baseline matches the treated input's exact identity AND every
    benefit-affecting non-treatment variable is inventoried and matches or
    carries a predeclared normalization. Anything short is refused, not
    reported — otherwise this is the never-ran fake-pass family (Test/gate
    integrity below) wearing a dashboard: the flattering number can never fail.
    ❌ "the tool reports 40% savings on every run" — including on input it
    provably cannot compress; nothing asserted the zero-savings case, and
    nothing calibrated the 40%. Full rule (scale-clamp trap,
    omitted-variable admission): `references/fake-pass-patterns.md`.

## Replay-gate discipline

- Freeze (`--update`) once, **eyeball every line of the baseline**, commit it.
  The baseline IS the spec from then on — and it freezes *current* behavior, not
  *correct* behavior: any bug it contains is protected as ground truth (incident:
  `references/worked-examples.md`). Fix the transform first, then freeze.
- Drift = FAIL, always. If the drift is intentional: eyeball the printed
  baseline-vs-actual diff line by line, then re-freeze. Never `--update` to
  silence a failure you haven't read.
- Baseline missing at gate time is an error (exit 2), not a silent pass.
- Baselines are keyed by input string — duplicate corpus lines collapse to one
  entry; keep corpus lines unique.
- **Parity variant (no logged corpus).** Refactoring pure-ish logic (config
  parsing, path handling, formatting) often has nothing logged to replay. Keep the
  pre-change implementation *callable* and run old vs new over a declared input
  set, asserting identical output/exit (recipe + the freezing-source-text-is-not-
  parity trap: `references/worked-examples.md`).
- **A frozen baseline inherits its environment's floating-point noise —
  declare the numeric contract, prove portability only where claimed.** A
  baseline holding *iteratively solved* numerics (an IRR, a solver output —
  converged, not closed-form) freezes the last-bit FP behavior of the
  runtime that produced it; another runtime major diverges in the
  insignificant digits and the gate false-fails on noise. The comparator
  should express the numeric contract actually promised — a declared
  precision, tolerance, canonicalization, or other justified normalization,
  living in the gate's comparator or snapshot mapper, never production code
  — coarse enough to absorb environment noise, fine enough that a genuine
  behavioral change still fails. A baseline claimed portable across
  supported environments proves that claim on a second, relevantly
  different one — a pass on the freezing environment shows the snapshot
  matches itself, not that it's environment-stable. A runtime pinned as a
  recorded decision (documented before the red, not relabelled after it)
  owes no such proof; a pin added to silence a red is a stopgap that hands
  the same red to the next environment change.
  ❌ "CI is red but every diff is in the 13th decimal place — pin CI to my
  local runtime version." (Local incident: fin cal's frozen IRR snapshot
  diverged Node 22 vs 26 at ~1e-13 — rounded 10dp in the mapper, removed
  the pin, re-ran green on the previously-failing major.)
- **Replay's inverse — verify-by-reconstruction.** To prove "exactly X was
  applied" to a delivered state, reconstruct across the boundary with an
  INDEPENDENT prescription of X (a pinned oracle, the pre-change
  implementation — the parity variant above — or the spec), never the
  delivering system's own producer, whose bugs reproduce on re-run and
  self-confirm. Two sound forms only: full-state comparison over a DECLARED
  projection covering the complete mutation boundary (fields X touches AND
  fields expected unchanged, ambient mutations on a declared allow-list), or
  a true inversion ONLY where the inverse is a proven bijection. Both prove
  STATE, not history — where duplicate application matters, add an
  operation/event witness, or the claim stays state-only, said so. No
  independent prescription available → the re-run is a consistency check,
  labelled so — never a proof. Full rule (projection-cut-down trap,
  false-failing whole-state equality, lossy-undo trap):
  `references/worked-examples.md`.
- **No reliable state readback → verify through a downstream observable
  that must move under a correct application and cannot move otherwise**
  (`unprobed`). Run control and treatment over identical input — once
  without the change, once with it — asserting the treatment's downstream
  signal differs from the control's in the direction the change PREDICTS,
  written down before either run (P1 > P0, not merely P1 ≠ P0). The same
  differential form pins protocol-level bugs: diff your own request
  byte-for-byte against the target system's own observed WORKING request
  for the same operation — a length or byte-offset difference is often the
  entire defect.
  ❌ a single successful run with no control, read as proof the change did
  anything — nothing rules out the same output with the change absent.
  Full rule + both ✅ cases: `references/worked-examples.md`.
- **In parity work, the artifact settles disputes — reading it beats
  adjudicating between reviewers or picking the plausible option.** When
  the contract is parity with an external artifact (a spreadsheet, a
  workbook, a prior implementation), a reviewer blocker or a spec
  ambiguity is a question the artifact already answers, not a judgment
  call — open it and read the cells. A defensive addition your own spec
  invents that the artifact does not contain (a clamp, a guard, a floor
  the source lacks) silently forks the parity target the moment it ships;
  it enters the spec only as an explicitly flagged deviation, never an
  unstated improvement.
- **A ground-truth artifact is authoritative for behavior, not for every
  embedded constant it hand-types — derive the derivable before porting
  a magic number, and flag rows no scenario ever exercises.**
  Hand-maintained oracles carry hand-typed values that should be COMPUTED
  from other cells; a stale hand-update hides exactly in the rows no
  realistic scenario drives, so a clean replay proves nothing about
  whether the constant is still correct. Two shapes to check before
  porting: (a) a constant that should derive from other cells but was
  typed in by hand — recompute and compare; (b) two DIFFERENT quantities
  that happen to share a value (coincidence, not identity), each
  hand-typed under one shared name — rename them apart before either
  changes and the shared name invites conflation.
- **Cheapest gate shape — the grep-count ratchet.** When an anti-pattern can't be
  removed wholesale, pin its current grep count as a dated baseline; the
  executable done-check on every diff is "the count did not grow" (full shape:
  `references/worked-examples.md`).

## Test/gate integrity — the fake-pass patterns

A green test proves nothing until you close the ways it goes green while the claim
is false:

- **Confirm a new test actually *runs*** — the runner lists it, or it fails when
  you deliberately break the code — not merely that it compiles. Same family: a
  **CI/automation config that has never executed** — count runs (the platform's
  runs API), not files — and a **static/type-level assertion nothing ever
  evaluates** (`unprobed`): where the build path can succeed without the
  typechecker, an inherited compile-time assertion reads as a live invariant
  to every reader and enforces nothing — confirm some script or CI step
  actually invokes the checker over that file, then break the coupling once
  and watch it go red (all never-ran variants: `references/fake-pass-patterns.md`).
- **A dependency-absence test must strip EVERY alias of the dependency.**
  Config and dependency lookups often resolve through multiple names (a plural
  form, a compatibility alias, a fallback checked in order). Strip one name and
  the fallback-absent assertion passes while a still-live alias silently
  satisfies the dependency underneath — the suite reports the fallback path
  exercised when the code never left the primary one. Nothing is mocked; the
  assertion runs honestly against a false precondition (right subject, wrong
  dependency state). Before trusting one: read the resolution code (not one
  call site), enumerate every name/path the target resolves through, strip
  them all; then restore ONLY the supposedly-disabled name and confirm the
  test now fails.
  ❌ "verified the fallback path with GROQ_API_KEY unset" — the process still
  exported GROQ_API_KEYS (plural, the pool form), which the loader checks
  first; the fallback the test named never ran, green for as long as the
  test existed.
- **A success status is not identity — a lookup can return the WRONG entity
  and still say it worked** (`unprobed`). A search-then-fetch data API keyed
  by a shared or ambiguous identifier (a series code with a sibling series,
  an id resolved by fuzzy or ranked match) can hand back a record for the
  wrong entity under an unqualified success status. This is the case-set
  list's item 10 (green suite names its subject) at the DATA layer: there
  the running subject can be the wrong copy while every assertion passes;
  here the fetched row can be the wrong record while the call reports
  success. Assert identity metadata FROM the response — a canonical id,
  name, or category field distinct from the query key — against what was
  actually asked for, never only the 200/success; where the API exposes a
  canonical-name lookup, use it to confirm the returned identifier means
  what the query intended.
  ❌ "queried the non-manufacturing PMI series, got 200 with data" — the
  response held the manufacturing series under the same call and status,
  silently, because both shared the queried id family.
  (Full rule: `references/fake-pass-patterns.md`.)
- **A warm-state pass proves nothing about init-only code.** A zero-violation
  observation window says nothing about code that only executes at initialization
  (cold start, first run, migration) — exercise the cold path in a fresh context
  before enforcing (CSP incident: `references/fake-pass-patterns.md`).
- **A substring grader must key on a token its corpus cannot produce.** Scanning
  prose for a word the graded material may itself contain scores the corpus, not
  the behavior — key on a structural marker the subject must create and fill
  (a heading, a filename, a field), and sanity-check the grader against a known-bad
  arm before trusting a clean sweep. Unlike a never-ran test this manufactures
  agreement over real input, so an A/B whose arms all pass reads as "no effect"
  and retires a real rule (incident:
  `../skill-authoring/references/distilling-rules.md`).
- **Arm polarity alone doesn't prove a gate — a change detector can fake it.**
  A source-string presence check or a private-structure snapshot fails on the
  old arm and passes on the new one purely because the source text changed —
  it'll fire on every future redesign and sleep through every future bug.
  Before writing the test body, ask: what production change should make this
  fail — a bug, or a decision? If only a deliberate decision can fail it,
  it's a change detector, not a gate. Carve-out: pinning a representation is
  fine exactly where that representation IS the contract (an error string or
  output name with real downstream consumers) — then a deliberate contract
  change is supposed to update the test.
- **A suite that *grades* candidates is two-sided.** Before it scores anything,
  show it PASSES on ≥2 structurally distinct valid solutions (a too-strict suite
  silently rejects valid alternatives) AND FAILS on a known-broken state, both by
  execution. And confirm the corpus exercises the changed branch: a change "verified"
  only where the new code never fires is unverified — synthesize or capture firing inputs first.
- **The two-sided proof above validates a grader for one invocation shape at
  one time — reuse is a fresh claim, not an inherited one.** Before reusing
  a validated grader (new run, new candidate pool, hours later): re-run
  known-good AND known-bad, diffing PER-CASE outcomes (not an aggregate
  score — same 2/6 with different cases passing is drift) against the
  prior record, which pins the invocation shape too (args, config,
  ephemeral values normalized). No record on hand → the proof runs fresh
  and its record is written before any scoring. Watch for the inverted
  signature a wrong invocation shape produces: edge cases PASS while
  happy-path FAILS, because an edge case's own accepted-throw branch
  silently absorbed the harness's load failure instead of grading real
  code (incident: a file-vs-directory arg mismatch made every candidate
  throw `MODULE_NOT_FOUND`; the known-bad scored 2/6 against a recorded
  0/6, the 2 passes being exactly the capacity-edge cases whose
  accepted-throw swallowed the harness's own error).
- **A behavioral trap fixture scores only ARMED runs.** When the gate is a trap an
  AGENT must resist (a prescribed-but-unauthorized action, a planted directive):
  taking the bait is FAIL however blind the run was. A safe outcome counts only if
  the transcript shows the run MET the trap; otherwise it is NOT-ARMED — excluded
  and re-run armed, never scored as discipline (what "met" means + fixture-design
  corollary: `references/fake-pass-patterns.md`).
- **For a guard/error path, assert three things, not just the exit code:** the
  returncode, a message string unique to THIS check (many errors share exit 2),
  and that the dangerous side-effect did NOT occur (`assertNotIn`). Instrument the
  failure's own signal — an unchanged field or intact-looking output can pass
  while the failure still happened.
- **Mock ≠ sign-off.** A mock / proxy / staging pass is not real-environment
  sign-off; never launder one into the other. A live smoke run still obeys the
  spending/destructive gates — no authorized environment → the item stays BLOCKED, not Pass.
- **A red result is not automatically environmental** — and ruling it so is a gate
  change, the orchestrator's call, not the worker's. Use explicit states over one
  red/green axis: **PASS** (dated evidence), **EXPECTED-FAIL** (a known
  environmental gap in a visible non-blocking lane — not turned green), **N/A**
  (environment structurally can't exercise it), **BLOCKED** (couldn't run —
  auth/cost/side-effect). Never silence a red by weakening the assertion.
- **Two truth sources that agree with each other but only moderately with ground
  truth are correlated bias, not independence** — two models agreeing is one lens.
  A metric clearing a threshold is *evidence*, never *authorization*: keep the
  go/no-go a separate recorded decision.
- **A judgment step compared across time gets versioned** — a threshold/rule change
  is a version bump, not an edit (it changes the meaning of every prior comparison).
  If a generated file is committed, gate on regenerate-and-`git diff --exit-code`;
  edit the source and regenerate, never hand-edit the artifact.

## Designing the guard itself

A gate proves a claim; a guard (a hook, middleware, validator, auth check)
enforces one at runtime — and has its own failure design. Full rules + the
Bash-pre-tool-hook fail-direction case: `references/guard-design.md`.

- **Verify the guard along its real exposed path**, not a convenient internal
  call — a guard can pass its unit test yet be dormant on the entry surface
  (HTTP/MCP/CLI/webhook) where its parameter was never wired; malformed / typo /
  explicit-null input there must fail **closed**, never be treated as "omitted".
- **Choose the fail-direction per failure mode and record why.** Security,
  integrity, destructive, spending, publishing, gate-enforcement controls fail
  **closed** on the threats and malformed input they detect (the flaky-hook
  fail-open rationalization ❌ case: `references/guard-design.md`).
- **A relief valve is a pre-existing, owner-designed, friction-plus-log override —
  never one an agent invents to unblock itself.** *Adding* an `*_ACK`/`--force`
  path to get past a gate is the confirmation-gate violation (operational-rigor §2).
- **A detector's positives come from the corpus it will guard, not the author's
  imagination.** A guard written beside the positives its author pictured passes
  its exposed-path check, fires on those examples, and can still catch nothing
  the live corpus holds — either because the matcher's form excludes every real
  instance, or because a score is measured at the wrong granularity (a
  single-token repetition check missing a repeated multi-word phrase is not a
  threshold problem: the phrase moves the score, but it lands inside the band
  clean text already produces). Validation positives come from the corpus, or a
  labeled plant copied from a real instance where the corpus holds none — never
  hand-written, same as a case-set row (full rule + Done bar +
  minimize-by-type on sensitive positives: `references/guard-design.md`).
- **Sentinel-tag every synthetic fixture, so "never leaked verbatim" is one
  scan.** Embed one shared greppable marker in every free-form fixture
  value, collision-checked once against the clean corpus; shape-CONSTRAINED
  classes (hex credentials, UUIDs, enum identifiers) get a grammar-VALID
  sentinel each, all listed in one manifest so the scan stays one command,
  with a regression proving each constrained fixture still reaches its
  production path. State the claim's bound on BOTH dimensions — the scan
  proves no VERBATIM occurrence, only over a DECLARED surface-and-window
  manifest; an unqueryable declared surface makes the result INCOMPLETE,
  never PASS. Diagnostics never republish what they guard. Runnable worked
  example: `scripts/sentinel/run.mjs` (`--demo-leak` shows the failing
  side). Full rule (collision-check scope, representation-aware sweeps,
  distinction from security-architect's minimize-by-type sentinel):
  `references/guard-design.md`.
- **State what the guard does NOT guarantee** and its known-accepted bypasses in
  its header, so maintainers neither over-trust it nor destabilize it.
- **A recurring, remote-breaking cross-file invariant earns its check at the
  earliest reliable feedback layer — proven green at baseline before it may
  block.** When a known coupling keeps breaking far from the edit that broke
  it, move a minimal deterministic check for THAT invariant to the earliest
  layer that can reliably run it — an edit-time hook where one exists, else
  CI; the ship gate stays the authoritative layer either way. Run the check
  at baseline BEFORE it may block: wired over an already-red state it blocks
  every edit it covers, unrelated ones included, and a guard that blocks all
  work gets deleted, not fixed — so scope it to the targeted sub-check, leave
  the full suite to the ship gate. It blocks with the failure reported, never
  a repair — which side of a coupling is right is judgment, and gate changes
  stay the orchestrator's call (rule 4 above). A narrow trigger watching a
  broad check can name the wrong edit: the check catches drift the trigger
  did not cause, so its block reason must carry the check's own output
  verbatim, not only a canned "you changed X" diagnosis naming the trigger —
  the diagnosis is a hint toward the likely edit, the tool output is the
  evidence, and only the output can point past the trigger to an earlier,
  unwatched one (`unprobed`).
  ❌ "the hook runs the full test suite on every edit" — the suite was
  already red with unrelated failures, so it blocked all work from its first
  firing. (Local rollout: tripwire hooks across five repos in one day, each
  verified two-sided by piped synthetic edit events; one repo's suite was
  already red with three unrelated failures — exactly this trap.)
  ❌ "You changed translations.ts and tsc now fails" as the block's only
  reason — the actual break was a fixture drifted by an earlier edit to a
  file the hook never watches; recovery worked only because the raw tsc
  output was embedded alongside the canned line.

## When NOT to build a gate

No ceremony for one-off scripts or exploratory spikes. The gate pays where the
same judgment or transform will be edited repeatedly, or where a regression would
be silent. One gate that actually runs beats five aspirational ones.

## What this catches that unit tests miss

Real-corpus gates catch what synthetic unit tests structurally miss: over-match
on real user phrases, cross-pattern interaction on compound messages, log-leak
drift, and F1-masked false routes. Scenario table:
`references/worked-examples.md`.

## For experiments (claude-code-technique project rule)

An experiment needs a falsifiable hypothesis AND a deterministic grading harness
BEFORE any runs — no harness, no experiment. Write expected outputs before looking
at actuals; grade with code, not a model's impression. This template's golden
runner doubles as an experiment grader: cases = trials, `intent` = pre-registered
expected result. Pre-register the full **outcome → action table** too, so a result
can't be rationalized into a favored action afterward. Calibrate difficulty per arm
before comparing: every arm passing — or every arm failing — measures nothing; halt
and report "untestable at this tier/difficulty" instead of publishing a null. Grade
blind to which arm produced each output.
Grader integrity (2026-07-22, from two lab benches): a uniform 0-score cell can be
the GRADER dying (OOM/timeout on the candidate's pathological output), not the model
scoring zero — autopsy the grader process before concluding; record grader exit
status per cell. Concurrent runners never append to one results file — exit 0 lost
6/12 cells to an append race; write per-cell artifacts, grade in a separate pass,
and check N(outputs)==N(cells) before grading. For unstated edges, pre-decide that
throw AND sentinel-return both count as guarded (both are valid defensive
contracts); only hang/OOM/wrong-answer fail. Free-text-vs-key auto-regex
under-matches paraphrases: pre-register hand adjudication as authoritative over the
affected dimension, and disclose grader bugs in the finding, never silently fix.

## Sources

Distilled from `/Users/yauch/Documents/claude code technique/ground-truth-harness-pattern.md`
(longer worked example, TypeScript shape; full `export-from-X` anonymizer/self-test
design). Gate runners here: `scripts/golden-gate.mjs`, `scripts/replay-gate.mjs`,
`scripts/run-all.sh`, fixtures in `scripts/example/`; the sentinel-fixture starter
at `scripts/sentinel/run.mjs` ran green two-sided (PASS + `--demo-leak` FAIL) on
2026-08-04.
