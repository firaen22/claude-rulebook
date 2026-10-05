#!/usr/bin/env python3
"""Claude Code PreToolUse hook (matcher: Bash): block `opencode run` unless its
stdin is closed or supplied.

Why it exists: `opencode run` (v2.0.21 and v2.0.22, reproduced 2026-10-05) reads
stdin until EOF whenever stdin is not a TTY. The Bash tool's stdin is an open
socket that never sends EOF, so the run prints 0 bytes until `timeout` kills it
(rc 124). That looked like "opencode hangs on NIM" for two days. Fix: append
`</dev/null`. See ~/.claude/memory/reference_nim_via_opencode.md.

Behavior:
- A small shell scanner (not shlex: shlex drops quote provenance, comments,
  heredocs and substitutions — round 1 review, 2026-10-05). It keeps quoted text
  as data, ends comments at the newline, joins backslash-newline, skips heredoc
  bodies, and scans `$(...)` / backticks (also inside double quotes) as nested
  command lists.
- `opencode run` counts when it is at command position: after a separator
  (; & && || | |& ( ) newline), after a shell keyword (if then elif else while
  until do ! {), skipping VAR=value assignments and wrappers with their
  options (env, command, nohup, nice, exec, sudo, stdbuf, time, timeout,
  gtimeout; matched by basename).
- Allowed when: the call is piped into (`|` or `|&` before it), or a stdin
  redirect on fd 0 (`<`, `<<`, `<<-`, `<<<`, `<>`, `<&`, with no fd number or
  fd 0) appears after it in the same command list — this also covers
  `(cd x && opencode run ...) </dev/null` and `while ...; done </dev/null`.
  Coarse on purpose: a later, unrelated stdin redirect lets a call through
  (false negative, accepted).
- Override: `OPENCODE_STDIN_OK=1` as a prefix assignment, an `env` argument or
  an `export` (e.g. to reproduce the hang on purpose). Not a raw substring: a
  prompt or comment that mentions it does not count (round 4 review).
- Fails OPEN on any parse or envelope error: this is a convenience gate against
  a multi-minute silent hang, not a security boundary.

Known limits (all false allows unless noted):
- `bash -c "..."`, `eval`, scripts, aliases, and functions defined in an
  earlier call are not inspected (a body defined in the same command is).
- The command word must be literal: `bin=opencode; $bin run`, `"${cmds[@]}"`.
- Commands run by another program: `trap '...' EXIT`, `env -S '...'`,
  `find -exec`, `xargs`, `coproc`.
- Unknown launcher commands: `taskset`, `ionice`, `flock`, `setsid`.
- Any fd-0 redirect counts as closed or supplied, even `<&0` and
  `</dev/stdin`, which re-attach the open socket.
- `a | case ... esac`: the case body does not inherit the pipe (false block).
- `(( x << 1 ))` as a bare command on its own line: its `<<` is read as a
  heredoc and the next lines are skipped.
- A conditional or function-body export still counts for later commands:
  `false && export OPENCODE_STDIN_OK=1; opencode run` is allowed.
Substitutions in an UNQUOTED heredoc body are scanned (they run: this hook once
missed a backticked `opencode run` in such a body, 2026-10-05).
dispatch.py and bench harnesses already pass stdin=DEVNULL.
"""

import json
import os
import re
import sys

OVERRIDE = "OPENCODE_STDIN_OK=1"
SEP_OPS = {";", "&", "&&", "||", "|", "|&", "(", ")", ";;", "\n"}
PIPE_OPS = {"|", "|&"}
# longest first
OPERATORS = ["<<<", "<<-", "&&", "||", "|&", ";;", "<<", "<>", "<&", ">>", ">&", ">|",
             "<", ">", "&", "|", ";", "(", ")"]
