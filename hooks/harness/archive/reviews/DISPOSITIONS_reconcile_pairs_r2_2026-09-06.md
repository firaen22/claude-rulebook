# reconcile_pairs.py — round-2 dispositions (2026-09-06)

Reviewers: codex gpt-6-astra medium (`CODEX_astra_last.md`, FIX F1–F6) and fresh-context
Fable 5.1 (`FABLE_reconcile_pairs_r2_2026-09-06.md`, FIX F-A F-B). Every finding was
reproduced by execution before a fix was authored; every fix has a fixture that the
matching single-point mutant turns RED. Suite after: 65/65 + CONTROL1/2 PASS, SUITE GREEN
under /bin/bash 3.2.57 + python 3.9.6 [verified: run]. 10 mutants, 10 killed [verified: run].

| id | finding | reproduced | disposition | fixture / mutant |
|---|---|---|---|---|
| codex F1 | `--since` loaded only pre-cutoff PCs; a pre-cutoff PC+SSC plus an in-scope dup SSC paired as healthy → false CLEAN | yes (PC@10 SSC@11 SSC@20 --since 15 → rc 0 pairs=1) | FIXED: pre-cutoff SSCs load as context too; group checked when any member in scope | A16e ×2 / MF1 RED |
| codex F2 | wholly pre-cutoff duplicate still reported ANOMALY rc 1 with in_scope=0 | yes | FIXED: skip groups with no in-scope member | A16f / MF2 RED |
| codex F3 = Fable F-A | no dup-SSC fixture; `len(sscs) > 1` mutant survives | yes (M01 passed 46/46) | FIXED: A14b, A14c | A14b ×2, A14c / M01 RED |
| codex F4 | lone surrogate in session_id → UnicodeEncodeError traceback rc 1 | yes | FIXED: reject in load_complete as UNPARSEABLE; `safe()` on names/ids in output | A8k / MF4 RED |
| codex F5 | `$` accepted trailing newline in filename; `--since` then hid it | yes | FIXED: `fullmatch`, `[0-9]` | A8l ×2 / MF5 RED |
| codex F6 | unrecognised name counted in neither in_scope nor excluded | yes (.DS_Store → in_scope=0 excluded=0) | FIXED: counted in_scope; invariant `files == in_scope + excluded` documented | A8b_counted / MF6 RED |
| Fable F-B | `saw_eof=false` never isolated; mutant dropping it accepts no-EOF PC as healthy | yes (M02 passed 46/46) | FIXED: A9c with valid PC raw | A9c ×2 / M02 RED |
| Fable F-C | `truncated` key absent untested | yes | FIXED: A9d | A9d / M03 RED |
| Fable F-D | pre-cutoff lone SSC exclusion untested | yes | FIXED: A16d | A16d / MF2 RED |
| Fable F-E | outer-list traceback under mutant, unreadable-file traceback under mutant, empty prompt_id | yes | FIXED: A8n, A8o, A8p | M08, M28 RED |
| Fable F-F | "pre-cutoff PCs never reported" not literally true (appear in pair ANOMALY line) | yes | FIXED: docstring + README reworded ("never reported on their own") | — |
| Fable F-G | rubric's SUMMARY invariant false; no field made it checkable | yes | FIXED (partly by F6): `files == in_scope + excluded` now holds; ANOMALY documented as a findings count, not a file count | A8b_counted |
| Fable F-H | `math.isfinite` redundant | yes | rejected-with-reason: harmless belt-and-braces, reviewer agrees; leave | — |
| Fable F-I | `--since` between an inverted pair's SSC and PC downgraded ANOMALY to ORPHAN | yes | FIXED as a side effect of codex F1 (SSC context): inversion now visible | A16g ×2 / MF1 RED |
| Fable F-J | live ORPHAN=5, new orphan in session d8a69179 prompt 2442fcef | yes at review time | resolved by data: SSC `1788701192169000000-26093` landed 72 s later; live now PC=72 SSC=68 pairs=68 ORPHAN=4 | — |

Not adopted verbatim: Fable's proposed A14b/A9c/A16d shell lines were used as the
specification of the fixture, re-authored against the suite's own helpers (`rec`,
`rawrec`, `$PCRAW`) — same expected tokens.

Live after fixes [verified: run 2026-09-06]: 407 files PC=72 SSC=68 pairs=68 VOID=0
ORPHAN=4 ANOMALY=7 rc 1 (the seven historical `.error.txt`); `--since 2026-09-06T00:00:00Z`
in_scope=70 PC=15 SSC=15 pairs=15 CLEAN rc 0.
