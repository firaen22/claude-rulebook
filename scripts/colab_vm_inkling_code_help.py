"""Run on Colab VM: spec path + out path from env (unique per request)."""
import json
import os
import urllib.error
import urllib.request

BASE = os.environ.get("INKLING_BASE_URL", "http://127.0.0.1:8092/v1").rstrip("/")
MODEL = os.environ.get("INKLING_MODEL", "inkling-2.5-mini")
SPEC_PATH = os.environ.get("INKLING_SPEC_PATH", "/content/elko_spec.md")
OUT_PATH = os.environ.get("INKLING_OUT_PATH", "/content/elko_inkling_out.md")
REQUEST_ID = os.environ.get("INKLING_REQUEST_ID", "")
DEFAULT_MAX_COMPLETION = 6144

SYSTEM = """You are a coding assistant. The user gives a tight spec.
Return one markdown doc: at most 3 plan bullets, then exactly one fenced diff or one fenced file.
No shell commands. No extra files."""


def _max_completion() -> int:
    raw = os.environ.get("INKLING_MAX_COMPLETION", str(DEFAULT_MAX_COMPLETION)).strip()
    try:
        n = int(raw)
    except ValueError:
        print("invalid INKLING_MAX_COMPLETION", flush=True)
        return -1
    if n <= 0 or n > 8000:
        print("INKLING_MAX_COMPLETION out of range", flush=True)
        return -1
    return n


def main() -> int:
    max_tokens = _max_completion()
    if max_tokens < 0:
        return 1
    if not REQUEST_ID or not REQUEST_ID.isalnum():
        print("INKLING_REQUEST_ID required (alphanumeric)", flush=True)
        return 1
    try:
        os.remove(OUT_PATH)
    except FileNotFoundError:
        pass
    if not os.path.isfile(SPEC_PATH):
        print(f"spec missing: {SPEC_PATH}", flush=True)
        return 1
    spec = open(SPEC_PATH, encoding="utf-8").read()
    try:
        os.remove(SPEC_PATH)
    except OSError:
        pass
    url = f"{BASE}/chat/completions"
    body = json.dumps(
        {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": spec},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.2,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        print(f"inkling request failed: {exc}", flush=True)
        return 1
    choices = payload.get("choices") or []
    if not choices:
        print("no choices in response", flush=True)
        return 1
    choice = choices[0]
    finish = choice.get("finish_reason")
    if finish != "stop":
        print(f"finish_reason={finish!r} (want stop); not writing output", flush=True)
        return 1
    msg = choice.get("message") or {}
    text = (msg.get("content") or "").strip()
    if not text:
        print("empty content (reasoning-only or truncated)", flush=True)
        return 1
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"INKLING_CODE_HELP_OK:{REQUEST_ID}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())