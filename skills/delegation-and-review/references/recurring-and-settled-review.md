# Recurring campaigns, settled-tree review, and channel attribution

Load when dispatching or reviewing a recurring review/audit round, or a
critic wave over a tree that you, a hook, the user, or a sibling process
may mutate while it reads. Pointers in delegation-and-review §2 (listing≠
callable) and §4 (ledgers, settled-tree).

## Settled-tree review

A verdict binds only the exact state whose immutability was enforced.
Neither incident below is the §8 silent-clobber case (a sandbox restoring
out-of-scope files on exit) — both are the tree moving DURING review:

- A read-only critic re-read a file the orchestrator had already fixed
  mid-review and voted REFUTED on a bug already confirmed elsewhere.
- A critic committed the very worktree it was reviewing, moving the tree
  out from under the requested end-state.

Protocol: capture a baseline over the WHOLE protected read set (not just
the files named in the brief) before dispatch; give each critic an
enforced copy or a frozen snapshot, never a linked/live worktree it or a
sibling can still write; apply verdicts only to the recorded baseline.
Anything less runs provisional — never a clean gate pass. A moved tree
after capture voids the verdict; re-dispatch against a fresh capture,
never re-bind the old verdict to the new state.

✅ "dispatched one enforced copy per critic, applied the verdicts to the
recorded baseline only."
❌ "kept fixing files in the live tree the critic was reading."

## Recurring review campaign ledgers

Scope: RECURRING review/audit campaigns only — never blocks a one-off
dispatch, and a recurring non-review dispatch (implementation, ops) is
outside this rule.

The ledger holds four record categories, reconciled against every prior
round's report before the next round dispatches:
- **Prior fixes** — what shipped, so a reviewer doesn't re-flag it as new.
- **Refuted finding-classes** — what an earlier round disproved against
  the dependency's own source, with the counter-evidence, so it isn't
  re-raised without new evidence.
- **Open findings** — carried forward, not yet resolved.
- **Unresolved** — flagged but neither fixed nor refuted; owner named.

Name the campaign's stable identifier and a concrete repository-relative
ledger path in the DISPATCHING side's own repository — never inside a
tree under review, which settled-tree rules above forbid mutating. The
ledger is dedup context, never authority: current artifact evidence
always overrides a stale ledger entry.

✅ "packet names styling-sweep-2026Q3 and reviews/styling-ledger.md,
reconciled item-by-item against rounds 1–2's reports."
❌ "the reviewer gets fresh context each round, so the packet doesn't
need the sweep's history."

**Absence is not resolution.** An OPEN FINDINGS or UNRESOLVED entry that
this round's report simply does not mention stays exactly where it is — an
entry moves only on evidence addressed to it, and each state has its own
exits. An OPEN FINDINGS entry (a confirmed defect) moves to PRIOR FIXES
only on re-examination of its locus showing the confirmed defect no longer
holds there, with the covering evidence (which round, which check) named
in the entry. An UNRESOLVED entry (never confirmed) can never become a
prior fix — there is no confirmed defect to have fixed; a counterexample
addressing its original claim moves it to REFUTED FINDING-CLASSES, and
anything less leaves it UNRESOLVED. Either kind, shown to duplicate another
tracked entry by an identity match (claim + location + judged-against
set), folds under the canonical entry as a pointer-annotated line, same as
the settled-tree supersession rule above. An entry whose locus no longer
exists — the code removed, the feature deleted — closes as OBSOLETE with
the removal evidence recorded: the one exit that examines an absence
rather than a living locus. A changed locus alone is none of these —
changed code can still carry the defect. A round whose coverage never
reached the entry's location has said nothing about it; silence downgrades
nothing, however many rounds it repeats across.

## Listing ≠ callable, label ≠ provider ID

Two separate checks, both about routing claims outrunning reality:

1. **Callability.** A model's presence in a wrapper's lineup listing is
   the tool's routing claim, not proof it answers — a listed entry has
   failed hard on first real invocation across two independent tools.
   Verify with a fixed trivial prompt sent through the SAME wrapper,
   flags, auth, and execution context the real work will use. A pass
   requires TWO observations from THIS invocation: a model answer, AND
   the wrapper's own route report naming this route as what answered (a
   banner echoing the requested slug is configuration, not attribution).
   A cached/replayed response is not a pass — run cache-bypassed. If the
   wrapper has no route-report channel at all (established only by
   positive evidence — docs, or a prior invocation that emitted one —
   never assumed from one silent response), the pass is
   reachability-only: record that limitation everywhere the pass is
   cited. A pass expires with the session; re-verify before the next
   session dispatches on it.
   ✅ "sent a fixed nonce prompt through the dispatch wrapper — answer
   carried the nonce, wrapper's route line named the model; recorded as
   verified-callable for this session."
   ❌ "no route line this time — must not have a channel; dispatched
   anyway" (unknown channel presence is a block, not a downgrade).

2. **Alias resolution.** A wrapper's model STRING is its own internal
   routing name, not necessarily the provider's API model ID — the same
   spelling existing on the provider's side proves nothing (an alias can
   collide with a different provider model). Before using a wrapper's
   model string in a direct provider API call, pricing lookup, or quota
   check: resolve the alias → provider-ID mapping from the wrapper's OWN
   config, docs, or a request trace, then validate that resulting ID
   against the provider directly. Mapping unresolved → the namespace
   crossing stays blocked.
   ❌ "the wrapper call worked and the alias exists in the provider's
   list, so they're the same model."

## Empty-output differential diagnosis

One observation of empty/dead-looking model output cannot classify it —
the reads route oppositely. Two ladders:

- **A single endpoint returns no bytes.** Before declaring it dead: (1)
  re-probe raw, ruling out your own parsing; (2) verify the key/gateway
  with a cheap call (e.g. models-list → 200); (3) send the SAME canary
  prompt to a different model on the same key/transport, seconds apart.
  Only a controlled differential — the alternate answers, the target's
  evidenced attempt still gets nothing, everything else held equal —
  isolates a model-specific outage from auth/gateway/your-own-parsing. A
  silent (unanswered, unattributed) alternate leaves the differential
  incomplete — record UNRESOLVED, never dead.
- **A model returns empty on some batch tasks.** Re-run before concluding
  anything, then classify PER TASK, not the run as a whole. Empty slot
  MOVES between re-runs → intermittent flake — usable but unreliable,
  demote to supervised/retry-wrapped use, don't drop it. Same task empty
  EVERY run → stable gap — rule out your own side for that task (parsing,
  a token cap) before recording it as a capability gap.

Either way, the ladder refines the DIAGNOSIS only — an unresolved or
flaky probe of a property that a routing/safety decision needs still
leaves that property UNKNOWN, and work relying on it does not route to
that model regardless of which ladder outcome you land on.

✅ "re-probed raw, confirmed the key with a 200, sent the same canary to a
different model — it answered, the target's evidenced attempt got
nothing: route-isolated outage, not an account block."
❌ "the output file was empty, so the model is dead" (one observation, no
differential, no re-run).

## Provenance

These three rules distill 2026-07 incidents from opus-pack upstream PRs
(#48 settled-tree, #55 recurring ledgers, #56 listing/label) merged via
the maintainer's cross-model integration review; ported into this cache
in compact form rather than the expanded upstream prose, to stay inside
this cache's size floor. The empty-output differential (added 2026-07-23)
distills #64, further refined through the maintainer's 5-round gate before
this fold (per-task classification, UNRESOLVED as a third state). Re-verify:
`grep -n "settled" references/*.md` and confirm this file still resolves
before citing it in a dispatch.
