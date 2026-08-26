# External-system boundaries — verify-before-trust rules

Load when the work builds against, configures, or verifies anything that
crosses a boundary into: an external tool's exit codes, a timeout, a cache, a
fallback chain, a clock/timezone, a deploy target, or a sync with delete
semantics. Each boundary reports success while lying about it in a specific,
incident-backed way; each rule names the observation that catches it.
Pointers in operational-rigor §2 (sync) and §4 (the rest).

## Sync with delete semantics (§2 gate detail)

`rsync --delete` / `rclone sync` is a MIRROR, not a backup — run after
source-side destruction, it propagates the destruction to the destination.
Before running:

- Confirm the destination is the live mount. `ls` is NOT enough — an unmounted
  ordinary directory lists fine, and an auto-`mkdir -p` in the script masks an
  unmounted cloud drive and silently mirrors into a dead local directory.
  Check `mountpoint -q` / `findmnt` / `df` on the path, or a sentinel file
  that exists only on the mounted volume.
- Dry-run first — and in a non-versioned location, dry-run via a COPY of the
  script: a forgotten `-n` left in the original silently kills every future
  real run.
  ❌ "it's just a backup script, run it."

## Exit codes are a contract to verify, not assume

Some tools exit non-zero on success-with-warnings while writing valid output
(qpdf exits 3); gating on `=== 0` misclassifies success as failure — a shipped
gate once made legitimately-owned locked files permanently unprocessable this
way. Read the documented exit table, and confirm success by validating the
output artifact's INTEGRITY — not mere existence; a partial or corrupt
artifact can be written on failure.

## Never tighten a timeout below the measured success-latency tail

Before setting or "tidying" a timeout constant, measure the distribution of
SUCCESSFUL runs on real payloads over multiple runs — high-variance backends
make one run meaningless (a 25s "tidy" once aborted a measured 42s
slow-but-successful call). A timeout under the success tail converts slow
successes into failures. Record the dated measurement beside the constant;
never retune from old numbers alone.

## Cache-write discipline: three states, scoped keys, minimized payloads

Never cache a failure, an UNVALIDATED empty result, or an unvalidated
payload — a long TTL converts a transient flake into a locked-in wrong answer.
The distinction that matters: an unvalidated empty (flake, parse failure) is a
miss to retry/overwrite; a VALIDATED known-empty (input legitimately has no
answer) is cached as an explicit sentinel. A cache in front of a paid producer
needs all three states (miss/error → retry; validated known-empty → sentinel;
value), or it re-spends budget on known-empties or locks in transient errors.
Scope the key by every dimension that can fail independently — a shared key
lets one path's failure poison the other's success. Store producer output
minimized and access-controlled (never third-party PII/secrets at rest by
default); apply curation/policy overrides at READ time — baking them in
freezes old policy into the cache until TTL.
❌ "cache whatever came back — empty is a valid result and saves an API call."

## A fallback chain is a set of unexercised dependencies that rot silently

A dead or capability-mismatched leg is invisible until the primary fails — it
errors on every call and falls through with zero visible errors (a chain's
highest-quota model once went unused for weeks this way). On any
add/remove/reorder: live-probe every leg end-to-end with a real payload and
record dated results. WITHIN the chain (and only there — never on an
auth/payment/security path, where fail-loud/fail-closed governs), each tier
helper normalizes its own failure to the chain's advance signal (return empty
so the next tier runs; a throw skips the remaining tiers and drops the item).
A terminal empty after every tier failed is an observed FAILURE to log and
meter, not a success. A last-resort tier with a hard quota is invoked at batch
granularity, or one refresh cycle exhausts the emergency budget exactly when
it is needed.

## Two time conventions will coexist — document which, round-trip dates

On a UTC server handling a local-wall-clock domain, expect two conventions
(shifted-epoch values read via UTC accessors vs. raw instants plus a timezone
formatter): document which convention each helper uses and never feed one
convention's value to the other's reader — the failure is a silent ±offset
double-shift. Validate dates by calendar ROUND-TRIP, not component ranges (a
day ≤ 31 still admits Feb 30): construct, then confirm the constructor did not
silently normalize (lenient constructors roll Feb 30 → Mar 2), or the
scheduled action fires on the wrong day with no error. Run time-logic tests
under at least two `TZ` values, and state an explicit DST gap/fold policy —
two `TZ` values alone do not cover it.

## A deploy target is a contract to verify, not a bigger laptop

On response-terminates-execution platforms (serverless): fire-and-forget work
after the response silently never runs — await side effects before responding;
in-memory state is per-instance and mortal (cold starts wipe it, concurrent
instances multiply it) — document each structure's behavior when it vanishes
or multiplies. Bundler file-tracers follow only statically-analyzable imports:
runtime-resolved assets silently vanish from the deployed artifact while local
dev AND local build both pass. "Every route 500s" points FIRST at module-load
or shared-init failure (module load, middleware, config, runtime init), not
one route's logic — and probe a route that MATCHES: an unmatched route's clean
404 comes from the platform fallthrough and masks a fully-broken deploy. The
truthful repro is building the production artifact and importing it; dev-mode
resolvers prove nothing about production module loading.

## The shell's glob dialect is an environment fact

macOS default bash is 3.2 — NO globstar (`shopt -s globstar` errors), so
`**` patterns silently expand empty under nullglob and a guard script
"passes" while scanning zero files (hit 2026-07-14: a subordinate-written
gate matched nothing in `api/**`, including the exact file its outage-guard
existed for). Never accept `**` in bash scripts on this machine — use
`find`. Corollary: any guard/gate script a subordinate writes gets a
mutation test before trust — prove it FAILS on the bad case it targets
(the guard-script instance of ground-truth-gates' fails-on-known-broken
rule).

