# Archive

Obsolete hook versions that are no longer live-by-reference in any code path.

## Contents

- `candidate/v22-installed.sh` — intermediate runner, live 2026-08-31
- `candidate/v23.sh` — intermediate runner
- `candidate/v24.sh` — intermediate runner
- `candidate/v25.sh` — intermediate runner
- `candidate/v27.sh` — intermediate runner (H1 defect detector)

**Why archived:** Zero live-by-reference uses in `run_all.sh`, `pidhang.py`, `budget_control.sh`, `README.md`, or any other live code path. Moved 2026-09-09 (P3′ Round 1).

## Gate scope

Neither `check_catalog` nor `check_density` inventories this tree, so the archive is **gate-invisible**: moves here do not trigger false-RED on governance gates, and archived content does not pull into gate scope.

## Retention

These files remain in the repo for historical traceability. No cleanup policy; they may be removed if the evidence base is ever fully extracted out-of-tree.
