# FABLE review r2 — reconcile_pairs.py + test_reconcile_pairs.sh (2026-09-06)

Reviewer: fresh-context Fable (claude-fable-5-1), adversarial posture (refute, not confirm).
Scope: packet `reviews/PACKET_reconcile_pairs_v2_2026-09-06.md`; working copy at
`<scratchpad>/fable-review2/` (harness/, scripts/, fx/ fixtures, mut/ mutants, live_check.py,
adv.sh, mutate.py). Nothing under `~/.claude/` edited except this file.

## BLUF

**No defect found in `reconcile_pairs.py` itself.** 29 adversarial fixtures (expectations
written before each run) and 31 single-point mutants did not produce one false negative,
one wrong exit code, or one traceback from the real code. The findings are all in the
**fixture suite**: two branches that matter for VOID detection have no test that can fail
(a wrong checker passes all 46 cases + 2 controls), plus smaller gaps and two doc/rubric
wording corrections. The live-data premise of the packet is confirmed, with one delta
(a new ORPHAN from this very session).

Verdict: code PROCEEDs as written; the suite needs two fixtures before the "a test that
cannot fail is not a test" claim in its own header is true for the dup-SSC and no-EOF
branches. `FIX F-A F-B` (both are 2-line fixture additions; F-C..F-E optional).

Setup [verified: `diff`]: copies of both files are byte-identical to the packet's inlined
versions; suite on the copy under `/bin/bash` 3.2.57 + python 3.9.6 → 46 passed, 0 failed,
CONTROL1 PASS, CONTROL2 PASS, SUITE GREEN.

---

## Findings (severity-ranked)

### F-A — MEDIUM — no fixture exercises the dup-SSC branch; a checker that drops it passes the whole suite
- **Location:** `scripts/test_reconcile_pairs.sh:488-491` (A14). Comment says
  "two PCs same id; two SSCs same id" but only the dup-PC fixture exists.
  Code branch under test: `harness/reconcile_pairs.py:260` (`len(pcs) > 1 or len(sscs) > 1`).
- **Mechanism:** the 1 PC + 2 SSC shape is exactly "a second compaction whose PreCompact
  dropped, reusing a prompt_id". The real code reports ANOMALY rc 1 (correct, loud). Mutant
  M01 (`if len(pcs) > 1:` — the `sscs` half removed) pairs `pcs[0]` with `sscs[0]`, reports
  `pairs=1 VOID=0 ANOMALY=0`, **RESULT: CLEAN rc 0**, and passes all 46 cases + both controls.
  This is a wrong checker that hides a VOID-class event (rubric item 4, and the round-1
  "irreducible ambiguity" residual the identity design was meant to make loud).
- **Fixture:** `PC(10s,S1,p1) SSC(20s,S1,p1) SSC(900s,S1,p1)`
  → expected real: rc 1 `PC=1 SSC=2 pairs=0 VOID=0 ORPHAN=0 ANOMALY=1`
  → actual real: rc 1, exactly that [verified: adv.sh X1_dup_ssc]
  → actual M01: rc 0 `PC=1 SSC=2 pairs=1 VOID=0 ORPHAN=0 ANOMALY=0` RESULT: CLEAN
  [verified: `python3 mut/M01.py fx/x1`]; suite on M01: 46 passed, SUITE GREEN [verified: mutate.py].
- **Minimal fix:** add after A14:
  ```bash
  d="$ROOT/a14b"; mkdir "$d"; rec "$d" $((10*S)) 1 PreCompact manual S1 p1; rec "$d" $((11*S)) 2 SessionStart compact S1 p1; rec "$d" $((12*S)) 3 SessionStart compact S1 p1
  check A14b_dup_ssc "$d" 1 "PC=1 SSC=2 pairs=0 VOID=0 ORPHAN=0 ANOMALY=1"
  check A14b_dup_ssc_line "$d" 1 "1 PreCompact \+ 2 SessionStart/compact records share"
  ```

