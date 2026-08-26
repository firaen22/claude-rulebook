# Guard design — full failure-design rules (kernel in SKILL.md "Designing the guard itself")

Extracted 2026-07-17 from SKILL.md during the size-control extraction. The
SKILL.md kernel (the four bullet triggers) is binding; this file carries the
depth: the Bash-pre-tool-hook fail-direction case, the relief-valve mechanism,
and the header-honesty rationale.

A gate proves a claim; a guard (a hook, middleware, validator, auth check)
enforces one at runtime — and has its own failure design.

## Verify the guard along its real exposed path

Not a convenient internal call. A guard can pass its own unit test yet be dormant
on the entry surface (the untrusted HTTP/MCP/CLI/webhook boundary where its
parameter was never wired). Malformed / typo / explicit-null input there must fail
**closed**, never be silently treated as "omitted".

## Choose the fail-direction per failure mode and record why

Security, integrity, destructive, spending, publishing, or gate-enforcement
controls fail **closed** on the threats and malformed input they detect. The hard
case is a guard that *itself gates every action* (a Bash pre-tool hook): it can't
hard-fail-closed on every internal error without bricking the agent, so it fails
closed on what it detects and raw-scans an unparseable command, while a malformed
envelope still fails open — a documented gap to narrow, never a licence to widen.
❌ "the hook is flaky and blocks me, so I'll make it fail-open" converts a guard
into a rationalized bypass.

## A relief valve is owner-designed, never agent-invented

A relief valve is a pre-existing, owner-designed, friction-plus-log override —
never one an agent invents to unblock itself. Removing an owner-shipped valve "to
harden" re-creates the deadlock it prevented; *adding* an `*_ACK`/`--force` path
to get past a gate is the confirmation-gate violation (operational-rigor §2), not
hardening.

## State what the guard does NOT guarantee

State its known-accepted bypasses in its header, so maintainers neither over-trust
it nor destabilize it chasing inherent bypasses into the parser.

## A detector's positives come from the corpus it will guard, not the author's imagination

A guard that classifies real material — a secret scanner, a redactor, a quality
or corruption check — is written beside the positives its author pictured, and
those are the ones it gets tried against. The miss is silent and total: it
passes the exposed-path check above, it fires on the author's examples, and it
still catches nothing the live corpus holds.

Two shapes seen:

- **Form mismatch.** A matcher whose *form* excludes every real instance — an
  assignment-pattern regex written lowercase where every credential on the host
  is uppercase, reporting clean across all of them.
- **Wrong granularity.** A score measured at the wrong level — a repetition
  check keyed on the most frequent SINGLE token where the real corruption is a
  repeated MULTI-WORD phrase. A transcript roughly one third watermark junk
  scored 0.078 against a 0.30 threshold, and summaries of it shipped for weeks.
  Granularity is the harder shape, and not simply a mistuned threshold: the
  author's synthetic single-token repetition can be constructed to clear
  whatever threshold is set, which is what made the check look sound; the
  phrase also moves the statistic, so its score is not zero — but it lands
  inside the band ordinary prose already produces (one common token is a few
  percent of ordinary text), so no threshold cleanly separates the real
  positive from clean material and tuning cannot rescue it.

The case-set capture rules above govern a guard's validation samples the same
way: the positive comes from the corpus the guard will face, never from the
author's imagination. Where the corpus genuinely holds no positive, plant one
whose form is copied from a real instance — labeled synthetic, and never a row
in the captured golden/replay corpus (the case-set integrity rule above: a
hand-written row corrupts the gate the same way here).

Before enabling: confirm it fires on that positive — and where the guard
scores rather than matches, confirm the score lands on the FIRING side of the
decision boundary, in whichever direction the guard fires (the incident's
0.078 against a fire-at-0.30 threshold sat deep on the non-firing side while
reading like a margin) — then confirm captured clean samples, hard negatives
included, do not fire.

**Done:** both directions shown — fire on validation positives representative
of each FORM the corpus holds (captured rows, or the labeled plant where the
corpus held none; a plant stays labeled, supplements captured rows where the
corpus holds that form, and stands alone only where the corpus held none); no
fire on captured clean samples including hard negatives. Keep the firing
positives as the guard's regression cases; where a positive is itself a secret
or sensitive value, keep a shape-preserving non-sensitive derivative instead
(security-architect's minimize-by-type — `REDACTED`-style blanking destroys
the very shape the guard keys on, so re-run the guard on each derivative and
keep it only once shown still firing; a live credential never lands in
fixtures).

❌ "it flags my test key, so the scanner works" — the test key is the shape
you already had in mind; the question is whether it flags the ones that are
actually there.

## Sentinel-tagged fixtures — full rule (kernel: SKILL.md "Designing the guard itself")

Moved here VERBATIM from SKILL.md on 2026-08-14 (reverse-port size offset;
move map: SKILL.md sentinel bullet at backup
`~/.claude/backups/ground-truth-gates.SKILL.md.2026-08-14-1338.bak` → this
section, disposition verbatim, no rewording; the SKILL.md kernel is a
compressed pointer and this copy wins on dispute).

Embed one shared greppable marker in every free-form fixture value,
collision-checked once against the clean corpus (grep it where nothing was
planted — zero hits means the marker is safe to plant for THIS suite; a
corpus check, not a proof about all possible content), so the leak check is
executable instead of per-fixture recall. A shape-CONSTRAINED class (a hex
credential, a UUID, a checksummed or enum identifier) cannot carry the
free-text marker without leaving its grammar and silently stopping short of
the production parser it exists to exercise: give each such class a
grammar-VALID sentinel (a fixed hex stem, a reserved UUID prefix), keep the
full sentinel list in one manifest so the scan stays one command over all of
them, and keep a regression proving each constrained fixture still reaches
its intended production path. Runnable worked example:
`../scripts/sentinel/run.mjs` (collision check + leak scan + the
constrained-class manifest; its `--demo-leak` mode shows the failing side).
State the claim's bound honestly on BOTH dimensions — representation and
coverage: the scan proves no VERBATIM occurrence (encoded, escaped,
truncated, or transformed copies need a representation-aware sweep over the
encodings the pipeline actually applies, or the record says "verbatim only"),
and it proves it only over a DECLARED surface-and-window manifest — every
downstream sink fixtures can reach, over the retention interval the claim
covers; a merely nonempty artifact pile is not coverage, and a declared
surface that cannot be queried makes the result INCOMPLETE, never PASS. The
tool's own diagnostics never republish what they guard: failure output names
class, count, and source ordinal — never the sentinel value or the raw
matched record. Distinct from security-architect's minimize-by-type sentinel:
that one proves a sensitive FIELD never appears past a parse boundary; this
one proves planted test material never ESCAPES the test boundary.
