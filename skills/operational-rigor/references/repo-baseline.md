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

**Non-empty two-dot is INCONCLUSIVE, and never a merge preview.** The base may
simply have moved on. A three-way merge applies the branch's delta from the
MERGE-BASE, so base-side work the branch never touched survives the merge even
though the two-dot lists it as deletions — survives is not untouched: a
branch-side rename of an enclosing directory can still relocate that file or
conflict on it. Those deletions materialize under `git reset --hard <branch>`, a DELETION-AWARE
sync of the tip tree (`rsync --delete`; a plain recursive copy leaves base-only
files in place), or piping the two-dot diff itself into `git apply`, but NOT
under `git format-patch --stdout $(git merge-base <base> <branch>)..<branch> |
git am` onto the base, which replays the branch's own commits and leaves
base-only files alone. Match the read to the action. A real merge preview is `git merge-tree
--write-tree <base> <branch>`. Read its EXIT STATUS first — 0 clean, 1
conflicted, anything else an error whose output is unspecified (it refuses
unrelated histories outright). On 0 and 1 its first stdout line is the OID of
the merged tree, with conflicted-file info following on 1. Diff that OID
against the base to read the merge's net change.
`git diff $(git merge-base <base> <branch>) <branch>` is the branch's
CONTRIBUTION, not the merge result; where a merge-base exists it is the same
computation as the `<base>...<branch>` form above, but only the longhand
degrades: on unrelated histories `git merge-base` prints nothing, the
substitution empties, and the command silently becomes a working-tree diff,
which the three-dot form never does. What
DELETING the branch would lose is its unlanded work, and the two-dot ADDITION
side does not measure it: once the base has moved on, that side also carries the
branch's older copy of base-side edits, which deleting the branch does not lose —
inconclusive for the same tip-to-tip reason as the deletion side. Use two
COMPLEMENTARY reads, never as equivalents: `git log <base>..<branch>` enumerates
the branch's unique COMMITS, `git diff <base>...<branch>` shows its net CONTENT
since the merge-base. They diverge — a commit plus its revert leaves the log
non-empty and the three-dot diff empty. Mind the dots on the log: two-dot
`<base>..<branch>` (or `^<base> <branch>`) is the one you want;
`git log <base>...<branch>` is the SYMMETRIC difference and lists base-side
commits too, recreating the very over-report this paragraph exists to stop.

**A torn-down worktree can make git act on the ENCLOSING repo instead of
failing.** Normal teardown fails loudly: the cwd is dead and commands there die
with "not a git repository" only when the path sits outside another checkout;
delete the directory while it is still your cwd and git dies earlier still,
with "Unable to read current working directory". `git worktree prune` does not create the silent case
below, but it does CLOSE the exit from it: it drops the admin entry of any
UNLOCKED worktree whose `.git` pointer file is missing — directory still fully
present or not ("gitdir file points to non-existent location"); `git worktree
lock` is what holds an entry through a prune. A bare `git worktree repair` run
from the main checkout rewrites the missing pointer from that admin entry, so
the exit works only until prune removes the entry; the `repair <path>` form also
restores it but exits 1 with an `error:` line, so its status reads as a failure
it is not. The silent case is
narrower and worse: the worktree's `.git` pointer file is gone while its path
still resolves INSIDE the main checkout's tree, so git's walk-up from cwd lands
on the main checkout and every later command silently rebinds to its branch, its
index, its uncommitted files — possibly another session's work. This changes
WHERE a commit or push acts, through no action of yours, and the dangerous case
is the one you did not notice. So the trigger is positional, not observational:
from any long-lived session in a linked worktree that cleanup could have touched,
re-verify identity before the first commit, push, or PR after a merge or cleanup
event. Decide it on `git rev-parse --show-toplevel` COMPARED against the worktree
path you expect — it does not error in this failure, it succeeds and prints the
enclosing checkout, so reading it without comparing proves nothing. And a rebound
checkout can sit on the very branch name you expect, so `--abbrev-ref HEAD`
alone can false-pass.

## History rewrites destroy the dirty tree — and a refs backup cannot restore it

Homed here 2026-08-29 from a 2026-08-28 incident that had been recorded only in
`harness/LESSONS-archive.md` (§4 forbids an evidence file as an order's only home;
a cross-model review found these three imperatives unhomed).

- **A backup is not a backup until you name what it does NOT cover.** `git bundle
  --all` captures REFS ONLY. Uncommitted worktree state is in no ref, so a bundle
  taken specifically to make a rewrite safe cannot restore what the rewrite
  destroys. Verifying the backup EXISTS is not verifying its CONTENTS — state the
  excluded set out loud before relying on it.
- **Before any history rewrite (`git-filter-repo`, `filter-branch`, a force
  rebase of shared history): `git stash` or copy the dirty tree first, or refuse
  to rewrite a dirty repo at all.** `git-filter-repo --force` hard-resets the
  working tree; it does not warn, and `--force` suppresses the check that would
  have. Measured: it silently destroyed 172 uncommitted insertions belonging to a
  concurrent session, recovered only by luck of an unrelated file-sync timing.
- **Leaving another session's uncommitted work in place is not the safe option it
  looks like.** "Don't touch it" protects provenance but gives zero protection
  against a destructive operation in the same repo. The safe move is
  stash-or-copy it, act, then restore it untouched.