### F-B — MEDIUM — `saw_eof=false` is never isolated; a checker that ignores it accepts a no-EOF record as a healthy PC
- **Location:** `scripts/test_reconcile_pairs.sh:459-461` (A9b sets `truncated:true` AND
  `saw_eof:false`, so the `truncated` test alone satisfies it). Code: `reconcile_pairs.py:175`.
- **Mechanism:** the truncatable-C2 / no-EOF class (the reason `saw_eof` exists in the
  envelope) is a `complete.json` with `truncated:false, saw_eof:false` and a fully valid
  `raw`. Real code → ANOMALY, and the SSC it would have paired with becomes VOID (loud).
  Mutant M02 (drop `or outer.get("saw_eof") is not True`) accepts the record as a healthy PC
  and the pair reports CLEAN rc 0. M02 passes all 46 + 2.
- **Fixture:** `PC(10s) with truncated=false saw_eof=false + valid raw; SSC(20s) healthy`
  → expected real: rc 1 `PC=0 SSC=1 pairs=0 VOID=1 ANOMALY=1`
  → actual real: exactly that, line `complete.json with truncated=False saw_eof=False` [verified: fx/x7b]
  → actual M02: rc 0 `PC=1 SSC=1 pairs=1 VOID=0 ANOMALY=0` RESULT: CLEAN [verified: `mut/M02.py fx/x7b`].
  Note A9b-style `raw:"{}"` would NOT catch M02 (falls to UNPARSEABLE rc 2 — X7 shows this);
  the fixture must carry a valid PC raw.
- **Minimal fix:** add after A9b (the `printf` needs a real PC raw):
  ```bash
  d="$ROOT/a9c"; mkdir "$d"
  printf '{"observed_at":"x","registered_matcher":"x","truncated":false,"saw_eof":false,"raw":"{\\"hook_event_name\\":\\"PreCompact\\",\\"trigger\\":\\"manual\\",\\"session_id\\":\\"S1\\",\\"prompt_id\\":\\"p1\\"}"}' > "$d/$((5*S))-5.complete.json"
  check A9c_no_eof_only "$d" 1 "PC=0 .*ANOMALY=1"
  check A9c_no_eof_line "$d" 1 "ANOMALY .*truncated=False saw_eof=False"
  ```

### F-C — LOW — `truncated` key absent is untested (mutant `is True` survives)
- **Location:** `reconcile_pairs.py:175`; no fixture in the suite.
- **Mechanism:** real code treats a missing `truncated` as ANOMALY (`None is not False`),
  which is the right fail-loud choice. Mutant M03 (`outer.get("truncated") is True`) lets
  a record without the key through as healthy. With valid raw: real → RESULT: ANOMALY;
  M03 → RESULT: CLEAN [verified: fx/x8b]. Suite passes M03.
- **Fix:** one more `printf` fixture like A9c with no `truncated` key, asserting
  `"ANOMALY .*truncated=None saw_eof=True"`.

### F-D — LOW — a pre-cutoff lone SSC being EXCLUDED (not reported) has no fixture
- **Location:** `reconcile_pairs.py:225-235` (--since context path); suite A16/A16b only cover
  pre-cutoff PCs.
- **Mechanism:** by design a pre-cutoff SSC with no PC is excluded silently (documented).
  Mutant M04b (also load pre-cutoff SSCs into the SSC bucket) reports `VOID=1 rc 1` with
  `in_scope=0 excluded=1` — a self-contradicting SUMMARY — and passes the suite.
  Over-report direction (cheap side of the asymmetry), so LOW.
- **Fixture:** `SSC(10s) only, --since 15s` → expected/actual real: rc 0
  `in_scope=0 excluded=1 ... VOID=0` [verified: X4]; M04b: rc 1 VOID=1 [verified].
- **Fix:** `check A16d_since_hides_old_void "$ROOT/a3" 0 "in_scope=0 excluded=1 $CLEAN0" --since $((15*S))`.

