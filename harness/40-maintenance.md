# Maintenance Protocol — how to update this system safely

Audience: future main-session models (sonnet/opus tier). The system's value decays
if it drifts from reality OR if it bloats. This file governs both.

## §1 — Edit permissions by file

**Standing rule only.** Port history, size ledgers, retarget maps and probe verdicts
moved to `41-file-registry.md` on 2026-08-26 (verbatim, word-checked) — read that
before a re-port or a size decision, not before an ordinary edit. On any disagreement
between the two, **this table wins**.

| File | May edit autonomously? | Rule |
|---|---|---|
| `~/.claude/harness/00-DIAGNOSIS.md` | NO (frozen) | Historical document. Never edit. If a diagnosis becomes stale, note that in LESSONS.md, don't rewrite history. |
| `~/.claude/CLAUDE.md` (global) | ASK USER first | Highest blast radius — every session loads it. Hard ceiling 100 lines (§4). Allowed autonomously: fixing a factually broken pointer (file moved/renamed) — fix it, tell the user in the same turn. Rules killed as redundant with a global R-rule are listed in `41-file-registry.md`; each verdict is TIER-BOUND and conditional on its R-rule surviving. |
| Project `CLAUDE.md` files | ASK USER first | Same rule as global. |
| `10-orchestration.md` | YES for §0 facts | Update tool/model availability when VERIFIED changed (a probe failed / harness offers different models). Routing-table strategy changes: ASK USER. |
| `20-judgment-rubrics.md` | NO thresholds; YES examples | Numeric thresholds (retry cap 2, ~3× scope, 20% spot-check) changed only with user sign-off. ADDING a good/bad example from a real session: autonomous, append-only. |
| `30-delegation-templates.md` | YES, append-only | Add a template or a field; never delete the "report failure honestly" or edge-case lines. Structural rewrite: ASK USER. |
| `50-letter-to-future-sessions.md` | Handoff section only | §Handoff is a live scratch area — update freely. The letter body is frozen like the diagnosis. |
| `41-file-registry.md` | YES, append/update per file | Evidence layer for this table: port history, size ledgers, probe verdicts. Update its entry in the SAME session as any port/extraction/probe touching a registered file. Never write an order here that isn't in §1. |
| `~/.claude/harness/LESSONS.md` | YES — this is YOUR file | See §3. Create it on first lesson. |
| Memory files (`.../memory/*.md`) | YES | Existing memory rules apply (update-in-place, no duplicates, delete wrong ones). |
| `~/.claude/skills/delegation-and-review/SKILL.md` | YES | CACHE over `10-orchestration.md`, `30-delegation-templates.md` and the subordinate playbooks — not a source of truth. §5 write-back applies. Over the §4 soft ceiling by user approval; the next addition must EXTRACT, not grow. |
| `~/.claude/skills/operational-rigor/SKILL.md` (+ `references/`) | YES wording; NO thresholds | CACHE over global CLAUDE.md R0–R8 + `20-judgment-rubrics.md`. §5 write-back applies; numeric thresholds change only with the source (user sign-off). Next addition must extract. |
| `~/.claude/skills/ground-truth-gates/` (SKILL.md + scripts + references/) | YES | CACHE over the ground-truth-harness-pattern doc (claude-code-technique). **Any edit to `scripts/` re-runs the PASS *and* FAIL probes before claiming run-verified.** Next addition must extract. |
| `~/.claude/skills/skill-authoring/SKILL.md` (+ `references/`) | YES | CACHE over `00-DIAGNOSIS.md`, this file, and the letter's degradation modes. §5 write-back applies. Well past the tested no-dilution band — the extraction order in `41-file-registry.md` is overdue and binds the next addition absolutely. |
| `~/.claude/skills/cross-model-review/SKILL.md` | YES wording; NO lineup | Installed port of opus-pack; doctrine only, NOT a cache over anything local. **Never write machine-specific detail into it** (which CLIs, slugs, effort flags, pins) — that lives in `workflow_*_subordinate.md`; its own §1 forbids a hard-coded lineup. Ships three in-body `unprobed` markers — never cite them as measured here. Re-port remaps sections against the LIVE files, never from a stored map. |
| `~/.claude/skills/skill-vetting/SKILL.md` + `~/.local/share/opus-pack/skill_snapshot.py` | YES wording; NO verdict semantics | DRIVER over `operational-rigor` §2 + `references/install-gate.md` — that file is canonical and WINS on disagreement. **The digest tool is deliberately OUTSIDE `~/.claude/`** (§3 requires running it from a trusted copy outside the tree being vetted, and `~/.claude/skills/` is exactly such a tree) — do not "tidy" it inward; set `TOOL=~/.local/share/opus-pack/skill_snapshot.py`. Re-run `python3 test-skill_snapshot.py` after ANY edit to the tool. **KNOWN UNFIXED HAZARD:** a candidate's DIRECTORY NAME is attacker-chosen and `$`, backtick, backslash and `"` survive double-quoting — a name that is not `[A-Za-z0-9][A-Za-z0-9._-]*` goes in NO shell command at all; record BLOCK. |
| `~/.claude/skills/security-architect/SKILL.md` | YES wording; NO severity ladder | Installed port of opus-pack; loads on trigger only. TWO rules ship `unprobed` (capability triangle, guardrail/denial-of-wallet) — never cite either as measured. Its per-platform secret-storage table is capability-NEGATIVE content, the class that rots silently: re-verify yearly, and re-probe before acting on any "platform X can't do Y" line. |
| `~/.claude/hooks/gate-before-commit.sh` + `~/.claude/hooks/parse-commit-command.py` | YES script; ASK USER to remove/disable | Blocks `git commit` while the TARGET repo's `checks/run-all.sh` is red; inert in repos without gates. Requires BOTH files and `python3`. Re-verify after ANY edit: `bash ~/.claude/hooks/test-gate-before-commit.sh` (34 paths). Known false negative: a commit inside `bash script.sh` bypasses it. **Known false POSITIVE — the parser treats shell variables as inert text, so `git -C "$VAR" commit` resolves the target to the literal `$VAR`, fails the dir check, and silently falls back to `$CLAUDE_PROJECT_DIR`'s gates. Write the absolute path LITERALLY in any command containing a commit, never via a variable.** (2 recurrences: 2026-07-11, 2026-08-04.) |
| `~/.claude/hooks/gate-credential-destruction.py` | YES script; ASK USER to remove/disable | Blocks destructive verbs (rm/unlink/shred/srm/truncate, git rm, incl. sudo/env wrappers and control-syntax prefixes) against credential-pattern paths (ssh keys, .env, .pem/.key, .ssh/.aws/.gnupg). Re-run `bash ~/.claude/hooks/test-gate-credential-destruction.sh` after ANY edit, and re-gate on any upstream update — a passed gate certifies the version read, not the path. **NB it is an accidental-destruction gate, NOT a security boundary** (newline-separated commands, `bash -c`/eval, redirect/var indirection are NOT caught — real protection is filesystem isolation). Override: `CRED_GATE_APPROVED=1` prefix, one command only, logged. Known false positive: it text-scans heredoc bodies, so docs QUOTING a destructive example trip it — write those via Write/Edit, not Bash heredocs. Blind spots: xargs rm, find -delete, `>` truncation, Write/Edit overwrites. |

