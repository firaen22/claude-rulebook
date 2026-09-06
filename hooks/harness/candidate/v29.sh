#!/bin/bash -p
# PHASE 0 — MEASUREMENT ONLY. v29 = v28 + two diagnostic breadcrumbs.
# *** HARNESS INSTRUMENT ONLY — DO NOT INSTALL. *** v28 (this file minus the two
# breadcrumbs) is what is INSTALLED 2026-09-01: registered 7 times in settings.json —
# PreCompact (manual, auto) + SessionStart (startup, resume, clear, compact, fork) —
# each as `/bin/bash --noprofile --norc -p <path> <matcher>`.
#
# v29 BREADCRUMB (2026-09-06), the ONLY change from v28: the two pre-worker
# `builtin exit 0` paths (OBS_CODE marker mismatch; no interpreter passed the probe)
# were silent by design, so the 2026-09-06 harness VOID — hook exit 0 at 26 ms with
# no file under observed/ — could not be attributed to either. Each now writes one
# small $LOG_DIR/<pid>.dropped.txt naming the path, and for the probe path each
# candidate's rc/killed plus SECONDS vs the budget. It did its job: a 1500-launch
# soak caught `secs=1 pend=1 ... rc137,killed=yes ... budget-spent-before-spawn`,
# i.e. the whole-second `_pend=$((SECONDS+1))` budget (below) collapses to <20 ms in
# ~1-2% of launches. The production correction is DEFERRED to v30 (not built as of
# 2026-09-06); this file does not fix it.
#
# WHY NOT INSTALLABLE (cross-model review 2026-09-06, codex gpt-6-astra + grok +
# fresh Fable, F1 reproduced at hook level): the breadcrumb is the ONLY place the
# PARENT opens a name under $HOME. bash `set -C` refuses an existing REGULAR file
# (and a dangling symlink) but NOT a FIFO or a symlink to one — a pre-planted
# FIFO at $LOG_DIR/<pid>.dropped.txt parks the parent in open() until a signal
# arrives (TERM releases it via EINTR, trap runs, rc 0 — contract 1 holds, contract 3
# bounded-time does not); nothing in this file bounds that wait (reproduced: >5 s). A wedged network/FUSE $HOME blocks the same way. The
# worker's O_EXCL|O_NOFOLLOW is not reproducible in builtins, and a backgrounded
# writer needs its own watchdog. In the harness a fresh isolated HOME per launch
# rules out pre-planted contents; the wedged-FS hazard is ruled out only by
# REQUIRING instrument runs on a healthy LOCAL filesystem ($TMPDIR), never a
# network/FUSE mount. That is the only place this file runs.
# Every added command ends `|| builtin true` so the ERR trap and the exit status
# are untouched; $LOG_DIR is NOT guaranteed to exist here (only the worker mkdirs
# it) and these paths do not fork one — the redirect just fails, breadcrumb lost.
#
# WHAT IT DOES: writes ONE file per hook event into $LOG_DIR/observed/, named
#   <ns>-<pid>.complete.json   EOF was OBSERVED and nothing was discarded
#   <ns>-<pid>.truncated.json  EOF observed, but more bytes existed than MAX_INPUT
#   <ns>-<pid>.partial.json    EOF was NEVER observed (read timed out or errored)
#   (there is no .part file: v7 writes straight to the final name, because the
#    unlink that published a .part could delete another writer's file — see the
#    write path. A worker killed mid-write therefore leaves a TRUNCATED .json,
#    which is not parseable and which the reader reports as UNREADABLE.)
#   <ns>-<pid>.error.txt       a diagnostic; the event was NOT recorded
# Each .json is one JSON object: observed_at, registered_matcher, truncated,
# saw_eof, raw. `raw` is the received text, decoded UTF-8, trailing CR/LF
# stripped. It is NOT byte-identical to stdin and does not claim to be.
#
# ONLY .complete.json IS A WHOLE EVENT. v4 labelled a timed-out partial read
# `.complete.json` with truncated:false — reproduced 2026-08-29 with 13 bytes and
# a held-open pipe. The stderr note said "may be incomplete" but the FILE, which
# is the only thing a reader ever sees, claimed otherwise. saw_eof now decides.
#
# WHAT IT DOES NOT DO: no shared log, no lock, no parse of the payload on the
# write path, no ftruncate, no unlink of anything it did not create this run,
# no rotation, no stdout on any path, and — since v13 — no stderr either: both
# are closed to /dev/null at the top of this file. Every diagnostic lives in a
# .error.txt; when even that cannot be written the event is silently lost,
# which the contract prices as CHEAP.
#
# WHY ONE FILE PER EVENT (v1-v3 were all rejected; this is why): a shared
# appended JSONL created most of the defect surface at once — a blocking flock
# hung the hook, a non-blocking one dropped 18.8% of close-pair events, a torn
# line killed the documented reader for the WHOLE log, an ftruncate rollback
# destroyed another writer's committed record, and O_NOFOLLOW does not refuse a
# hardlink to that one inode. None of those exist when each event is its own file.
#
# CONTRACT:
#  1. FAIL OPEN. Exit 0 and zero bytes on stdout on EVERY path. PreCompact can
#     BLOCK compaction; SessionStart stdout enters the model's context window.
#  2. NEVER DELETES AND NEVER REPLACES ANY FILE. There is no unlink, no rename,
#     no ftruncate anywhere in this hook. Every file is created with O_EXCL, so
#     an existing name makes the create fail instead of clobbering it. v4 used a
#     replacing rename; v5-v6 published a .part with link + unlink, and that
#     unlink resolves a pathname another writer can have taken over.
#  3. Bounded in bytes per event (MAX_INPUT) and in TIME (the worker deadline).
#     THE DIRECTORY CAPS ARE ADVISORY, NOT HARD: MAX_BYTES and MAX_FILES are a
#     check-then-act against a directory other processes are writing, so N
#     concurrent workers can each pass the check and overshoot by up to N records.
#     A hard bound needs a lock, and a lock is what made v1-v3 unshippable.
#  4. D10 IS NARROWED, ON PURPOSE: the time bound holds on a responsive local
#     filesystem. A worker wedged in an uninterruptible syscall on a network or
#     FUSE $HOME cannot be killed by any userspace watchdog; this parent abandons
#     it and still exits 0, so the HOOK is bounded even when the worker is not.
#     Claiming more than that would be false. Since round 27 the interpreter
#     probe runs in its OWN direct-child subshell at parent level, with the
#     [ -x ]/[ -f ] stat kept off the parent's synchronous path by that ( )
#     (round 12: a parent-side stat of an automounted path had no time bound at
#     all; before round 27 the probe was nested inside the worker child). The
#     parent still execs
#     /bin/sleep every 50ms in the watchdog (a standing, adjudicated
#     trade-off: a builtin busy-poll burns CPU on every event and a same-UID
#     STOP can freeze the parent either way) and /dev/null; those are the
#     parent-side filesystem touches, stated plainly.
#
# INVOCATION — THE SHEBANG CANNOT SAVE YOU HERE.
# LAUNCHER-OWNED, NOT FIXABLE IN THIS FILE (round 13, reproduced): with
# RLIMIT_NOFILE forced to ~4-12 by the launcher, the `exec >/dev/null`
# below cannot get a descriptor and BASH ITSELF writes redirect-failure
# diagnostics to the still-inherited stderr before any line of this file
# has control — on a full pipe that is an indefinite hang, and at limit 3
# bash aborts (rc 134). No trap or redirect written HERE runs early enough.
# The same class: SHELLOPTS=xtrace writes trace lines to inherited stderr
# before the redirect under a non -p invocation — and with BASH_XTRACEFD=1
# the same trace lands on STDOUT (round 15, reproduced: `+ exec` on fd 1
# before line 183 runs), a direct contract-2 byte. Both are properties of the
# invoking configuration, listed here so they are not rediscovered. The live
# settings.json had already been calling `bash -p <path> <matcher>` when measured
# 2026-08-31/09-01; what it lacked was `/bin/bash --noprofile --norc`. An explicit
# `bash` IGNORES the shebang: measured 2026-08-31, a BASH_ENV payload RAN under
# the bare form and was ignored under both `./<path>` and the -p form below.
# Installing this file without also changing settings.json leaves the
# code-execution path open.
# This hook is registered in SEVEN settings.json entries: PreCompact (manual, auto)
# and SessionStart (startup, resume, clear, compact, fork). All seven were moved to
# the full form above and INSTALLED on 2026-09-01; changing only one entry silently
# leaves six on the old form.
# settings.json must call this as:
#   /bin/bash --noprofile --norc -p <path-to-this-file> <matcher>
# FLAG ORDER MATTERS on this bash 3.2: `-p` must come AFTER the GNU long
# options. `/bin/bash -p --noprofile ...` is rc 2 plus a usage dump to the
# inherited stderr BEFORE this file runs (reproduced round 14) — a launcher
# footgun that violates contract 1 (rc 2) and the zero-stderr promise by
# itself (stdout stays clean; contract 2 is not the one it breaks).
# The shebang on line 1 ALSO carries -p, because a settings.json entry that names
# the script by path executes it through that shebang instead, and a plain
# `#!/bin/bash` there would undo the whole defence. Verified 2026-08-30: with
# `#!/bin/bash` a BASH_ENV payload RAN; with `#!/bin/bash -p` it did not.
# `-p` is load-bearing, not tidiness: without it a non-interactive bash sources
# $BASH_ENV before line 1 of this script and imports exported shell functions,
# which is the same arbitrary-code-execution shape as the python3 defect below.
# Verified 2026-08-29: BASH_ENV ran under `bash`, was ignored under `bash -p`.
#
# READ THE RESULTS WITH:
#   /usr/bin/python3 -I -S -c '
#   import json,os
#   d=os.path.expanduser("~/.claude/session-state/observed")
#   for n in sorted(os.listdir(d)):
#     if not n.endswith(".json"): continue
#     try: r=json.loads(open(os.path.join(d,n)).read())
#     except Exception: print((n,"UNREADABLE")); continue
#     p={}
#     if r.get("saw_eof") and not r.get("truncated"):
#       try: p=json.loads(r.get("raw") or "")
#       except Exception: p={}
#     if not isinstance(p,dict): p={}
#     print((n.split(".")[-2],p.get("hook_event_name"),p.get("session_id"),
#            repr(p.get("cwd")),r.get("registered_matcher")))'
# The legacy ~/.claude/session-state/observed.jsonl (20 records, 4 of them
# synthetic from broken test harnesses of mine) is NOT migrated and NOT deleted.

