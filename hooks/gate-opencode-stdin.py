#!/usr/bin/env python3
"""Claude Code PreToolUse hook (matcher: Bash): block `opencode run` unless its
stdin is closed or supplied.

Why it exists: `opencode run` (v2.0.21 and v2.0.22, reproduced 2026-10-05) reads
stdin until EOF whenever stdin is not a TTY. The Bash tool's stdin is an open
socket that never sends EOF, so the run prints 0 bytes until `timeout` kills it
(rc 124). That looked like "opencode hangs on NIM" for two days. Fix: append
`</dev/null`. See ~/.claude/memory/reference_nim_via_opencode.md.

Behavior:
- Tokenizes with shlex (punctuation_chars); quoted text stays one token, so a
  mention inside a string (commit message, grep pattern) is not a call.
- Finds `opencode run` at command position: after a separator, skipping
  VAR=value assignments and the wrappers timeout/gtimeout (with its options and
  duration), env, command, nohup, time, nice, exec.
- Allowed when: the call is piped into (`... | opencode run`), or ANY stdin
  redirect token (`<`, `<<`, `<<<`) appears after it in the command — this also
  covers `(cd x && opencode run ...) </dev/null`. Coarse on purpose: a later,
  unrelated `<` lets a call through (false negative, accepted).
- Override: `OPENCODE_STDIN_OK=1` anywhere in the command (e.g. to reproduce
  the hang on purpose).
- Fails OPEN on any parse or envelope error: this is a convenience gate against
  a 4-minute silent hang, not a security boundary.

Known limits: `bash -c "..."`, `eval`, scripts, aliases and functions are not
inspected. dispatch.py and bench harnesses already pass stdin=DEVNULL.
"""

import json
import os
import shlex
import sys

SEPARATORS = {";", "&", "&&", "|", "||", "(", ")", "{", "}", "!"}
SIMPLE_WRAPPERS = {"env", "command", "nohup", "time", "nice", "exec"}
TIMEOUTS = {"timeout", "gtimeout"}
STDIN_REDIRECTS = {"<", "<<", "<<<", "<<-", "<>"}
OVERRIDE = "OPENCODE_STDIN_OK=1"


def tokens_of(command):
    # Newlines separate commands; make them explicit before shlex eats them.
    lex = shlex.shlex(command.replace("\n", " ; "), posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    return list(lex)


def is_assignment(tok):
    name, eq, _ = tok.partition("=")
    return bool(eq) and name.replace("_", "a").isalnum() and not name[0].isdigit()


def offending_calls(toks):
    hits = []
    i, n = 0, len(toks)
    prev_sep = ";"
    at_cmd = True
    while i < n:
        tok = toks[i]
        if tok in SEPARATORS or tok == ";":
            prev_sep, at_cmd = tok, True
            i += 1
            continue
        if not at_cmd:
            i += 1
            continue
        if is_assignment(tok) or tok in SIMPLE_WRAPPERS:
            i += 1
            continue
        if tok in TIMEOUTS:
            i += 1
            while i < n and toks[i].startswith("-"):
                i += 1
            i += 1  # duration
            continue
        at_cmd = False
        if os.path.basename(tok) == "opencode":
            j = i + 1
            while j < n and toks[j].startswith("-"):
                j += 1
            if j < n and toks[j] == "run":
                piped = prev_sep == "|"
                redirected = any(t in STDIN_REDIRECTS for t in toks[j + 1:])
                if not (piped or redirected):
                    hits.append(i)
        i += 1
    return hits


def main():
    try:
        envelope = json.loads(sys.stdin.read(1 << 20))
        command = envelope.get("tool_input", {}).get("command", "") or ""
        if OVERRIDE in command:
            return 0
        toks = tokens_of(command)
        hits = offending_calls(toks)
    except Exception:
        return 0  # fail open
    if not hits:
        return 0
    sys.stderr.write(
        "BLOCKED by gate-opencode-stdin: `opencode run` with the Bash tool's open stdin "
        "hangs until timeout (0 bytes, rc 124) — it reads stdin to EOF when stdin is not "
        "a TTY.\nFix: add `</dev/null` to the opencode command, e.g.\n"
        "  timeout 600 opencode run --standalone -m <model> \"<msg>\" </dev/null\n"
        "or pipe the prompt in. To run it unchanged on purpose, prefix OPENCODE_STDIN_OK=1.\n"
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
