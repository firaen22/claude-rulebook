# LESSONS — write-backs after mistakes (format: 40-maintenance.md §3)

Append-only between compressions. Compress at >150 lines / >20 entries.
Compressed 2026-07-12: six applied entries (2026-07-05 → 2026-07-12) moved
verbatim to `LESSONS-archive.md`; their rules live in the compiled caches
(skill-authoring §5, delegation-and-review §4, 40-maintenance §1, NIM memory).

## 2026-07-11 — Install gate passed a hook that had three live bypasses
- What happened: gate-credential-destruction.py cleared the full install gate
  (provenance, 220-line read, fixture suite both paths, live block proof);
  hours later upstream's second reviewer (gpt-5.5 xhigh, opus-pack PR #13)
  found three bypasses my read and the author's fixtures both missed:
  control-syntax wrapping (an `if…then` prefix holds command position so the
  verb goes unseen), `--` end-of-options (dash-prefixed credential filename
  read as a flag), and the blanket `.pub` exemption (secret.pub slipped
  through with ssh public keys). All three reproduced; fixed version
  re-installed + re-verified same day.
- Root cause: install gate and cross-family-review rule existed separately but
  were never composed — the gate's fixture step is bound by what its writer
  imagined, so no second family got dispatched; and a passed gate certifies
  the VERSION read, not the file path, so no re-check duty existed for
  upstream fixes.
- Bonus false-positive class: the cred gate text-scans the ENTIRE Bash
  command, heredoc bodies included — documentation QUOTING a destructive
  example trips it. Such docs go through Write/Edit, not Bash heredocs; that
  is the correct dodge, not the override.
- Rule change needed: install-gate clause extended (cross-family source
  review + re-gate on any update to the installed artifact).
- Status: applied-on 2026-07-11 locally (operational-rigor §2 clause, further
  refined 2026-07-12 to upstream's reviewed wording); upstream PR #16 opened,
  passed the repo's cross-model review (grok-4.5 + gpt-5.5, 2 rounds), was
  still OPEN at last verified check — confirm merge next time it matters.

## 2026-07-11 — gate-before-commit resolved the WRONG repo when the target dir was a shell variable
- What happened: committing to a scratch clone via `SCRATCH=<path>; git -C
  "$SCRATCH" commit ...` was blocked 4 times running, always citing THIS
  project's own (intentionally red, demo) gate — not the scratch repo's
  (which has none). Invisible until I temporarily instrumented the hook's
  stdin (reverted after, diffed clean against backup).
- Root cause: `parse-commit-command.py` deliberately treats shell variables as
  inert literal text (correct — it never executes substitutions), so `dir`
  parsed as the literal string `$SCRATCH`; `[ -d "$dir" ]` failed and the hook
  silently fell back to `$CLAUDE_PROJECT_DIR`, which had real (red) gates —
  so the misresolution masqueraded as an ordinary red-gate block.
- Rule: any Bash command whose target-repo dir gate-before-commit will read
  (`git commit` / `git -C` / `cd` sequences) writes the ABSOLUTE PATH
  LITERALLY — no `$VAR` indirection, even one set earlier in the same script.
  Same principle as "subagents inherit no env — write literal paths", turned
  back on my own tool calls: the hook is exactly as blind to my env as a
  subagent is.
- Status: applied-on 2026-07-11; also registered in 40-maintenance §1's hook
  rows 2026-07-12.
