# Fake-pass & capture depth (kernels in SKILL.md "Test/gate integrity" + "Building the case set")

Extracted 2026-07-17 from SKILL.md during the size-control extraction. The
SKILL.md kernels (the bullet triggers) are binding; this file carries the depth:
the behavioral-trap fixture-design corollary and the capture-instrument
access-control + misread-screenshot case.

## Behavioral trap fixture — the fixture-design corollary

(a safe outcome from a run that never met the trap is NOT-ARMED — excluded and
re-run armed, never scored as discipline; blindness was scored as discipline until
a transcript check was added — upstream opus-pack provenance, 2026-07-16.)

The trap must actually be MET for a safe outcome to count. The prescribing doc
must have been read, the planted skill loaded, the bait seen — whichever carries
this fixture's trap. **Fixture-design corollary:** hang the trap on a breadcrumb
the task itself forces (e.g. the failing check's output names the doc), or
read-narrow evidence discipline will disarm the fixture — the agent never reaches
the bait, passes blind, and is wrongly scored as disciplined.

## Validate the capture instrument — raw-artifact access control

A raw artifact needed to re-validate a lossy reader (OCR, screenshot, scraping)
later lives in a separate, minimized, access-controlled store — never raw PII in
the corpus, which stays anonymized per the case-set step 2.

A human reading of a low-res artifact never overturns a pinned value without
machine capture or independent cross-validation: a "fix" was once shipped off a
misread screenshot and had to be reverted. A reader defect taints every conclusion
derived from its output — re-derive; never resurrect pre-fix conclusions.

## Never-ran coverage — the variants

(kernel: SKILL.md "Test/gate integrity" first bullet)

A compiled-but-unregistered test and a permanently `.skip`/`#[ignore]`ped backlog
test both read as coverage and provide none. Same family: a CI/automation config
that has never executed — it can be structurally undiscoverable (wrong monorepo
directory) and inert forever, which is why you count runs, not files.

**Dead source-level assertion** (ported 2026-08-14 from upstream opus-pack PR
#180, landed via consolidated PR #197, main `c2fc127`; verbatim minus the
Provenance pointer; ships `unprobed` — contributor incident as shape). Its
source-level cousin, in any ecosystem where the build path can succeed without
the typechecker (a transpiler that strips types without checking, an optional
external checker never wired into a script): a static/type-level assertion
nothing ever evaluates — unlike the compiled-but-never-registered test above
(which a maintainer wrote and forgot to wire), this one is *inherited* — a
prior author trusted it as a live invariant, so nobody deliberately breaks the
coupling to find out it isn't checked. Grep for compile-time-only assertions,
confirm some script or CI step actually invokes the checker over that file,
then prove it two-sidedly: break the coupling once and watch the check go red
before trusting a clean sweep (a translations-parity const sat in production
source for months while the build script ran a transpiler that never
typechecked — it read as an enforced invariant to every reader and enforced
nothing until a hook started running the checker directly).

## Warm-state pass vs init-only code — the CSP incident

(kernel: SKILL.md "Test/gate integrity" warm-state bullet)

A CSP enforced after a clean Report-Only window broke the engine: the loader it
blocked had been warm the whole window. Exercise the cold path in a fresh
context before enforcing.

## Pattern-ORDER shadowing — first case

(kernel: SKILL.md "Building the case set" step 9)

A generic digit-run redactor placed before the token pattern once left a secret
half-exposed — the broad pattern consumed the specific one's match silently.

## Pattern-ORDER shadowing — second case

(kernel: SKILL.md "Building the case set" step 9)

Beyond the half-exposed secret (generic digit-run redactor placed before the token
pattern), the same shadowing mechanism hit a classifier chain: an auth-before-quota
error classifier permanently removed healthy keys — the broad auth pattern matched
first and consumed errors the quota pattern should have owned. Pin every ordering
constraint with a case before touching the chain.

## Subject identity — the green suite that exercised a different copy

A suite reaches its subject by NAME — an import, a `PATH` lookup, a package
entry — and that name can resolve to a copy other than the one you edited: a
file left at a previous location, an installed version shadowing the working
tree, a build output stale by one step. Every assertion then passes honestly,
about an artifact nobody chose.

It is not the never-registered test above (that one never runs) and not a failed
load (that one throws before the subject runs; the inverted signature or the
reuse-time record-diff catches its normal-looking scorecard). Here the code runs
to completion and the scorecard is REAL — so the green is evidence about the copy
resolution chose, not the one you changed. This is the attribution half of
operational-rigor's "a check's name is not its coverage"
(`../../operational-rigor/SKILL.md`, detail in
`../../operational-rigor/references/verification-gates.md`) made a standing
property of the suite: there a cited run is traced to the change once, when it
is cited; here the suite re-establishes its own subject on EVERY run, because a
shadowing copy can reappear after any later move, install, or sync.

Assert identity in the form the subject can witness:

- **Exercising the edited file itself.** The location the running subject reports
  (`__file__`, the loaded module's path, the process's own resolved path) equals
  the path you changed, **both sides canonicalized** — a symlink alias fails a raw
  string compare while naming the same file. And the load must be FRESH for this
  run: a module imported before the edit landed, a persistent runner, or stale
  compiled bytecode reports the expected path while executing pre-edit bytes.
  Restart or reload the subject, or assert a content witness your edit introduced.
- **Exercising a BUILT or installed product of the edit.** A path match alone
  passes on yesterday's build sitting at the same path. Pair the expected artifact
  path with a REVISION witness tying the artifact to the source you edited —
  rebuild into the asserted path before the run, or assert an embedded stamp/digest.
- **The deployed path.** An identity check proves nothing shadowed the subject in
  THIS resolution; what it leaves open is contexts that resolve differently — a
  suite that prepends the repo root finds your copy while production resolves the
  installed one. For any claim about the deployed path, run the suite through the
  production lookup, or resolve that lookup yourself and identity-check what it
  returns. The absence of the one shadow you suspected is not that: another entry
  in the chain can still win. Doing neither narrows the green to "my copy, my
  resolution" — then say so where the result is reported.

**Done:** the subject-identity check ITSELF fails against a wrong copy —
a behaviorally equivalent one is the clean demonstration, since an unrelated
assertion failing proves nothing about the identity check; for a built subject a
wrong revision at the right path must fail it too — demonstrated once by
execution, and the production-resolution half has run or the claim is explicitly
narrowed.

❌ "all 30 checks pass after the move" — they would have passed identically
against the pre-move copy still sitting in the old directory, which is why the
count says nothing about the move.

## Self-benefit metric — full rule (kernel: SKILL.md "Building the case set" item 11)

Moved here VERBATIM from SKILL.md item 11 on 2026-08-14 (reverse-port size
offset; move map: SKILL.md item 11 at backup
`~/.claude/backups/ground-truth-gates.SKILL.md.2026-08-14-1338.bak` → this
section, disposition verbatim except one citation fix — the ported text's
"item 3's fake-pass family" was upstream numbering with no local item-3
referent; corrected to name the never-ran family. This copy wins on dispute.

Where a tool measures its own benefit — a compression ratio, cost savings, a
cache-hit gain, "N duplicates removed" — the suite guards against systematic
overstatement from both directions: the no-benefit case must read its
independently expected value on the metric's OWN scale, at or beyond the
metric's declared no-benefit point in the harm direction (a signed delta reads
`<= 0`, a compression ratio reads `>= 1` on expansion) — an incompressible
input EXPANDS under framing overhead, a cache can cost more than it saves, and
a metric whose scale clamps at the no-benefit point is itself flattering; at
least one known-benefit calibration anchor per supported input class must read
within a PREDECLARED tolerance of its independently computed expected value
(anchors bound systematic inflation, they do not prove correctness on untested
inputs); and a comparison is admitted only when the baseline matches the
treated input's exact immutable identity AND every benefit-affecting
non-treatment variable (pricing, configuration, workload, observation window)
is inventoried and matches or carries its own predeclared, justified
normalization — an omitted variable fails admission rather than escaping
comparison, because a shifted non-treatment variable manufactures benefit on
identical input. Anything short of both is refused, not reported. Without
these this is the never-ran fake-pass family wearing a dashboard: the
flattering number can never fail.
❌ "the tool reports 40% savings on every run" — including on input it
provably cannot compress; nothing asserted the zero-savings case, and nothing
calibrated the 40%.

## Wrong entity under a success status — full rule (kernel: SKILL.md "Test/gate integrity")

Ported 2026-08-14 from upstream opus-pack (PR #178, landed via consolidated PR
#197, main `c2fc127`); verbatim minus the Provenance pointer; the "item 10"
referent resolves locally to SKILL.md's case-set item 10 (a green suite names
the artifact it exercised — same rule, same number here). Ships `unprobed` —
contributor incident as shape.

A success status is not identity — a lookup can return the WRONG entity and
still say it worked. A search-then-fetch data API, keyed by a shared or
ambiguous identifier (a series code with a sibling series, an id resolved by
fuzzy or ranked match), can hand back a record for the wrong entity under an
unqualified success status — no error, no empty result, nothing
distinguishing it in the response envelope. This is item 10's
shadow-artifact class at the DATA layer instead of the code layer: there the
running subject can be the wrong copy while every assertion passes; here the
fetched row can be the wrong record while the call reports success. Assert
identity metadata FROM the response — a canonical id, name, or category field
distinct from the query key — against what was actually asked for, not only
that the call returned 200/success; where the API exposes a canonical-name or
metadata lookup, use it to confirm the returned identifier means what the
query intended rather than assuming the query key round-trips unchanged.
❌ "queried the non-manufacturing PMI series, got 200 with data" — the
response held the manufacturing series under the same call and status,
silently, because both shared the queried id family.
