---
name: compact-context
description: >
  Proactive context compaction for Claude Code sessions. Use this skill the moment the user mentions
  "compact context", "context is getting long", "let's compact", "summarize progress", "we're hitting
  context limits", "context window is filling up", "compact before continuing", or any phrasing that
  suggests they want to preserve session state before the conversation grows too large. Also trigger
  proactively when the conversation is clearly very long and the user is mid-task — don't wait to be
  asked. Also trigger immediately when a system reminder says context is ~50% full. The skill produces
  a structured CONTEXT HANDOFF block that captures everything needed to continue work seamlessly in a
  fresh context or after /compact runs.
---

# compact-context

## Why this matters

Claude Code sessions accumulate context fast. By the time auto-compaction kicks in, important nuance
gets lost — the architectural decision you made in message 3, the constraint the user mentioned
casually, the specific error you already ruled out. Proactive compaction at ~50% context means you
still have full visibility into everything, and can write a complete, accurate summary that acts as
a lossless hand-off to the next context window.

The output of this skill is a **CONTEXT HANDOFF** block — a single markdown section the user can
reference (or that gets preserved through /compact) to let you pick up exactly where you left off.

## When to run

- User explicitly asks for compaction or says context is getting long
- A system reminder says context is ~50% full (act on this immediately)
- The conversation is visibly very long (30+ back-and-forth exchanges) and you're still mid-task
- Before a large code generation step that will consume a lot of context
- User says "let's start fresh but keep our progress"

## How to produce the CONTEXT HANDOFF

Scan the full conversation history and extract the following, in order. Be concrete — file paths,
line numbers, function names, error messages. Vague summaries are useless; specific ones are gold.

### 1. Mission (1–2 sentences)
What is the overarching goal of this session? What does success look like?

### 2. Completed Work
A bulleted list of what has been DONE and CONFIRMED working. Include:
- File paths that were created or modified (with what changed)
- Features/bugs that are resolved
- Commands that were run and their outcomes

### 3. Current State
What is IN PROGRESS right now — the exact task that was being worked on when compaction was triggered.
Include the specific step within that task if it's multi-step.

### 4. Key Decisions & Constraints
Things that were decided or ruled out that the next context MUST know:
- Architectural choices and why (e.g., "chose X over Y because...")
- Things the user said NOT to do
- Errors already investigated and ruled out
- Environment quirks discovered (e.g., "this project uses pnpm, not npm")

### 5. Critical Artifacts
The exact identifiers needed to continue:
- Key file paths
- Key function/class/variable names
- Key API endpoints, env vars, or config values
- Any error messages still unresolved

### 6. Next Steps
An ordered list of what needs to happen next, starting with the immediate next action.

---

## Output format

Produce the handoff as a fenced markdown block labeled `CONTEXT HANDOFF`. After the block, offer
to run `/compact` if the user wants to actually compact the context window now.

````
## CONTEXT HANDOFF

**Mission:** [1–2 sentence goal]

**Completed:**
- [file/feature/fix — with specifics]
- ...

**In Progress:** [exact current task and step]

**Decisions & Constraints:**
- [decision or rule — with reasoning]
- ...

**Critical Artifacts:**
- Files: `path/to/file.ts`, `path/to/other.py`
- Functions: `functionName()` in `file.ts:42`
- Errors unresolved: [error message or "none"]
- Env: [stack, key deps, quirks]

**Next Steps:**
1. [immediate next action]
2. [step after that]
3. ...
````

After the block, say:

> "Run `/compact` now to compress the conversation — paste the CONTEXT HANDOFF above at the start of
> your next message so I can pick up seamlessly. Or keep going and I'll remind you again when we get
> closer to the limit."

---

## Tone

Be precise, not verbose. The handoff block should be dense with specifics, not padded with prose.
If you're not sure whether something is important enough to include, include it — omission is the
real risk here. A 40-line handoff is fine; a 10-line vague one is not.
