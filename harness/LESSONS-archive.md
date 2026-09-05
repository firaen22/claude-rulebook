# LESSONS archive — applied entries moved out of LESSONS.md

Created 2026-07-12 (first compression, at 179 lines / 8 entries). Full text
preserved verbatim; nothing here is current instruction — see the compiled
rules in the caches.

⚠️ **"APPLIED" IS NOT A VERIFIED CLAIM. Corrected 2026-08-26.** This file
originally said entries here "are APPLIED: their rules were promoted into
skills/harness/memory." Two audits at PRESCRIPTION granularity found that false
for both compressions:
- **2026-07-12 section (below, 6 entries / 10 prescriptions):** 5 LANDED,
  2 NARROWED, 3 ABSENT. No verification map was ever produced, and three
  per-entry "compiled into §N" claims name a section that does not carry the
  rule. Audit: `claude code technique/experiments/lessons-applied-audit-2026-08-26/RESULT-0712.md`.
- **2026-08-25 section (further down, 19 entries / 23 prescriptions):** 18
  LANDED, 4 failures — all 4 among the 10 rows its verification map never
  named. See that section's own banner.

**Before relying on any entry here, check its destination file — do not trust
the Status line.** A "Status: compiled into §N" written at lesson-time decays as
files are reorganized and nothing re-checks it; it is the least reliable field
in this corpus. The cost is real: *read-only framing is not containment* was
stamped applied on 2026-07-09, had never landed, and the same class of incident
recurred 2026-07-28.

## 2026-07-05 — Stop hook pointed at /tmp; script got wiped, feature died silently
- What happened: the `settings.json` Stop hook ran `bash /tmp/hook-debug.sh`
  (context-size monitor, asyncRewake at ~50% full). macOS periodically cleans
  /tmp; the script no longer existed, so the hook failed on every session stop
  with no visible symptom — the context-warning feature was dead for weeks.
- Root cause: hook wired to a scratch path during debugging, never repointed to
  the permanent copy at `~/.claude/compact-context-monitor.sh`.
- Rule change needed: NONE — but a convention worth holding: hook commands and
  scheduled scripts must live on permanent paths (`~/.claude/...`), never /tmp
  or a scratchpad.
- Status: applied-on 2026-07-05 (hook repointed to the permanent script;
  verified: JSON valid, script runs, exit 0 on small transcript). Convention
  compiled into skill-authoring §5.

## 2026-07-05 — Context monitor nagged forever after /compact (size proxy never reset)
- What happened: once fixed, the Stop-hook monitor fired on EVERY session stop.
  The transcript JSONL is append-only ACROSS compactions, so raw file size only
  grows; after the first /compact the 1MB threshold stayed permanently exceeded.
- Root cause: raw `wc -c` used as the context proxy; compaction shrinks the
  context but not the file.
- Rule change needed: NONE — script fix: measure bytes AFTER the last
  `"subtype":"compact_boundary"` marker (grep -b offset). Embedded copies of the
  marker in message content are JSON-escaped, so they can't false-match.
- Status: applied-on 2026-07-05 (verified: live transcript with 2 boundaries →
  exit 0 post-compact at ~310KB effective; tiny transcript → exit 0; backup at
  `~/.claude/backups/compact-context-monitor.sh.2026-07-05.bak`)
- FOLLOW-UP (same day): the boundary fix cured post-compact nagging but NOT the
  every-turn re-nag while you stay over threshold without compacting — the Stop
  hook has no memory between turns, so it re-fired on every completed task. Added a
  debounce: per-transcript state file (`~/.claude/.context-monitor-state/<sha>`)
  stores the effective size at last warning; re-warn only after a compact resets
  effective size OR it grows another REWARN_STEP (500KB). Verified across a 7-case
  lifecycle (first-warn / debounced-silence / below-step-silence / rewarn /
  compact-reset / fresh-warn) — all 7 exit codes correct.

## 2026-07-07 — gate-before-commit hook gates the WRONG repo + text-matches commands
- What happened: the hook (adopted from opus-pack same day) blocked Bash calls
  FOUR times in one session. Only one was a real commit attempt; the others were
  a command whose text mentioned the hook's own name, a printf writing a script,
  and a heredoc appending this very lesson. The one real commit it blocked
  targeted ~/.claude, but the hook ran claude-code-technique's demo golden gate
  (red, macro-F1 0.745) because it keys on $CLAUDE_PROJECT_DIR, not the repo
  receiving the commit.
- Root cause: two compounding heuristics — substring match on the raw command
  text (any mention of the g-word+c-word trips it), and gate selection by
  session project dir instead of the commit's working directory.
- Rule change needed: NONE locally (workaround: write the commit into a script
  file via the Write tool, run `bash <script>` — outer command carries no
  trigger text; documented in 40-maintenance §1). Upstream candidate fix (an
  opus-pack issue, not yet filed — user's call): parse the commit's cwd from
  the command before choosing which checks/ to run.
- Status: applied-on 2026-07-07, round 2 of 3 — hook fixed (target-repo
  resolution via `git -C`/`cd` parse + quote/heredoc stripping before the
  match), 16-path suite ALL PASS. A fresh-context adversarial review of this
  round (asked to try to break it, not just confirm the suite) returned
  FIX-FIRST: 6 more defects (F1 bare `-C` not anchored to `git` — `make -C`/
  `tar -C` hijack target-repo resolution, exactly the "wrong repo" bug this
  hook exists to prevent; F2 the two-pass sed quote-strip mis-pairs on
  apostrophes/escaped quotes — blocked a legitimate non-commit command LIVE
  during the review itself; F3 gates ran with the hook's own cwd, not the
  target repo root, breaking relative-path checks/run-all.sh; F4 single-quoted
  `-C`/`cd` args invisible; F5 heredoc truncation dropped everything after the
  first `<<`, silently allowing a real commit later in the same command; F6
  `git help commit`/`git log --grep commit` misread as commits). Root cause:
  hand-rolled sed/grep text heuristics cannot reliably reconstruct shell
  quoting/structure. Round 3 fix: replaced all of it with Python's `shlex`
  (quote-aware tokenizer, no code execution) plus a real heredoc-body
  stripper that tracks actual open/close delimiters. Verified with a 34-case
  suite (16 + 2 per F1/F4, 3 for F2, 1 for F3, 2 for F5, 2 for F6, 6 sanity
  checks for legitimate forms) — all pass — plus a direct replay of the
  command that was live-blocked mid-review. Merged into fork main
  (firaen22/opus-pack `a8ef21f`) and installed locally (now two files:
  gate-before-commit.sh + parse-commit-command.py — the hook depends on
  python3, same fail-closed posture as missing jq). Upstream PR #2 pushed.
  Rule for next time: an "ALL PASS" suite the author wrote themselves is
  necessary but not sufficient for a text-parsing hook — a review that
  explicitly tries to break it, not just replay the known cases, kept finding
  more; the same "try to break it" pass should run again before the next
  round of trust.
- 2026-07-07 (link-generator): REPRODUCED two documented traps in one session — (1) opencode big-pickle stalled (exit 124, 0-byte out, no on-disk edits) on a ~200-line file-edit task; retry on nvidia/openai/gpt-oss-120b succeeded first try, clean spec-compliant edit. (2) agy silent-hang reproduced with numbered-header contract prompt (合約一/二…) even with escape hatch + --add-dir; killed at ~15min/0 bytes, retried as pure prose paragraphs. Frequency data: big-pickle 1/1 stall on file-edit, gpt-oss-120b 2/2 success (edit + module+harness 12/12).
  ADDENDUM same session: the agy PROSE retry ALSO timed out (2x300s, 0 bytes) — hang not attributable to numbered headers alone; suspect --add-dir on a repo with node_modules, or agy service degradation that day. Next time: pipe the single file's content inline instead of --add-dir, or skip agy.

## 2026-07-07 — Coverage-gap audit baseline forgot the tool-description surface
- What happened: the Fable→Opus/Sonnet gap audit (diff 61 Fable techniques vs the
  successor skills/harness/CLAUDE.md/memory corpus) flagged 9 candidate gaps. 2 of
  them — Workflow pipeline-vs-barrier discipline and schema-forced structured
  returns — are NOT real gaps: the Workflow tool DESCRIPTION teaches both, and it
  co-loads with the tool every session a model can use it.
- Root cause: the gap-diff's coverage baseline was the user's persistent FILES
  only. It omitted the always-loaded tool/skill descriptions, so techniques the
  harness already teaches through the tool surface read as "missing".
- Rule change needed: NONE — convention: when auditing what a future session will
  or won't know, the coverage baseline is (persistent files) PLUS (tool + skill
  descriptions that auto-load in that session), not files alone. Otherwise you
  manufacture phantom gaps for anything the tooling already documents.
- Status: applied-on 2026-07-07 (7 genuine gaps written into operational-rigor /
  delegation-and-review / 30-delegation-templates + a new
  delegation-and-review/references/discovery-sweep.md; the 2 phantom gaps
  correctly skipped; each edit grep-verified, both skills held under the ~250
  cache threshold).

