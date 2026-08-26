# Mutation gates — at-mutation recheck and name-last publishing (kernel in SKILL.md §2)

Ported 2026-08-04 from upstream opus-pack. Two refinements of §2's
orient-then-act ordering, both at the boundary where the plan stops and the
side effect happens. The SKILL.md kernel is binding; this file carries the
mechanism, the primitive requirements, and the re-drive rules.

## Re-validate a mutable precondition immediately before the effect it guards

Plan-time validation goes stale while the plan executes: the name that was
free at planning is taken at write time, the branch that was clean has a new
commit, the quota that had room is spent. Re-check the precondition at the
mutation, not at the plan.

The recheck NARROWS the race window; it does not close it. Where a concurrent
writer can interleave between recheck and effect, closing it takes the
platform's own atomicity — a lock, a transaction, a compare-and-swap, or
detect-conflict-and-retry. A recheck alone is never cited as exclusion.

## A publish that assigns a stable human-visible name runs name-LAST

Where the platform offers any intermediate identity: produce and verify the
artifact under a content-addressed or staging identity, then bind the stable
name and re-read it, confirming it resolves to the verified content. A
name-first write with no post-publish comparison never satisfies this — a name
bound first points consumers at an artifact whose verification can still fail.

**Every stable-name bind is non-clobbering** — the final alias bind after
staging just as much as a direct put. Use the platform's create-if-absent /
compare-and-swap / lock primitive where one exists. A plain overwriting bind
destroys a concurrent or pre-existing foreign binding before any re-read can
see it, and the post-bind digest then matches YOUR content while someone
else's binding is already gone. **A name found holding foreign content is
never overwritten** — not to make a check pass, not as a retry.

Where the stable name is the ONLY handle (a bare `put(name, content)` store, a
registry's `name@version`), verify the artifact locally to a recorded digest
first, then bind under the same discipline.

With no such primitive on the bind path, a read-then-bind still overwrites
whatever lands in the read-bind window. Proceed only under an established
exclusive-writer or quiescence guarantee for that name (a registry only this
task publishes to, a maintenance window). No primitive and no such guarantee →
fail closed and report, or obtain explicit authorization for a labelled
best-effort overwrite that names this exact risk.

## The post-bind read, and when a failed publish may be re-driven

Re-read AUTHORITATIVELY and compare against the recorded digest. An
eventually-consistent read can return stale bytes, so a non-authoritative
mismatch is "uncertain", not a verdict.

An authoritative mismatch is a FAILED PUBLISH to report with the observed
digest. Re-drive it only under the same non-clobbering primitive, carrying
this task's recorded generation/object identity from its own earlier bind, or
a durable idempotent request outcome.

Two things that license NO re-drive on their own:

- **An authoritative "absent".** Absence on a mutable name is non-monotonic —
  another actor's bind may have come and gone.
- **Bytes matching this task's prior content.** Byte equality does not
  establish ownership; identical content re-created by another actor is
  theirs (the same rule as §3's cleanup attribution).

Either alone → report "uncertain", do not re-drive.
