# claude-rulebook

The versioned part of one person's `~/.claude` — the standing orders a Claude Code
session reads before it does anything, plus the hooks that enforce some of them and
the evidence trail behind both.

This is a working corpus, not a distribution. It is published so the rules can be
read, argued with, and borrowed from; it is not packaged for drop-in use, and some
of it is specific to this machine and this operator. See **Using any of this**.

## Start here

[`CLAUDE.md`](CLAUDE.md) is the entry point and the only file loaded every session.
It is capped at 100 lines and holds current-state orders only — no history, no
evidence. Everything else is reached from its routing table, on demand.

The core rules it carries, in one line each:

| | |
|---|---|
| **R0** | Reproduce before trusting — including your own "it works". |
| **R1** | Verification is not self-verification; acceptance goes to fresh context. |
| **R2** | Think, then simplify. State assumptions; ask when genuinely ambiguous. |
| **R3** | Surgical changes — touch only what the task requires. |
| **R4** | Delegate reading, keep deciding. |
| **R5** | Fail loud, checkpoint often. |
| **R6** | Code answers what code can answer; models are for judgment. |
| **R7** | Surface conflicts and stale premises. |
| **R8** | On conflict, the harness wins over a skill. |

## Layout

| Path | What it is |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Always-loaded orders + routing table. 100-line hard ceiling. |
| [`harness/`](harness/) | **Source of truth for doctrine.** Numbered by situation: `10-orchestration`, `20-judgment-rubrics`, `30-delegation-templates`, `40-maintenance` (permissions + growth limits), `50-letter-to-future-sessions`. `00-DIAGNOSIS` is frozen history. |
| [`skills/`](skills/) | Skill caches — doctrine compiled into loadable form. On any conflict with `harness/`, the harness wins (R8). |
| [`memory/`](memory/) | Global reference and workflow files: subordinate playbooks (codex, agy, grok, opencode, spawned sessions), routing map, tool gotchas. |
| [`hooks/`](hooks/README.md) | The executable side — commit gates, a credential-destruction gate, compaction observability. Has its own README; read it before registering anything. |
| [`lib/`](lib/) | Shared helpers. Only `grok_preflight.py` is versioned. |
| [`settings.example.json`](settings.example.json) | Hook registration template. The real `settings.json` is machine-specific and deliberately untracked. |

`.gitignore` is a **whitelist** — `*` then explicit negations. Sessions, caches,
tokens, runtime logs and `*.bak*` snapshots stay out by construction rather than by
remembering to exclude them.

## The evidence layer

Two files carry history rather than orders, and are exempt from the line ceilings
the rules files obey:

- [`harness/LESSONS.md`](harness/LESSONS.md) — write-backs after mistakes. Append-only
  between compressions; compressed at 150 lines / 20 entries.
- [`harness/LESSONS-archive.md`](harness/LESSONS-archive.md) — every compressed entry,
  verbatim, under a dated banner.

They exist because a rule with no incident behind it is hard to weigh later. Two
conventions are load-bearing:

**"Applied" is a claim that gets checked.** Marking a lesson applied requires
grepping the destination file and pasting the operative sentence — not a "compiled
into §N" reference, which decays silently as files are reorganised. Two audits found
earlier passes had overclaimed exactly this way; the corrections are in the archive's
banners, and the compression ledger in `LESSONS.md` records what each pass verified
and what it got wrong.

**Corrections stay visible.** Retracted findings are marked retracted in place rather
than deleted, so a later reader can see which way the evidence moved. Several entries
supersede an earlier entry by name.

## What is deliberately not here

- The real `settings.json` — absolute paths, permissions, MCP servers.
- Session transcripts, caches, credentials, runtime logs.
- Per-project memory (`projects/*/memory/`) — private working notes.
- Model lineups and API specifics beyond what a playbook needs, because they rot fast.

## Using any of this

Read before borrowing. Specifically:

- **Paths are absolute and personal.** Hooks and rules reference `~/.claude/...` and
  this operator's repos; nothing auto-detects your layout.
- **Hooks execute in your shell on every matching tool call.** Read each one and run
  its test script before registering it — `hooks/README.md` says how, and the
  install-gate discipline in `skills/operational-rigor` is there for a reason.
- **Some skills are domain-specific** to work unrelated to Claude Code technique
  (`aia-eclaims`, `bazi-ziwei-lesson-notes`, `native-engine-parity-decoding`). The
  general ones are `operational-rigor`, `delegation-and-review`, `cross-model-review`,
  `ground-truth-gates`, `skill-authoring`, `skill-vetting`.
- **Numbers go stale.** Where a file cites a measurement, it names the date and the N.
  Re-measure before relying on one; model names and tool behaviour especially.

The parts most likely to transfer are the general skills and the harness rubrics —
they are about how to verify work and delegate it, which is not machine-specific.

## License

MIT — see [`LICENSE`](LICENSE). Borrow freely; the caveats above are about
whether a given piece will *work* for you, not about permission.

## Provenance

Grown incrementally from real sessions since 2026-07, mostly after something went
wrong. The harness was a separate repo until 2026-09-05, when it was subtree-merged
here with history preserved; the compaction-hook harness under `hooks/harness/` was
merged the same way. Both keep their own dated review trails.