REDIRECTS = {"<<<", "<<-", "<<", "<>", "<&", ">>", ">&", ">|", "<", ">"}
STDIN_REDIRECTS = {"<<<", "<<-", "<<", "<>", "<&", "<"}
KEYWORDS_KEEP_CMD = {"if", "then", "elif", "else", "while", "until", "do", "!", "{"}
KEYWORDS_END = {"fi", "done", "}", "esac"}
LOOP_HEADERS = {"for", "select", "case"}  # their words are not commands until a separator
# compound commands whose body shares one stdin; `case` left out: its `)` patterns
# would unbalance the ( ) group stack
COMPOUND_OPEN = {"{", "if", "while", "until", "for", "select"}
COMPOUND_CLOSE = {"}", "fi", "done"}
# wrapper -> options that take a separate argument
WRAPPERS = {
    "env": {"-u", "--unset", "-C", "--chdir", "-S", "--split-string"},
    "command": set(),
    "nohup": set(),
    "nice": {"-n", "--adjustment"},
    "exec": {"-a"},
    "sudo": {"-u", "-g", "-p", "-C", "-D", "-h", "-r", "-t", "-U", "-T", "-R"},
    "stdbuf": {"-i", "-o", "-e", "--input", "--output", "--error"},
    "time": {"-o", "-f", "--output", "--format"},
    "timeout": {"-s", "--signal", "-k", "--kill-after"},
    "gtimeout": {"-s", "--signal", "-k", "--kill-after"},
}
TIMEOUTS = {"timeout", "gtimeout"}
# opencode flags that take a separate value (`opencode --help`, v2.0.22)
OPENCODE_VALUE_OPTS = {"--log-level", "--completions", "--server", "--session", "-s", "--prompt"}


class Word:
    __slots__ = ("text",)

    def __init__(self, text):
        self.text = text


class Op:
    __slots__ = ("op", "fd")

    def __init__(self, op, fd=None):
        self.op, self.fd = op, fd


def _end_ansi_c(s, i):
    """s[i] is just after "$'"; return index just after the closing quote."""
    n = len(s)
    while i < n:
        if s[i] == "\\":
            i += 2
            continue
        if s[i] == "'":
            return i + 1
        i += 1
    raise ValueError("unbalanced $'")


def _skip_heredoc(s, i):
    """s[i] is just after '<<' or '<<-' inside a substitution; skip the body."""
    strip = s.startswith("-", i)
    if strip:
        i += 1
    while i < len(s) and s[i] in " \t":
        i += 1
    d = []
    while i < len(s) and s[i] not in " \t\n;&|<>()":
        if s[i] not in "'\"\\":
            d.append(s[i])
        i += 1
    delim = "".join(d)
    j = s.find("\n", i)
    if j < 0:
        return len(s)
    k = j + 1
    while k < len(s):
        e = s.find("\n", k)
        line = s[k:] if e < 0 else s[k:e]
        k = len(s) if e < 0 else e + 1
        if (line.lstrip("\t") if strip else line) == delim:
            break
    return k