# BOTH stdout and stderr are closed before anything else runs. stdout is
# contract 1. stderr is round 11 + round 12, one lesson in two halves:
#   round 11: a synchronous foreground `printf >&2` onto an already-full
#     65536-byte pipe blocked this hook indefinitely, and bash defers traps
#     while a foreground write is in progress, so TERM did not help.
#   round 12: the fix — a BACKGROUNDED write with a kill budget (emit) — was
#     itself broken on the signal path: TERM during the poll made the parent
#     exit 0 while the blocked writer was reparented to PID 1 STILL HOLDING
#     the stderr pipe, so a caller draining stderr to EOF hung instead.
#     Reproduced 5/5 by the round-12 reviewer and again by me.
# Both reviewers converged on the same prescription: there is no safe way to
# write to an arbitrary inherited fd 2 under a hard time bound, so do not
# write to it at all. Diagnostics live in the .error.txt files the worker
# writes; when those cannot be written the message is LOST, which the
# contract prices as cheap. A hung or hanging-on caller is the expensive case.
# `exec` here CANNOT take the `builtin` prefix: bash persists exec's
# redirections only when `exec` is the command word itself — under `builtin
# exec >...` the redirection is temporary to the builtin invocation and fd
# state reverts (reproduced in v16 verification: fd 3 was gone one line
# later and stderr leaked). Redirection-only exec stays bare; the exported-
# function exposure of the NAME exec under a non -p invocation is the same
# launcher-owned residue as export -f builtin, listed above.
# ROUND 17 (sol): install a no-output terminating-signal trap BEFORE the very
# first executable command. The early exit-0 trap at line 181 is the first
# executable command; the redirect at line 183 follows it.
# a catchable terminating signal (TERM/INT/...) arriving in the microsecond
# window between the redirect and the full trap took DEFAULT disposition and
# exited 143 (contract 1 violation, reproduced rc 143 on bash 3.2). This early
# trap makes `builtin exit 0` the disposition from the first command onward;
# it omits the job-cleanup kill because no worker exists yet. The only window
# left is BEFORE bash runs its first command, which is launcher/process-
# lifecycle territory, not in-file fixable. The full trap below supersedes it
# once the worker can exist (adds ERR + the background-job kill).
# ROUND 18 (sol): both traps cover EVERY catchable default-terminating
# signal on Darwin, not just TERM/INT — an untrapped USR1/ALRM/XCPU/etc.
# took its default disposition and exited nonzero (rc 158 from USR1,
# reproduced), violating contract 1. KILL and STOP cannot be trapped and
# stay launcher-owned. Fault signals (SEGV/BUS/...) are near-unreachable for
# a small script but are trapped too so no reachable signal path exits nonzero.
# ROUND 19 (sol): TSTP/TTIN/TTOU default to SUSPEND, not terminate. In a
# non-orphaned process group (a hook spawned by a live parent in the same
# session -- the normal launch shape) an untrapped TSTP left the parent
# stopped indefinitely (reproduced via waitpid WUNTRACED), violating
# contract 3. ROUND 20 (sol+grok independently): trapping them to `exit 0`
# (the v20 fix) only covers PID-directed delivery. A trapped signal resets
# to SIG_DFL in children; only an IGNORED one is inherited. So killpg TSTP
# stopped the foreground /bin/sleep and the worker, bash deferred the
# trapped handler until the stopped-forever foreground child returned, and
# the hook blocked indefinitely (reproduced 4/4 timings). `trap ''` is the
# correct disposition: the parent cannot be suspended AND every child
# inherits SIG_IGN, covering both delivery shapes. In an orphaned group
# the kernel discards these anyway; inherited-ignored cannot be re-trapped
# but also cannot suspend. KILL and STOP remain untrappable/launcher-owned.
# ROUND 21 (sol): line 182's `trap ''` only takes effect once it RUNS. Between
# this early exit-0 trap (the FIRST executable line) and line 182, TSTP/TTIN/TTOU
# briefly sit at default-SUSPEND -- an in-file window, distinct from the
# launcher-owned pre-first-line window both reviewers accept as unfixable here.
# A TSTP delivered in that window (PID- or group-directed) suspended the process
# (reproduced STOPPED via a pure-builtin busy-wait; an earlier /bin/sleep marker
# gave a false BLOCKED by itself becoming a killable foreground child). Fix:
# include TSTP/TTIN/TTOU in THIS exit-0 trap too, so the gap is covered; line 182
# then upgrades them to inherited-SIG_IGN for the worker. No foreground child
# exists in the gap, so exit-0 here cannot defer -- the round-20 deferral needs a
# stopped foreground child, and none is spawned until after line 182.
builtin trap 'builtin exit 0' HUP INT QUIT ILL TRAP ABRT EMT FPE BUS SEGV SYS PIPE ALRM TERM XCPU XFSZ VTALRM PROF USR1 USR2 TSTP TTIN TTOU
builtin trap '' TSTP TTIN TTOU
exec >/dev/null 2>/dev/null

