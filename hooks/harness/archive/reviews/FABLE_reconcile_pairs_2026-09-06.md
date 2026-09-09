# FABLE review — reconcile_pairs.py + test_reconcile_pairs.sh (2026-09-06)

Reviewer: fresh-context Fable 5.1. Worked on a copy under the session scratchpad
(`fable-review/`); nothing under `~/.claude/` edited except this file; the live
`observed/` dir was only READ (checker run against it read-only).

Setup verified: copied `harness/reconcile_pairs.py` is byte-identical to the packet
inline (`diff` clean) [verified: diff]. Suite on copy under `/bin/bash` 3.2.57 +
python 3.9.6: 21/21 + CONTROL PASS [verified: ran it]. Live dir today: 405 files,
PC=71 SSC=67 pairs=67 VOID=0 ORPHAN=4 ANOMALY=7 (two more files than the packet's
403; verdict unchanged) [verified: ran checker read-only].

Every adversarial fixture below had expected output written into `adv.py` BEFORE
running (`run(name, (rc, substrings...))`); "DIFF" = checker disagreed with what a
correct detector should say. Mutation results come from `mut.sh` (18 sed
mutations of the checker, suite re-run against each).

---

## Findings (severity-ranked)

### F-1 [HIGH, silent false negative] Orphan PreCompact inside the window masks a later real VOID
- Location: `harness/reconcile_pairs.py:126-131` (claim loop keyed on session_id + window only).
- Mechanism: an unclaimed PC from a cancelled/abandoned compaction sits in `unclaimed`. The next
  compaction's PC is silently dropped (the v30 class), its SessionStart/compact arrives within
  `--window` and claims the stale orphan. Result `pairs=1 VOID=0 ORPHAN=0 RESULT: CLEAN rc=0`.
  The one failure class this tool exists to catch is converted into a clean run, and the orphan
  that would at least have hinted at it disappears too.
- Fixture (adv/F1_orphan_masks_void): `10s PC S1 prompt_id=p1`; `300s SSC S1 prompt_id=p2`.
  Expected (truth): VOID=1 ORPHAN=1 rc=1. Got: `pairs=1 VOID=0 ORPHAN=0 RESULT: CLEAN` rc=0
  [verified: ran]. Same with three stacked PCs (adv/F17): `pairs=1 ORPHAN=2 CLEAN` — the masked
  VOID is invisible, only the two older orphans show.
- Is it real? Yes. Orphans DO occur live (4 in 405 files) and one live session (846598ea) had an
  orphan PC followed 2518s later by a real PC+SSC pair — 718s later and the orphan would have
  been inside the default window. Shrinking `--window` only lowers the probability.
- Minimal fix (verified on copy, `patched.py`): pair on `prompt_id` when both sides carry it.
  Live data: PreCompact and SessionStart/compact records carry the SAME `prompt_id` in 66/66
  live pairs, 0 mismatches, 0 missing [verified: script over observed/]. Change
  `load_complete` to return `raw.get("prompt_id")` as the detail for PC/SSC, keep it in the
  unclaimed tuple, and make the claim condition
  `ns - pc_ns <= window_ns and (pid is None or pc_pid is None or pc_pid == pid)`.
  With the patch: F1 → `VOID=1 ORPHAN=1 rc=1`; suite still 21/21 (fixtures have no prompt_id
  → fallback path); live dir output byte-identical to the unpatched checker (PC=71 SSC=67
  pairs=67 VOID=0 ORPHAN=4) [verified: all three run]. Residual irreducible case: an orphan
  and the missing PC share a prompt_id (two auto-compactions inside one user turn) — state it
  in the docstring; also add a fixture for F1 so the suite can fail on regression.

### F-2 [HIGH, wrong exit class] Non-string `raw` → uncaught TypeError → traceback with rc=1 (the VOID/ANOMALY code)
- Location: `harness/reconcile_pairs.py:64` (`json.loads(outer["raw"])`), except tuple at `:106`.
- Mechanism: `TypeError` is not in `(ValueError, JSONDecodeError, UnicodeDecodeError, OSError)`.
  Python exits 1 on an uncaught exception, which is the documented "VOID or anomaly" code, and
  NO `SUMMARY`/`RESULT` line is printed, so every later file in the directory is skipped —
  contradicting the docstring's "fail loud, never silently skip".
- Fixtures: adv/F9_raw_not_string (`"raw": {...}` object) and adv/F9b_raw_null (`"raw": null`).
  Expected rc=2 + UNPARSEABLE line. Got: traceback, rc=1, no SUMMARY [verified: ran].
- Fix (verified on copy): before `json.loads`, `if not isinstance(outer["raw"], str): raise
  ValueError("raw is not a string")`. Optionally also add `TypeError` to the except tuple.

