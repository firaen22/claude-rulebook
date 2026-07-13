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
| ~~`~/.claude/skills/subordinates/SKILL.md`~~ `~/.claude/skills/delegation-and-review/SKILL.md` (merged 2026-07-07) | YES | Process + dispatch quick-card — a CACHE over `10-orchestration.md`, `30-delegation-templates.md` and the subordinate playbooks, not a source of truth. See §5 write-back rule; ~~keep it ≤~150 lines~~ soft ceiling ~200 per §4 since the merge (depth still belongs in playbooks/harness). User-approved 2026-07-07: hold past the soft ceiling; split (§9–10 → references/) only if >~250 — EXECUTED 2026-07-11 (invocations + trap table now in `references/invocations-and-traps.md`, SKILL.md back to ~216 lines). Same threshold applies to operational-rigor. |
| `~/.claude/skills/operational-rigor/SKILL.md` (+ `references/`) | YES wording; NO thresholds | CACHE over global CLAUDE.md R0–R8 + `20-judgment-rubrics.md`. §5 write-back applies; numeric thresholds change only with the source (user sign-off). Split 2026-07-13 to stay ≤~250: `references/install-gate.md` (third-party/instruction-content install gate), `references/when-stuck.md` (wrong-direction check + retry gate + mechanism replacement), `references/external-data.md` (fail-loud data-path + clue-is-a-map) — main file carries a one-line pointer to each. |
| `~/.claude/skills/ground-truth-gates/` (SKILL.md + scripts) | YES | CACHE over the ground-truth-harness-pattern doc (claude-code-technique project). Any edit to `scripts/` re-runs the pass AND fail probes before claiming run-verified. |
| `~/.claude/skills/skill-authoring/SKILL.md` (+ `references/project-skill-templates.md`) | YES | CACHE over `00-DIAGNOSIS.md`, this file, and the letter's degradation modes. §5 write-back applies. `references/project-skill-templates.md` (added 2026-07-13) holds the per-category entry-shape templates the §3 taxonomy points at. |
| `~/.claude/hooks/gate-before-commit.sh` + `~/.claude/hooks/parse-commit-command.py` (+ its PreToolUse/Bash entry in `settings.json`) | YES script; ASK USER to remove/disable | Blocks `git commit` while the TARGET repo's `checks/run-all.sh` is red; inert in repos without gates. Adopted 2026-07-07 from opus-pack (upstream `F-e-u-e-r/opus-pack`, fork `firaen22/opus-pack` main — merged there 2026-07-07, `a8ef21f`). Re-verify after ANY edit: `bash ~/.claude/hooks/test-gate-before-commit.sh` (34 paths, expected exits printed inline). Round 3 (2026-07-07, after a fresh-context adversarial review returned FIX-FIRST on round 2 — see LESSONS.md): commit detection and target-repo resolution now run on Python `shlex` tokens (quote-aware, no code execution) instead of sed/grep substring heuristics, requires `python3` (degrades the same way as missing `jq`). Requires BOTH files present — the `.py` is not optional. Upstream PRs: F-e-u-e-r/opus-pack #2 (this hook), #1 (cost-asymmetric golden gate, unrelated). Known false negative (inherent): a commit inside `bash script.sh` bypasses the hook. Known false POSITIVE (2026-07-11): the parser treats shell variables as inert text, so `git -C "$VAR" commit` resolves the target dir to the literal string `$VAR`, fails the dir check, and silently falls back to $CLAUDE_PROJECT_DIR's gates — write the absolute path LITERALLY in any command containing a commit, never via a variable. |
| `~/.claude/hooks/gate-credential-destruction.py` (+ its PreToolUse/Bash entry in `settings.json`, second in the array after gate-before-commit) | YES script; ASK USER to remove/disable | Blocks destructive verbs (rm/unlink/shred/srm/truncate, git rm, incl. sudo/env/etc. wrappers and if/for/while control-syntax prefixes) against credential-pattern paths (ssh keys, .env, .pem/.key/etc., .ssh/.aws/.gnupg trees). Adopted 2026-07-10 from opus-pack PR #11 after full install gate; **re-installed 2026-07-11 with PR #13's bypass fixes** (control-syntax command position, `--` end-of-options, secret.pub hole); **re-installed 2026-07-13 with PR #24's hardening** (fail-open→degraded-raw-scan on malformed/internal-error envelopes so a malformed envelope carrying a destructive command can't slip; oversized >1 MiB envelope blocked unread; now 291 lines) — re-verified via 50/50 fixtures + direct fail-open-vuln repro (old exit 0 → new exit 2) + live in-session block. Re-run `bash ~/.claude/hooks/test-gate-credential-destruction.sh` after ANY edit, and re-gate on any upstream update (a passed gate certifies the version read, not the path). NB the hook is an **accidental-destruction gate, NOT a security boundary** (newline-separated commands, bash -c/eval, redirect/var indirection are NOT caught — real protection is filesystem isolation). Override: `CRED_GATE_APPROVED=1` prefix, one command only, logged. Known false positive: it text-scans heredoc bodies, so documentation QUOTING a destructive-command example trips it — write such docs via Write/Edit, not Bash heredocs. Blind spots (inherent): xargs rm, find -delete, `>` truncation, Write/Edit overwrites. |

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