# ROUND 26 (sol finding, reproduced 2026-09-01): under the plain (non--p)
# invocation a BASH_ENV file can set IFS=":" and the trap's unquoted
# $(jobs -pr) expansion then joins two newline-separated pids into ONE word,
# so neither job is killed (measured: alive=2 plain vs alive=0 under -p).
# The -p invocation never reads BASH_ENV; this assignment makes the plain
# form carry the same invariant instead of inheriting it from the flag.
# Pure assignment: no command, no fork, cannot fail, runs before any
# expansion in this file that splits words.
IFS=$' \t\n'
# The trap KILLS any background job before exiting (round 12): with a worker
# still in the job table, a bare `exit 0` on TERM abandoned it holding the
# stdin pipe. `jobs -pr` is a builtin; an empty list makes kill fail, which
# `|| true` absorbs so the ERR trap cannot re-enter this handler. XFSZ is
# included because a write past RLIMIT_FSIZE on a regular fd delivers SIGXFSZ
# and killed the round-12 parent with exit 153 — with fd 1/2 on /dev/null the
# trigger is gone, but the trap converts any residual delivery into exit 0.
# `builtin` is round-13/14 defence in depth: under a non -p invocation bash
# imports exported shell functions, and an exported kill() that does not
# signal was shown to win over the builtin — the round-12 orphan, back via
# the trap. Round 14 proved the SAME dispatch bites `jobs`: an exported
# jobs() printing nothing made this kill a no-op (and blinded the watchdog
# below). Round 15 went further: bare `:`, `[` and `|| true` in the watchdog
# were STILL function-dispatched (an exported : hung the hook past its
# deadline, reproduced), so v16 swept builtin names file-wide — and round 16
# caught the name that sweep still missed: bare `break` in the watchdog
# (an exported break() looped the parent forever / exited it rc 1,
# reproduced), so v17 prefixes `break` too. The sweep target is every bash
# builtin in command position, with redirection-only `exec` as the sole
# documented exception (see the exec comment below). That prefix is BEST-EFFORT ONLY: `builtin` is itself a builtin
# NAME, and `export -f builtin` defeats every prefixed site at once
# (round 15, reproduced — rc 41 from an exported builtin()). There is no
# in-file spelling that survives that; only the -p invocation does. The
# prefix narrows the exported-function surface, it does not close it.
builtin trap 'builtin kill -KILL $(builtin jobs -pr) 2>/dev/null || builtin true; builtin exit 0' ERR HUP INT QUIT ILL TRAP ABRT EMT FPE BUS SEGV SYS PIPE ALRM TERM XCPU XFSZ VTALRM PROF USR1 USR2
builtin trap '' TSTP TTIN TTOU
builtin umask 077

