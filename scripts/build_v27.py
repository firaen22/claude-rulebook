import io, os
R = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(R,"candidate","v26.sh")).read().split("\n")
# 1-indexed anchors verified: 608 = 'exec 3<&0' ; 763 = 'exec 0</dev/null'
assert src[607].strip() == "exec 3<&0", repr(src[607])
assert src[762].strip() == "exec 0</dev/null", repr(src[762])
head = src[:608]          # lines 1..608 inclusive (through 'exec 3<&0')
# find watchdog 'end=$(( SECONDS + DEADLINE ))'
end_idx = next(i for i,l in enumerate(src) if l.strip()=="end=$(( SECONDS + DEADLINE ))")
tail = src[end_idx:]      # watchdog through end (unchanged)
# sanity: nothing between 763 and end_idx we need except comments
mid_kept = src[763:end_idx]   # the watchdog comment block (lines 764..end_idx)

PROBE_BODY = r"""import os, sys
try:
    _fds = sorted(int(_n) for _n in os.listdir("/dev/fd"))
except Exception:
    _fds = None
if _fds is not None:
    for _fd in _fds:
        if _fd > 2:
            try:
                os.close(_fd)
            except OSError:
                pass
else:
    try:
        _hi = os.sysconf("SC_OPEN_MAX")
    except Exception:
        _hi = 4096
    if not isinstance(_hi, int) or _hi < 64 or _hi > 1048576:
        _hi = 1048576 if (isinstance(_hi, int) and _hi > 1048576) else 4096
    try:
        os.closerange(3, _hi)
    except Exception:
        pass
sys.exit(37 if sys.version_info >= (3, 7) else 0)"""