### F-E — LOW — five more shapes the real code handles correctly but nothing in the suite pins
All [verified: adv.sh + mutate.py]; each mutant passes all 46 + 2:
| shape | real behaviour (correct) | surviving mutant | consequence under mutant |
|---|---|---|---|
| outer JSON missing `observed_at`/`registered_matcher`/`raw` | rc 2 `missing key 'raw'` (X9) | M07 (check only `raw`) | schema drift in the envelope invisible |
| outer JSON is a list | rc 2 `outer JSON is not an object` (X10) | M08 (drop dict check) | **AttributeError traceback** on `["observed_at","registered_matcher","raw"]` [verified: mut/M08.py fx/x10] |
| empty-string `prompt_id` | rc 2 `no prompt_id` (X13d) | M05 (drop `or not v`) | "" becomes a shared identity |
| `--window 0` | accepted, every positive gap ANOMALY (X18) | M06 (`0 <`) | documented `[0,1e9]` contract silently narrowed |
| unreadable in-scope file (chmod 000) | rc 2 `UNPARSEABLE ... Permission denied` (X14b) | M28 (drop OSError) | traceback rc 1 |
- **Fix:** one `check` each; the M08 and M28 ones are the most valuable because a traceback
  is the one rc-1-where-rc-2-is-documented path that mutation can reach.

### F-F — INFO (doc wording) — "pre-cutoff PreCompacts are never reported" is not literally true
- **Location:** `reconcile_pairs.py:132-135` docstring, `:227-228` comment, README
  "older files are not counted or reported".
- **Mechanism:** a pre-cutoff PC that pairs with an in-scope SSC and fails a pair sanity
  check IS named in the ANOMALY line: `PC(10s) SSC(2000s) --since 15s` →
  `ANOMALY 10000000000-1.complete.json 2000000000000-2.complete.json :: pair gap 1990.0s ...`
  [verified: fx/x26]. This is the RIGHT behaviour (loud), so the fix is wording:
  "never reported on their own / never counted; they may appear as the PC half of an
  in-scope pair's ANOMALY line".

### F-G — INFO (rubric item 3) — the stated SUMMARY invariant does not hold; there is no field that lets a reader check it
- **Location:** `reconcile_pairs.py:213-255`; rubric text
  "in_scope = PC + SSC + other + ANOMALY-files + UNPARSEABLE-files".
- **What I checked [verified: X19, X19b, live run]:**
  - `files = in_scope + excluded + name-UNPARSEABLE` (a `.DS_Store` is counted in `files` and
    `UNPARSEABLE` but in neither `in_scope` nor `excluded`: `files=1 in_scope=0 excluded=0 UNPARSEABLE=1`).
  - `in_scope = PC + SSC + other + ANOMALY_file + UNPARSEABLE_content`, but `ANOMALY` in the
    SUMMARY also counts pair-level anomalies: `--window 0` on one healthy pair prints
    `in_scope=2 PC=1 SSC=1 ANOMALY=1`, sum 3 ≠ 2.
  - Live: `405 = 71+67+260+7+0` held only because live has 0 pair anomalies and 0 name failures.
- **Fix (optional):** either count name-UNPARSEABLE in `in_scope`, or add
  `pair_anomalies=` to the SUMMARY, or just state the true invariants in the docstring.

### F-H — INFO — `math.isfinite` at `main:303` is redundant, not wrong
Mutant M25 (drop `isfinite`) survives because `0 <= nan <= 1e9` and `0 <= inf <= 1e9` are
already False [verified: python one-liner]. Leave it; harmless belt-and-braces.

### F-I — INFO (design note, --since) — --since between an INVERTED pair's SSC and PC hides the inversion
`SSC(10s) PC(20s) --since 15s` → SSC excluded, PC in-scope → `ORPHAN=1 rc 0`; without
`--since` → `ANOMALY rc 1` [verified: X3/X3b]. Consistent with "older files not reported",
0/67 live pairs inverted, so not a defect — but if the M19-M22 stall class is what the
ANOMALY exists for, loading pre-cutoff SSCs as context (not reported on their own, F-D
fixture guards the other direction) would keep the inversion visible under --since.