### F-3 [MEDIUM, silent] Unknown `hook_event_name` / SessionStart with missing or unknown `source` are counted as `other` and exit 0
- Location: `harness/reconcile_pairs.py:71-73` (bare `else: return ("other", ...)`).
- Mechanism: the docstring (`:24-25`) promises rc=2 for "a shape this script did not define",
  but any event name (including `None`) and any SessionStart source (including `None`) is
  silently `other`. If the host ever renames/omits `source` on compact events, every VOID
  disappears with `RESULT: CLEAN`. Nothing in the SUMMARY distinguishes "260 legitimate
  startup/resume" from "260 unclassifiable".
- Fixtures: adv/F7_ssc_source_missing (SessionStart, no `source`) → `other=1 CLEAN rc=0`;
  adv/F8_event_missing (`hook_event_name: "Bogus"` and absent) → `other=2 CLEAN rc=0`
  [verified: ran]. Expected rc=2 UNPARSEABLE for both.
- Fix (verified on copy, live output unchanged): whitelist — `SessionStart` with source in
  `{startup, resume, clear, fork}` and `InstallCheck` → `other`; anything else →
  `raise ValueError("unrecognized event %r source/trigger %r" ...)`.

### F-4 [MEDIUM, false positive] `--since` cutting between a PC and its SSC reports a VOID
- Location: `harness/reconcile_pairs.py:95-97` (excluded files never enter `events`).
- Mechanism: exclusion is applied before pairing, so an in-scope SSC whose PC is just before
  the cutoff has nothing to claim. A user who runs `--since <now-ish>` right after a
  compaction gets `RESULT: VOID rc=1` on a healthy pair. Not silent, but it is exactly the
  false alarm the README's `--since` example invites.
- Fixture: adv/F6_since_splits_pair: PC@10s, SSC@100s, `--since 50000000000`. Expected
  CLEAN pairs=1. Got `PC=0 SSC=1 pairs=0 VOID=1 RESULT: VOID rc=1` [verified: ran].
- Fix (verified on copy, `patched2.py`): let out-of-scope PC/SSC still participate in pairing;
  only COUNT/REPORT items (pairs, VOID, ORPHAN, ANOMALY, other) whose own ns is in scope.
  Suite 21/21 unchanged, F6 → `pairs=1 VOID=0 CLEAN`, live `--since 2026-09-05T00:00:00Z`
  output identical to the unpatched checker.

### F-5 [MEDIUM, false positive] SSC filename-ns earlier than its PC's → VOID + ORPHAN
- Location: `harness/reconcile_pairs.py:120` (`evs.sort()` on ns only) + claim loop.
- Mechanism: ordering key is the WORKER's `time.time_ns()` (packet: verified monotone with
  observed_at, which is the same worker's clock — so that check does not test what matters
  here). If a PreCompact worker is delayed past the SessionStart worker (heavy compaction
  path, fork stall — the M19–M22 orphan class this same harness documents), the pair inverts.
  Live gaps are 60–90s so it hasn't happened yet; it is loud (rc=1), not silent.
- Fixture: adv/F4_ssc_before_pc: SSC@100s, PC@101s same session. Expected pairs=1 CLEAN.
  Got `pairs=0 VOID=1 ORPHAN=1 RESULT: VOID` [verified: ran]. Equal-ns tie (adv/F5) is fine:
  `"PC" < "SSC"` in the tuple sort puts the PC first → pairs=1 [verified].
- Fix: with F-1's prompt_id pairing, allow a claim by a PC whose ns is within a small
  tolerance AFTER the SSC (e.g. `-5s <= ssc_ns - pc_ns <= window_ns`) when prompt_id matches.
  Without prompt_id, leave as-is and document. [reasoned]

### F-6 [LOW, suite gap] No fixture proves per-session pairing; A6 passes on a session-blind checker
- Location: `scripts/test_reconcile_pairs.sh:67-71` (A6).
- Mechanism: A6's two interleaved sessions happen to pair correctly under GLOBAL most-recent
  pairing as well (counts identical). Mutation M2 (`events.setdefault("x", [])`, i.e. ignore
  session_id entirely): SUITE GREEN, 21/21 [verified: mut.sh]. The tool's central invariant
  ("same session_id") has no test that can fail.
