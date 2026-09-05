# Lens: contract drift

For any artifact that claims to implement something written elsewhere — a spec,
proposal, design doc, rule, schema, or docstring.

**Read the claimed contract FIRST, in full, before the implementation.** Then read
the implementation and diff them yourself. Do not read the implementation first: it
supplies a plausible story that the contract then seems to confirm.

Report each hit as: contract location → implementation location → the divergence.

- **Enumerate every promise the contract makes, one line each, before looking at the
  code.** Then mark each promise KEPT / PARTIAL / ABSENT. An ABSENT promise nobody
  noticed is the highest-value finding this lens produces. (Measured 2026-08-29: a
  design promised a distilled record of goal/acceptance/open-actions; the
  implementation wrote one gzip of the raw transcript and nothing else. Four
  reviewers converged on it; it was the real defect.)
- **Follow the output to its CONSUMER.** An artifact that is produced correctly but
  cannot be consumed is a broken contract. Ask: who reads this, with what command,
  under what constraints? (Same incident: the recovery path told a post-compact
  session to "re-read the durable record" — the very thing that had just overflowed
  the context, and no read command was given at all.)
- **Check the contract for things the implementer CANNOT do.** A doc can promise
  judgment, summarization, or distillation that the executing layer has no model to
  perform. A hook cannot distil — a hook has no model. Name any promise that is
  structurally unachievable at that layer; the fix is amending the contract.
- **Docstring/comment vs behavior.** Where they disagree, that disagreement IS the
  finding — report it and say which side you trust and why. Never silently assume
  the code is right.
- **Interface promises: name, arity, types, error shape, ordering, units.** Each is a
  separate check. A returned value with the right name and wrong units passes review
  by eye every time.
- **What did the implementation add that the contract never asked for?** Scope
  creep is drift in the other direction and carries unreviewed risk.
- **When the artifact DECLARES itself a cache, port, or extract** (a SKILL.md over a
  harness file, a registry split out of a table): the SOURCE wins, and drift is a
  defect in the cache. Amending the contract is the fix only when the source promised
  something the implementing LAYER cannot do — not when a cache grew extra rules.