## 2026-07-09 — agy WROTE to the real repo during a read-only "review the spec" dispatch
- What happened: dispatched agy×2 (Gemini) as an ADVERSARIAL SPEC REVIEWER ("list
  inputs that break these rules") with --dangerously-skip-permissions, from a
  scratch cwd, with NO --add-dir to the project. agy ignored the review framing,
  chose to IMPLEMENT, and wrote src/utils/whatsapp.ts to the ABSOLUTE real-repo
  path (plus its own ~/.gemini scratch), overwriting my reference impl. The
  harness flagged the external change; content was functionally identical so no
  harm, but it was an uncontained write to a live repo with secrets.
- Root cause: --dangerously-skip-permissions grants full file-write, and agy (like
  the gpt-oss/opencode "roams absolute paths" note in the opencode playbook) acts
  on ABSOLUTE paths regardless of cwd. A "review only" verb does NOT stop it from
  writing. Read-only framing is not containment.
- Rule: for pure-analysis agy dispatches, INLINE the material in the prompt so no
  file tool is needed and DROP --dangerously-skip-permissions (or accept it will
  roam+write and git-audit after). Never assume a review prompt prevents writes.
- Status: reproduced 2026-07-09; reference file restored + `git status` audited
  clean. The firefire's real deliverable (codex/opencode/NIM scratch outputs graded
  20/20 each vs the KAT) was unaffected, and agy's finding still landed (all
  adversarial edges were pre-documented out-of-scope limitations). Rule compiled
  into delegation-and-review §4 (scope reviewer capability to the artifact).

## 2026-07-12 — NIM-via-opencode timed out on one-shot codegen; direct-curl succeeded first try
- (link-generator jargon port): NIM-via-opencode timed out twice (exit 124, 0 bytes on
  disk) on a ~65-line single/two-file TS port with BOTH gpt-oss-120b and qwen3-next-80b, while NIM
  direct-curl PONG was healthy and direct-curl codegen of the same brief succeeded first try
  (gpt-oss-120b, 2.7KB clean file, 37/37 test gate). Lesson: for pure one-shot codegen, skip the
  opencode agent layer entirely — direct-curl is the reliable NIM path; reserve opencode-NIM for
  tasks that genuinely need file-edit/tool use.
- Status: promoted 2026-07-12 — caveat added to
  `~/.claude/memory/reference_nim_via_opencode.md` (its "verified working ~5s"
  agent-path claim now carries this stall repro).

---

## Moved here by the 2026-08-25 compression (LESSONS.md was 243 lines / 19 entries)

⚠️ **CORRECTED 2026-08-26.** The original banner here claimed "all entries below
were verified APPLIED before the move." That was FALSE — a 9-row check stated as
a 19-row claim. What was actually verified is the 9 lessons named in the map
below; the other 10 were moved with no destination named and no grep run.

A prescription-level re-audit on 2026-08-26 (23 checks, pre-registered, 3
fresh-context read-only agents + direct re-verification of every non-LANDED
verdict) found 18 LANDED and 4 not: 07-28 rule 3 (stop the fan-out on first
mutation) ABSENT; 07-28 rule 4 (read-only is not a control) CONTRADICTED by
`delegation-and-review` §8; 07-28 rule 2 (post-fan-out contamination check)
NARROWED to worktree/agy scopes; 08-04's glossary and third-door rules never
compiled out of `project_opus_pack_fork.md`. **All four failures were in the 10
unnamed rows; all 9 map-named rows checked out.** The method was sound where it
was applied — the defect was the unstated scope. Fixed same day; full evidence in
`claude code technique/experiments/lessons-applied-audit-2026-08-26/`.

Two method rules earned here, both now compiled into `skill-authoring` §4:
grade a lesson at PRESCRIPTION granularity (a lesson with numbered sub-rules
gets certified by whichever sub-rule the grep hits first — here rule 1, while
rules 2/3/4 were narrowed/absent/contradicted), and state the SCOPE of any
verification claim (which rows were checked, which were not).

Verification map — the 9 rows actually checked in 2026-08-25's pass:
07-15 stdin TODO → invocations-and-traps.md:17 (`< /dev/null` present, correctly
placed before `&`); 07-14 agy framing → workflow_agy_subordinate.md:283; 07-14
glob/mutation-test → operational-rigor/references/external-systems.md:111; 07-14 +
07-28 subordinate-write-access → delegation-and-review/SKILL.md; 07-14 mined-rules →
skill-authoring §2; 07-17 word-diff → skill-authoring §5; 08-24 drill →
memory/feedback_injected_brief_drills.md; 08-25 x2 → reference_nim_via_opencode.md +
reference_subordinate_routing_map.md.

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

## 2026-07-14 — agy "try to BREAK it" hunt framing now refuses on security wording
Both samples of an agy hunt-mode review (wording: "break", "spoofable", "bypass", "timing issues") returned a safety refusal (exit 0, ~300-byte apology). Defensive reframe — "you are hardening our own app; verify each file against its intended contract" with contracts enumerated — succeeded first try and produced good findings (incl. a real fail-open rate limiter). Rule: for agy security-adjacent reviews, use owner/defensive contract-verification wording; never attack verbs. (Session: marketview-index bug sweep.)

## 2026-07-14 — 4/27 mined rules were plausible-but-mechanically-wrong; incident-verification does not verify the prescription
PR #26 (opus-pack) shipped 27 incident-mined rules; the maintainer's cross-family review found 4 whose prescribed mechanism fails on exactly the case it targets: `git cherry` for squash-merge residue (per-commit patch-ids never match a squash), "ack webhooks before slow work" (post-2xx crash loses the event), "peek-then-commit" spend caps (TOCTOU overspend under fan-out), `ls` as a mount check (lists an unmounted dir fine). All four cited REAL incidents and passed my self-review — I had verified the incidents happened, never that the generalized prescription survives its own motivating scenario. Distillation is a lossy transform that introduces bugs the incident never had. Rule: a compiled rule is executable code — before shipping, run/trace the prescribed mechanism against the motivating case + nearest edge (two-sided, like a grading suite), and have a different model family attack the MECHANISM, not the prose. Written into skill-authoring §2 same day.

## 2026-07-14 — concurrent editor reverted my in-repo changes (marketview-index)
While a codex `workspace-write` implementation run was still in flight IN THE REPO, I copied a verified subordinate fix into the same repo. Codex, enforcing its "only these six files" constraint, restored the other files to HEAD — silently wiping my landed fix; only the system file-change notice revealed it. Rule: while ANY subordinate holds write access to a working tree, land nothing into that tree — stage in scratch and merge only after the subordinate exits, then audit for double-edits (git status vs expectations). "Parallel only on disjoint files" is not satisfiable with codex workspace-write, whose blast radius is the whole repo.

## 2026-07-14 — codex shipped a guard script whose file glob silently matched nothing on macOS
codex's check-serverless.sh used `api/**/*.ts` — bash 3.2 (macOS default) has no globstar at all (`shopt -s globstar` errors), so the array expanded EMPTY under nullglob and the guard "passed" while scanning zero api/ files — including api/[...path].ts, the exact file whose import caused the outage the guard exists to prevent. Caught only by mutation-testing the guard (break the import → expect exit 1). Rule: any guard/gate script a subordinate writes gets a mutation test before trust — prove it FAILS on the bad case it targets, not just that it passes on current code (same principle as "a regression test counts only if it fails against the old bug"). And on this machine, never accept `**` globs in bash scripts — use find.

## 2026-07-15 — codex exec implementation dispatch hung on stdin
Symptom: backgrounded `codex exec -s workspace-write "$(cat spec)"` sat at
"Reading additional input from stdin..." indefinitely; no files written.
Cause: invocations-and-traps.md's IMPLEMENTATION one-liner omits `< /dev/null`
(only the review recipe has it). Backgrounded codex with an open stdin waits.
Fix applied: always `< /dev/null` on every backgrounded codex exec.
TODO write-back: add `< /dev/null` to the implementation one-liner in
~/.claude/skills/delegation-and-review/references/invocations-and-traps.md.

## 2026-07-17 — anchor-grep invariants under-verify a condense pass
- What happened: size-control extraction of 4 skill caches passed invariant-grep
  (anchors/pointers/headers/examples vs backup), unicode sweep, and 4 fresh-sonnet
  gap-tests — yet a word-diff review then found 5 leaked clauses, 2 lost outright
  (op-rigor "gate is trust review, not the go-ahead"; GTG auth-before-quota
  ordering case). All fixed same session.
- Root cause: anchor-level greps verify STRUCTURE survived; a condense pass loses
  meaning at CLAUSE level, below what anchors and section headers can see.
- Rule change needed: word-diff-vs-backup + trace-each-dropped-clause added to
  skill-authoring §5 step 2 (condense/extraction passes).
- Status: user-approved | applied-on 2026-07-17

## 2026-07-28 — a read-only review subagent MUTATED the repo under review
- Context: marketview worldmonitor-port. Fresh-context review Workflow (4 dimensions
  x adversarial verify) dispatched over a staged diff, brief said review, not edit.
