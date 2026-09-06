# v30 probe-budget fix — cross-model review dispositions (2026-09-06)

Author: this session (Opus, Claude family). Change: `candidate/v30.sh` = `v28.sh`
with the single executable edit `_pend=$(( SECONDS + 1 ))` → `+ 2` (probe budget
floor (0,1]s → (1,2]s), closing the `D_pid_INT` boundary-collapse VOID). Everything
else in v30 is comments. v29 (breadcrumb instrument) is NOT an install candidate.

Reviewers (dry-run confirmed this session; two non-author families → cross-family
gate met): codex `gpt-6-astra` medium (openai), grok `grok-4.6` (xai), fresh Fable
(claude, same-family third lens). Packet: `PACKET_v30.md` (self-contained; diff +
finding + verification + rubric). **All three verdicts: PROCEED. Round 1, no FIX.**

## Verification (all executed 2026-09-06, by the author before dispatch)
- Positive control (the R0 control the finding's first "REJECTED" lacked):
  exact-probe-loop replica, 0.05s startup, 150 trials — `+1` KILLED 5/150 (3.3%),
  `+2` KILLED 0/150.
- run_all.sh v30 --pidhang: contract 57/57, gap PASS, grpsig2 5/5+5/5, pidhang
  DISCRIMINATED (v26 control leaks 10/10, v30 clean 10/10).
- soak_launch.py v30, 1500 launches: 0 anomalies, 0 dropped files.
- Fable independently EXECUTED the arithmetic (bash 3.2.57 arm64: N=2 floor
  measured 1.96–2.00s; python probe startup 44ms → ~22× headroom) and computed
  P(0 hits in 1500 | p≈0.015) ≈ 1.4e-10.

## Findings (all LOW / non-blocking; each reproduced before acting)

| id | reviewer(s) | finding | reproduction | disposition |
|---|---|---|---|---|
| F1 | Fable | v30.sh comment "the shared 1s budget … UNCHANGED from v26" is stale (now 2s) | CONFIRMED by read (line 652) | **fixed**: reworded to say the budget kept the SECONDS mechanism through v29 and v30 widened +1→+2; body/channel/kill still UNCHANGED from v26. |
| D1 | codex | header "dropped ~1-2% of hook launches" conflates the synthetic spin rate with the observed live rate | CONFIRMED: live = 1/1500 (~0.07%), synthetic spin ~1.5%, control 3.3% — three different populations | **fixed**: header now lists all three rates separately with their populations. |
| C3-prose | codex D2, grok N1, Fable | new comment "probe phase is < 2s" ignores poll/kill/reap slop, and cites a 10s ceiling where contract.py WALL_CEIL=12 (graded 11.5) | CONFIRMED: Fable read `contract.py:16` WALL_CEIL=12.0 | **fixed**: comment now says kill fires ≤2s + one 0.05s poll + SIGKILL/reap slop, sum ~4s, well under WALL_CEIL 12 (graded 11.5). |
| F2 / S1 | Fable, grok | worker watchdog `DEADLINE=2` comment (~line 239) overstates the floor as a flat 2s; effective (1,2]s | CONFIRMED present in v28 (merge-base) → **pre-existing**, not a v30 regression | **pre-existing-tracked**: NOT changed (touching an unrelated v28 comment is scope creep on a one-token fix). Noted in the C3 comment. A clipped worker leaves an UNREADABLE truncated file (not a silent VOID), floor 1s vs ~0.41s normal run — different, lower-severity class; no VOID ever traced to it. Queue: fold into any future worker-budget change. |
| S2 | grok | `+2` still floors at 1s; an exec whose startup exceeds 1s (EDR/NFS/CPU-starvation) can still silent-drop; optional `+3` → (2,3]s | reasoned; not reproduced (no >1s-startup host available) | **rejected-with-reason for THIS fix**: `+2` is the minimal change that closes the REPRODUCED 16ms collapse; `+3` targets a DIFFERENT, unreproduced class at the cost of +1s wedged-host latency on every launch. Recorded as the escalation if a future VOID traces to a slow-exec host. |
| F3 | Fable | PACKET_v30.md says "10s ceiling"; real WALL_CEIL=12 | CONFIRMED, packet-only, no code impact | **recorded**: packet is a spent review artifact (not edited retroactively); the hook comment was corrected (see C3-prose). |

All fixes are comment-only; post-fix the non-comment diff vs v28 is still exactly
`_pend=$(( SECONDS + 1 ))` → `+ 2`, `bash -n` clean. No re-review round needed
(all PROCEED round 1; the doc fixes change no behavior and were verified against
ground truth, not against the reviewers' prose).

**Status: v30 is review-clean and merge-eligible. NOT INSTALLED — install is the
owner's call** (would replace `~/.claude/hooks/observe-compaction-events.sh`, the
live compaction hook, and update its registration/backup per the v28 install trail).
