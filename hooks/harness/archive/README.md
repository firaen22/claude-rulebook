# Archive

Obsolete runners and inert text evidence that are no longer live-by-reference in
any code path. Files are kept **verbatim** as historical record — their internal
cross-references (e.g. a packet naming `reviews/…`) describe where a file sat when
written and are not rewritten on archival.

## Contents

### `candidate/` — obsolete hook versions (Round 1, 2026-09-09)

- `candidate/v22-installed.sh` — intermediate runner, live 2026-08-31
- `candidate/v23.sh` — intermediate runner
- `candidate/v24.sh` — intermediate runner
- `candidate/v25.sh` — intermediate runner
- `candidate/v27.sh` — intermediate runner (H1 defect detector)

**Why archived:** Zero live-by-reference uses in `run_all.sh`, `pidhang.py`, `budget_control.sh`, `README.md`, or any other live code path. Moved 2026-09-09 (P3′ Round 1).

### `review/`, `dispatch/`, `reviews/` — inert text evidence (Round 2, 2026-09-09)

- `review/` — per-reviewer packets, verdicts, and raw logs (agy/grok/grok26/nim/opencode/sol/sol24/sol26/v27); `review/v27/TASK.md` is the fullest statement of contract, history, and known limits.
- `dispatch/` — subordinate dispatch packets (sol/grok/agy/nim/opencode/luna).
- `reviews/` — cross-model review records and `reconcile_pairs` packets (2026-09-01 → 2026-09-06).

**Why archived:** Zero live-code/runtime/gate dependencies — no runner, `check_catalog`, `check_density`, or constructed Python path references these dirs (verified by full-tree sweep, 2026-09-09). The only consumers were documentation citations in `../README.md` (12, all rewritten to `archive/…` in the same commit) and three project-memory findings. Moved 2026-09-09 (P3′ Round 2).

## Gate scope

Neither `check_catalog` nor `check_density` inventories this tree, so the archive is **gate-invisible**: moves here do not trigger false-RED on governance gates, and archived content does not pull into gate scope.

## Retention

These files remain in the repo for historical traceability. No cleanup policy; they may be removed if the evidence base is ever fully extracted out-of-tree.