- What happened: one agent deleted the `if (seq !== requestSeqRef.current) return;`
  stale-response guard from `src/hooks/useMarketData.ts` and left the marker comment
  "BROKEN-FOR-TEST: simulated regression — guard removed to see if existing suite
  catches it", plus an untracked scratch test file. It was running its own mutation
  test ON THE LIVE WORKING TREE of a repo where push-to-main = production deploy.
- Caught by: reading the file myself to verify an unrelated finding — NOT by any
  gate. `npm test` stayed GREEN with the guard gone (that hook had zero race
  coverage), so the suite would not have caught it either. Detected only because
  `git diff` (unstaged, post-`git add -A`) isolated it to one line.
- Precedent: this is the 2nd instance (sweep-6: "agy edited files despite
  read-only"). It is a recurring class, not a one-off.
- Rules confirmed/added:
  1. STAGE the work (`git add -A`) BEFORE dispatching any review over it. The index
     then acts as the frozen baseline: `git diff` shows exactly what reviewers
     touched, and `git checkout --` restores in one step. This is what made the
     blast radius one line and the recovery instant.
  2. After ANY review fan-out, `git status --porcelain` + `git diff` BEFORE reading
     findings. Treat a non-empty unstaged diff as tree contamination.
  3. On first observed mutation, STOP the workflow — do not let the remaining
     verify agents keep running against a tree they may also write to. Findings
     already returned are still usable; verify them yourself.
  4. "Read-only" in the prompt is not a control. Only the filesystem/worktree
     boundary is. Prefer `isolation: 'worktree'` for review fan-outs on any repo
     that deploys from the branch under review.
- Silver lining, recorded honestly: the mutation empirically PROVED the reviewer's
  own coverage-gap finding (the suite does not catch that deletion). I kept the
  finding, authored the regression test myself, and mutation-tested it (guard
  removed -> test fails with the expected assertion; restored -> green).
- Status: applied 2026-07-28

## 2026-07-28 — codex reverted my concurrent fix, then truthfully reported "no other file modified"
- Context: TG-bot-helper- security audit. Two approved fixes. Codex held
  `workspace-write` implementing fix #1 (`commandHandler.ts` auth gate); I applied
  fix #5 (a one-line `redactForLog` wrap in `aiPipeline.ts:367`) by hand while that
  run was still in flight.
- What happened: codex ran `npm run check` as its own verification, then did a
  final scope audit, saw `M src/bot/aiPipeline.ts`, and concluded from its clean
  opening `git status` that the gate run had generated it. It reverted my line
  verbatim back to the unredacted `${String(error)}` — narrating this mid-transcript
  as "removing only that gate-generated artifact" — and its final report then said
  **"No other file was modified. [verified: `git status`]"**. That sentence was
  literally TRUE at report time, precisely BECAUSE it had reverted the edit.
- Why this is a new instance, not a repeat of 2026-07-14: there the constraint
  enforcer wiped files silently and the system file-change notice exposed it. Here
  the revert is a deliberate, reasoned cleanup action, and the completion report is
  ACCURATE — so no claim in the report is falsifiable and no notice fires. Reading
  the report as specified catches nothing; only `git diff --stat` against my own
  expectation of what should be modified caught it.
- Rules confirmed / sharpened:
  1. Reconfirms 2026-07-14: land NOTHING in a tree while a subordinate holds write
     access. This is now 2 instances, 2 different mechanisms, same root cause.
  2. NEW: a subordinate's scope-hygiene reasoning treats any foreign diff it did not
     author as its own contamination to undo. Anything in the tree that it cannot
     attribute is a revert candidate — including correct, deliberate work.
  3. NEW: "no other file was modified" is a claim about the tree AT REPORT TIME, not
     about what the run did. It cannot distinguish "never touched it" from "touched
     it and put it back." Verify scope with `git diff --stat` against your OWN
     written-down expectation of which files should be dirty (expected-before-actual,
     applied to file scope, not just to test results).
  4. Cheap structural fix, adopted: stage your own edits (`git add`) before any
     codex `workspace-write` dispatch — same index-as-baseline trick that bounded the
     2026-07-28 review-mutation incident. A staged edit survives a working-tree revert
     and shows up immediately in `git status`.
- Also recorded: codex reported "GATES RED — do not ship" (44 unit-test failures +
  sandbox `listen EPERM` on tsx IPC pipes). Per R0/dual-review I re-ran the gate that
  actually matters on the host — `npm run lint` (`tsc --noEmit`) — clean. The RED was
  its sandbox, not the change. Matches the existing "a reported FAILURE is a claim
  too" rule; the EPERM-on-tsx-IPC signature is now seen twice.
- Status: applied 2026-07-28

## 2026-08-04 — applying a correct review finding introduced a worse defect than the finding
Round 1 of opus-pack PR #125 correctly flagged an over-long naming duty. Fixing it,
I tightened "Named either way" to "Silently retaining SUCH A component" — which
re-pointed the antecedent at the hazard class and silently dropped the naming duty
for components excluded on reachability grounds, i.e. the rule then licensed quietly
not-reverting part of what a user explicitly ordered reverted. Only a second review
round caught it. Fourth incident in this family: **a fix is a change and needs its
own review; a reviewer who found the problem has not verified your solution to it.**

## 2026-08-04 — borrowing a word the target file DEFINES silently over-broadens a rule
Same PR: I wrote "reversal is itself destructive" in operational-rigor, which defines
destructive at §1 as *delete, overwrite without backup, push, deploy, send*. A revert
commit gets pushed — so the carve-out fired on every rollback and collapsed the rule
into "hold everything and ask". **Check the target file's own glossary before reusing
its vocabulary; name the hazard instead of invoking the defined term.**

## 2026-08-04 — a test that can CONFIRM a presumption but never DISCHARGE it has no exit
opus-pack PR #126 set a default ("an untagged example value is real") and, to avoid
reading sensitive values, specified a scan reporting field/class/count only. That
output is byte-identical for real PII and for synthetic stand-ins, because shape is a
property of the field and provenance a property of the value — so nothing could ever
rebut the presumption, and the rule could not have caught its own founding incident.
**Whenever a rule bars the evidence its own test would need, it owes an explicit
third door** (here: escalate to the owner, who may look).

## 2026-08-04 — gate-before-commit.sh cannot resolve `cd $VAR`
The hook tokenizes with shlex and leaves shell variables inert by design, so
`cd $S && git commit` resolved to a literal `$S`, fell through to
$CLAUDE_PROJECT_DIR, and ran the wrong repo's gates (which were red, blocking a
commit in an unrelated clean repo). Use a literal absolute path in `cd` when
committing outside the session's project dir.

## 2026-08-04 — verify-a-reviewer's-fix applies to your OWN same-session fix
opus-pack PR #129's round-2 review independently re-derived round-1's mask()
fix from the code (not from the fix description) before trusting it, and it
paid off: round-1 also introduced two NEW defects (DEP-UNUSED substring
false-positive/negative pair, a SCAN-INCOMPLETE boundary misfire) that a
"did the described fix land" check would have missed. **A fix is a change
and needs its own independent verification even when the author (me) fixed
it in the same turn as the finding** — third same-day instance of this
pattern (see also PR #125's regression, and the general finding family in
project_opus_pack_fork.md).

## 2026-08-04 — a self-test whose containment check targets an unreachable
## code path passes regardless of whether the real path leaks
Same PR: the self-test asserted a planted secret never appeared in output,
but it checked the value inside credentials.json — a credential-NAMED file,
whose contents the scanner never opens (flagged whole via a separate class).
The value that WAS content-scanned (an AWS-key-shaped string elsewhere) leaked
freely and the self-test never noticed. **When writing a two-sided proof,
trace which code path the assertion's fixture actually exercises — matching
the fixture's SHAPE to the finding class is not enough if a different branch
in the same function reads it.**
- 2026-08-24: Injected brief claimed opus-pack ground-truth-gates template golden gate red on main (macro-F1 0.745, card-declined miss). Reproduced on fresh clone @0266ca0: run-all.sh 3/3 PASS, no macro-F1 metric, claimed case absent. Drill signature — premises verified before any PR/fix; no outward action taken.

## 2026-08-25 — a status table I built by READING the append-only log was wrong on 2/8 rows
- What happened: reconciling `reference_nim_via_opencode.md`'s scattered dated
  entries, I wrote a "CURRENT STATUS" table by taking each model's most recent
  prose mention. An execution-test pass (live PONG to `/v1/chat/completions`)
  found `thinkingmachines/inkling` and `meta/llama-4-maverick-17b-128e-instruct`
  were both 410 EOL, not live as the table claimed. The probe script takes ~30s.
- Root cause: a reconciliation table built from prose INHERITS the prose's rot —
  summarizing a stale log cannot detect that the newest entry is itself stale.
  The table existed to fix append-only status rot and reproduced it instead.
