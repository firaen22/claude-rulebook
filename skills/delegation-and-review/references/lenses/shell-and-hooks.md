# Lens: shell scripts and hooks

For bash/sh scripts, and anything the harness EXECUTES rather than imports (hooks,
gates, wrappers, cron bodies). A hook fails differently from a program: it runs
unattended, its failure mode is often silence, and some hooks can block the session.

Report each hit as location + the exact invocation that misbehaves + the fix. Where
a claim is about a specific tool's behavior, RUN that tool — do not reason about it.

- **Fail posture by hook CLASS — name the class before judging any exit path.**
  Observability/context hooks (PreCompact, SessionStart loggers) fail OPEN: exit 0 on
  every internal error, because a bug there must never freeze the session. Policy
  gates (PreToolUse: destructive-action, credential, authorization) split on a finer
  question: **did the gate actually EVALUATE?** "Could not evaluate" — missing
  interpreter, unparseable envelope, empty stdin — must fail CLOSED or fall back to a
  coarse raw scan that blocks a clear match. An internal error AFTER a definite
  non-match may fail open. Report any gate that exits 0 without evaluating and
  without a backstop, and any observability hook that can block. Do not cite one
  class's rule against the other class. (Both live postures verified 2026-08-29.)
- **stdout is not free.** Where stdout enters the session context (SessionStart) or
  is harness-parsed, a stray `echo`, banner, or debug print IS payload — stderr only.
- **Unbounded reads, and SILENT bounds.** A bare `cat`/`$(<&0)` on stdin can hang or
  OOM, so bound it — but a bare `head -c N` truncates a legitimate large payload into
  malformed input that the next stage parses as garbage. A bound must be detectable:
  signal the overflow, or record that truncation occurred.
- **Non-regular inputs.** A path can be a FIFO, directory, symlink, socket, or
  `/dev/*`. `[ -r "$f" ]` is true for all of them. **Verify the consuming tool's
  actual behavior by running it** — do not assert a hang. (Measured 2026-08-29: two
  reviewers independently claimed Apple gzip hangs on a FIFO; it exits 1,
  `not a regular file`, under 2s. Both were wrong and both ranked it #1.)
- **Unquoted expansions and `set -e` gaps.** `$var` unquoted splits on spaces;
  `set -e` does not fire inside `if`, `&&`, pipelines, or command substitution.
- **Shell operand boundaries.** Feed a pathname containing a space, a glob character,
  a newline, and a leading dash. If the command word-splits it, expands the glob, or
  parses it as an option, report the exact invocation; the fix is quoting or a `--`
  boundary. Same probe for argv, env, and parsed-JSON values reaching a command.
- **Traps and cleanup.** Exercise the success, failure, and interrupt paths
  separately. A trap must remove this run's own temporaries on ALL of them, and must
  never remove a deliverable the success path is supposed to leave behind, or
  anything this run did not create. Report which of the three paths you exercised.