LOG_DIR="${HOME}/.claude/session-state/observed"
MAX_BYTES=5242880               # advisory: ~5 MB across the whole directory
MAX_FILES=2000                  # advisory: a killed worker can leave a 0-byte
                                # file, which adds 0 bytes but 1 inode forever
MAX_INPUT=65536                 # a hook event is a few KB; 1 MB was absurd
DEADLINE=2                      # seconds of wall clock for the worker

# /usr/bin/python3 IS NOT AN INTERPRETER. On macOS it is the xcrun dispatcher —
# verified 2026-08-31: /usr/bin/python3, /usr/bin/git and /usr/bin/clang are all
# the SAME inode, and DEVELOPER_DIR redirects which real tool it runs. Pinning it
# pinned a dispatcher, not a binary, so the environment still chose the code. The
# real interpreter it dispatches to is listed first below, and the variables that
# steer the dispatcher are removed from the environment before anything runs.
builtin unset DEVELOPER_DIR SDKROOT TOOLCHAINS XCODE_DEVELOPER_DIR_PATH
# The CLT python3 pinned below is NOT a SIP platform binary (codesign flags=0x0,
# no hardened runtime), so unlike /bin/bash and /usr/bin/python3 dyld does NOT
# strip DYLD_* for it, and -I -S -B does not block dylib injection. Today the
# launcher is a SIP /bin/bash whose environment already had these removed, so
# this is latent — which is exactly what the shebang defect looked like before
# settings.json turned out to bypass it. Closing it here does not depend on how
# this file is invoked.
# The WHOLE namespace, not a name list (round 12): a seven-name unset left
# DYLD_VERSIONED_LIBRARY_PATH, DYLD_OVERLAY_PATH and DYLD_PRINT_TO_FILE alive,
# and DYLD_PRINT_TO_FILE makes dyld APPEND its log onto a caller-chosen
# existing file — in-place corruption, which contract 2 exists to prevent.
# ${!DYLD_@} enumerates every DYLD_-prefixed variable bash can see, so a dyld
# version that grows a new variable is covered without editing this file.
for _v in ${!DYLD_@}; do builtin unset "$_v"; done
builtin unset _v
builtin export OBS_DIR="$LOG_DIR" OBS_MAX="$MAX_BYTES" OBS_MAXFILES="$MAX_FILES" \
       OBS_MAXIN="$MAX_INPUT" OBS_MATCHER="${1:-unset}"

# OBS_CODE MUST be cleared first. If the heredoc redirection below fails — bash
# stages a here-document in a temporary file — the `read` builtin never runs, the
# `|| true` swallows the failure, and an INHERITED OBS_CODE from the environment
# survives into `python3 -c` at the bottom of this file. Reproduced 2026-08-29
# with a failing redirection: OBS_CODE kept its attacker-supplied value and rc
# was 0. The sentinel check after the heredoc is the second half of that fix.
builtin unset OBS_CODE