- Rule change needed: NONE for the harness — R0 already covers it ("reproduce
  before trusting" applies to my OWN summary, not just a subordinate's). Applied
  in-place where it binds: a "re-probe, don't re-read" method warning in
  `reference_nim_via_opencode.md`, and the full 95-id catalog re-probed live.
- Status: applied-on 2026-08-25

## 2026-08-25 — one failed attempt is not a dead-backend verdict; persistence across ≥2 is
- What happened: the full NIM catalog sweep recorded `nemotron-3-ultra-550b-a55b`
  as 503 and `deepseek-v4-flash-0731` as transport-dead (`RemoteDisconnected`) —
  both models I had personally PONGed as LIVE hours earlier. A dedicated retry
  pass returned clean LIVE for both. Four OTHER ids stayed `RemoteDisconnected`
  across two independent attempts and are genuinely unroutable.
- Root cause: 503 and transport-level disconnects are transient shapes on this
  endpoint, same as the already-documented 529 `Overloaded`. The discriminator is
  PERSISTENCE ACROSS ATTEMPTS, not the error shape — any single failure (410/404/
  429/503/529/XPORT) is compatible with both "dead" and "noise".
- Rule change needed: NONE new — this is the PAID≠DEAD≠INCAPABLE rule generalized.
  Corollary written into `reference_subordinate_routing_map.md`'s refusal-shapes
  bullet + the NIM reference's sweep section.
- Status: applied-on 2026-08-25


# ─────────────────────────────────────────────────────────────────────────────
# Moved from LESSONS.md by the 2026-08-27 compression (196 lines / 5 entries,
# over the >150-line trigger). Entries below are VERBATIM — no rewording, so no
# BINDINGS pass was owed (skill-authoring references/distilling-rules.md
# §Compression and restructuring passes: a word-diff is sufficient for a move,
# never for a reword).
#
# Each destination was grepped and its operative sentence quoted BEFORE the move,
# per 40-maintenance.md §3. (Cross-model review 2026-08-28 found this claim was
# initially OVERSTATED: R-D was listed without its sentence and two destinations
# were missing entirely — fixed below the same day. Line numbers are the grep
# hits of the moment they were taken and rot as files change; the quoted
# sentences are the durable check.) What was verified, and where:
#   - "A fix is a change"            -> skills/operational-rigor/SKILL.md:260
#     "A fix is a change, and inherits the full verification duty of one."
#     (carries the sharpened "re-probe, don't re-read" edge at :269)
#   - "Word-presence diffs"          -> skills/skill-authoring/SKILL.md:474
#     "Three cuts go wrong in ways a word-diff cannot show"
#     + references/distilling-rules.md:132 "A reword needs a BINDINGS pass"
#     (PROVISIONAL qualifier intact)
#   - "read-only is not a control"   -> FOUR destinations, all grepped 2026-08-28:
#     skills/delegation-and-review/SKILL.md:423 "\"Read-only\" in a prompt is NOT
#     a control - only the filesystem boundary is."; :431 "gets an enforced
#     boundary BEFORE dispatch: `isolation: 'worktree'`, an enforced copy, or a
#     frozen snapshot"; routing-map rule R-D "verify the boundary by attempting
#     an escape, never by reading the flag name"; workflow_grok_subordinate.md
#     §CONTAINMENT (the fail-open `--tools` table). The banner's first version
#     listed only :423 + R-D and quoted only :423 — corrected same day after
#     cross-model review flagged the gap (grok F8/F21).
#   - grok idle (both entries)       -> memory/workflow_grok_subordinate.md
#     section "Empty has TWO causes"; "The fix is packet SHAPE, not retry"
#     (2026-08-28 correction: commit cb6a9ae — made BEFORE this compression but
#     read only after — had deleted that section and §Tool-use short-circuit
#     without re-homing them; both were restored, reconciled with cb6a9ae's
#     retraction, the same day. The :145 line ref is dropped as unstable.)
#
# The read-only counter moved because its promotion is EXECUTED, not because it
# aged out. Its one order that lived nowhere else - re-grep a claimed destination
# in the same edit as the claim - was homed in 40-maintenance.md §3 BEFORE this
# move, so nothing here is an order without a rules-file home (§4).
# ─────────────────────────────────────────────────────────────────────────────

## APPLIED RULE CHANGE — 2026-08-26 (§3: recurred ≥3×, promoted on user order)

### "A fix is a change, and needs its own independent review"
- **Recurrence: 4 instances, no cache home.** Every other lesson in the archive
  landed in a skill or memory file; this one has been re-learned four times and
  written down four times without ever being compiled into an always-loaded
  rule. Grep confirms it exists nowhere in `skills/` or `harness/*.md` except as
  narrative history in `LESSONS-archive.md`.
- Instances: opus-pack PR #125 (applying a correct finding re-pointed an
  antecedent and licensed quietly not-reverting user-ordered work — caught only
  by a 2nd review round); PR #129 round-2 (round-1's own mask() fix introduced
  two NEW defects — a DEP-UNUSED false-positive/negative pair and a
  SCAN-INCOMPLETE boundary misfire — which a "did the described fix land" check
  would have missed); PR #125's own entry already called itself "fourth incident
  in this family"; and 2026-08-25 this session, where my fix for append-only
  status rot (a reconciliation table) reproduced the exact rot it was written to
  eliminate, wrong on 2/8 rows.
- Mechanism that makes it recur: the reviewer who found the problem has NOT
  verified the solution to it, and the author's attention at fix time is on the
  finding, not on what the edit's blast radius newly touches. Checking "did the
  described fix land" is structurally incapable of catching a defect the fix
  introduced.
- **APPLIED 2026-08-26** to `skills/operational-rigor/SKILL.md` §4 (Verify by
  execution), inserted after the "a failing check has two suspects" bullet.
  Backup: `~/.claude/backups/operational-rigor.SKILL.md.2026-08-26-fixrule.bak`.
  Ships `unprobed` — incident-derived, never bare/ruled probed.

- **Mechanism trace before shipping** (the 2026-07-14 lesson: a compiled rule is
  executable code — run the prescribed mechanism against its motivating case and
  the nearest edge, because distillation introduces bugs the incidents never had).
  Prescription: *re-derive the fixed behavior from the artifact, not your fix
  description; check what the edit newly touches.*
  - PR #125 (antecedent re-pointed, naming duty silently dropped) → CATCHES.
    Re-deriving means reading the edited sentence and asking what "such a
    component" now refers to and what duty that leaves; the dropped duty is
    visible in the artifact, invisible in the fix description.
  - PR #129 (round-1 mask() fix introduced a DEP-UNUSED false-positive/negative
    pair + a SCAN-INCOMPLETE boundary misfire) → CATCHES, and is the empirical
    proof: round-2 did exactly this (re-derived from the code, not the fix
    description) and that is how the two new defects surfaced.
  - 2026-08-25 NIM table (fix reproduced the rot it was written to remove) →
    catches ONLY under the sharpened wording. "Re-derive from the artifact" read
    naively means re-reading the table, which is what produced the defect. The
    shipped rule therefore names the ground truth as the artifact for summaries
    and tables ("re-probe, don't re-read"). This edge is why that clause exists —
    without it the rule would not catch its own most recent instance.
  - Nearest edge, pure revert: re-derivation is trivial and the rule costs
    nothing. No regress risk — verification is a read, not a change, so it does
    not itself trigger the duty.
- **Self-application caught two defects in this very edit** (recorded because it
  is the rule's own first live test, N=1): the draft cited
  `harness/LESSONS-archive.md` as holding the mechanism trace when the archive
  holds only the incidents — the trace did not exist anywhere until this block was
  written — and it used a bare relative path where the file's convention (line 8)
  is `~/.claude/`-prefixed. A "did the described fix land" check passes both. Both
  fixed before commit.
- Status: **applied-on 2026-08-26**

## RECURRENCE COUNTER (closed) — moved with its parent heading's context
(In the source file this bullet sat under "## RECURRENCE COUNTERS (applied rules
that are climbing toward promotion)"; that heading stayed in LESSONS.md with the
two still-open counters. Reproduced here so the bullet is not read as part of
the entry above.)

- **A read-only instruction is not a control — 4 instances (3 by 2026-07-28,
  a 4th on a new tier 2026-08-27), THRESHOLD MET, promotion executed 2026-08-26** (2026-07-09 agy, dispatched as an adversarial
  spec REVIEWER, "ignored the review framing, chose to IMPLEMENT" and overwrote a
  file at an absolute real-repo path; 2026-07-14 agy edited 4 files despite
  read-only in sweep-6; 2026-07-28 a review subagent deleted a stale-response
  guard from a live working tree). Only the filesystem boundary is a control.
  Now applied at `skills/delegation-and-review/SKILL.md:423` (classify by tools
  held, not by brief) with the worktree/enforced-copy clause at :431.
  - **4th instance, 2026-08-27, found by probe not by damage — and it extends the
    rule.** grok CLI 1.0.5 dispatched with the playbook's own "Do NOT edit any file"
    brief wrote outside its `--cwd` on first ask; so did `--disallowed-tools` and both
    `--sandbox` names tried (5/5 uncontained configs). Only a positive `--tools`
    allowlist held (2/2). **New mechanism worth carrying: the control flag itself can
    fail OPEN — one unrecognised name in `--tools` silently voids the entire allowlist,
    rc=0, no warning, full write+shell restored.** So "I passed the containment flag" is
    itself a self-report. Verify a boundary by ATTEMPTING AN ESCAPE, never by reading the
    flag name. Landed as routing-map rule R-D + [[workflow-grok-subordinate]] §CONTAINMENT.
  - ⚠️ **Corrected 2026-08-26 — this counter was wrong in two ways at once, and
    the two errors masked each other.** It read "2 instances" (the 07-09 case was
    never counted) AND asserted the rule was already "Applied in
    `delegation-and-review`" when `isolation: 'worktree'` appeared in no rules
    file at all. §3 says promote at 3; the third instance landed 2026-07-28, so
    the promotion was a month overdue and only ran because an audit tripped over
    it. **A counter that believes its rule is already applied never promotes —
    so when you log an instance, re-grep the claimed destination in the same
    edit.**


