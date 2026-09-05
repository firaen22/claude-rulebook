# Lens: rules text

For prose that instructs a future session: harness files, SKILL.md, memory files,
CLAUDE.md. The failure mode is not a crash — it is a rule that is followed and
produces the wrong action, or a rule that reads fine and cannot be acted on.

Report each hit as location + why a session following it would go wrong + the fix.

- **Evidence file or order file?** If the artifact declares it holds no standing
  orders (a registry, an archive, a session recap), do NOT report "unactionable
  rules" — that is its job. Hunt pointer rot, claim-vs-destination mismatch, and any
  IMPERATIVE that leaked into an evidence file. A leaked order is the finding.
- **Is it actionable?** Every rule must name a trigger ("when X"), an action, and an
  observable done-state. A rule that is only a value ("be careful with Y") changes no
  behavior and costs context. Quote the rule and state the action it implies; if you
  cannot, that is the finding.
- **Does the CLAIM match the EVIDENCE cited?** A rule derived from one incident
  must not be stated as a general law. Check the scope of any cited probe, sweep, or
  N — a sound grep with an overstated scope is the recurring defect here (2026-08-26
  audit: 43 checks, 9 defects, several of exactly this shape).
- **Every pointer resolves.** File paths, `[[wikilinks]]`, section numbers, and
  script names named in the text must exist right now. Check them; do not assume.
- **Contradiction with a neighbor.** Does this text conflict with another rule in the
  same file, its parent source of truth, or a cache over it? Name both sides. A cache
  that has drifted from its source is a defect in the cache, not the source.
- **Stale world-facts.** Version numbers, model slugs, tool availability, "X is
  suspended/dead" claims, byte thresholds. These rot in days while method rules do
  not. Anything capability-NEGATIVE ("platform X can't do Y") is the highest-rot
  class — flag it for re-probing rather than trusting it.
- **Permission bit present?** For any file governed by an edit-permissions table: is
  this new standing order in the table, and does it name who may change it? A rule
  with no permission bit was added through a gap.
- **Density.** Prose ≤ ~13 words/line; a table row ≤ ~150 **whitespace-separated
  tokens** (NOT columns — the live harness max is 140). Over that, the rule is being
  skimmed, not applied. Check with
  `awk '/^[[:space:]]*\|/ {print NF}' FILE | sort -rn | head`.
- **Redundancy.** A rule already stated elsewhere in the same load path should be a
  pointer, not a second copy — copies drift apart and then contradict.