# NO HERE-DOCUMENT. bash 3.2 stages a here-doc by creating /tmp/sh-thd-*,
# reopening it BY PATHNAME and then unlinking that pathname — the same
# open-then-unlink-a-name-you-no-longer-own class that was removed from the write
# path in v7, except here it is bash doing it, in the parent, before the watchdog
# exists. A single-quoted assignment needs no temporary file at all. The worker
# body below therefore contains NO apostrophe; `bash -n` catches it if one
# returns.
OBS_CODE='#OBSERVE-WORKER-V9
import sys
# Belt and braces behind `-I`: nothing on sys.path may be the cwd. Claude Code
# runs hooks in the PROJECT directory, and a project file named json.py / re.py /
# fcntl.py executed arbitrary code inside the previous version of this hook on
# every session start (reproduced 2026-08-29). `import sys` is builtin and cannot
# be shadowed, so this runs before any other import.
sys.path[:] = [p for p in sys.path if p not in ("", ".")]
import json, os, select, stat, time

# Round 13/14: the launcher may leak descriptors above 2 that are not
# CLOEXEC, and an abandoned worker wedged in a filesystem syscall would keep
# holding them — including a pipe some caller is draining to EOF. Everything
# this worker needs is fd 0 (stdin), 1 and 2 (/dev/null); drop the rest
# first. Round 14: a fixed 4096 ceiling left a leaked fd 5000 OPEN.
# Round 15 killed SC_OPEN_MAX as the ceiling both ways (reproduced): it is
# the CURRENT soft limit, so under `ulimit -n unlimited` Darwin returns
# LONG_MAX and closerange raises OverflowError (every event silently lost),
# and after a launcher LOWERS the limit an fd opened under the old high
# limit sits ABOVE the new ceiling and survives. Ground truth is the
# kernel: /dev/fd lists the fds this process actually holds, so close that
# snapshot. closerange with a clamped ceiling remains only as the fallback
# when /dev/fd itself cannot be read, and is wrapped so no value it is
# handed can crash the worker. Neither covers the bash probe window before
# exec, which is documented at the launch site.
_fds = None
try:
    _fds = sorted(int(_n) for _n in os.listdir("/dev/fd"))
except (OSError, ValueError):
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
    except (ValueError, OSError, AttributeError):
        _hi = 4096
    if not isinstance(_hi, int) or _hi < 64 or _hi > 1048576:
        _hi = 1048576 if (isinstance(_hi, int) and _hi > 1048576) else 4096
    try:
        os.closerange(3, _hi)
    except (OverflowError, OSError, ValueError):
        pass

MAXIN = int(os.environ["OBS_MAXIN"])
BUDGET = 1.0
DIAG = []

# Bounded HERE, before anything can put it in a message. v6 sanitised the matcher
# for the record but interpolated the RAW environment value into the "empty stdin"
# diagnostic, so a 100,000-character matcher produced a 100KB diagnostic file —
# a sequential path straight past MAX_BYTES with no concurrency involved.
ALLOWED = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
matcher = "".join(c if c in ALLOWED else "_"
                  for c in os.environ.get("OBS_MATCHER", "unset"))[:64] or "unset"

def note(m):
    DIAG.append(m)