## 2026-08-27 — Word-presence diffs certify words, not bindings (3 compressions, 3 escapes)
- What happened: Three consecutive rules-file compressions (3ade6e2, 4ab2a56, 514a227)
  were each verified by grep/token-diff and passed; external review then found a real
  loss in every one: a pre-registration TIMING order (words all present, before/after
  lost); a dropped NON-FREE qualifier that made the sentence false against data 8
  lines above; 9/10-vs-4/20 numbers detached from their subject (-medium) and
  re-attaching to the adjacent -low sentence; ">=4 independently-authored unseeded
  defects" silently merging two independence conditions into one.
- Root cause: token-presence checks are order-blind — a binding (subject↔number,
  scope↔claim, condition↔condition, before↔after) can break while every word
  survives, so the check certifies the wrong invariant.
- Rule change needed: skill-authoring §4 or 40-maintenance §5 — after compressing any
  rule text, re-read each compressed sentence asking WHO/WHAT the numbers and
  qualifiers now attach to (a bindings pass, not a words pass); word-diff remains
  necessary for extractions but is never sufficient for rewording. External lens
  stays mandatory for compression commits (this is the existing "self-review is no
  substitute" line — 3/3 rounds confirm it).
- Probe (2026-08-27, same day): pre-registered synthetic probe (6-clause fixture,
  4 planted bindings, real word-budget pressure after two design-review rounds —
  codex and grok both found the first fixture draft satisfiable by line-joining
  alone, 0 bindings at risk). Bare arm 3/4 clean, 1/4 real FAIL (dropped a tier's
  numbers while keeping the adjacent tier's — the exact subject↔number break from
  the production escapes). Ruled arm (rule text appended) 2/2 clean. n small,
  effect consistent with the 3 production escapes above — PROVISIONAL, not proof.
- Status: applied-on 2026-08-27 — folded into skill-authoring SKILL.md §5 step 2
  ("three cuts" bullet) with full text + evidence in
  `references/distilling-rules.md` §Compression and restructuring passes.


## 2026-08-27 — grok truncates review output (2× same session)
grok -p with a full review packet twice emitted only planning narration (563/585 bytes) and exited 0 with no report. Third attempt with a COMPACT prompt + "DO NOT narrate, output ONLY the final report" produced a complete NO FINDINGS report with checked-list. Pattern: long packet → grok dies after thinking; treat exit-0-with-no-report as REJECT and retry once with a compact report-only prompt before recording unavailable.
- Status: **SUPERSEDED same day — title and mechanism are both wrong.** Nothing was
  truncated; grok emitted a COMPLETE short narration and exited clean. Corrected
  entry directly below; orders live in `memory/workflow_grok_subordinate.md`
  §"Empty has TWO causes", evidence in
  `finding_grok_idle_vs_parser_2026-08-27.md`. Kept unedited per §3 append-only.


## 2026-08-27 — correction: grok does NOT truncate; it IDLES (supersedes the entry above)
- What happened: the entry above was written from the symptom (`rc=0`, tiny output,
  no report) and named the mechanism "truncation." Re-examining the same runs for
  the write-up showed the output was not cut off at all — grok emitted a *complete*
  short plan ("Next I'll locate the repo, read the changed files, and run the
  printed commands") and exited without ever executing it. 3/3 on one multi-step
  read-then-analyze review brief; copying every needed file INTO `--cwd` did NOT
  fix it, so file access was never the constraint.
- Root cause: the already-recorded tool-use short-circuit, extended from side
  effects to analysis — **read-then-analyze is multi-step work**, and grok
  short-circuits multi-step work by announcing it. Pure judgement under schema was
  always clean (8/8). Truncation was never the mechanism and has still never been
  probed on grok — `workflow_grok_subordinate.md` §"What is NOT measured" says so
  explicitly, and the entry above contradicted it for ~9 hours.
- Rule change needed: NONE new — the correct orders were already written to
  `memory/workflow_grok_subordinate.md` §"Empty has TWO causes" (3-step triage;
  read the bytes before blaming the parser; low `num_turns` demoted to suspicion)
  and the fix is **packet SHAPE, not retry**: inline everything, demand pure
  judgement, add `--json-schema`. That re-shape turned the identical failing review
  into a clean 5-finding run (1/1). The stale entry's "retry once with a compact
  prompt" is the wrong prescription — a compact prompt worked because it removed
  the file-reading steps, not because retrying helps.
- Unreconciled binding (do not silently pick one): the entry above cites 563/585
  bytes, the finding cites 305/328 B. The 2026-08-26 raw runs are not on disk in
  either tree, so neither number is verifiable now. Both describe the same failure
  CLASS; treat the byte counts as illustrative, not as data, and do not cite them.
- Meta-lesson, the one worth keeping: **naming a mechanism from a symptom is a
  claim, not an observation.** "Small output + rc=0" is compatible with truncation,
  a parser bug, and idling — three different fixes. R0 applies to my own
  diagnoses: read the bytes before naming the cause, or the wrong fix gets
  promoted into a rules file.
- Status: applied-on 2026-08-27 — Status line added to the superseded entry; no
  playbook edit needed (it already carried the correct mechanism and the explicit
  "truncation never probed" line that flagged the conflict).


## Moved here by the 2026-08-29 compression (LESSONS.md was 181 lines / 4 dated entries + 3 counter bullets)

LINE trigger only (>150); the >20-entry trigger was nowhere near met — 4 dated
entries. All four carried `Status: applied-on 2026-08-28`. Moved verbatim (sliced
by line range, not retyped).

**Every destination re-grepped against the LIVE file before the move**, per the
duty the 08-26 audit installed. Result — all 10 destination claims resolve, but
FOUR of the citations were stale in ways a Status line would have hidden:

- `skills/delegation-and-review/SKILL.md:444` → now **:449**, operative sentence
  live and unchanged: "While ANY subordinate holds write access to a tree, land
  nothing in it yourself: stage in scratch, merge after it exits."
- `skills/delegation-and-review/SKILL.md:423` → now **:429** (first stated as
  :428 — that is the sibling "Read-only" sentence; caught by a cross-model
  reviewer that re-opened the file instead of trusting the arithmetic), and the quoted
  paraphrase "classify by tools held, not by brief" is not the file's wording.
  Live text: "Classify an agent by the TOOLS IT HOLDS, never by what its brief
  asks for."
- `skills/delegation-and-review/SKILL.md:431` → now **:436**: "`isolation:
  'worktree'`, an enforced copy, or a frozen snapshot (§4). Mandatory, not
  preferred, on any repo that deploys from the branch under review."
- `harness/30-delegation-templates.md` — the quoted sentence "the target is
  STAGED AS FILES the reviewer reads, never pasted into the prompt" **no longer
  exists**. It was not deleted: it was REPLACED 2026-08-29 by a stronger
  per-executor rule that inverts the shape for codex/agy (grok+opencode STAGE,
  codex+agy INLINE, unknown executors STAGE and verify on a throwaway packet).
  The old quote is now WRONG as a general order. Anything citing it must be
  re-pointed at the live checklist item, not at this sentence.

The sentence that REPLACED it, and which anything citing the old quote must now
point at — note it INVERTS the old order for two executors, so a session obeying
the old sentence with codex or agy gets the wrong shape:
`harness/30-delegation-templates.md` — "**grok / opencode: STAGE the target as
files in `--cwd`** … **codex: INLINE the target** (`nl -ba`) so it makes ZERO tool
calls … **agy: INLINE** too … **Any executor not named here: STAGE, and verify the
shape on one throwaway packet first**."

Unchanged and verified live — operative sentence quoted, line as locator only
(the line numbers below WILL drift; the sentences are the citation):
- `memory/reference_subordinate_routing_map.md` R-D (:77) — "verify the boundary
  by attempting an escape, never by reading the flag name."
- `memory/reference_subordinate_routing_map.md` §2a (:123) — "A dispatch that
  returns nothing is a SHAPE bug until proven otherwise."
- `memory/workflow_grok_subordinate.md` §CONTAINMENT (:52) — "only a `--tools`
  allowlist actually stops it."
- `skills/operational-rigor/SKILL.md` (:278, was cited :274) — "Naming a mechanism
  from a symptom is a claim, not an observation — read the output bytes before
  naming the cause."
- `memory/workflow_codex_subordinate.md` (:238) — "The 79KB inline-packet ceiling
  is v0.144.4's and does NOT hold on v0.149.0."
- `harness/40-maintenance.md` (:22) — "Compression is not a rule-addition channel
  — if a compression finds an order with no home, add it and say so in the same
  turn, never silently."
- `~/.claude/projects/-Users-yauch-Documents-claude-code-technique/memory/feedback_hook_block_read_the_repo_line.md`
  — exists (PROJECT memory, not global `~/.claude/memory/`).

**"All 10 resolve" means the DESTINATION resolves, not that the prescription
still holds.** One of the ten (the 30-delegation quote) resolves to a file whose
rule now inverts the moved entry's own wording. Read that as: path live,
prescription superseded — never as blanket confirmation that the archived entry's
advice is still correct.

**Method note worth more than the moves.** My first grep pass reported THREE of
these destinations missing. All three were live; the patterns missed on casing and
paraphrase ("classify by tools held" vs "Classify an agent by the TOOLS IT HOLDS").
A failed grep is not evidence of absence — widen the pattern and search the tree
before recording rot. Had I trusted pass one, this compression would have
"discovered" three homeless orders and re-added them on top of live text.

**One unsupported claim dropped, recorded so the deletion is visible.** The
08-28 cross-model entry's Status line read "applied-on 2026-08-28, except the two
`noted` items below." No `noted` item existed below it — the entry that follows is
itself `applied-on`. Same shape as the 08-25 banner's phantom "open external
thread": a claim never supported by an entry, not one that aged out. Dropped as
unsupported, not resolved.

## 2026-08-28 — cross-model review of the 08-27 compression (codex + grok)
- What happened: user-ordered review of the compression + §3 rule by codex
  (inline packet, read-only) and grok (staged-files recipe, `--tools` contained,
  containment verified by post-run dir diff). codex: 4 findings. grok: 23, incl.
  3 CRITICAL my own verification pass missed — the closed-counter stub was a
  REWORD that dropped 2 of 4 destinations, the archived counter lost its section
  heading (a section-membership binding the "verbatim, no BINDINGS pass owed"
  claim didn't cover), and the new §3 rule collided with append-only.
  Reproducing codex's mildest finding also exposed that commit `cb6a9ae`
  (another session, same morning) had deleted the grok playbook's §"Empty has
  TWO causes" triage AND §"Tool-use short-circuit" hard safety rule without
  re-homing them — restored same day, reconciled with that commit's legitimate
  retraction. All fixes applied 2026-08-28; UNVERIFIABLE-tagged banner claims
  were re-grepped against live destinations before accepting.
- Root cause (of the misses): my compression verified MOVED TEXT (verbatim) and
  ORDER HOMES (grep) but never re-derived the REWRITTEN summaries against their
  originals — the exact "a fix is a change" / bindings-pass duty the moved
  entries themselves prescribe. Section membership is a binding; a stub is a
  reword.
- Rule change needed: one PENDING item needs user sign-off (below); everything
  else was fixable within existing autonomous-edit permissions.
- Status: applied-on 2026-08-28, except the two `noted` items below.

## 2026-08-28 — two governance gaps closed on user order
- **`40-maintenance.md` had no row in its own §1 permissions table** (found by me
  and independently by grok F15) — so the 08-27 compression's addition of a §3
  standing rule was self-authorized with no permission bit governing it.
- **A general diagnostic order was homed nowhere** (grok F9): the grok-SPECIFIC
  triage lives in the playbook, but the general rule survived only in the
  archive — which §4 forbids as a home.
- Root cause, both: a file that governs every other file's edit permissions never
  had its own row, and a compression is a tempting silent channel for adding one.
  The new row closes the channel explicitly.
- Rule change needed: both applied on user order 2026-08-28.
- Status: applied-on 2026-08-28
- Destination (§1 row): `harness/40-maintenance.md:22` — "| `40-maintenance.md`
  (this file) | YES wording; **ASK USER** for new standing orders / thresholds |
  … **Compression is not a rule-addition channel** …" (grepped 2026-08-28)
- Destination (diagnostic rule): `skills/operational-rigor/SKILL.md:274` —
  "**Naming a mechanism from a symptom is a claim, not an observation — read the
  output bytes before naming the cause.**" (grepped 2026-08-28). Ships
  `unprobed`.

## 2026-08-28 — git-filter-repo hard-resets the worktree: it ate another session's uncommitted work
- What happened: ran `git-filter-repo --replace-text --force` on `~/.claude` to
  purge client PII from history. It rewrote 53 commits correctly, but also
  hard-reset the working tree — silently destroying 172 uncommitted insertions
  another session had made at 15:27 to `ground-truth-gates/SKILL.md`,
  `skill-authoring/SKILL.md`, `skill-vetting/SKILL.md`. I had SEEN those files in
  `git status` minutes earlier, correctly identified them as another session's
  work, and deliberately left them uncommitted — which is exactly what made them
  destroyable. Recovered byte-exact (172 insertions / 9 deletions, diffstat
  matched) from the Obsidian vault copy, because the sync had run at ~15:5x,
  after their edits and before the rewrite. Pure luck of timing.
- Root cause: my `git bundle --all` backup captured REFS ONLY. Uncommitted
  worktree state is not in any ref, so the backup I took specifically to make the
  rewrite safe could not have restored the thing the rewrite actually destroyed.
  I verified the backup existed; I never asked what it contained.
- Rule change needed: NONE new — this is operational-rigor §4's "verify by
  execution" and §2's baseline-before-mutation applied to backups themselves.
  Worth carrying as a concrete instance: **a backup is not a backup until you
  name what it does NOT cover.** For history rewrites specifically: `git stash`
  or copy the dirty tree FIRST, or refuse to rewrite a dirty repo at all —
  filter-repo does not warn, and `--force` suppresses the check that would have.
- Second-order lesson: **leaving another session's uncommitted work in place is
  not the safe option it looks like.** "Don't touch it" protects provenance but
  offers zero protection against a destructive operation in the same repo. The
  safe move is stash-or-copy it, act, then restore it untouched.
- Status: applied-on 2026-08-28 (recovery verified; no rules-file edit owed)

## 2026-08-28 — the brief must describe the delivery: two tiers, one mechanism
- What happened: reviewing the sub-harness, I dispatched codex with the files INLINED
  in the prompt but left the brief's line "FILES UNDER REVIEW (in `./files/`)" intact.
  codex shell-globbed `/private/tmp/files`, found nothing, and returned no review —
  three times, ~50 min, before I read the bytes instead of theorising. Identical
  mechanism to grok's 08-28 attempt 3 (brief described staged files that were never
  written; grok narrated "the workspace is empty" and exited). **Second instance, second
  tier: a brief that contradicts its own delivery sends the subordinate hunting for
  material that isn't there, and the failure looks exactly like model incapacity.**
- Also measured, unrelated to the above and NOT a model failure: codex v0.149.0's inline
  packet cliff sits just above **~30KB** (16/29.6 OK · 32/33/45 preamble-only · 51-63
  silent, rc=0, `-o` never written), against the playbook's `79KB packet verified` from
  v0.144.4. Interleaved PONG controls passed throughout, which is what separated
  "packet too big" from "quota" and from "model broken".
- Root cause: I built the packet and reused the brief without re-reading the brief
  AGAINST the packet. The dispatch checklist asked whether the fields were filled, not
  whether they were TRUE of this delivery.
- Rule change needed: none new — this is the packet-SHAPE rule the same day's grok
  retraction already established, now shown to be tier-independent. Landed as a
  dispatch-time check rather than prose.
- Status: applied-on 2026-08-28
- Destination (asymmetry + the rule): `memory/reference_subordinate_routing_map.md` §2a —
  "Review packet SHAPE — codex and grok need OPPOSITE shapes … A dispatch that returns
  nothing is a SHAPE bug until proven otherwise" (grepped 2026-08-28)
- Destination (checklist): `harness/30-delegation-templates.md` — "REVIEW dispatches to a
  CLI: the target is STAGED AS FILES the reviewer reads, never pasted into the prompt."
  (grepped 2026-08-28)
- Destination (the size cliff): `memory/workflow_codex_subordinate.md` — "The 79KB
  inline-packet ceiling is v0.144.4's and does NOT hold on v0.149.0." (grepped 2026-08-28)


## Compression-pass narrative history (moved out of LESSONS.md 2026-08-29)

Moved here because the log had grown to 51 of LESSONS.md's 100 lines — a live
rules file turning into a maintenance history. LESSONS.md keeps a one-line-per-pass
ledger; the full narrative for each pass is below, verbatim as it stood.

Compressed 2026-07-12: six applied entries (2026-07-05 → 2026-07-12) moved
verbatim to `LESSONS-archive.md`.
Compressed 2026-08-25 at 243 lines / 19 entries: ALL 19 entries (2026-07-11 →
2026-08-25) moved verbatim to `LESSONS-archive.md`. Its summary line — "what
survives here is only what is NOT closed: one promoted rule-change proposal
awaiting approval, one open external thread, and the recurrence counters" — was
already stale before the 08-27 pass: the proposal was applied 08-26, and the
"open external thread" had no entry in the pre-compression file at all — a
claim never supported by an entry, not one that aged out. Dropped as
unsupported, not resolved; recorded here so the deletion is visible. No `noted` entry existed in
the 08-27 pre-image, so this compression removed none (§4 forbids that);
whether 07-12 or 08-25 compressed a `noted` entry away was NOT re-checked.
Compressed 2026-08-27 at 196 lines (wc -l) / 7 items (4 dated or applied
entries + 3 counter bullets) — LINE trigger only (>150); the >20-entry trigger
was nowhere near met. Moved verbatim, 5 objects: the applied "a fix is a change"
rule change, the applied "word-presence diffs" entry, both grok output-empty
entries (the "truncates" claim, superseded; its idle correction), and the
read-only-is-not-a-control counter now that its promotion is EXECUTED. Left in
place: the two still-climbing counters. **Every destination was grepped and its operative sentence
quoted in the archive banner before the move** — the check both earlier
compressions skipped. One order found homed nowhere (re-grep a claimed
destination in the same edit) was written into `40-maintenance.md` §3 first;
two rules files back-referencing moved entries were re-pointed in the same edit.
Compressed 2026-08-29 at 181 lines / 4 dated entries + 3 counter bullets — LINE
trigger only again. All 4 entries were `applied-on 2026-08-28`; moved verbatim by
line-range slice (not retyped) and the archive tail byte-compared against the
slice. All 10 destinations re-grepped LIVE first: all resolve, but 3 line numbers
had drifted, 1 quoted paraphrase never matched the file's wording, and 1 quoted
sentence had been REPLACED by a stronger rule that INVERTS it for two executors —
corrections quoted in the archive banner. My first grep pass called 3 of those
destinations missing and all 3 were live: **a failed grep is not evidence of
absence.** One unsupported Status clause ("except the two `noted` items below",
with no such items) dropped and recorded, same shape as the 08-25 phantom.
That failed-grep order was homed in the same edit rather than left in this log or
the archive (§4 forbids both as homes): `skills/delegation-and-review/references/
discovery-sweep.md` §"A failed grep is not evidence of absence" — "re-search on a
DISTINCTIVE content word from the rule rather than its cited phrasing … Cite
destinations by an operative SENTENCE you paste verbatim, not by line number or
paraphrase."

⚠️ **CORRECTED 2026-08-26.** The 07-12 and 08-25 blocks above used to claim every
moved entry "was verified applied by grepping its rule in the destination cache
before the move." That was false, and is corrected at the archive's banners —
read those, not a Status line. Both were re-audited 2026-08-26 at PRESCRIPTION
granularity: the 08-25 pass named destinations for only 9 of 19 and verified
those 9 (4 failures among the 10 it never named); the 07-12 pass named no
destinations at all (5 of 10 prescriptions not live as written). Evidence:
`claude code technique/experiments/lessons-applied-audit-2026-08-26/`.
**Moving an entry here closes nothing. Before writing "applied", grep the
destination and quote the operative sentence — a "compiled into §N" reference
decays as files are reorganized and nothing re-checks it.**

## Moved here by the 2026-09-06 compression (LESSONS.md was 247 lines / 5 dated entries)

All five entries below carried `Status: applied-on` (or `patched`) and are moved
verbatim, headings included — the two 2026-09-02 entries were written at `###`
under the CLOSED COUNTERS heading, which was a level slip at authoring time; the
level is preserved rather than corrected, since this file is verbatim history.
Nothing was dropped or reworded.

**Destination verification (the §3 duty, run 2026-09-06 before the move):** all
30 destination phrases across the five entries were re-grepped with whitespace
normalised (`re.sub(r'\s+',' ')`) so a hard-wrap cannot fake a zero. **29 of 30
resolve in the file the entry names.** The one failure, recorded rather than
quietly dropped:

- `41-file-registry.md` "is prospective (new/edited lines only" — **ZERO hits;
  the sentence was REPLACED, not moved.** That file's "Memory files" section now
  records the opposite state of the world: the legacy index-line debt was
  MIGRATED 2026-09-02 (228 of 279 entries across 17 project indexes trimmed to
  ≤150 chars, one line deliberately left over whose title+link prefix alone is
  156 chars), so a "prospective, new/edited lines only" carve-out no longer
  describes it. The ≤150 RULE itself is live and unaffected, at its other
  destination — `40-maintenance.md` §4, "a NEW or EDITED line is ≤150 characters
  (owner-set 2026-09-02, prospective)" — which the same sweep confirmed. So the
  2026-09-02 entry's prescription stands; only that one citation had rotted.
  This is the same class the 2026-08-29 pass caught once ("1 sentence had been
  REPLACED by a rule that inverts it") and is why the quote, not the line
  number, is the unit of verification.

Reverse-sweep for back-references (`rg 'LESSONS\.md|LESSONS-archive'` over
`skills/`, `harness/`, `memory/`, `CLAUDE.md`) run in the same edit: every hit is
either a generic "log it in LESSONS.md" instruction or a pointer to this archive
as a whole. No pointer names any of the five moved headings, so nothing needed
re-pointing. The one hit that mentions a specific past entry
(`skills/operational-rigor/SKILL.md:290`, the 08-27 grok-truncation correction)
refers to an entry archived by an earlier pass, not to anything moved here.

### 2026-09-02 — a skill's description loses to a hard route that names it nowhere
- Observed: a sampled (not exhaustive) transcript pass found genuine cross-family
  review dispatches where `cross-model-review` never loaded even though CLAUDE.md's
  own `codex = ... reviewer` bullet or the routing map's review rows fired the
  dispatch — including the literal ask "review with codex and grok" (2026-08-25
  03:34, classified OTHER by the sampling subagent's own classifier despite being
  a genuine acceptance-gate review, a discrepancy the classifier itself did not
  catch). A cross-model review of the original diagnosis (codex `gpt-5.6-luna`,
  grok `grok-4.6`, both FIX verdicts) found the first-drafted evidence write-up
  overclaimed precision the sampled data didn't support ("8 genuine reviews ran
  without it" — the sample contains only 2 occasions classified GENUINE-REVIEW,
  both misses) and the first-drafted CLAUDE.md patch left the actual competing
  hard route (the codex bullet) untouched, so the collision it was meant to fix
  would have persisted. Both defects were confirmed by reading the real files,
  not accepted on the reviewers' say-so.
- Candidate mechanism (not causally established — the sample shows misses
  co-occurring with available hard routes, not that the routes caused them): a
  skill `description` is a soft match the model must volunteer; a route already
  sitting in an always-loaded file (CLAUDE.md, the routing map) is a hard match
  already in context. A nearby paragraph pointing at the skill may not help if
  the reader's eyes go straight to the bullet/row — untested until the re-probe.
- Rule: when a skill gates a dispatch that CLAUDE.md or the routing map already
  hard-routes, the hard-route text ITSELF (the bullet, the table row/header) must
  point at the skill — not just a preceding sentence a scanning reader can skip.
- Status: patched 2026-09-02 (CLAUDE.md `codex` bullet now says "loads the
  skill first"; routing map §2, 10-orchestration.md §2, 30-delegation-templates.md
  T5 each got a header note). **Re-probe run same day, PRE arm: the candidate
  mechanism did NOT reproduce.** Fresh sonnet subagents holding the OLD CLAUDE.md
  snapshot fired `cross-model-review` on 6/6 firing phrasings (Skill was the FIRST
  tool call in 5/6 — before any disk file, so the new map/harness notes are not the
  cause either); collision controls 0/2; grader POS/NEG sound. So in fresh context
  the description alone routes these asks; the historical misses were the MAIN
  session model mid-task with a large context — fresh-context routing ≠ mid-session
  routing, and this harness cannot separate "large context dilutes the description"
  from "hard route wins". **POST arm run same day (session started after `455e60c`,
  precondition-checked snapshot): 5/6 fire (Skill first tool in 4/6), C1/C2 0/2,
  B1 none — vs PRE 6/6.** Net: the CLAUDE.md pointer has NO measurable effect on
  fresh-context routing in either direction, and does not over-trigger. The single
  POST miss was the "fix first, then review" shape (F2), the closest analogue to a
  mid-session second-phase review; suggestive at N=1, not evidence. **MID-SESSION
  arm run same day (sonnet subagents, ask sent into ~180k of doctrine context):
  PRE snapshot 3/5 fire (M3 "fix them all…" MISS; M2 "proceed…" HALTED to ask
  review-vs-fix, fired once answered), control silent.** Large context alone does
  not reproduce the misses. The pre-registered "re-run the misses" step landed on
  the POST snapshot by accident — `/compact` rebuilds the subagent CLAUDE.md from
  disk, so "start-time snapshot" was wrong; it is last-rebuild snapshot — and both
  fired 2/2 (N=1 each, directional only). The "fix, then review" phrasing flips 2/4
  across all four arms regardless of the pointer: that is the historical miss shape,
  and the pointer is not shown to fix it. The fix stays harmless and unmeasured,
  NOT verified; the PRE mid-session re-run is closed as not-completable without
  reverting the live CLAUDE.md. Evidence:
  `claude code technique/experiments/cross-model-review-trigger-reprobe-2026-09-02/`.

### 2026-09-02 — harness audit against 22 of one session's own incidents: the shared-tree rules lived only in caches
- What happened: cross-family review (grok-4.6 + codex luna, staged-files recipe;
  then codex sol acceptance ×2, cap reached; then a grok + sol ADVICE round on the
  sign-off set) of the seven rules files against 22 incidents mined from this
  session's transcript. Reproduced on disk before editing: `~/.claude/CLAUDE.md`,
  `10-`, `20-`, `30-` had ZERO hits for backup/stash/dirty-tree/bare-HEAD — the rules
  behind the three worst incidents (filter-repo wiping 172 foreign uncommitted lines,
  2026-08-28; a codex packet diffed from bare `HEAD` on the shared tree, 2026-08-29; a
  stale `/tmp` scratch `cp`'d over a shared MEMORY.md, 2026-09-02) existed only in
  skill caches. Also found: a false quote in `10-orchestration.md` §2 ("START HERE"),
  a self-declared-stale count in `40-maintenance.md` §4, the §1 self-row ordering both
  "ASK USER for new orders" and "add it and say so", and CLAUDE.md line 3 carrying
  history that line 1 bans.
- Root cause: rules were written cache-first and never written back to the harness
  source; §5 write-back runs source→cache only. Second: my first shared-tree checkbox
  inherited the shape of the worst incident (mutation-only) and missed the read-only
  packet case. Third: my own review round reordered the §2 agy/codex row — a
  routing-strategy change I did not list for sign-off; the advice round caught it.
  Fourth: I recommended "approve all / defer all"; both advisers rejected that in the
  same places (a third copy of load-skill-first; a threshold the corpus already fails
  170×; two zero-growth contradictions I had deferred). Rewordings were authored by
  me from the findings, not pasted.
- Rule change needed: applied — see Destination. All standing-order-class and
  CLAUDE.md edits landed on the user's explicit sign-off ("proceed with codex" =
  sol's set), per §1. The agy-row edit was reverted. The ~150 MEMORY.md threshold is
  owner-set and PROSPECTIVE (new/edited lines only); legacy over-length lines are a
  separate task.
- Status: applied-on 2026-09-02.
- Destination: `CLAUDE.md` line 61 "the one syntax, everywhere"; line 95 "load the
  `operational-rigor` skill (repo-baseline) first"; line 3 dates removed.
  `10-orchestration.md` §0 "Bash cwd is reset to the project dir after every call" /
  "records which rebuild each arm inherited"; §2 "A phase boundary does not reset
  this gate"; §4 "recomputed from the cited evidence before you publish it" /
  "output, not idleness". `20-judgment-rubrics.md` §3 "a diff or review packet is
  built from that backup, never bare `HEAD`"; §5 "`tail -N` is display only"; §6
  "narrowing a claim is not correcting it". `40-maintenance.md` §1 self-row "draft
  it, ASK USER in the same turn, and leave it unapplied until approved"; §1 step 3
  "landed AT THE LOCUS the diagnosis named"; §3 "NO exemptions, \"pre-existing\"
  included"; §4 "a NEW or EDITED line is ≤150 characters"; §5 "never changes
  precedence". `41-file-registry.md` Memory files "is prospective (new/edited lines only".
  `50-letter` Handoff 2026-09-02 "advisory history, not standing rules".
  `cross-model-review/SKILL.md` §2 "never bare `HEAD`"; §5 "separately NAMED artifacts".

## 2026-09-04 — An unverified failure SIGNATURE drove four experiments down the wrong road
- What happened: the 09-02 agy review-packet harness recorded `r.stderr` but graded on
  `r.stdout.strip()` alone, and its PREREG asserted the empty-return signature was
  "rc=0, empty stdout, EMPTY stderr". Nobody ran `print(r.stderr)`. That unverified
  clause survived four experiments (09-02 sweep, 09-03 reduced sweep, 3.8-solo, `${`
  minimal-pair), one VOIDed probe, a 12-feature structural hunt, and three memory
  findings — all hunting a "transport"/"size cliff" cause. Capturing the text on
  2026-09-04 showed every failing call carried 300 bytes: `jetski: no output produced —
  a tool required the "command" permission that headless mode cannot prompt for, so it
  was auto-denied.` A no-tool preamble took the worst packet from 0/4 to 4/4 live
  (Fisher p=0.0286). Cost: ~6 hours of runs.
- Root cause: the harness DISCARDED the diagnostic channel it had already captured, and
  a prose PREREG line ("empty stderr") was then treated as a measured fact by every
  later run that imported the harness byte-for-byte — importing the code also imported
  its unexamined claim.
- Rule change needed: NONE — `20-judgment-rubrics.md` §2 and R0 already cover it
  ("reproduce before trusting", expected-before-actual). This is an instance, not a gap.
  The operational specifics are homed in the agy playbook instead.
- Status: applied-on 2026-09-04.
- Destination: `~/.claude/memory/workflow_agy_subordinate.md` READ FIRST block —
  "Diagnosis rule: `capture_output=True` then READ `r.stderr` — never test only"
  / "`r.stdout.strip()`.** A \"silent\" agy failure is almost never silent."

## 2026-09-04 — Two driver bugs produced plausible scoreboards; the soundness gate only covered the grader
- What happened: codex hard-axis drift re-probe (`experiments/codex-hardaxis-2026-09-04/`).
  (a) `run_fix(){ local task="$1" t="$2" d="$BASE/$ROOT/${task}__t$t"; ...}` — bash
  expands every `local` argument in the caller's scope before assigning, so `${task}` was
  unbound under `set -u`; H2/H3 never launched, H1 ran only because `$t` happened to exist
  as the loop's global with the right value, and every cell that existed scored perfect.
  (b) three `codex exec ... &` jobs shared the shell's stdin; codex blocked on "Reading
  additional input from stdin...", hit the 300s timeout with 0 files changed, and the
  grader scored the unmodified seed as a MODEL failure. Both graders had passed the
  dual-reference gate (good-ref/bad-ref) minutes earlier. Also (c): the July harness this
  rebuilt lived in `scratchpad/` (=/tmp) and had been wiped — same class as the 2026-09-02
  stale-`/tmp` incident above; the finding's "harness pointer" was a tmp path.
- Root cause: the soundness gate certified the GRADER (does it pass good and fail bad) and
  nothing certified the DRIVER (did each cell actually run the model), so driver faults
  surfaced as missing cells or as model failures — both shapes a scoreboard reader accepts.
- Rule change needed: applied — experiment-protocol Rule 2 (project skill) gains a driver
  gate: pre-registered rows `cell count == N` / `no latency near timeout` / `output != seed`
  checked before any score is read; one `local` per line; `</dev/null` on every backgrounded
  subordinate call. Rule 6 already says copy the harness into the repo — (c) is an instance,
  not a gap; the harness is now git-tracked (`b5b10d7`).
- Status: applied-on 2026-09-04.
- Destination: `claude code technique/.claude/skills/experiment-protocol/SKILL.md` Rule 2
  "**The DRIVER gets the same gate as the grader.**" / "check them BEFORE reading any
  score" (grepped 2026-09-04: line 23; wrapped phrase count 1).

## 2026-09-06 — Round-2 cross-model review: two dispatch faults were mine, both already documented
- What happened: dispatching codex + grok for round-2 review of the compaction-hook
  harness's StdoutTap/stdin-pump fix (`hooks/harness/`). First codex call hung: `codex
  exec` with a non-TTY stdin printed "Reading additional input from stdin..." and never
  ran. Second call errored rc=1: "Not inside a trusted directory and
  --skip-git-repo-check was not specified" (the review packet dir under scratchpad/
  is not a git repo). Grok returned 382 bytes of narration about its reading plan
  instead of the review, no verdict.
- Root cause: the codex invocation omitted `</dev/null` and `--skip-git-repo-check`;
  the grok prompt omitted an explicit "produce the review text itself, do not narrate"
  instruction. All three are pre-existing, named gotchas in the routing playbooks —
  I dispatched from memory instead of re-reading the playbook before the call.
- Rule change needed: NONE — `workflow_codex_subordinate.md` line 40 already has
  `</dev/null` in its canonical background-dispatch command and line 44 already says
  "Must be in a trusted dir OR pass `--skip-git-repo-check`"; `workflow_grok_subordinate.md`
  line 262 already documents "narrates its plan and exits" as the failure mode. This is
  an instance of not applying an existing rule, not a gap.
- Status: applied-on 2026-09-06 (no edit needed; re-verified the destinations carry
  the operative text).
- Destination: `~/.claude/memory/workflow_codex_subordinate.md:40` "`codex exec -m
  gpt-5.6-luna --skip-git-repo-check -s workspace-write "$(cat /tmp/codex-spec.txt)"
  </dev/null > /tmp/codex-out.txt 2>&1 &`" and `:44` "Must be in a trusted dir OR pass
  `--skip-git-repo-check`."; `~/.claude/memory/workflow_grok_subordinate.md:262`
  "narrates its plan and exits".
