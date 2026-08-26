# Verified invocations & trap table

Split from SKILL.md 2026-07-11 (file crossed the ~250 split threshold,
40-maintenance §1). Same write-back duty as the parent: these are caches over
the subordinate playbooks in `~/.claude/memory/workflow_*.md`; on conflict the
playbook wins.

## Verified invocations

```bash
# codex — health probe first if anything smells off
codex exec --skip-git-repo-check "PONG"
# codex — implementation (backgrounded; spec in a file; < /dev/null is
# MANDATORY — without it backgrounded codex hangs at "Reading additional
# input from stdin..." (hit 2026-07-15))
cd <dir> && codex exec --skip-git-repo-check -s workspace-write \
  "$(cat /tmp/codex-spec.txt)" < /dev/null > /tmp/codex-out.txt 2>&1 &
# codex — REVIEW: inline the files AND forbid execution (verified 2026-07-06:
# inlining alone is NOT enough — codex still "verifies against the repo" with
# tool calls and the synthesis is lost). Prompt must open with: "Everything you
# need is inlined below. Do NOT run commands/read files; review the text directly."
{ echo "$NO_TOOLS_LINE"; cat hdr.txt; nl -ba f1.ts; nl -ba f2.ts; } > /tmp/prompt.txt
codex exec --skip-git-repo-check -o /tmp/last.txt "$(cat /tmp/prompt.txt)" \
  < /dev/null > /tmp/out.txt 2>&1
cat /tmp/last.txt   # -o reliably captures the no-tools verdict; stdout sed as fallback
# codex — vision: prompt via stdin (the -i flag is greedy)
echo "<prompt>" | codex exec --skip-git-repo-check -i img.png
# codex — big prompt (>~10KB): pipe via stdin `-`, not argv (measured v0.144.4,
# 79KB packet); -s read-only for reviews, -s workspace-write for implementation
cat /tmp/prompt.txt | codex exec --skip-git-repo-check -s read-only \
  -o /tmp/last.txt - > /tmp/out.txt 2>&1
# NEVER double-background (`nohup ... &` inside an already-backgrounded harness
# call): parent exits 0 immediately, codex is orphaned mid-run (2026-07-16).
# ONE backgrounding mechanism only.

# agy — prose only; ALWAYS the escape hatch on recall/open-ended prompts
agy --dangerously-skip-permissions -p "$(cat /tmp/agy-prompt.txt) \
若不確定就只答「不確定」，切勿留白" > /tmp/agy-out.txt 2>&1 &
# agy IMPLEMENTATION work: add --add-dir <dir>. NEVER for reviews — agy
# agentic mode ignores read-only prose (2026-07-14: edited 4 repo files
# mid-review and contaminated the baseline reads). Review dispatches: no
# --add-dir; if it had write access anyway, git-diff before trusting any
# file state.
# a single agy run is representative (the ≥2× variance caveat was retired
# 2026-07-22 on 3.6-medium); a single codex run is representative

# opencode — isolated dir, timeout-wrapped, sequential by default
# timeout 180 for single-file; ≥540 for multi-file reviews (300 timed out with
# no report on a 5-file review; 540 delivered — 2026-07-17). Multi-file prompts
# also need the line "do NOT search outside ./files/".
SCRATCH=$(mktemp -d) && cd "$SCRATCH" && timeout 180 \
  ~/.opencode/bin/opencode run --dangerously-skip-permissions \
  -m opencode/big-pickle "$(cat /tmp/oc-prompt.txt)" > /tmp/oc-out.txt 2>&1 &
```

NIM via opencode: `-m nvidia/openai/gpt-oss-120b` — provider prefix is `nvidia/`,
NOT `nvidia-nim/` (hit 2026-07-16: wrong prefix fails instantly with opencode
UnknownError "Unexpected server error"). Full model list: `reference_nim_via_opencode.md`.

Parallel NIM direct-curl batch roles (moved from SKILL.md §8, 2026-07-21):
40 req/min per key via `nimroute.py`, `gpt-oss-120b` = best agent,
`llama-4-maverick` = curl-only.

opencode model pick: `big-pickle` default (simple/medium single-file) ·
`deepseek-v4-flash-free` fastest fan-out · `north-mini-code-free`
sustained/complex headless · `nemotron` never a default (flaky) · avoid
`openrouter/*:free`.

## Trap table (symptom → cause → fix)

