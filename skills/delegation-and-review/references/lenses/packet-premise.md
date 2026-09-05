# Lens: packet premise (reviewing a review)

For an artifact that is itself a review, finding list, audit, or verdict produced by
someone else. This lens hunts findings that are correct GIVEN the dispatch packet and
false given the system.

Default posture is REFUTE, not confirm. Report NOT CONFIRMED unless you can reproduce.

- **Check the packet's own claims before crediting any CRITICAL.** An overstated
  contract, a fabricated precondition, or a wrong architectural premise in the brief
  manufactures findings whose correct fix is amending the PACKET, not the code.
- **Agreement between reviewers is not corroboration.** Two reviewers sharing one
  wrong premise is the same error counted twice, and a claim ranked #1 by both is the
  most likely to be acted on unchecked. (Measured 2026-08-29: codex and grok,
  different families, different packet shapes, both ranked the same false claim #1.
  Cost to refute: three shell commands.) Treat convergence as a pointer to something
  worth EXECUTING, never as confidence.
- **Every load-bearing premise gets one command.** For each finding, write the exact
  command that would settle it. Run it and record input → expected → actual. If you
  cannot execute in this environment, still write the command, mark the premise
  UNVERIFIED, and say so — the DISPATCHER then runs it before acting. Never soften an
  unrun premise to "verified by static analysis": that is the exact move that let a
  false claim reach #1 CRITICAL twice on 2026-08-29. Unverified is a reportable
  terminal state, not a failure of the review.
- **Verification tags are claims about method, not evidence.** Check whether the
  reviewer's stated method is one it can actually perform. A model that executes
  nothing cannot have run a CLI. A wrong concrete number inside a tag (a byte count,
  a line number) is the tell that the method was not run — and the underlying finding
  may still be real, so refute the tag, not automatically the finding.
- **Separate the finding from its proposed remedy.** Reproducing a finding licenses
  the finding only. The remedy is a suggestion; author the fix yourself.
- **Does the verdict bind to a state that still exists?** A review of a tree that
  moved after capture is void, not re-bound. Check the artifact's identity (hash,
  SHA, mtime) against what the reviewer actually read.
- **Silence has two causes.** An empty or short return can be a real "no findings",
  a parser/envelope bug, or the model narrating a plan and exiting. Read the raw
  bytes before recording either "clean" or "incapable".
- **What did the review NOT cover?** Name the axis with no finder. An unbounded
  review reported as complete is the failure this lens most often catches.