### F-J — INFO (live delta since packet) — one new ORPHAN, in THIS session
Live dir now 406 files: `PC=72 SSC=67 pairs=67 VOID=0 ORPHAN=5 ANOMALY=7` (packet: 405/71/4).
New orphan: `1788701120700069000-25993.complete.json` = PreCompact/manual,
`observed_at 2026-09-06T13:25:20Z` (21:25 local), session `d8a69179` prompt `2442fcef`
— the review session itself, no SessionStart/compact witness yet [verified: read-only
live_check.py + checker run]. Either an in-flight/cancelled compaction or the SessionStart
hook dropping; not a checker fault, but the author should look at it before quoting "ORPHAN=4".

---

## Packet premise check (read-only over `~/.claude/session-state/observed/`)
Script: `fable-review2/live_check.py` [verified: run 2026-09-06].
| claim in packet | measured |
|---|---|
| 405 files, nothing unrecognised | 406 files (one new PC), 0 non-matching names |
| inventory startup 186 / resume 73 / compact 67 / PC manual 70 / auto 1 / InstallCheck 1 | startup 186, resume 73, compact 67, **manual 71**, auto 1, InstallCheck 1, error.txt 7 |
| 67/67 pairs identical prompt_id PC↔SSC | 67 pairs; 0 SSC whose nearest-preceding PC in-session has a different prompt_id |
| 0 PC/SSC lacking prompt_id | 0 |
| 0 prompt_id recurring across sessions | 0; also 0 PC prompt_id reused within a session |
| 0 pairs with SSC ns ≤ PC ns | 0 inverted; 0 dup-identity groups |
| gaps 39.3–282.1 s, median 94 | 39.309 / 94.173 / 282.077 s |
| error files six 08-31, one 09-05 | Counter({'2026-08-31': 6, '2026-09-05': 1}) |
| README section as inlined | on-disk README contains the packet section verbatim [verified: substring] |

---

## Tried and did NOT break it
All [verified: adv.sh, expectations pre-written; 27/29 matched exactly, the 2 "DEVIATES" were
my regex anchoring on a trailing `:` — actual rc and text were correct].
- Item 1 (false negatives): 1 PC + 2 SSC same id → ANOMALY rc 1 (X1). Cancelled PC + same-pid
  SSC under window → CLEAN (X2; the documented residual, reproduces exactly as the docstring
  says). Dup PC across the --since cutoff → ANOMALY (X6). Pre-cutoff PC corrupt → context
  skipped → in-scope SSC is VOID rc 1 (X5). SessionStart/resume with the same (sid,pid) as an
  SSC-less PC is NOT a witness → ORPHAN + other (X20). PC recorded as `.partial.json` + healthy
  SSC → ANOMALY + VOID (X21). prompt_id with trailing space → distinct identity → VOID+ORPHAN
  (X22). Same ns, same pid, different session → two groups → VOID+ORPHAN (X23). Every in-scope
  SSC reaches exactly one of pair / VOID / dup-ANOMALY — there is no code path that drops one.
- Item 2 (fail-loud): missing outer keys, outer list, raw list, raw invalid JSON, BOM, UTF-16,
  empty file, invalid UTF-8, source/event/session_id as list or dict, empty prompt_id, a
  directory named like a record, chmod 000 file, chmod 000 directory, `--since` "", -5, 1.5,
  "²" (isdigit True but int() fails), year 0000, year 9999, 30-digit int, `--window` abc/0/1e9/
  1e9+1/nan/inf/-1 → rc 2 or the documented result in every case; zero tracebacks. Fullwidth
  digits `--since １` and Arabic-Indic digits in a filename are accepted and parsed correctly
  (harmless). Pre-cutoff unreadable / corrupt PC → silently skipped as documented.
- Item 3: invariants measured (F-G).
- Item 5: suite ran clean under `/bin/bash` 3.2.57 (no arrays/mapfile used); python literals
  `1_000_000_000`, `json.JSONDecodeError`, `math.isfinite` all ≥3.6 → fine on 3.9.6.
- ISO `--since` float exactness: `int(ts*1e9) == ts*10**9` for every 7th second 2020→2040
  (90 164 571 samples, 0 inexact) [verified] — the boundary-inclusive semantics A16c asserts
  also hold for ISO input.
- Suite mechanics: `check` regex is whole-token anchored (CONTROL2 confirms); fixture writer
  `exit 3` aborts the script, not a subshell; `trap rm -rf "$ROOT"` fires on EXIT.