Environment-specific facts to re-verify before relying on them: a tool's exit
table (qpdf's), real success-latency distributions, cache TTL semantics,
fallback-provider quotas, date-constructor normalization + TZ/DST behavior,
serverless lifecycle + bundler tracing, the shell's glob dialect.

## A deployed bundle's content-grep must follow the SERVED chunk graph

Prod bundlers chunk differently than local builds — a marker verified present
in the local entry chunk sat in a nested sub-chunk in prod, producing a false
deploy-failure alarm. Walk imports from the served entry (not the local
build's chunk boundaries), or use the deploy-status API as the primary signal
over a content-grep guess (2026-07-22).

## Background-wait is notify + fallback wakeup, never a foreground sleep/poll

A shell timeout on a waiting loop kills the WATCHER process, not the worker
it's watching — Exit 143 then reads as job failure when the job is still
running; check which process actually died before concluding failure. Prefer
notify-on-completion with an idempotent fallback wakeup over any sleep/poll
loop. Scope monitor triggers to anomalies: a monitor that fires on
pre-registered EXPECTED outcomes burns a turn per non-event — kill it and rely
on the completion notification instead (2026-07-22).

## A one-directional flag is meaningful in only one direction

Some external status fields carry signal only when SET: set ⇒ a failure was
recorded; unset ⇒ nothing — not success, not health. Type them that way, make
absence representable (`unknown`, never a defaulted `false`), and reject any
inference from the direction the producer never writes. **Absent ≠ false.**
Operational-rigor §4's field-semantics rule (a field's name is not its
contract) names the general trap; this is its named one-directional shape.

## A side-effecting create whose outcome is unknown is never blindly retried

A timeout, dropped connection, or ambiguous response after a create/send/charge
leaves the effect UNKNOWN. A retry can double it, and "it probably failed" is
not evidence. Run such mutations serially — one in flight — then resolve in
this order:

1. **No destination query API, or no request identity to query by**
   (fire-and-forget email/SMS/webhook) → report "uncertain" as a TERMINAL state
   immediately. Never invent a probe loop, never retry.
2. **Otherwise read back from the DESTINATION** by the request's idempotency key
   or unique payload identity, under a recorded time/attempt cap.
   (`../../security-architect/SKILL.md`'s money-path reserve/commit +
   query-by-key form is the canonical instance; this entry generalizes it.)

Only an AUTHORITATIVE read settles anything — a stale or eventually-consistent
"not found" does not authorize a retry, because the original can still land
after it. The read-back has exactly three exits:

- **Authoritative positive identity match** → success.
- **Authoritative absence under the request's identity** → failed-not-applied
  ONLY on evidence covering BOTH axes: the FUTURE (the original provably can no
  longer apply — a terminal request-status, a cancellation/fencing receipt, a
  documented passed expiry) AND the PAST (it never applied — a durable
  application-history query, or a terminal receipt explicitly attesting
  never-applied). Absence-now on a non-monotonic store also matches
  applied-then-deleted/consumed/expired, and a "failed" verdict there
  resurrects or duplicates a consumed effect. With either axis open, a re-issue
  is safe only under a documented idempotency guarantee whose retention window
  covers concurrent and late arrivals (the same key deduplicates the
  straggler) — and the read is never described as proof the original failed.
- **At the cap, on any non-authoritative ambiguity, or where neither both-axis
  evidence nor an idempotency guarantee can be established** → terminal
  "uncertain": a report value the caller decides on, never a retry trigger.

## A recurring scheduled task's "completed" report proves nothing about landed artifacts

One task silently ran green weekly for 3 months while writing zero files (all
output mtimes frozen; its second channel was also dead, on a stale hardcoded
secret nobody re-checked). Before arming or after reviewing a schedule:

- Run it once supervised before arming — watch it produce real output.
- Verify each output channel end-to-end: read back the artifact itself or the
  response body, never just an HTTP 200 or an exit code.
- Have the task write a dated health line it can't fake by skipping a step.
- Pre-allowlist every permission-gated tool it calls — a headless scheduled
  run dies silently on an interactive permission prompt.
- Audit output mtimes periodically — the only signal that catches a
  long-silent failure between manual checks.

## Content moved over a lossy channel needs a hash gate (kernel: SKILL.md §4)

Ported 2026-08-14 from upstream opus-pack (PR #175, landed via consolidated
PR #195, main `c2fc127`); upstream wording kept verbatim minus the Provenance
pointer (local convention). Ships `unprobed` — contributor incident as shape:
over a remote-desktop session, a clipboard paste silently delivered a stale
prior value instead of the composed command, and separately a typed keystroke
stream dropped characters mid-word (a backup command mangled into a
different, silently-run command immediately before an overwrite it was meant
to protect against).

A clipboard relay, a remote-desktop paste, a GUI keystroke stream, an
OCR/scrape read — any side-channel that can silently drop, stale, or mangle
bytes in transit — turns "I sent X" into an unverified claim about what the
far side actually received: a paste can deliver yesterday's clipboard
content, a keystroke stream can drop a chunk mid-word, and neither errors.
Compose the content locally, encode it (base64 is enough to survive most
lossy text paths), transfer, then decode-and-verify a content hash before the
far side acts on it — treat a hash mismatch as a resend, never a
partial-apply; for a transfer split into chunks, key each chunk by index so a
resend is idempotent rather than compounding the corruption. State the
verification in the report ("MD5-verified byte-identical"), not just that the
transfer "completed."
❌ "pasted the deploy command over RDP, it ran" — the clipboard delivered a
stale prior value; the command that ran was not the one composed, and nothing
in the transcript would have shown it without a hash check.