# Diagnostics go to a FILE, never to stderr. The worker can outlive this parent
# (see the watchdog), and a stderr it still holds is the Claude Code capture pipe —
# a reader waiting for EOF on that pipe would wait for the abandoned worker,
# defeating the whole point of abandoning it.
def flush_diag(stem):
    """True only if the WHOLE diagnostic reached disk. v5 swallowed EROFS /
    ENOSPC / EACCES here and still exited 0, so a read-only observed/ produced
    no record, no message and success (reproduced by the reviewer)."""
    if not DIAG:
        return True
    body = ("\n".join("observe-compaction: " + m for m in DIAG)
            + "\n").encode("utf-8", "backslashreplace")
    try:
        fd = os.open(stem + ".error.txt",
                     os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    except OSError:
        return False
    # The event fd got its guarded close in v11 and THIS one did not — the same
    # defect, one call site away. Reproduced 2026-08-31 with an injected EIO on
    # the diagnostic close: the queued `return True` was discarded, the OSError
    # escaped flush_diag, CPython exited 1, and the parent announced "event NOT
    # recorded" while BOTH the truncated .complete.json and the .error.txt sat
    # on disk. A close that fails means the diagnostic did not land, so it must
    # return False, not raise.
    ok = False
    try:
        ok = os.write(fd, body) == len(body)
    except OSError:
        ok = False
    finally:
        try:
            os.close(fd)
        except OSError:
            ok = False
    return ok

STEM = [None]

def die(m, code=0):
    """Diagnostic goes to a file. If it cannot, exit nonzero anyway: since v13
    the parent reaps the code silently (stderr is closed), but the code is kept
    as a machine-readable status for tests and any future phase that reads it."""
    note(m)
    if STEM[0] and flush_diag(STEM[0]):
        sys.exit(code)
    # The diagnostic did NOT reach disk. Code 16 implies a .error.txt exists to
    # be read later; using it here would point at a file that does not exist.
    # 15 is the code that already means "event state unknown, diagnostic did not
    # reach disk" — it deliberately asserts nothing about the file existing.
    if code == 16:
        sys.exit(15)
    sys.exit(code or 13)

def die_nofile(code):
    """Refuse WITHOUT touching the directory. A cap refusal that writes an
    .error.txt raises the very count it is enforcing: the v5 MAX_FILES=2 run
    left four files, the diagnostics reading "at 2 files" then "at 3 files", and
    every later event added another. Sequential unbounded growth, inside the
    cap that exists to prevent it. The code names the refusal; no file traces it."""
    sys.exit(code)

# Read BYTES (os.read), never sys.stdin.read(N) — that bounds CHARACTERS, so one
# emoji counted as 1 against the cap while costing 4 bytes. Keep draining after
# the cap: stopping early gives the PRODUCER (Claude Code) EPIPE, and the
# installed binary turns EPIPE during hook input delivery into hook status 1.
raw = bytearray()
truncated = False
saw_eof = False
timed_out = False
read_error = ""
t0 = time.monotonic()
while True:
    left = BUDGET - (time.monotonic() - t0)
    if left <= 0:
        timed_out = True
        break
    try:
        r, _, _ = select.select([0], [], [], left)
    except OSError as e:
        read_error = "select %s" % e.errno
        break
    if not r:
        timed_out = True
        break
    try:
        chunk = os.read(0, 65536)
    except OSError as e:
        read_error = "read %s" % e.errno
        break
    if not chunk:
        saw_eof = True            # the ONLY place completeness may be claimed
        break
    room = MAXIN - len(raw)
    if room > 0:
        raw.extend(chunk[:room])
    if len(chunk) > room:
        truncated = True          # exact: os.read does not over-read like head(1)

# Close stdin BEFORE any filesystem call. After this the watchdog can kill us
# without the producer ever seeing EPIPE.
try:
    os.close(0)
except OSError:
    pass

# The directory and the stem must exist BEFORE the first die(), or its diagnostic
# has nowhere to go: worker stderr is /dev/null, so the v5 first draft dropped the
# "empty stdin" message entirely — silently. Reproduced 2026-08-29 (U7: zero
# files, zero diagnostics, rc 0).
d = os.environ["OBS_DIR"]
try:
    os.makedirs(d, 0o700)
except FileExistsError:
    pass
except OSError:
    die_nofile(10)

# ADVISORY caps (contract clause 3), checked HERE — before STEM exists, so no
# refusal path can add a file to the directory it is capping. Bytes alone are not
# enough: a worker killed between O_EXCL create and its first write leaves a
# ZERO-byte file, which adds no bytes and can repeat forever, so inodes are
# capped too. The reserve is 2: one event file plus one possible .error.txt, the
# most any single run can create. Neither bound is hard under concurrency: this is a check-then-act.
# The reserve covers the record plus one possible .error.txt, so the precise size
# is not needed yet and the check can run this early.
total = 0
count = 0
try:
    for e in os.scandir(d):
        count += 1
        try:
            total += e.stat().st_size
        except OSError:
            pass
except OSError:
    die_nofile(14)
if count + 2 > int(os.environ["OBS_MAXFILES"]):
    die_nofile(11)
# 6x, not 1x. ensure_ascii escapes one NUL byte to the six characters \u0000, so
# 65,536 NULs serialise to a 393,331-byte record — v6 reserved 66,560 and would
# have sailed past MAX_BYTES sequentially. Measured on this exact serialiser.
if total + 6 * MAXIN + 8192 > int(os.environ["OBS_MAX"]):
    die_nofile(12)

STEM[0] = os.path.join(d, "%d-%d" % (time.time_ns(), os.getpid()))

# Order matters: a read that produced nothing is not an empty event when it timed
# out or errored, and reporting it as one hides a hung producer behind a routine
# message.
if not raw:
    if timed_out:
        die("stdin still open with no data after the read budget — event NOT recorded")
    if read_error:
        die("stdin %s before any data — event NOT recorded" % read_error)
    die("empty stdin for matcher %s — event NOT recorded" % matcher)

try:
    txt = raw.decode("utf-8")
except UnicodeDecodeError:
    txt = raw.decode("utf-8", "backslashreplace")
txt = txt.rstrip("\r\n")

# The payload is NEVER json.loads-ed here. Parsing it would turn NaN / Infinity /
# 1e999 in the input into bare NaN / Infinity in our OUTPUT, which strict parsers
# reject (reproduced). `raw` stays a string; allow_nan=False guards the wrapper.
rec = json.dumps({
    "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "registered_matcher": matcher,
    "truncated": truncated,
    "saw_eof": saw_eof,
    "raw": txt,
}, ensure_ascii=True, allow_nan=False) + "\n"
data = rec.encode("utf-8")

stem = STEM[0]

# WRITE STRAIGHT TO THE FINAL NAME. v6 wrote a .part and published with
# link + unlink, but that unlink resolves a PATHNAME: another same-UID writer can
# remove our .part and create its own file at that name in the window between the
# link and the unlink, and we then delete THEIR data. O_EXCL cannot protect a
# later path lookup. The hook now never unlinks anything, so contract clause 2 is
# literal rather than nearly true.
#
# The cost, stated plainly: a worker killed mid-write leaves a TRUNCATED final
# file instead of an ignorable .part. That is survivable — the record ends with
# "}\n", so a short write is not parseable JSON and the reader reports it
# UNREADABLE — whereas deleting another writer file is not survivable.
if not saw_eof:
    suffix = ".partial.json"      # EOF never observed: NOT a whole event
elif truncated:
    suffix = ".truncated.json"
else:
    suffix = ".complete.json"
final = stem + suffix
flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
if hasattr(os, "O_CLOEXEC"):
    flags |= os.O_CLOEXEC
try:
    fd = os.open(final, flags, 0o600)
except OSError as e:
    die("cannot create event file — event NOT recorded (%s)" % e.errno)
# wrote_ok carries the short-write fact PAST this block. v10 only note()d it,
# and note() alone reaches exit 0 whenever flush_diag succeeds: nothing then
# recorded that a file named .complete.json held a truncated record. Measured
# on v10 under ulimit -f 1: a 1024-byte .complete.json that raises
# JSONDecodeError. The suffix is chosen before the write and the no-unlink
# rule forbids renaming afterwards, so the durable remedy is the SHORT WRITE
# line note() puts into the .error.txt. Exit 17 remains as a machine-readable
# status for the parent, which reaps it silently since v13.
wrote_ok = True
try:
    st = os.fstat(fd)
    if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
        # 16, not 15: v8 reused 15 here, whose parent message asserts the
        # diagnostic could not be written — false whenever it WAS written. 16
        # says only that the file was refused. st_nlink can also be 0 (another
        # writer removed the name), so this does not claim a husk remains.
        die("event file was not freshly created (nlink=%d) — not written"
            % st.st_nlink, 16)
    w = os.write(fd, data)
    if w != len(data):
        wrote_ok = False
        note("SHORT WRITE %d of %d — the file is truncated and will not parse"
             % (w, len(data)))
except OSError as e:
    # ENOSPC, EFBIG, EIO and friends. v10 let these escape the worker entirely:
    # an uncaught OSError exits CPython 1, so the parent said "worker exited 1 —
    # event NOT recorded" while a .complete.json sat on disk holding a partial
    # record. Same lie as the short write, reached by a different route.
    wrote_ok = False
    note("WRITE FAILED errno %s — the file is truncated and will not parse"
         % e.errno)
finally:
    # v11 swallowed this and in the same motion HID the failure: NFS and FUSE
    # report a deferred write error on close, not on write, so os.write could
    # return the full count, close could fail, wrote_ok stayed True and the
    # parent said nothing about a file named .complete.json. Reproduced
    # 2026-08-31 with an injected EIO: worker exit 0, no diagnostic, no stderr.
    # It still must not raise — that was the v11 lesson — so it clears the flag.
    try:
        os.close(fd)
    except OSError as e:
        wrote_ok = False
        note("CLOSE FAILED errno %s — the file may not have reached disk"
             % e.errno)

if timed_out:
    note("stdin still open at the read budget — record is .partial")
if read_error:
    note("stdin %s — record is .partial" % read_error)
# v6 threw this Boolean away, so a diagnostic that could not be written after a
# SHORT WRITE reached exit 0 and the parent said nothing at all. Code 15 is
# deliberately NOT 13: by this point an event file exists, so "event NOT
# recorded" would be a lie.
if not flush_diag(stem):
    sys.exit(15)
# Order matters: 15 (no diagnostic at all) outranks 17 (diagnostic written, file
# truncated), because 15 is the case where the .error.txt cannot be read later.
if not wrote_ok:
    sys.exit(17)
'

# Second half of the D13 fix: prove the heredoc actually produced OUR code before
# handing it to an interpreter. An inherited or truncated OBS_CODE fails here.
case "$OBS_CODE" in
  "#OBSERVE-WORKER-V9"*) builtin : ;;
  *) # v29: was silent by design — stderr is closed and no worker ran, so there is
     # no .error.txt either. The event is still lost (cheap); the breadcrumb below
     # is the only trace that it was THIS path and not the probe path.
     builtin set -C
     builtin printf '%s\n' "drop=OBS_CODE_MARKER_MISMATCH pid=$$ secs=$SECONDS" \
       > "$LOG_DIR/$$.dropped.txt" 2>/dev/null || builtin true
     builtin exit 0 ;;