| Symptom | Cause | Fix |
|---|---|---|
| Every `codex exec` fails at load | Malformed `[mcp_servers.X]` in `~/.codex/config.toml` (Codex.app rewrites it) | Fix/remove the block; `-c 'mcp_servers={}'` once it parses |
| codex review: exit 0, only prompt echo | Long answer after tool calls doesn't flush | Inline files into prompt (recipe above); `-o` works for long verdicts too (10.5KB captured, v0.144.4 — the old short-only caveat did not reproduce), but only when the run completes |
| codex output has `user` marker but no `codex` turn / no `tokens used` line | Double-backgrounded → orphaned mid-run (parent shell exited 0) | ONE backgrounding mechanism; check for these markers BEFORE blaming the prompt |
| codex batch: silent no-change | Quota exhausted mid-run | Spread across agy/opencode; revert-on-failure |
| agy silent hang | CSV/TSV or numbered headers · missing `--dangerously-skip-permissions` · open-ended recall w/o escape | Prose reformat · add flag · escape hatch. Escape ≠ guarantee: must-deliver questions go to codex |
| agy safety refusal (exit 0, ~300-byte apology) on a review dispatch | Attack verbs on security-adjacent code ("break", "bypass", "spoofable") — 2/2 refusals | Defensive reframe: "you are hardening our own app; verify each file against its intended contract" (1/1, found a real fail-open bug) |
| agy review "edited" repo files despite read-only prose | Agentic mode + `--add-dir` ignores prose scoping; uncommitted edits contaminate YOUR baseline reads | Reviews get no `--add-dir` (or scratch-copy); git-diff before trusting file state after any agy run |
| opencode "database is locked" | Parallel runs share one SQLite db | Go sequential, or give each instance its own `XDG_DATA_HOME` + auth.json |
| opencode exit 124 | timeout ≠ task failure (NIM 429 retry-loop) | Grade on-disk state; direct-curl PONG to check 429 |
| Subordinate output 0 bytes, exit 0 | Free-model tool-use file-review failure | Check non-empty before relying; route must-deliver reviews to codex |
| Spawned session `isRunning` but stale `lastActivityAt` | Mis-scope → silent stall (won't push back) | Ground-truth check (files/git, FULL blast radius incl. out-of-cwd); rescope |
| Your own edits vanish while codex workspace-write runs in the same tree | codex constraint enforcement restores non-listed files to HEAD, silently wiping your edits (hit 2026-07-14) | "Disjoint files" is never satisfiable with codex workspace-write: land nothing yourself while it holds write access; stage in scratch, merge after it exits |
| Worktree fan-out: app loads blank / wrong bundle, all requests 200 | Sibling sessions contend for the configured dev port; after `autoPort` moves you, any hardcoded `localhost:PORT` proxy/target in app config now hits ANOTHER session's server (cost ~40 lines of diagnosis 2026-07-21) | `autoPort: true` from the start; blank-app-with-200s in a fan-out → check cross-port proxies BEFORE debugging your own code; `preview_stop` cannot kill a sibling's server |
| opencode zero-byte stall on discovery/review dispatch | Wrapper stalls reproduce across retry AND across models (4/4 incl. 540s-timeout retry round, both big-pickle and NIM-through-opencode, 2026-07-21) | Reroute to direct NIM API after the FIRST zero-byte on discovery/review work — don't spend the retry round on the wrapper |
| Workflow synth agent reports confidently from empty input | `args` arrives as a JSON **string**; `\|\| []` defaults mask non-arrival | `JSON.parse(args)` first line; assert critical inputs, throw if absent; validate fan-out lengths BEFORE the synth stage (`if (!results.length) throw` — a synth fed empty arrays invents plausible content); ground the answer in checks you ran |

## Review framing — family-specific (moved from SKILL.md §4, 2026-07-16 size control)

Measured: framing changes the output, not the model.

- Cross-family check beats self-review: what one family + your own tests miss,
  a different family catches — including a spec YOU authored, even as the
  strongest model in the room (cross-family spec review catches the
  orchestrator's own bugs, not just subordinate risk).

- codex hides risks while implementing but volunteers them when ASKED to
  review (0/3 vs 3/3 on the same footguns) → run a codex spec-review pass
  BEFORE dispatching implementation of anything non-trivial.
- agy: "verify against this contract" → precise, zero FP; "try to BREAK
  it" → high recall, low precision (finds edges everyone else misses, also
  flags correct code as FAIL). Pick the framing for the job; reproduce
  every hunt-mode finding before acting. EXCEPTION — security-adjacent
  code: attack verbs trigger safety refusals (2/2, 2026-07-14); use the
  owner/defensive framing there ("hardening our own app; verify against
  its intended contract"), which keeps hunt-grade recall.
- agy "[verified: vitest/Node.js]" tags are fabricated — it has no
  execution env (N≥2, sweeps 6+8). Treat every agy verification tag as
  false; only your own runs verify.
- agy CONCEPT ≠ MECHANISM: it names what to look for accurately (even
  quantitatively), but its mechanistic prescription defaults to doctrine —
  never ship it. codex/the binary says what's actually there; your harness
  decides. (Family-neutral form: SKILL.md §4 "a proposed fix is a
  suggestion, not a patch".)