- Fix: add `PC S1 @10s; SSC S2 @20s` → expect rc=1 `VOID=1 ORPHAN=1` (adv/F11 shows the
  current checker gets this right; it just isn't asserted).

### F-7 [LOW, suite gap] Other surviving mutants: `--since` boundary and event ordering
- Mutants that left the suite GREEN [verified: mut.sh]:
  - M6 `ns <= since_ns` (boundary off-by-one): no fixture places a file exactly at the cutoff.
    Add `--since $((10*S))` on a dir with a file at 10s → expect `in_scope` to include it
    (adv/F14 shows current behaviour: included).
  - M13/M14 (sort by name / no sort): all fixture ns values have the same digit count, so
    lexicographic == numeric. Live names are all 19 digits so this is nearly an equivalent
    mutant, but a fixture with `9*S` PC and `10*S` SSC would make ordering load-bearing.
- Mutants CAUGHT (for the record): VOID-never-increments (A3,A3s,A5,A10), window ignored (A5),
  claim-oldest (A11), anomaly suffix ignored (A9), unparseable→rc1 (A8×3,A9bad,A13),
  truncated unchecked (A9b), ORPHAN never increments (A4,A5), pairs never increments (6 cases),
  auto≠PC (A12), VOID→rc0 (4 cases), sid-missing accepted (A8c), any SessionStart=SSC (A7),
  claim-all (9 cases), excluded-still-in-scope (A9_since_ns). The positive control is real
  but weak: it only proves an rc mismatch is detected (a stub printing `VOID=1` + exit 1 would
  pass CONTROL and A3 while failing the rest — acceptable).

### F-8 [LOW, doc mismatch] README/docstring claims vs code
- "fail loud — never silently skip a shape this script did not define" (`:24-25`, README):
  false for F-2 (traceback, rc=1) and F-3 (unknown shapes → `other`, rc=0).
- "`--since` scopes out legacy files": unrecognized filenames (`.DS_Store`, editor temp files)
  are classified UNPARSEABLE at `:89-93` BEFORE the since check, so they can never be scoped
  out — one stray `.DS_Store` in observed/ makes every run rc=2 forever until deleted
  (adv/F12: ` 100-1.complete.json`, `1é-1…`, `…json.tmp`, and a DIRECTORY named like a record
  → UNPARSEABLE=4 rc=2 [verified]). Loud, so arguably correct; but the README should say so.
- A7 uses `$RANDOM` for ns AND pid: two draws colliding on both is ~1e-9 — nit, not flaky in
  practice; deterministic values would cost nothing.

---

## Sequences tried that did NOT break it [verified: adv.py, all matched pre-written expectation]
- F2 two compactions in window, SECOND PC missing (PC,SSC,SSC) → pairs=1 VOID=1 rc=1.
- F3 two compactions, FIRST PC missing (SSC,PC,SSC) → pairs=1 VOID=1 rc=1.
- F5 identical ns for PC and SSC → PC sorts first → pairs=1.
- F10 session_id changes across compaction (host semantics shift) → VOID+ORPHAN rc=1 (loud).
  Live data check: compaction keeps session_id in 67/67 pairs; `startup` and the `resume`
  that follows it 0.5s later carry DIFFERENT session_ids (new shell sid, then the resumed one)
  — irrelevant to pairing since both are `other`. `clear`/`fork` sources: 0 live records, so
  their sid semantics are unverified; either way they are `other` and cannot cause a silent miss.
- F11 PC only in S1, SSC in S2 → VOID+ORPHAN rc=1.
- F12 odd/unicode/space-prefixed names, `.tmp`, a directory with a record-shaped name → rc=2.
- F13 gap exactly == window → paired (`<=`); F19 `--window 0` with equal ns → paired.
- F14 `--since` exactly equal to a file's ns → included (`<` semantics).
- F15 PreCompact with `trigger` absent → still PC, paired.
- F16 `truncated`/`saw_eof` keys absent → ANOMALY rc=1.
- F18 `--since` with `+00:00`, fractional seconds, or negative int → rc=2 "bad --since".
- F21 dangling symlink, F26 UTF-8 BOM, F27 zero-byte file, F28 mode-000 file → UNPARSEABLE rc=2.
- F22 empty-string session_id → rc=2 "no session_id".
- F23 filename ns disagreeing with observed_at → pairs by filename (as documented).
- F24 pid reuse across two records → distinct names, paired. F25 registered_matcher
  contradicting raw → not checked, paired (acceptable; matcher is the hook's own field).
- bash 3.2: suite executed under `/bin/bash` 3.2.57 green; grep for `declare -A`, `mapfile`,
  `${x,,}`, `|&`, `&>>`, `coproc`, `[[ =~` → none. python: only `json/re/datetime/argparse`,
  f-strings absent; runs on 3.9.6 (system CLT python).

## Verdict
F-1 is the finding that matters: the tool's stated purpose is the silent PreCompact VOID and
the current pairing rule turns the most plausible real-world instance of it (orphan earlier in
the window) into `RESULT: CLEAN`. The fix is small, uses a field already present in 100% of
live PC/SSC records, and is verified not to change the live result. F-2/F-3 break the
fail-loud contract the docstring makes. F-4 will produce the first false alarm the moment
someone runs the README's `--since` example shortly after a compaction.

FIX F-1 F-2 F-3 F-4
