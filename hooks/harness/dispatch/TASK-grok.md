# TASK — break the hook in a way the harness does not test

Read COMMON-CONTEXT.md first. Do NOT review the harness's code quality. Your job
is adversarial: find an input, environment, or timing that makes hook.sh violate
C1, C2, C3 or C4, and that is NOT already covered by the 50 cases in
harness/contract.py.

Read the case table in harness/contract.py first so you do not duplicate it. The
covered ground is: input shapes (empty/oversize/binary/NUL/non-JSON/argv flood/
argv metacharacters/deep nesting), environment hostility (BASH_ENV, ENV,
SHELLOPTS+BASH_XTRACEFD, PS4, empty PATH, hostile python3 stub on PATH, HOME
unset/missing, IFS, locale, CDPATH/GLOBIGNORE, PYTHONPATH/PYTHONSTARTUP,
observed/ being a file, observed/ unwritable, bad TMPDIR), stdin liveness
(never-EOF, slow drip, /dev/zero), and signals (11 terminating signals PID-
directed, 4 group-directed, and TSTP/TTIN/TTOU both shapes).

Angles that are deliberately NOT covered yet — start here, but do not stop here:
 - resource limits: ulimit -n very low, -u process cap, -f file size, -v memory
 - the filesystem underneath: observed/ on a full disk, a path component that is
   a symlink, a directory the hook expects being replaced mid-run
 - the python3 interpreter probe: what if python3 exists, passes the probe, then
   behaves badly? what if it is a shell script, a broken symlink, hangs?
 - concurrency: several copies of the hook racing on the same observed/ dir
 - the invocation itself: wrong flag order, missing matcher, a matcher that is a
   long string, being started with fd 0/1/2 already closed
 - clock and locale: time going backwards, TZ garbage

For each candidate, actually RUN it against hook.sh and report what happened.
A hypothesis you did not execute is worth nothing here — say [unverified] if you
could not run it, and do not present it as a finding.

Report: location (file:line if in-file) + mechanism + a concrete reproduction
command + the contract clause broken. Rank by severity.

End with exactly one line:
VERDICT: NO-NEW-VIOLATION
or
VERDICT: VIOLATION-FOUND