esac

# `exec 3<&0` + `<&3` is LOAD-BEARING. bash redirects a background job's stdin
# from /dev/null when job control is off, which it is in a hook — without this the
# worker reads ZERO bytes and reports success on a perfectly normal event.
# Reproduced twice on 2026-08-29, once in my own draft and once in a reviewer's.
# stderr goes to /dev/null for the reason given at flush_diag() above.
exec 3<&0
# The parent drops its OWN stdin now: fd 3 already holds the caller's event for
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
# The C3 bound still holds: the probe phase is < 1s (SECONDS+1) and the worker
# watchdog is a SEPARATE fresh DEADLINE=2 AFTER it, so the hook is bounded by
# their sum (~3s worst case), not by a single DEADLINE=2 shared with the worker.
_chosen=""
_pdrop=""                 # v29 breadcrumb: per-candidate probe outcome, pure assignments
_pend=$(( SECONDS + 1 ))
for _p in /Library/Developer/CommandLineTools/usr/bin/python3 \
          /usr/bin/python3; do
  # Budget already spent by an earlier candidate: do not even spawn (the wedged
  # first-candidate host prices as event loss, round 26).
  if builtin [ "$SECONDS" -ge "$_pend" ]; then _pdrop="$_pdrop [$_p=budget-spent-before-spawn]"; builtin break; fi
  # `( stat && exec python )` -- see (a)/(b) above. `</dev/null` so the probe
  # cannot eat event bytes; `3<&-` so an abandoned probe cannot hold the caller's
  # fd-3 event dup during python startup (before the body's own closerange runs);
  # stdout/stderr to /dev/null. Probe body is byte-identical to v26: it closes
  # inherited fds >2 then exits 37 on python >= 3.7 (a 3.6 that would die on
  # time.time_ns at every event is version-gated OUT here), 0 otherwise; an
  # ENOEXEC/corrupt candidate exits != 37 and is skipped.
  (
    if builtin [ -x "$_p" ] && builtin [ -f "$_p" ]; then
      builtin exec "$_p" -I -S -B -c 'import os, sys
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
sys.exit(37 if sys.version_info >= (3, 7) else 0)'
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
  _pdrop="$_pdrop [$_p=rc$_prc,killed=$_pkilled]"
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
if builtin [ -z "$wid" ]; then
  # v29 breadcrumb (see header): record WHY each candidate failed, plus the
  # SECONDS/budget pair, so this path is distinguishable from the OBS_CODE one.
  builtin set -C
  builtin printf '%s\n' "drop=NO_INTERPRETER pid=$$ secs=$SECONDS pend=$_pend probes:$_pdrop" \
    > "$LOG_DIR/$$.dropped.txt" 2>/dev/null || builtin true
  builtin exit 0
fi

# Poll with a BUILTIN, never by forking /bin/ps. A synchronous ps runs BEFORE the
# shell can look at its own deadline, and Apple ps retries a failing process-table
# sysctl for ~1000s, so the watchdog could outlast the thing it bounds. `jobs -pr`
# reads bash memory: it cannot block, cannot fail open, and needs no fork.
# Verified 2026-08-31 in a non-interactive script with job control off: a live
# child is listed, a completed one is NOT, and `wait` on the completed one
# returned its saved status (7) in 0s — so the exit-code channel survives.
#
# A worker wedged in an uninterruptible syscall is still "running", so it stays
# listed, we reach the deadline, and we kill and abandon it. That is the intent.
#
# NO EXTERNAL COMMAND HERE. v9 wrote `jobs -pr | grep -q`, and `grep` resolves
# through the INHERITED PATH. Measured 2026-08-31: with PATH=/nonexistent, grep
# exited 127, `!` inverted that into the "worker finished" branch on the FIRST
# iteration, and the parent fell into an unbounded `wait` — a worker forced to
# outlive DEADLINE=2 held the hook for its full 10s, and the deadline never
# fired. A wedged worker would have wedged the hook forever, silently: stdout
# stayed empty and the exit stayed 0, so nothing else would have flagged it.
# `jobs`, `wait` and `kill` are all bash BUILTINS — but round 14 proved a
# builtin NAME is still FUNCTION-dispatched first under a non -p invocation:
# an exported jobs() printing nothing blinded this loop (the deadline kill
# was never reached) and an exported kill() swallowed the deadline signal,
# orphaning the worker with Claude stdin. All three are `builtin`-forced
# below; PATH was never the only dispatch channel. The case below reproduces
# grep's anchoring: the newline guards make a pid that is a substring of a live
# pid (2923 vs 29235) fail to match, which `^...$` was there to guarantee.
end=$(( SECONDS + DEADLINE ))
while builtin :; do
  running=$(builtin jobs -pr)
  case "
$running
" in
    *"
$wid
"*) builtin : ;;             # still running — fall through to the deadline check
    *)
    # Gone from the job table means bash already reaped it and holds its
    # status, so this wait returns immediately. The status is REAPED AND
    # DISCARDED: stderr is closed (see the top of this file), so the parent
    # has nowhere to put a message and deliberately says nothing. The worker
    # exit codes still exist (10-17 documented at the worker, 18 = no
    # interpreter) and every one that can leave a durable trace already wrote
    # a .error.txt before exiting; codes 13, 15 and 18 are the ones that
    # cannot, and those events are silently lost — priced cheap by contract.
    builtin wait "$wid" 2>/dev/null || builtin true
    builtin break
    ;;
  esac
  if builtin [ "$SECONDS" -ge "$end" ]; then
    # Abandon without wait: a worker wedged in an uninterruptible syscall
    # cannot complete SIGKILL, and a wait here would hang the parent on it.
    # The event file, if one was opened, may be left truncated; the reader
    # reports such a file as UNREADABLE.
    builtin kill -KILL "$wid" 2>/dev/null || builtin true
    builtin break
  fi
  # `|| true` IS LOAD-BEARING. The trap at the top of this file catches ERR, and
  # with no `set -e` a BARE failing command still fires it: a /bin/sleep that
  # ever returned non-zero would run `exit 0` here and abandon a live worker
  # without reaching the deadline kill. Verified 2026-08-31: bare fails, guarded
  # continues. Every other command in this loop is already inside if/case/||.
  /bin/sleep 0.05 || builtin true
done
builtin exit 0

