#!/usr/bin/env python3
"""
dispatch — ONE wrapper for every subordinate CLI (codex, agy, grok, opencode/NIM).

WHY (2026-09-22 six-lens review, converged MISSING item): every "dead model" misdiagnosis
came from reading a raw shell result by hand — my own timeout, a swallowed argv, a denial
on stderr, an error envelope on stdout with rc=0. The wrapper returns a NAMED status
instead of bytes, records elapsed vs cap, keeps both streams, scans the packet for
secrets before anything leaves the machine, and cleans up isolated HOME/dirs.

    python3 ~/.claude/lib/dispatch.py <tool> --model M --prompt-file F --outdir D [--name N]
        [--cwd C] [--timeout S] [--effort E] [--files f1 f2 ...] [--pong]
    python3 ~/.claude/lib/dispatch.py --selftest      # fixtures: known-bad must FAIL

Status (stdout, last line, also <outdir>/<name>-result.json):
  PASS · PONG_FAIL · EMPTY · STDOUT_ERROR · STDERR_DENIAL · RATE_LIMIT · TIMEOUT
  LAUNCH_ERROR · ERROR · SECRET_BLOCK
Exit code 0 only on PASS. A status is a classification of the bytes, not a diagnosis
of the model — read <name>-err.txt / <name>-out.txt before naming a cause.
NEVER prints secret values.
"""
import argparse, fcntl, json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

TOOLS = ("codex", "agy", "grok", "opencode", "nim")
DENYLIST = Path.home() / ".claude" / "lib" / "dispatch_denylist.txt"   # one pattern per line
SECRET_SHAPES = [r"sk-[A-Za-z0-9_-]{16,}", r"xai-[A-Za-z0-9]{16,}", r"nvapi-[A-Za-z0-9_-]{16,}",
                 r"ghp_[A-Za-z0-9]{20,}", r"AKIA[0-9A-Z]{16}", r"AIza[0-9A-Za-z_-]{30,}",
                 r"gsk_[A-Za-z0-9]{20,}", r"Bearer [A-Za-z0-9._-]{20,}",
                 r"-----BEGIN [A-Z ]*PRIVATE KEY-----"]
# the loose phrases must sit near a line START: a short successful answer saying "was not found" is not
# an error envelope (grok review 2026-09-22)
STDOUT_ERR = re.compile(r"^\s*(\x1b\[[0-9;]*m)*(Error|error|ERROR)\b"
                        r"|^[^\n]{0,15}\b(Not signed in|not (available|found|callable)|unknown model|invalid model|No payment method)"
                        r"|^\s*\{\s*\"(error|detail|message)\"\s*:", re.M)   # JSON error envelope, rc=0
# phrases, not bare words: codex prints "approval: never" in its stderr banner on every run, and the
# banner+denial rule below read a live PONG PASS as STDERR_DENIAL (2026-09-22) on the loose form
DENIAL = re.compile(r"denied|not allowed|requires? approval|approval (required|needed)|permission (error|required)", re.I)
PROMPT_ON_STDIN = object()   # stdin_override sentinel, see run_one
RATE = re.compile(r"\b429\b|rate.?limit|quota", re.I)
# the invocation itself was rejected (argv/usage) — distinct from a model that failed mid-run
USAGE = re.compile(r"usage:|unrecognized|unknown (option|argument|flag|command)|conflicts with"
                   r"|(required|invalid value|unexpected argument|argument .* required)", re.I)


def scan_secrets(texts):
    """Return list of hit LABELS (never values). Env values + key shapes + denylist."""
    hits = []
    for k, v in os.environ.items():
        # case-insensitive name; floor of 8 keeps `TOKENIZERS_PARALLELISM=false`-class values from
        # blocking every packet containing the word (review 2026-09-22: 12 + case-sensitive missed real creds)
        if re.search(r"KEY|TOKEN|SECRET|PASSWORD", k, re.I) and len(v) >= 8:
            if any(v in t for t in texts):
                hits.append(f"env:{k}")
    for pat in SECRET_SHAPES:
        if any(re.search(pat, t) for t in texts):
            hits.append(f"shape:{pat[:12]}")
    if DENYLIST.is_file():
        for i, line in enumerate(DENYLIST.read_text().splitlines(), 1):
            line = line.strip()
            if line and not line.startswith("#") and any(re.search(line, t) for t in texts):
                hits.append(f"denylist:line{i}")   # the pattern may itself be a literal secret — never echo it
    return hits


