---
name: workflow-fable-subordinate
description: "How to use Fable (slug `fable`, routed to `claude-fable-5-1` as of 2026-09-09) as a REVIEW subordinate via the Agent tool — invocation, the identity-confirmation limit (no provider route-report), family accounting (Fable = Claude author-family, NOT a second non-author lens), verified review behaviour. Fable's measured edge is beyond-the-brief defect discovery."
metadata:
  node_type: memory
  type: reference
---

Fable (requested model slug `fable`, which the harness routes to `claude-fable-5-1`;
the served identity is **confirmable post-hoc** from the subagent transcript — see the
identity-confirmation section below) as a REVIEW / second-opinion subordinate. Unlike the CLI subs
(codex/grok/agy/opencode), Fable is not a separate binary — it is reached as an
in-harness **subagent** through the Agent tool's `model` override
(`subagent_type: "general-purpose"`, `model: "fable"`). It runs live in the repo and
reads ground truth itself, so it is a live-execution reviewer (packet-optional): give
it the spec + WHERE the work is. ⚠️ `general-purpose` grants the **full toolset,
including Edit/Write/Bash** — a reviewer that can mutate the artifact it judges is an
author≠judge hole. The review brief MUST forbid **all mutation — Edit, Write, AND
Bash/shell writes** (a "no edit/write" alone leaves `rm`, output redirects, and
`git checkout` open) and scope the run to read + reproduce (reproduce may RUN
commands, but none that change the artifact) (`Explore` is read-only but is documented as unsuitable for review —
it reads excerpts and misses content past its window — so it is not the substitute).

## Invocation
Agent tool: `{ subagent_type: "general-purpose", model: "fable", prompt: <review brief> }`.
The brief carries the same review contract as any T5 dispatch — GOAL, the specific
claim to REFUTE, the cost asymmetry (which failure direction is expensive), a rubric
demanding input→expected written BEFORE actual, `[verified: ran/read X]` tags, an
explicit **forbid-all-mutation** instruction covering Edit, Write, and Bash/shell
writes (general-purpose can mutate — see above),
and a required last line that is exactly `PROCEED` or `FIX <items>`. Write literal
absolute paths into the prompt — the subagent inherits neither your scratchpad nor cwd.

## Identity confirmation — confirmable post-hoc from the subagent transcript (2026-09-09)
A CLI sub echoes an **inline** route-report (cross-model-review §5). The Agent-tool path
has no inline echo, but the harness DOES persist an independent served-model record you
read back after the run — so identity is confirmable, just not in-band:
- **Requested slug** — `…/projects/<project>/<session>/subagents/agent-<id>.meta.json`,
  field `model` (e.g. `"fable"`), keyed to the Agent call by `toolUseId`.
- **Served model** — the sibling `agent-<id>.jsonl`: every `type:"assistant"` record
  carries `message.model` (e.g. `claude-fable-5-1`) from the API response envelope (it
  also carries the `msg_…` id and `usage`; harness-injected records are marked
  `"model":"<synthetic>"`). This is response-derived, **NOT an echo of the requested
  slug**: measured this session, one requested `opus` served BOTH `claude-opus-4-8` and
  `claude-opus-5`, and no-override subagents served five different models — the field
  tracks what actually served. A silent fallback to the orchestrator would therefore
  show its own model here (e.g. `claude-opus-*`), not the requested flagship.

Confirm by matching the two files on `toolUseId` and record BOTH in the review log.
Caveats: this is **post-hoc** (read the transcript; no in-band proof mid-run) and depends
on the transcript being present — if the jsonl is unavailable or its `message.model`
disagrees with the requested flagship, record the unconfirmed-identity gap and treat the
review as requested-identity only. Identity being confirmable does NOT by itself let a
Fable lens carry a "confirmed cross-family pair" claim — that is blocked separately by
family accounting (next section), Fable being Claude-family.

## Family accounting — Fable is NOT a second non-author family
Fable is Anthropic/Claude-family. When the orchestrator is also a Claude model (the
usual case), a Fable lens shares the AUTHOR family (cross-model-review §1). It is a
legitimate extra fresh-context lens, but it does NOT satisfy the "≥1 reviewer outside
the author's family" invariant on its own — pair it with a genuinely non-author
family (codex = gpt, grok = xAI) when the gate needs cross-family coverage.

## Verified review behaviour (N=1, provisional)
- 2026-09-09, P3′ Round 2 archive re-review: the Fable-requested subagent ran a
  repo-wide sweep WIDER than the author's own (checked `settings*.json`, `hooks/*`, all
  memory dirs — not just the harness-local tree), reproduced the governance gates green
  at HEAD, and returned a
  disciplined input→expected rubric that handled the documented false-positive
  correctly. Verdict PROCEED, zero findings — corroborated independently by codex
  `gpt-6-astra`. Clean and on-contract.
- Fable's documented edge is **beyond-the-brief defect discovery** (the Fable full-sweep
  finding; the adopt-Fable-habits feedback). Use it where a miss is costly and the brief
  may be incomplete, not where you only need a spec'd checklist run — a cheaper tier
  suffices there.

Would change this entry: a harness change that stops persisting `message.model` in the
subagent transcript (→ downgrade the served-identity channel back to requested-only); a
measured review miss; a drift re-probe that changes the behaviour above.
