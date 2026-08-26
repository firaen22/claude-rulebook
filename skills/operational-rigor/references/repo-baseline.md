# Repo baseline — first moves on a live repo

Consult on the first mutating move in a live repo; the pointer in
operational-rigor §2 points here.

First move on a live repo: baseline before you mutate. Capture the starting
state (`git status` + the safe checks) and attribute every red to
pre-existing-vs-your-change; confirm intent before "restoring" a dirty tree (a
deletion may be a deliberate migration). And don't build on already-merged work:
if your branch tip is an ancestor of the upstream default
(`git merge-base --is-ancestor HEAD origin/main` succeeds), its unique work
already merged and continuing can silently revert it — being merely *behind* is
normal, don't auto-rebase to "fix" it. Leftover branches and closed do-not-merge
PRs are usually residue, not in-progress work — verify against history before
adopting or cleaning them. Squash merges defeat BOTH `git branch --merged` and
`git cherry` (per-commit patch-ids never match the one squash commit) — trust
the merged-PR record, or a two-dot `git diff <base> <branch> -- <paths>`
(empty ⇒ already landed; a three-dot `...` diff measures from the merge-base
and still reads as unlanded).
