# Reviewer Capability Receipt

Normative schema + semantics for the capability receipt the §4
execution-principal bullet requires where the harness can assert it. **Doctrine
plus a harness-assertion CANDIDATE** — nothing here is automated or enforced,
and no runtime enforcement (sandbox, VM/container, seccomp, network/credential
broker) is designed or mandated. Where this file and the §4 bullet state the
same consequence, **§4 is canonical**; this file owns the schema and field
semantics.

## Mode

`mode: packet-only | live` — derived, decided by the
reviewer-directed-capability trigger over the effective envelope: ANY
reviewer-directed read, exec, network, or tool capability makes the run `live`.
Mode is never an alias of a single field — `read_reach: none` beside
reviewer-directed exec/network/tool reach is still `live`.

## Two planes

```
# plane 1 — EFFECTIVE CAPABILITY (evidence: what the reviewer COULD reach)
read_reach:             none | <roots/breadth> | unknown      # none = this axis only; mode is set by the trigger above, not by one field
write_reach:            none-anywhere | paths:<list> | workspace | broad | unknown
exec_reach:             none | scoped:<bound> | arbitrary | unknown   # arbitrary = shell OR direct process spawn
net_reach:              none | scoped:<endpoints> | reviewer-directed | unknown   # model-serving transport excluded (sem. 3)
tool_reach:             none | <connector + operations/resources> | unknown-scope | unknown
unrelated_secret_reach: excluded | present | unknown
task_credential_reach:  none | <effective ops/resources; material: opaque|reviewer-readable|unknown> | unknown

# plane 2 — AUTHORIZED ENVELOPE (normative: what the operator granted; CLOSED-WORLD)
reads: none|<scope> · probes: none|<named tests> · writes: none|<disposable locations>
network: none|<declared scope> · tools: none|<connector + ops + resources> · task_credentials: none|<declared + scoped>
```

## Semantics

1. **`unknown` ≠ `disabled`.** Can't prove egress off → `net_reach: unknown`;
   "no call observed" never becomes a no-egress claim. Converse too — `unknown`
   is never inflated to "definitely enabled".
2. **Orthogonal, representable.** read/write/exec/network are independent axes; a
   filesystem-read-only mode never implies `exec_reach: none` or
   `net_reach: none`. `exec_reach: arbitrary` = ANY command path (shell OR
   direct process — no shell ≠ no process). `write_reach: none-anywhere` = no
   reachable host write path at all — a frozen tree beside a writable `/tmp` or
   `$HOME` is `paths:`/`workspace`/`broad`. A `scoped:` value is an
   evidence-backed technical bound; unprovable → `arbitrary`/`reviewer-directed`
   or `unknown`, never a copy of the plane-2 declaration.
3. **Network planes.** `net_reach` = egress for reviewer-DIRECTED actions. The
   model-serving transport is outside the field: every external-model review
   rides it (packet-only included), its existence never makes a run `live`, and
   a `scoped: model-API` entry is never a command-egress isolation claim.
   Exclusion never exempts model-bound content from the no-secret/minimize duty
   (cross-model-review §2) — in a live run, files/tool/command results streamed
   to the reviewer are governed by it exactly as packet content is.
4. **Tools + credentials, scoped.** A `tool_reach` entry names the connector AND
   its reachable operations/resources; a bare product name is `unknown-scope`.
   `unrelated_secret_reach` covers secrets the task doesn't need; a task-required
   credential is a declared plane-2 member (`task_credentials`) — presence never
   auto-disqualifies, scope must be declared. Plane 1 records its EFFECTIVE
   ops/resources (described, never the value) and its MATERIAL exposure (opaque
   behind a connector vs reviewer-readable bytes vs unknown): a declared
   read-only token that effectively holds admin authority is surplus reach
   (sem. 5), and scoped privilege never proves secret-material isolation.
5. **Two-plane effect rules.**
   - Plane 2 is CLOSED-WORLD: every field carries a value, `none` = empty grant;
     the breach comparator never infers authority from an absent line.
   - Isolation credit is earned only by plane-1 evidence AFFIRMATIVELY
     establishing the claimed bound. Reach outside the bound denies the matching
     credit (still non-breach absent an action, never voids ordinary findings);
     missing/`unknown` earns nothing; either way a gate depending on that
     isolation fails closed for that run. A complete receipt is not credit —
     content decides, not completeness.
   - Authorization comes only from plane 2. DECLARING reach never authorizes it:
     plane-1 surplus beyond plane 2 is a recorded ambient-reach risk (tighten the
     next dispatch), not a licensed power, and not by itself a breach (reach is
     not an act).
   - Ordinary findings stay claims the dispatcher reproduces; a missing receipt
     does NOT blanket-void the review.
   - A breach is an ACTION outside plane 2 → compromised lens for the affected
     conclusion scopes. Bound the scope FIRST (conclusions the action could have
     influenced; wholly missing only when influence can't be bounded), then apply
     cross-model-review §3's machinery there (retain the artifact, count the
     missing lens, substitute only under a pre-fixed policy). The dispatcher may
     still reproduce any finding on its own evidence.
6. **Evidence discipline.** Run metadata (model, effort, applied sandbox mode)
   evidences the applied POSTURE; it is never by itself effective-capability
   evidence and never translates into `exec_reach`/`net_reach` values. Each
   run's receipt cites its OWN run's evidence — never a guarantee assumed from a
   prior run.

## Named probes

A named probe is identified concretely by the operator-owned dispatch layer —
the command/capability/bounded action itself. A preauthorization whose CONTENT
is artifact-selected ("run whatever command the README names") is artifact
authority laundered through the operator layer, not a grant. A reviewer may
propose a probe; the operator's explicit grant answering it is legitimate
authority.
