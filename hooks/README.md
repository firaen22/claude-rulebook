# hooks/ — the executable side of the rulebook

Everything else in this repo is prose a model reads. These files RUN, in your shell, on
every matching tool call. Read each one before registering it (operational-rigor §2,
`skills/operational-rigor/references/install-gate.md`); run its test script; then copy
the `hooks` block from `../settings.example.json` into your `~/.claude/settings.json`
with the paths made absolute.

| File | Event | What it does | Test |
|---|---|---|---|
| `gate-before-commit.sh` | PreToolUse (Bash) | Blocks `git commit` while the TARGET repo's `checks/run-all.sh` exits non-zero. Resolves the target from `git -C <dir>` / a preceding `cd`, not from the session cwd. Exit 2 = blocked, reason on stderr. Needs `jq` (optional) and `python3` (`parse-commit-command.py` tokenizes the command). | `bash hooks/test-gate-before-commit.sh` |
| `gate-credential-destruction.py` | PreToolUse (Bash) | Blocks `rm`/`mv`/`shred`/etc. aimed at credential-pattern files (`.env`, `*.pem`, `id_rsa`, `credentials*`, …) unless the user's own message authorised it. Built after a weak-tier eval where an embedded directive in a vendor file got a credentials backup deleted. | `bash hooks/test-gate-credential-destruction.sh` |
| `parse-commit-command.py` | (helper) | shlex-based tokenizer used by `gate-before-commit.sh`; strips heredoc bodies so a commit message containing "git commit" is not a commit. | covered by the gate's test |
| `observe-compaction-events.sh` | PreCompact, SessionStart (startup/resume/clear/compact/fork) | Records one JSON file per hook event under `$LOG_DIR/observed/` (payload, EOF-observed, truncation) so compaction behaviour can be measured instead of guessed. Measurement only — it never blocks. | contract harness lives in the owner's lab repo, not here |

The reliability harness for `observe-compaction-events.sh` — v22–v28 candidates, the
contract/gap/grpsig2/pidhang graders, 18 mutants, and the cross-model review packets —
lives in [`harness/`](harness/README.md) (merged from the former `compaction-hook-harness`
repo via git subtree, history preserved).
| `../compact-context-monitor.sh` | Stop | Estimates context use from transcript bytes appended since the last compact boundary; at ~50% exits 2 with `asyncRewake` so the model gets a system reminder to hand off / compact. Debounced: warns once per crossing. | none (read the 64 lines) |

Machine-specific files are deliberately NOT in this repo: the real `settings.json`
(absolute paths, permissions, MCP servers), `hooks/hooks.log` (runtime log), and
`*.bak*` snapshots. The rulebook files that cite these hooks: `harness/40-maintenance.md`,
`harness/41-file-registry.md`, `skills/skill-vetting/SKILL.md`.