def build(tool, a, prompt_text, cwd):
    """Return (argv, env, stdin_text). Playbook-derived invocations."""
    env = dict(os.environ)
    if tool == "codex":
        argv = ["codex", "exec", "-m", a.model, "-c", f"model_reasoning_effort={a.effort}",
                "--sandbox", "read-only", "--skip-git-repo-check",
                "-o", str(Path(a.outdir) / f"{a.name}-final.txt"), "-"]
        return argv, env, prompt_text
    if tool == "agy":
        # agy demands --effort for an un-suffixed slug and rejects it when it disagrees
        # with a -low/-medium/-high suffix, so the suffix wins when present
        argv = ["agy", "--model", a.model]
        if not re.search(r"-(low|medium|high)$", a.model):
            argv += ["--effort", a.effort]
        return argv + ["-p", prompt_text], env, None
    if tool == "grok":
        # packet is STAGED in cwd (inline prompts idle/truncate); HOME isolated + seeded
        staged = Path(cwd) / "00-BRIEF.md"
        staged.write_text(prompt_text)
        home = Path(a.outdir) / f"_home_{a.name}"
        (home / ".grok").mkdir(parents=True, exist_ok=True)
        # playbook recipe: rsync the whole dir minus the heavy/irrelevant ones. A two-file
        # copy (auth.json+agent_id) worked 3x then returned "Not signed in" in 0.4s on a
        # FRESH auth.json (2026-09-22) while the real HOME answered — seed everything.
        subprocess.run(["rsync", "-a", "--exclude", "downloads", "--exclude", "marketplace-cache",
                        "--exclude", "sessions", str(Path.home() / ".grok") + "/", str(home / ".grok") + "/"],
                       check=True, capture_output=True)
        env.update(HOME=str(home), PWD=str(cwd))
        argv = [os.path.expanduser("~/.grok/bin/grok"), "-p",
                "Read ./00-BRIEF.md with read_file and carry out what it says. Print the full result to stdout.",
                "-m", a.model, "--cwd", str(cwd), "--always-approve", "--disable-web-search",
                "--no-subagents", "--output-format", "plain", "--tools", "read_file,grep,list_dir"]
        return argv, env, None
    if tool in ("opencode", "nim"):
        staged = Path(cwd) / "00-BRIEF.md"
        staged.write_text(prompt_text)
        env["PWD"] = str(cwd)
        # prompt positional BEFORE -f: -f is an array flag and swallows a trailing positional
        argv = ["opencode", "run", "--auto", "-m", a.model, "--dir", str(cwd),
                "Read the attached 00-BRIEF.md and carry out what it says. Do not edit any file. "
                "Print the full result to stdout.", "-f", "00-BRIEF.md"]
        for f in a.files:
            argv += ["-f", f]
        return argv, env, None
    raise SystemExit(f"unknown tool {tool}")


def served_model(tool, err):
    m = None
    if tool == "codex":
        m = re.search(r"^model:\s*(\S+)", err, re.M)
    elif tool in ("opencode", "nim"):
        m = re.search(r"build · (\S+)", err)
    return m.group(1) if m else None


