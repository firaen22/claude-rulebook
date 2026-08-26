---
name: phase-plan-architect
description: >
  Use this skill the moment a user expresses intent to add, build, implement, or refactor
  something in their codebase — even if they haven't asked for a plan. This is the entry
  point for any implementation task: UI features, backend systems, API integrations,
  architectural changes, new subsystems. Invoke it before writing code, not after. The skill
  architects a phased plan and gets user sign-off first. Skip only for: debugging errors,
  answering questions, explaining code, single atomic operations (rename/comment/regex),
  git commands, and explicitly deferred future ideas.
---

# Phase Plan Architect

Your job is to prevent premature coding. Before writing a single line of implementation code,
you will understand the goal deeply, surface hidden complexity, and produce a phase plan the
user can sign off on.

## When you've been invoked

The user wants to build or implement something. Do NOT start coding yet. Follow the steps below.

---

## Step 1: Interview the User

Decide on interview style based on context:
- **Batch** (ask all at once): user clearly knows what they want, gave a detailed request
- **Sequential** (one at a time): user is vague, exploratory, or new to the problem space

Cover these areas — skip what's already clear from context:

| Area | Question to answer |
|---|---|
| End state | What does "done" look like, concretely? |
| Success criteria | How will you know it works? (quantify where possible) |
| Stack / constraints | Any fixed tech choices, patterns, or conventions? |
| Edge cases | What are the hardest inputs or likely failure modes? |
| External dependencies | APIs, databases, auth, third-party services involved? |
| Scope boundary | What is explicitly NOT in scope? |

Keep it focused — 3 to 5 sharp questions beat 10 vague ones. If the user gave enough context to answer most of these already, just confirm the gaps.

---

## Step 2: Present the Phase Plan

Output the plan directly in the conversation (no files). Use this exact structure:

---

## Plan: [Feature / Task Name]

**Goal:** [one sentence — what this achieves]
**Success criteria:** [measurable — e.g., "all tests pass", "API returns correct data for edge inputs", "user can complete the flow end-to-end without errors"]

---

### Phase 1: [Name]
**Scope:** [what gets built in this phase]
**Tasks:**
- [ ] specific task
- [ ] specific task

**Gate:** [what must be verified true before Phase 2 can start]

---

### Phase 2: [Name]
**Scope:** ...
**Tasks:**
- [ ] ...

**Gate:** ...

---

*(add as many phases as needed)*

**Out of scope:** [explicit exclusions to prevent scope creep]
**Risk flags:** [anything that could go wrong — highlight auth, DB migrations, external APIs, irreversible operations]

---

## Choosing Phase Gates

Gates are not optional. Every phase needs one. Pick the gate that matches the risk of what was just built:

| What was built | Gate |
|---|---|
| Core data model / DB schema | Manual review + migration dry-run before applying |
| API or backend logic | Automated tests pass + manual smoke test |
| Auth / permissions / roles | **Manual review required — never automate this gate** |
| UI / frontend components | Build passes + visual check by user |
| Integration / glue code | End-to-end test or manual walkthrough |
| Refactor / cleanup | All existing tests still pass, no behaviour change |
| Third-party API integration | Integration test with real credentials in staging |

Default gate: **automated tests pass**.
Escalate to **manual review required** for auth, DB changes, or anything touching production data or user permissions.

---

## Step 3: Get Sign-off

The plan is not complete until you ask for confirmation. After the risk flags, always end with this exact line:

> "Does this plan look right? Any phases to add, merge, or cut before I start?"

Do not begin implementation until the user explicitly confirms. Do not skip this step even if the plan seems obvious — alignment now prevents rework later.

---

## Principles

- Phases should be independently verifiable — each one should produce something you can check
- Fewer phases with sharp gates beat many phases with fuzzy ones
- If you can't write a concrete gate, the phase boundary isn't well-defined yet — refine it
- Risk flags are not optional: surface them even when the user didn't ask
- Scope exclusions are as important as scope inclusions — write them down