## Mutant table (31 single-point mutants; suite run per mutant under /bin/bash)
| id | mutation | predicted | actual | VOID-detection relevant |
|---|---|---|---|---|
| M01 | dup-SSC not flagged (1 PC + 2 SSC pairs as healthy) | SURVIVES | **SURVIVES** | **YES → F-A** |
| M02 | saw_eof check dropped | SURVIVES | **SURVIVES** | **YES (no-EOF PC pairs as healthy) → F-B** |
| M03 | truncated check weakened to `is True` | SURVIVES | **SURVIVES** | partial → F-C |
| M04 | pre-cutoff SSC appended into the PC bucket (malformed mutant, kept for honesty) | SURVIVES | SURVIVES | marginal |
| M04b | pre-cutoff SSC loaded into SSC bucket (excluded VOID reported) | SURVIVES | **SURVIVES** | over-report → F-D |
| M05 | empty-string session_id/prompt_id accepted | SURVIVES | SURVIVES | no → F-E |
| M06 | --window 0 rejected | SURVIVES | SURVIVES | no → F-E |
| M07 | outer key check reduced to raw only | SURVIVES | SURVIVES | no → F-E |
| M08 | outer-is-dict check removed (traceback on list) | SURVIVES | SURVIVES | no → F-E |
| M09 | equal-ns tolerated | KILLED | KILLED by A15_equal_ns | YES |
| M10 | --since off-by-one | KILLED | KILLED by A16c | YES |
| M11 | window boundary >= | KILLED | KILLED by A5_window_exact | no |
| M12 | prompt-blind pairing (session only) | KILLED | KILLED by A2,A10,A11×3,A11b | YES |
| M13 | session-blind pairing (prompt only) | KILLED | KILLED by A6b | YES |
| M14 | pre-cutoff orphan reported | KILLED | KILLED by A16b | no |
| M15 | rc1 needs VOID and ANOMALY | KILLED | KILLED by 16 cases | YES |
| M16 | anomaly suffixes not special-cased | KILLED | KILLED by A9_anomalies | no |
| M17 | ns compared lexically | KILLED | KILLED by 18 cases incl. A17 | YES |
| M18 | RecursionError not caught | KILLED | KILLED by A8j | no |
| M19 | compact/other inverted | KILLED | KILLED by 23 cases | YES |
| M20 | UNPARSEABLE not fatal | KILLED | KILLED by A8* | no |
| M21 | window in seconds not ns | KILLED | KILLED by 11 cases | no |
| M22 | pre-cutoff non-complete files also attempted | SURVIVES | SURVIVES | no (harmless) |
| M23 | excluded not counted | KILLED | KILLED by A9_since*,A16,A16b | no |
| M24 | Stop event whitelisted as other | KILLED | KILLED by A8h | no |
| M25 | isfinite check removed | KILLED | SURVIVES | no (redundant check, F-H) |
| M26 | dup branch falls through | KILLED | KILLED by A14_dup_pc | no |
| M27 | VOID counted as ORPHAN | KILLED | KILLED by A3,A6b,A10,A11*,A11b | YES |
| M28 | OSError not a load error (unreadable → traceback) | SURVIVES | SURVIVES | no → F-E |
| M29 | pre-cutoff PC context stored as in-scope | KILLED | KILLED by A16b | no |
| M30 | unknown SS source tolerated as other | KILLED | KILLED by A8g,A8i | no |

Score: 19 killed / 12 survived; of the 8 VOID-relevant mutants, 6 killed, **2 survived (M01, M02)**.
Every VOID-relevant kill was by the fixture the packet says was added for it (A6b, A15,
A16c, A17, A11/A11b) — the round-1 fixes are load-bearing, not decorative.

## Verdict
Code: no defect found after trying the above. Suite: two VOID-relevant branches (dup-SSC,
no-EOF) have no test that can fail; add A14b and A9c (F-A, F-B; ~6 lines total), optionally
F-C/F-D/F-E, and reword F-F. Re-run the mutant set afterwards: M01 and M02 must die.

FIX F-A F-B