def classify(rc, out, err, elapsed, cap, timed_out, pong):
    if timed_out:
        return "TIMEOUT"
    if rc != 0:
        if RATE.search(err) or RATE.search(out):
            return "RATE_LIMIT"
        if DENIAL.search(err) and not out.strip():
            return "STDERR_DENIAL"
        # LAUNCH_ERROR = the CLI rejected the invocation (no binary / usage error), never "it was fast":
        # a server HTTP 400 one second in is a model-side ERROR (review 2026-09-22)
        return "LAUNCH_ERROR" if rc == 127 or USAGE.search(err) else "ERROR"
    if not out.strip():
        return "STDERR_DENIAL" if DENIAL.search(err) else "EMPTY"
    # a banner on stdout does not clear a denial on stderr
    if DENIAL.search(err) and len(out.strip()) < 200:
        return "STDERR_DENIAL"
    # an error envelope LEADS the output whatever its length; the anywhere-match stays short-only so a
    # long review that merely quotes "Error:" is not misread (review 2026-09-22: the <2000 gate alone
    # let "Error: "+1993 chars read PASS)
    first = out.strip().splitlines()[0]
    if STDOUT_ERR.search(first) or (len(out) < 2000 and STDOUT_ERR.search(out)):
        return "STDOUT_ERROR"
    if pong:
        # digit-bounded: "14200" must not satisfy 420, prose around the number may
        return "PASS" if re.search(rf"(?<!\d){pong}(?!\d)", out) else "PONG_FAIL"
    return "PASS"


def run_one(tool, a, prompt_text, argv_override=None, stdin_override=None):
    outdir = Path(a.outdir).resolve(); outdir.mkdir(parents=True, exist_ok=True)
    a.outdir = str(outdir)   # build() reads a.outdir; a relative HOME/-o path breaks under the child's cwd
    cwd = Path(a.cwd).resolve() if a.cwd else outdir / f"_dir_{a.name}"   # absolute: --dir/--cwd are read from the child's cwd
    cwd.mkdir(parents=True, exist_ok=True)
    # resolve attachments ONCE: the scan and the child (running in `cwd`, not here) must read the same
    # file — a relative `-f x.md` would otherwise point the child at cwd/x.md, a file never scanned
    a.files = [str(Path(f).resolve()) for f in a.files]
    # argv strings the caller controls are scanned too (a credential pasted as --model would otherwise leave)
    texts = [prompt_text, a.model, str(a.effort)] + a.files + [Path(f).read_text(errors="replace") for f in a.files]
    hits = scan_secrets(texts)
    res = {"name": a.name, "tool": tool, "model": a.model, "cap": a.timeout, "pong": a.pong}
    if hits:
        res.update(status="SECRET_BLOCK", hits=hits, elapsed=0, rc=None)
        return finish(res, outdir, a.name)
    pong = None
    if a.pong:
        # arithmetic nonce, not "reply with exactly PONG-<hex>": mistral-nemotron via NIM stalled
        # 2/2 on the literal-echo shape (120-180s, route line printed) and answered 2+3 in 2.5s
        x, y = int.from_bytes(os.urandom(2), "big") % 900 + 100, int.from_bytes(os.urandom(2), "big") % 900 + 100
        pong = str(x + y)
        prompt_text = f"What is {x}+{y}? Answer with the number only."
    t0 = time.time(); timed_out = False; argv = []
    # opencode/nim share one sqlite DB: two concurrent launches → "database is locked", rc=1.
    # The lock is taken BEFORE build() stages 00-BRIEF.md, so a waiting invocation on a shared --cwd
    # cannot overwrite the packet the running one is reading; build() (grok's auth rsync included)
    # runs INSIDE the try so a failed/interrupted seed still reaches the HOME cleanup below
    lock = open(Path(tempfile.gettempdir()) / "dispatch-opencode.lock", "w") if tool in ("opencode", "nim") else None
    try:
        if lock: fcntl.flock(lock, fcntl.LOCK_EX)
        argv, env, stdin_text = (argv_override, dict(os.environ), stdin_override) if argv_override \
            else build(tool, a, prompt_text, cwd)
        if stdin_text is PROMPT_ON_STDIN:   # selftest: feed the real (nonce-bearing) prompt like codex gets it
            stdin_text = prompt_text
        p = subprocess.run(argv, input=stdin_text.encode() if stdin_text is not None else None, capture_output=True, timeout=a.timeout,
                           env=env, cwd=str(cwd),
                           stdin=None if stdin_text is not None else subprocess.DEVNULL)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, out, err, timed_out = 124, e.stdout or b"", e.stderr or b"", True
    except FileNotFoundError as e:
        rc, out, err = 127, b"", str(e).encode()
    except subprocess.CalledProcessError as e:   # build()'s seeding rsync failed → nothing launched
        rc, out, err = 127, b"", b"seed failed: " + (e.stderr or b"")
    finally:
        if lock: fcntl.flock(lock, fcntl.LOCK_UN); lock.close()
        home = outdir / f"_home_{a.name}"
        shutil.rmtree(home, ignore_errors=True)   # copied auth never survives
        home_leak = home.exists()
        if home_leak:
            print(f"WARNING: copied credentials still present at {home}", file=sys.stderr)
    dec = lambda b: b.decode(errors="replace") if isinstance(b, bytes) else (b or "")
    out, err = dec(out), dec(err)
    elapsed = round(time.time() - t0, 1)
    (outdir / f"{a.name}-out.txt").write_text(out)
    (outdir / f"{a.name}-err.txt").write_text(err)
    status = classify(rc, out, err, elapsed, a.timeout, timed_out, pong)
    if home_leak:
        status = "ERROR"; res["home_leak"] = str(home)   # a PASS must never leave an auth copy behind
    res.update(status=status, rc=rc,
               elapsed=elapsed, out_bytes=len(out), err_bytes=len(err),
               served_model=served_model(tool, err), out=str(outdir / f"{a.name}-out.txt"),
               err=str(outdir / f"{a.name}-err.txt"), cwd=str(cwd),
               # --effort reaches codex and un-suffixed agy only; grok --reasoning-effort and
               # opencode --variant exist but every pin was measured without them — visible, not forwarded
               effort_applied=(tool == "codex" or (tool == "agy" and "--effort" in argv)))
    return finish(res, outdir, a.name)


