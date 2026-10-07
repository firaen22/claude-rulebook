---
name: finding-splash-qwen-routing-2026-10-07
description: "Routing for local Qwen3.8-27B-Splash (Splash OpenAI API): optional same-model methods cross-lens only; not an implementation subordinate. Evidence from the claude-code-technique bench harness merged 2026-10-07."
metadata:
  node_type: memory
  type: finding
---

# Local Qwen3.8-27B-Splash — routing finding (2026-10-07)

**Verdict:** promote a **rulebook routing row**, not a new default coder. Local Splash is an
optional **cross-lens** for harness/methods packets when the server is up; **do not route
implementation or multi-file agentic work** to it. Among the harness lenses measured
2026-10-07, Qwen was the **weak** lens (not a ranked fleet-wide "weakest subordinate").

## Evidence (harness on `main`, experiment `experiments/qwen-splash-local-2026-10-07/`)

**N counts (explicit):**

| Arm | What N counts | N |
|-----|----------------|---|
| Throughput / golden | Independent bench **sessions** (same config, different clock times) | **3** |
| TypeSafe | Preregistered **tickets** in `typesafe/cases.jsonl` | **2** |
| Qwen cross-review | **Review rounds** (`r1`, `r2`) on the harness packet | **2** |
| grok cross (harness) | Review **rounds** until FIX cleared | **1** cross cycle + adjudication |
| sol pre-commit (harness) | Review **rounds** | **5** sol rounds (r5 PROCEED) |
| grok pre-commit (harness) | Review **rounds** | **4** grok rounds (r2 PROCEED, r3 FIX, r4–r5 PROCEED) |

Golden selftest is **43 deterministic checks**, not a session count.

| Arm | Outcome |
|-----|---------|
| Deterministic golden + selftest | PASS — validates **harness + frozen golden**, not Qwen review quality |
| TypeSafe Jev + `grade_typesafe_metrics.py` | PASS on 2 bench **state strings** — not Qwen judgment |
| Qwen3.8-Splash self-review | r1 FIX F1–F4 (adjudicated); r2 printed **PROCEED** | R-B: verdict line is not evidence; read-only; **missed 3 defects** gpt-6.1-sol found by running grader mutations |
| grok-4.7 cross | FIX → fixed | independent family |
| Pre-commit gpt-6.1-sol + astra pack, grok | r5 **PROCEED** both | independent family |

**Scope:** one machine, one Splash build (2026-10-07). Throughput bands frozen in golden v3;
not a general local-coding benchmark (no tool use, JSON-only, or Chinese workloads).
**No Splash model capability** (review or coding) is inferred from golden/TypeSafe PASS alone.

## Routing doctrine (what to write in the map)

1. **Server:** `http://127.0.0.1:8000/v1`, model `incoai/Qwen3.8-27B-Splash`. Fail closed if
   down (`check_server.py` exit 2).
2. **Use:** optional methods/harness review via `ask_splash.py` + `grade_verdict.py`
   (`PROCEED` / `FIX` last line). Same-model confound — treat as **weak lens**; never
   single-source a ship decision.
3. **Do not use:** default implementation, opencode substitute, security/privacy/auth review,
   or multi-file agentic work (unmeasured; aligns with §2 "none of them" for long-horizon).
4. **Artifact home:** harness code stays in **claude-code-technique**; this finding + map row +
   `workflow_splash_qwen.md` live in **claude-rulebook** (`~/.claude/memory/`).

## What would change the conclusion

- Splash or model swap without re-bench and golden refresh.
- A measured implementation bench on Splash that clears the free-pool / codex bar for a
  stated task family (would add a new map row, not overwrite the weak-lens row).
- Qwen cross-lens reliably catching defects sol finds by mutation (would raise trust).

## Retractions

None. Supersedes informal "use Qwen for coding" assumptions only.
