# Maintenance Protocol — how to update this system safely

Audience: future main-session models (sonnet/opus tier). The system's value decays
if it drifts from reality OR if it bloats. This file governs both.

## §1 — Edit permissions by file

| File | May edit autonomously? | Rule |
|---|---|---|
| `~/.claude/harness/00-DIAGNOSIS.md` | NO (frozen) | Historical document. Never edit. If a diagnosis becomes stale, note that in LESSONS.md, don't rewrite history. |
| `~/.claude/CLAUDE.md` (global) | ASK USER first | Highest blast radius — every session loads it. Exception, allowed autonomously: fixing a factually broken pointer (file moved/renamed) — fix it, tell the user in the same turn. |
| Project `CLAUDE.md` files | ASK USER first | Same rule as global. |
| `10-orchestration.md` | YES for §0 facts | Update tool/model availability when VERIFIED changed (a probe failed / harness offers different models). Routing-table strategy changes: ASK USER. |
| `20-judgment-rubrics.md` | NO thresholds; YES examples | Numeric thresholds (retry cap 2, ~3× scope, 20% spot-check) changed only with user sign-off. ADDING a good/bad example from a real session: autonomous, append-only. |
| `30-delegation-templates.md` | YES, append-only | Add a template or a field; never delete the "report failure honestly" or edge-case lines. Structural rewrite: ASK USER. |
| `50-letter-to-future-sessions.md` | Handoff section only | §Handoff is a live scratch area — update freely. The letter body is frozen like the diagnosis. |
| `~/.claude/harness/LESSONS.md` | YES — this is YOUR file | See §3. Create it on first lesson. |
| Memory files (`.../memory/*.md`) | YES | Existing memory rules apply (update-in-place, no duplicates, delete wrong ones). |
| ~~`~/.claude/skills/subordinates/SKILL.md`~~ `~/.claude/skills/delegation-and-review/SKILL.md` (merged 2026-07-07) | YES | Process + dispatch quick-card — a CACHE over `10-orchestration.md`, `30-delegation-templates.md` and the subordinate playbooks, not a source of truth. See §5 write-back rule; ~~keep it ≤~150 lines~~ soft ceiling ~200 per §4 since the merge (depth still belongs in playbooks/harness). |
| `~/.claude/skills/operational-rigor/SKILL.md` | YES wording; NO thresholds | CACHE over global CLAUDE.md R0–R8 + `20-judgment-rubrics.md`. §5 write-back applies; numeric thresholds change only with the source (user sign-off). |
| `~/.claude/skills/ground-truth-gates/` (SKILL.md + scripts) | YES | CACHE over the ground-truth-harness-pattern doc (claude-code-technique project). Any edit to `scripts/` re-runs the pass AND fail probes before claiming run-verified. |
| `~/.claude/skills/skill-authoring/SKILL.md` | YES | CACHE over `00-DIAGNOSIS.md`, this file, and the letter's degradation modes. §5 write-back applies. |
| `~/.claude/hooks/gate-before-commit.sh` (+ its PreToolUse/Bash entry in `settings.json`) | YES script; ASK USER to remove/disable | Blocks `git commit` while a project's `checks/run-all.sh` is red; inert in repos without gates. Adopted 2026-07-07 from opus-pack (upstream `F-e-u-e-r/opus-pack`, fork `firaen22/opus-pack` — sync fixes from upstream when they land). Re-verify after ANY edit: `bash ~/.claude/hooks/test-gate-before-commit.sh` (13 paths, expected exits printed inline). Fixed 2026-07-07 (same day, after 5 live misfires): gates now resolve from the repo the commit TARGETS (`git -C`/`cd` in the command, fallback `$CLAUDE_PROJECT_DIR`), and detection strips quoted strings + heredoc bodies before matching — prose mentioning "git commit" no longer trips it. Upstream PR: F-e-u-e-r/opus-pack (branch `fix-hook-resolve-commit-target-repo`). Known false negative (inherent): a commit inside `bash script.sh` bypasses the hook. |

**Before ANY edit to ANY harness file:**
1. `cp <file> ~/.claude/backups/<name>.$(date +%Y-%m-%d-%H%M).bak` (backups dir
   exists; the timestamp includes hour+minute so same-day edits never overwrite an
   earlier backup).
2. Make the edit.
3. Read the file back; check the edit landed and broke no adjacent text.
4. If the file is referenced by CLAUDE.md and you renamed/moved it — you almost
   certainly shouldn't have. Restore from backup.

## §2 — Verify before you "fix"

A harness instruction that fails once is not necessarily wrong — reproduce first
(R0 applies to the harness itself). Example trap from the evidence base: a grader
once mislabeled 3 real bugs as false positives because its own reference data was
buggy. Before editing a rule because "it didn't work": run the probe twice, check
whether YOU deviated from the rule, and only then edit.

## §3 — Where lessons go: `~/.claude/harness/LESSONS.md`

After any mistake that cost >15 minutes, or any harness rule that misfired, append
an entry (this replaces scattering lessons across chat and random memory files):

```
## YYYY-MM-DD — <one-line title>
- What happened: <2–3 lines, concrete — commands, files, error text>
- Root cause: <one sentence with a MECHANISM, not "it failed">
- Rule change needed: NONE | <proposed edit + which file> 
- Status: noted | user-approved | applied-on <date>
```

Rules for LESSONS.md:
- Append-only between compressions. Never edit old entries except Status.
- A lesson proposing a CLAUDE.md/threshold change stays `noted` until the user
  approves — surface pending ones when relevant, don't nag every session.
- If the same lesson recurs 3 times, that's no longer a note — promote it: draft
  the rule edit and ask the user in the current session.

## §4 — Growth limits and compression

- LESSONS.md: compress when >150 lines or >20 entries. Compression = merge
  duplicates, promote recurring items to rule-change proposals, move applied/dead
  entries to `LESSONS-archive.md`. Never compress unapplied `noted` entries away.
- Global CLAUDE.md: hard ceiling 100 lines. If an addition would exceed it,
  something else must move to a harness/memory file first.
- Harness files: soft ceiling ~200 lines each. Past that, split — don't summarize
  away examples (examples are the load-bearing part for weaker readers).
- MEMORY.md index: one line per memory, always. Content in memory files only.
- Cadence: no scheduled maintenance. Compress on threshold-hit only. Do not
  "tidy" these files as a side quest during other work (R3: surgical changes).

## §5 — Staleness checks (cheap, do when touched — not on a schedule)

When a session actually USES a subordinate CLI or model route and it errors
unexpectedly: probe (`codex exec --skip-git-repo-check "PONG"` etc.), and if the
tool changed/vanished, update `10-orchestration.md` §0 + the relevant playbook,
with the date and the probe output as evidence. Never delete the old line —
strike it through with the replacement beside it, so the next reader sees the
change happened rather than silently different advice.

**Quick-card write-back:** whenever an edit to a subordinate playbook or a new
finding changes DISPATCH BEHAVIOR (invocation syntax, a trap and its fix, model
choice, a routing or verification rule), update the matching line in
~~`~/.claude/skills/subordinates/SKILL.md`~~ `~/.claude/skills/delegation-and-review/SKILL.md`
(merged 2026-07-07) in the same session. The same rule covers the other three
skill caches registered in §1 when their harness sources change. The card is a cache;
a stale cache silently overrides the corrected playbook because it loads first.
Evidence, N counts, and history stay in the playbooks — the card gets only the
changed operational line.