def _balanced_paren(s, i, arith=False):
    """s[i] is just after '$(' ; return index just after the matching ')'.
    arith: inside $(( )), where `<<` is a shift, not a heredoc."""
    depth, n, start = 1, len(s), i
    while i < n:
        c = s[i]
        if c == "\\":
            i += 2
            continue
        if c == "#" and (i == start or s[i - 1] in " \t\n;|&("):
            j = s.find("\n", i)  # comment: its quotes and parens are text
            i = n if j < 0 else j
            continue
        if s.startswith("$'", i):
            i = _end_ansi_c(s, i + 2)
            continue
        if s.startswith("$(", i):  # nested $( ) / $(( )): its own mode
            i = _balanced_paren(s, i + 2, s.startswith("$((", i))
            continue
        if not arith and s.startswith("<<", i) and not s.startswith("<<<", i):
            i = _skip_heredoc(s, i + 2)
            continue
        if c == "'":
            j = s.index("'", i + 1)
            i = j + 1
            continue
        if c == '"':
            i = _end_dq(s, i + 1)
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced $(")


def _end_dq(s, i):
    """s[i] is just after an opening '"'; return index just after the closing one."""
    n = len(s)
    while i < n:
        c = s[i]
        if c == "\\":
            i += 2
            continue
        if c == '"':
            return i + 1
        if c == "$" and s.startswith("$(", i):
            i = _balanced_paren(s, i + 2, s.startswith("$((", i))
            continue
        if c == "`":
            i = s.index("`", i + 1) + 1
            continue
        i += 1
    raise ValueError("unbalanced \"")


def scan(s, subs):
    """Tokenize shell text into Word/Op; nested command strings go to `subs`."""
    toks, word, in_word = [], [], False
    pending_heredocs = []  # (delimiter, strip_tabs, body_expands)
    i, n = 0, len(s)

    def end_word():
        nonlocal word, in_word
        if in_word:
            toks.append(Word("".join(word)))
        word, in_word = [], False

    while i < n:
        c = s[i]
        if c == "\\":
            if i + 1 < n and s[i + 1] == "\n":
                i += 2  # line continuation
                continue
            word.append(s[i + 1] if i + 1 < n else "")
            in_word = True
            i += 2
            continue
        if c in " \t\r":
            end_word()
            i += 1
            continue
        if c == "#" and not in_word:
            j = s.find("\n", i)
            i = n if j < 0 else j
            continue
        if c == "\n":
            end_word()
            toks.append(Op("\n"))
            i += 1
            for delim, strip, expands in pending_heredocs:
                body = []
                while i < n:
                    j = s.find("\n", i)
                    line = s[i:] if j < 0 else s[i:j]
                    i = n if j < 0 else j + 1
                    if (line.lstrip("\t") if strip else line) == delim:
                        break
                    body.append(line)
                if expands:  # unquoted delimiter: $(...) and `...` in the body run
                    _collect_subs("\n".join(body), subs)
            pending_heredocs = []
            continue
        if s.startswith("$'", i):
            j = _end_ansi_c(s, i + 2)
            word.append(s[i + 2:j - 1])
            in_word = True
            i = j
            continue
        if c == "'":
            j = s.index("'", i + 1)
            word.append(s[i + 1:j])
            in_word = True
            i = j + 1
            continue
        if c == '"':
            j = _end_dq(s, i + 1)
            body = s[i + 1:j - 1]
            _collect_subs(body, subs)
            word.append(body)
            in_word = True
            i = j
            continue
        if c == "$" and s.startswith("$((", i):
            j = _balanced_paren(s, i + 2, True)  # arithmetic: not a command itself,
            _collect_subs(s[i + 3:j - 2], subs)  # but $(...) inside it runs
            word.append(s[i:j])
            in_word = True
            i = j
            continue
        if c == "$" and s.startswith("$(", i):
            j = _balanced_paren(s, i + 2)
            subs.append(s[i + 2:j - 1])
            word.append("$()")
            in_word = True
            i = j
            continue
        if c == "`":
            j = s.index("`", i + 1)
            subs.append(s[i + 1:j])
            word.append("``")
            in_word = True
            i = j + 1
            continue
        if c in "<>" and s.startswith("(", i + 1):
            j = _balanced_paren(s, i + 2)
            if c == "<":  # <(cmd): cmd inherits the shell's stdin
                subs.append(s[i + 2:j - 1])
            word.append("<()")
            in_word = True
            i = j
            continue
        if c == "(" and in_word and word and word[-1].endswith("="):
            j = _balanced_paren(s, i + 1)  # NAME=( ... ) array: elements are data,
            scan(s[i + 1:j - 1], subs)  # but $(...) inside them runs
            word.append(s[i:j])
            i = j
            continue
        op = next((o for o in OPERATORS if s.startswith(o, i)), None)
        if op:
            fd = None
            if op in REDIRECTS and in_word and "".join(word).isdigit():
                fd = "".join(word)
                word, in_word = [], False
            end_word()
            toks.append(Op(op, fd))
            i += len(op)
            if op in ("<<", "<<-"):
                # read the delimiter word (quotes removed)
                while i < n and s[i] in " \t":
                    i += 1
                d, quoted = [], False
                while i < n and s[i] not in " \t\n;&|<>()":
                    if s[i] in "'\"":
                        quoted = True
                        q = s[i]
                        j = s.index(q, i + 1)
                        d.append(s[i + 1:j])
                        i = j + 1
                    else:
                        if s[i] == "\\":
                            quoted = True
                        else:
                            d.append(s[i])
                        i += 1
                pending_heredocs.append(("".join(d), op == "<<-", not quoted))
                toks.append(Word("".join(d)))
            continue
        word.append(c)
        in_word = True
        i += 1
    end_word()
    return toks


def _collect_subs(dq_body, subs):
    i, n = 0, len(dq_body)
    while i < n:
        c = dq_body[i]
        if c == "\\":
            i += 2
            continue
        if dq_body.startswith("$((", i):
            j = _balanced_paren(dq_body, i + 2, True)
            _collect_subs(dq_body[i + 3:j - 2], subs)
            i = j
            continue
        if dq_body.startswith("$(", i):
            j = _balanced_paren(dq_body, i + 2)
            subs.append(dq_body[i + 2:j - 1])
            i = j
            continue
        if c == "`":
            j = dq_body.index("`", i + 1)
            subs.append(dq_body[i + 1:j])
            i = j + 1
            continue
        i += 1


_ASSIGN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(\[[^]]*\])?\+?=")  # x=, x+=, x[i]=, x[i]+=