def finish(res, outdir, name):
    (outdir / f"{name}-result.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k not in ("out", "err")}))
    print(res["status"])
    return res


def selftest():
    """Known-bad fixtures must NOT read PASS; known-good must. Uses the wrapper's own path."""
    d = Path(tempfile.mkdtemp(prefix="dispatch-selftest-"))
    os.environ["DISPATCH_SELFTEST_KEY"] = "abcdef0123456789SECRET"
    os.environ["dispatch_selftest_password"] = "short-pass"   # lowercase name, 10 chars
    def A(**kw):
        base = dict(model="x", outdir=os.path.relpath(d), name="t", cwd=None, timeout=3, effort="medium",
                    files=[], pong=False)
        base.update(kw); return argparse.Namespace(**base)
    cases = [
        ("good",        A(name="good"),  "hello", ["sh", "-c", "echo real output"], "PASS"),
        ("timeout",     A(name="to"),    "x", ["sh", "-c", "sleep 10"], "TIMEOUT"),
        ("empty",       A(name="empty"), "x", ["sh", "-c", "true"], "EMPTY"),
        ("stdout_err",  A(name="se"),    "x", ["sh", "-c", "echo 'Error: model not found'"], "STDOUT_ERROR"),
        ("denial",      A(name="den"),   "x", ["sh", "-c", "echo 'tool call denied: permission' >&2"], "STDERR_DENIAL"),
        ("launch",      A(name="la"),    "x", ["sh", "-c", "echo 'error: unrecognized arguments: --foo' >&2; exit 2"], "LAUNCH_ERROR"),
        ("no_binary",   A(name="nb"),    "x", ["/nonexistent/cli"], "LAUNCH_ERROR"),
        ("fast_server_err", A(name="fs"), "x", ["sh", "-c", "echo 'HTTP 400 Bad Request' >&2; exit 1"], "ERROR"),  # fast ≠ launch
        ("rate",        A(name="rl"),    "x", ["sh", "-c", "echo 'HTTP 429 Too Many' >&2; exit 1"], "RATE_LIMIT"),
        ("secret_env",  A(name="sec"),   "key=abcdef0123456789SECRET", ["sh", "-c", "echo leaked"], "SECRET_BLOCK"),
        ("secret_lower_short", A(name="sl"), "pw is short-pass", ["sh", "-c", "echo leaked"], "SECRET_BLOCK"),
        ("secret_shape",A(name="sh"),    "sk-" + "A" * 26, ["sh", "-c", "echo leaked"], "SECRET_BLOCK"),   # built at runtime so
        ("secret_model",A(name="sm", model="sk-" + "A" * 26), "x", ["sh", "-c", "echo leaked"], "SECRET_BLOCK"),  # this source can be a packet
        ("long_error",  A(name="le"),    "x", ["sh", "-c", "printf 'Error: %s' \"$(head -c 3000 /dev/zero | tr '\\0' x)\""], "STDOUT_ERROR"),
        ("long_review", A(name="lr"),    "x", ["sh", "-c", "head -c 3000 /dev/zero | tr '\\0' x; echo; echo 'Error: quoted mid-review'"], "PASS"),
        ("json_env",    A(name="je"),    "x", ["sh", "-c", "echo '{\"error\":\"HTTP 400 Bad Request\"}'"], "STDOUT_ERROR"),
        ("banner_denial",A(name="bd"),   "x", ["sh", "-c", "echo 'Starting agent'; echo 'permission denied' >&2"], "STDERR_DENIAL"),
        ("not_found_prose", A(name="nf"), "x", ["sh", "-c", "echo 'The config file was not found, so I created one.'"], "PASS"),
        ("codex_banner", A(name="cb"),   "x", ["sh", "-c", "echo 1435; printf 'model: m\\napproval: never\\n' >&2"], "PASS"),  # live 2026-09-22
        ("pong_fail",   A(name="pf", pong=True), "", ["sh", "-c", "echo 7"], "PONG_FAIL"),
        ("pong_substr", A(name="ps", pong=True), "", ["sh", "-c", "read -r l; set -- $l; x=${3%%+*}; y=${3#*+}; y=${y%%\?}; echo 1$((x+y))0"], "PONG_FAIL"),   # 1<sum>0 ⊃ sum
        ("pong_prose",  A(name="pp", pong=True), "", ["sh", "-c", "read -r l; set -- $l; x=${3%%+*}; y=${3#*+}; y=${y%%\?}; echo \"The answer is $((x+y)).\""], "PASS"),
        ("stdin_path",  A(name="si"),    "x", ["sh", "-c", "cat"], "PASS"),   # codex feeds the prompt on stdin
    ]
    fails = 0
    for label, a, prompt, argv, want in cases:
        stdin = "packet on stdin" if label == "stdin_path" else PROMPT_ON_STDIN if label.startswith("pong_") else None
        got = run_one("opencode", a, prompt, argv_override=argv, stdin_override=stdin)["status"]
        ok = got == want
        fails += not ok
        print(f"  {'ok ' if ok else 'BAD'} {label:12s} want={want:13s} got={got}")
    # build() shape fixtures — the argv path the live fixtures above bypass via argv_override
    # (2026-09-22: agy's missing --effort shipped through 11/11 green because nothing exercised build)
    shape = [
        ("codex_stdin",   "codex",    A(model="m"),        lambda v, s: v[:2] == ["codex", "exec"] and v[-1] == "-"
                                                            and "model_reasoning_effort=medium" in v and s == "P"),
        ("agy_bare",      "agy",      A(model="g-flash"),  lambda v, s: v[v.index("--effort")+1] == "medium" and v[-2:] == ["-p", "P"]),
        ("agy_suffixed",  "agy",      A(model="g-flash-high"), lambda v, s: "--effort" not in v and v[-2:] == ["-p", "P"]),
        ("opencode_f_last","opencode",A(model="m", files=["x.md"]), lambda v, s: v.index("-f") > v.index("--dir") + 2
                                                            and v[-4:] == ["-f", "00-BRIEF.md", "-f", "x.md"]),
        ("nim_same_shape","nim",      A(model="m"),        lambda v, s: v[:3] == ["opencode", "run", "--auto"]),
    ]
    for label, tool, a, check in shape:
        cwd = d / f"_dir_{label}"; cwd.mkdir(exist_ok=True)
        a.outdir = str(d)
        v, env, s = build(tool, a, "P", cwd)
        try:
            ok = bool(check(v, s))
        except (ValueError, IndexError):   # a missing flag is a BAD row, not a crash
            ok = False
        fails += not ok
        print(f"  {'ok ' if ok else 'BAD'} {label:12s} shape {'ok' if ok else v}")
    # integration fixtures — real build() → real launch, against fake executables (review 2026-09-22:
    # nothing exercised argv+env+staging+HOME cleanup together). Fake HOME so grok's rsync seeds and
    # its absolute ~/.grok/bin/grok path resolve to fakes; fake opencode shadows the real one on PATH.
    real_home, real_path = os.environ["HOME"], os.environ["PATH"]
    fake_home = d / "home"; (fake_home / ".grok" / "bin").mkdir(parents=True)
    (fake_home / ".grok" / "auth.json").write_text('{"fixture": true}')
    fg = fake_home / ".grok" / "bin" / "grok"
    fg.write_text('#!/bin/sh\ntest -f "$HOME/.grok/auth.json" || { echo "Not signed in"; exit 0; }\n'
                  'echo "HOME=$HOME"; cat ./00-BRIEF.md\n'); fg.chmod(0o755)
    fo = d / "bin"; fo.mkdir(); (fo / "opencode").write_text('#!/bin/sh\nfor f in "$@"; do :; done; cat "$f"\n')
    (fo / "opencode").chmod(0o755)
    os.environ["HOME"], os.environ["PATH"] = str(fake_home), f"{fo}:{real_path}"
    integ = []
    try:
        r = run_one("grok", A(name="ig", model="g"), "BRIEF-BODY")
        home_after = (Path(r["cwd"]).parent / "_home_ig").exists()
        out = Path(r["out"]).read_text()
        integ.append(("grok_seeded", r["status"] == "PASS" and "BRIEF-BODY" in out
                      and f"HOME={Path(r['cwd']).parent / '_home_ig'}" in out and not home_after, r["status"]))
        shutil.rmtree(fake_home / ".grok" / "sessions", ignore_errors=True)
        os.environ["HOME"] = str(d / "no-such-home")   # rsync source missing → seed fails inside build()
        r = run_one("grok", A(name="is", model="g"), "x")
        integ.append(("grok_seed_fail", r["status"] == "LAUNCH_ERROR" and not (d / "_home_is").exists(), r["status"]))
        os.environ["HOME"] = str(fake_home)
        att = d / "att.md"; att.write_text("ATTACHED")
        r = run_one("opencode", A(name="io", model="m", files=[os.path.relpath(att)]), "x")
        integ.append(("opencode_abs_file", r["status"] == "PASS" and Path(r["out"]).read_text().strip() == "ATTACHED",
                      r["status"]))   # the last -f is the attachment, resolved absolute
    finally:
        os.environ["HOME"], os.environ["PATH"] = real_home, real_path
    for label, ok, got in integ:
        fails += not ok
        print(f"  {'ok ' if ok else 'BAD'} {label:12s} integ got={got}")
    shutil.rmtree(d, ignore_errors=True)
    n = len(cases) + len(shape) + len(integ)
    print(f"selftest: {n-fails}/{n}")
    return 0 if fails == 0 else 1


def main():
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    ap = argparse.ArgumentParser()
    ap.add_argument("tool", choices=TOOLS)
    ap.add_argument("--model", required=True)
    ap.add_argument("--prompt-file")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--name")
    ap.add_argument("--cwd")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--files", nargs="*", default=[])
    ap.add_argument("--pong", action="store_true")
    a = ap.parse_args()
    a.name = a.name or a.tool
    if not a.pong and not a.prompt_file:
        ap.error("--prompt-file required unless --pong")
    prompt = Path(a.prompt_file).read_text() if a.prompt_file else ""
    res = run_one(a.tool, a, prompt)
    sys.exit(0 if res["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