**Before ANY edit to ANY harness file:**
1. Back up to a **path-derived** name — never the bare basename:
   ```
   f=<file-relative-to-~/.claude>   # e.g. skills/skill-authoring/SKILL.md
   cp ~/.claude/"$f" ~/.claude/backups/"$(echo "$f" | tr / -).$(date +%Y-%m-%d-%H%M).bak"
   ```
   → `skills-skill-authoring-SKILL.md.2026-08-26-1555.bak`. The timestamp alone is
   NOT collision-proof: `SKILL.md` is the most common filename in the tree, so two
   basename backups in the same minute silently clobber — it happened 2026-08-26,
   destroying `skill-authoring`'s pre-edit copy while `delegation-and-review`'s
   survived under the identical name. The path is what disambiguates, not the clock.
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
- **The line ceilings bind RULES files. Evidence layers are exempt from the LINE
  ceiling only** — `LESSONS-archive.md` (429) and `41-file-registry.md` (603) are
  append-only history that a strong reader opens on demand, and truncating them
  destroys the provenance they exist to hold. The exemption is conditional and
  checkable: an evidence file may carry NO order that isn't in a rules file, so if
  you ever find yourself obeying one of these files directly, it has drifted and the
  exemption lapses. Both density twins still apply — exempt from the line count is
  not exempt from measurement.
- **Every line ceiling above has two density twins.** A file inside its line ceiling
  but past either one has evaded the gate, not passed it. Wrapping prose to more
  lines is never the fix; moving history to an evidence file is.
  1. **Prose: ~12 words/line, measured over NON-TABLE lines** (corpus runs 7–11).
     `python3 -c "l=[x for x in open(F) if not x.lstrip().startswith('|')];
     w=sum(len(y.split()) for y in l); print(len(l), w, w/len(l))"`
  2. **Tables: ~150 words in any single row.** Markdown rows cannot wrap, so they
     are invisible to a line count AND they drag the file average — measure them
     separately, never as an excuse to skip measuring. Check with
     `grep '^|' F | awk '{print NF}' | sort -rn | head -3`.
  A row past 150 words is narrating history, not stating a rule: move the history to
  an evidence file and leave the standing rule. This is calibrated, not arbitrary —
  `40-maintenance.md` hid 6,605 words behind 103 lines for a month (64 w/line, one
  row at **2,716 words**) until the 2026-08-26 split into `41-file-registry.md`. Its
  longest legitimate row today is 119 words (a live hook hazard), so 150 clears every
  real rule while firing on that defect 18× over — and would have fired in 2026-07.
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