def _is_assignment(t):
    return bool(_ASSIGN.match(t))


def offending(command, depth=0):
    if depth > 20:
        return False
    subs = []
    toks = scan(command, subs)
    if any(offending(sub, depth + 1) for sub in subs):
        return True
    n = len(toks)
    i, at_cmd, prev_sep, skip_header = 0, True, "\n", False
    cmd_start = 0  # index of the first token of the current simple command
    override = exported = False  # OPENCODE_STDIN_OK=1 as a prefix / env arg / export
    group_piped = []  # one entry per open ( or { group: does its stdin come from a pipe?
    export_saved = []  # `exported` at each open `(`: a subshell's export ends at its `)`
    while i < n:
        t = toks[i]
        if isinstance(t, Op):
            if t.op in REDIRECTS:
                i += 2  # operator + its target word
                continue
            if t.op == "\n" and cmd_start == i and prev_sep in PIPE_OPS | {"&&", "||"}:
                cmd_start = i + 1  # `a |<newline> b`: the line break continues the pipeline
                i += 1
                continue
            if t.op in SEP_OPS:
                # `a | (b)` / `a | { b; }`: the group inherits the pipe
                inherit = t.op == "(" and prev_sep in PIPE_OPS and cmd_start == i
                if t.op == "(":
                    group_piped.append(inherit or bool(group_piped and group_piped[-1]))
                    export_saved.append(exported)
                elif t.op == ")":
                    if group_piped:
                        group_piped.pop()
                    if export_saved:
                        exported = export_saved.pop()
                if not inherit:
                    prev_sep = t.op
                at_cmd, skip_header, cmd_start, override = True, False, i + 1, False
            i += 1
            continue
        w = t.text
        if skip_header:
            if w == "do":
                skip_header, at_cmd = False, True
            i += 1
            continue
        if not at_cmd:
            i += 1
            continue
        if w in COMPOUND_OPEN:
            # `a | { b; }`, `a | while read x; do b; done`: the body inherits the pipe
            inherit = prev_sep in PIPE_OPS and cmd_start == i
            group_piped.append(inherit or bool(group_piped and group_piped[-1]))
            if inherit:
                cmd_start = i + 1
        elif w in COMPOUND_CLOSE and group_piped:
            group_piped.pop()
        if w == OVERRIDE:
            override = True
        if w == "function":  # `function f { ...; }` / `function f() { ...; }`
            i += 2
            if i + 1 < n and isinstance(toks[i], Op) and toks[i].op == "(" \
                    and isinstance(toks[i + 1], Op) and toks[i + 1].op == ")":
                i += 2
            continue
        if w == "[[":  # conditional: its words and parens are operands, not commands
            k = next((k for k in range(i + 1, n) if isinstance(toks[k], Word) and toks[k].text == "]]"), n)
            i, at_cmd = k + 1, False
            continue
        if w in ("export", "unset"):
            args, k = [], i + 1
            while k < n:
                if isinstance(toks[k], Op) and toks[k].op in REDIRECTS:
                    k += 2  # `export > /dev/null X=1`: redirect + its target
                    continue
                if not isinstance(toks[k], Word):
                    break
                args.append(toks[k].text)
                k += 1
            name = OVERRIDE.split("=")[0]
            for a in args:
                if a.split("=")[0] != name:
                    continue
                if w == "unset" or "-n" in args:
                    exported = False
                elif "=" in a:
                    exported = a == OVERRIDE
        elif _is_assignment(w) and w.split("=")[0] == OVERRIDE.split("=")[0] and w != OVERRIDE:
            exported = False  # `OPENCODE_STDIN_OK=0`: reassigned
        if w in KEYWORDS_KEEP_CMD or w in KEYWORDS_END or _is_assignment(w):
            i += 1
            continue
        if w in LOOP_HEADERS:
            skip_header, at_cmd = True, False
            i += 1
            continue
        base = os.path.basename(w)
        if base in WRAPPERS:
            argopts = WRAPPERS[base]
            i += 1
            while i < n:
                if isinstance(toks[i], Op) and toks[i].op in REDIRECTS:
                    i += 2  # `timeout > out 90 ...`: redirect + its target
                    continue
                if not isinstance(toks[i], Word):
                    break
                o = toks[i].text
                if o == "--":
                    i += 1
                    break
                if base == "command" and o in ("-v", "-V"):
                    break  # lookup only, runs nothing
                if o.startswith("-") and len(o) > 1:
                    i += 2 if o in argopts else 1
                    continue
                if base == "env" and _is_assignment(o):
                    override = override or o == OVERRIDE
                    i += 1
                    continue
                break
            if base in TIMEOUTS and i < n and isinstance(toks[i], Word):
                i += 1  # duration
            if base == "command" and i < n and isinstance(toks[i], Word) and toks[i].text in ("-v", "-V"):
                at_cmd = False
                i += 1
            continue
        at_cmd = False
        if base == "opencode":
            j = i + 1
            while j < n:
                if isinstance(toks[j], Op) and toks[j].op in REDIRECTS:
                    j += 2  # `opencode > out run`: redirect + its target
                elif isinstance(toks[j], Word) and toks[j].text.startswith("-"):
                    j += 2 if toks[j].text in OPENCODE_VALUE_OPTS else 1
                else:
                    break
            if j < n and isinstance(toks[j], Word) and toks[j].text == "run":
                end = next((k for k in range(j + 1, n) if isinstance(toks[k], Op) and toks[k].op in SEP_OPS), n)
                rest = [x.text for x in toks[j + 1:end] if isinstance(x, Word)]
                if "--" in rest:  # after `--`, `--help` is message text
                    rest = rest[:rest.index("--")]
                if "--help" in rest or "-h" in rest:  # prints help, never reads stdin
                    i += 1
                    continue
                piped = prev_sep in PIPE_OPS or bool(group_piped and group_piped[-1])
                redirected = any(isinstance(x, Op) and x.op in STDIN_REDIRECTS and x.fd in (None, "0")
                                 for x in toks[cmd_start:])  # incl. `opencode </dev/null run`
                if not (piped or redirected or override or exported):
                    return True
        i += 1
    return False


def main():
    try:
        envelope = json.loads(sys.stdin.read(1 << 20))
        command = envelope.get("tool_input", {}).get("command", "") or ""
        if "opencode" not in command:
            return 0
        hit = offending(command)
    except Exception:
        return 0  # fail open
    if not hit:
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