NEW = r'''# The parent drops its OWN stdin now: fd 3 already holds the caller's event for
# the worker, and every fork the parent makes during the probe below (the poll
# `/bin/sleep`, each probe subshell) must NOT inherit the caller's pipe. A probe
# child abandoned mid-startup therefore cannot hold caller stdin. v26 nested the
# probe inside the worker and closed fd 3 there with `3<&-`; the probe now runs
# one level up, so the parent closes its fd 0 here and each probe child re-closes
# fd 3 explicitly.
exec 0</dev/null

# ROUND 27 (codex-sol + grok review of v26; H1 reproduced 2026-09-01): the
# interpreter self-test moved OUT of the worker subshell and UP into the parent.
# v26 ran the probe as a GRANDCHILD (a child of the worker). The top-of-file trap
# runs `builtin kill -KILL $(builtin jobs -pr)`, and `jobs -pr` lists only the
# parent's OWN jobs -- so a terminating signal delivered PID-directed to the hook
# while a probe hung killed the worker ($wid) and ABANDONED the hung probe: a
# runnable stub (`while :; do :; done`) reparented to launchd and span at 100% CPU
# with no deadline left, because the inner 1s killer lived inside the worker that
# just died. Reproduced under H01+SIGTERM@0.35s: v26 left 1 spinning survivor,
# v22 left 2. The comment v26 shipped ("window at most the 1s probe budget") was
# false -- the orphan's lifetime is unbounded. The fix reconciles two invariants
# that pull against each other:
#   (a) ROUND 12 -- the `[ -x ]` stat(2) must NOT run in the parent: a wedged
#       automount would block the parent with a terminating signal deferred
#       inside the syscall and no watchdog yet alive. So each candidate's stat
#       AND probe run inside a background subshell `( ... )`.
#   (b) H1 -- the probe must be a DIRECT child of the parent so the trap reaches
#       it. `builtin exec "$_p"` at the tail of that subshell REPLACES the
#       subshell with the interpreter, so `$!` IS the interpreter pid and it is a
#       job of the PARENT: `jobs -pr` lists it and the top-of-file trap kills it.
# NO process-group change anywhere (keeps the approved v22 delivery; answers the
# withdrawn v24's F1/F2). The probe body, the exit-37 success channel, the shared
# 1s budget and the pid-directed inner kill are UNCHANGED from v26 -- only the
# process that owns them moved up one level. The worker below is now a bare `exec`
# of the chosen interpreter: no poll loop and no `/bin/sleep` run in it, so no
# foreground grandchild can inherit caller stdin (this also closes v26's M1 nit).
#
# Candidates are ROOT-OWNED absolute paths only (round 15): /opt/homebrew/bin and
# /usr/local/bin are same-UID-writable, and this probe is a skip-broken-file
# check, NOT an authentication -- ANY program that exits 37 is then exec-ed with
# this environment. `-x` alone is TRUE for a directory, so `-f` pins each
# candidate to a regular file. If no candidate passes, no worker is spawned and
# the event is silently lost -- priced cheap by the contract.
#
# The shared 1s budget is set ONCE before the loop. SECONDS is whole-second
# granularity, so the budget expires at the next integer tick -- between (0,1]s
# after this assignment depending on the sub-second phase when it runs (v26's
# comment claimed a 0.05s lower bound; corrected here per the L1 review nit). A
# slow-but-honest first interpreter whose startup crosses that tick is killed and
# the event lost: load/FS-dependent event loss, which the contract prices cheap.
# The C3 bound still holds: the whole probe phase is < the outer DEADLINE=2.
_chosen=""
_pend=$(( SECONDS + 1 ))
for _p in /Library/Developer/CommandLineTools/usr/bin/python3 \
          /usr/bin/python3; do
  # Budget already spent by an earlier candidate: do not even spawn (the wedged
  # first-candidate host prices as event loss, round 26).
  if builtin [ "$SECONDS" -ge "$_pend" ]; then builtin break; fi
  # `( stat && exec python )` -- see (a)/(b) above. `</dev/null` so the probe
  # cannot eat event bytes; `3<&-` so an abandoned probe cannot hold the caller's
  # fd-3 event dup during python startup (before the body's own closerange runs);
  # stdout/stderr to /dev/null. Probe body is byte-identical to v26: it closes
  # inherited fds >2 then exits 37 on python >= 3.7 (a 3.6 that would die on
  # time.time_ns at every event is version-gated OUT here), 0 otherwise; an
  # ENOEXEC/corrupt candidate exits != 37 and is skipped.
  (
    if builtin [ -x "$_p" ] && builtin [ -f "$_p" ]; then
      builtin exec "$_p" -I -S -B -c '@BODY@'
    fi
    builtin exit 1
  ) </dev/null 3<&- >/dev/null 2>/dev/null &
  _ppid=$!
  _pkilled=no
  while builtin :; do
    _prun=$(builtin jobs -pr)
    case "
$_prun
" in
      *"
$_ppid
"*) builtin : ;;
      *) builtin break ;;
    esac
    if builtin [ "$SECONDS" -ge "$_pend" ]; then
      builtin kill -KILL "$_ppid" 2>/dev/null || builtin true
      _pkilled=yes
      builtin break
    fi
    /bin/sleep 0.05 </dev/null >/dev/null 2>/dev/null || builtin true
  done
  _prc=137
  if builtin [ "$_pkilled" = no ]; then
    if builtin wait "$_ppid" 2>/dev/null; then _prc=0; else _prc=$?; fi
  fi
  if builtin [ "$_prc" -eq 37 ]; then _chosen="$_p"; builtin break; fi
done

# WORKER: only if a candidate passed. A bare exec of the chosen interpreter with
# the event on fd 0 (via `<&3`). `3<&-` closes the parent's event dup inside the
# worker after it becomes fd 0, so an abandoned worker's own os.close(0) frees the
# producer's pipe (round-13 rationale, unchanged).
if builtin [ -n "$_chosen" ]; then
  (
    builtin exec "$_chosen" -I -S -B -c "$OBS_CODE"
  ) <&3 3<&- >/dev/null 2>/dev/null &
  wid=$!
else
  wid=""
fi
exec 3<&-

# No interpreter passed the probe: no worker exists to bound. The event is
# already lost (cheap); skip the watchdog entirely -- an empty $wid would make
# the poll `case` below match a blank line and mis-detect "finished".
if builtin [ -z "$wid" ]; then builtin exit 0; fi
'''.replace("@BODY@", PROBE_BODY)

out = "\n".join(head) + "\n" + NEW + "\n".join(mid_kept) + "\n" + "\n".join(tail) + "\n"
# collapse any accidental double blank between NEW and mid_kept
open(os.path.join(R,"candidate","v27.sh"),"w").write(out)
print("wrote v27.sh, lines:", out.count("\n"))
