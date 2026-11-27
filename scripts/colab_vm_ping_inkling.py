"""Run on Colab VM via: colab exec -s SESSION -f .../colab_vm_ping_inkling.py"""
import json
import os
import urllib.error
import urllib.request

BASE = os.environ.get("INKLING_BASE_URL", "http://127.0.0.1:8092/v1").rstrip("/")
MODEL = os.environ.get("INKLING_MODEL", "inkling-2.5-mini")


def main() -> int:
    url = f"{BASE}/chat/completions"
    body = json.dumps(
        {
            "model": MODEL,
            "messages": [{"role": "user", "content": "Reply with exactly: inkling-ok"}],
            "max_tokens": 512,
            "temperature": 0,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        print(f"inkling unreachable at {url}: {exc}", flush=True)
        return 1
    choices = payload.get("choices") or []
    if not choices:
        print(f"no choices in response: {payload}", flush=True)
        return 1
    choice = choices[0]
    finish = choice.get("finish_reason")
    if finish != "stop":
        print(f"finish_reason={finish!r} (want stop)", flush=True)
        return 1
    msg = choice.get("message") or {}
    text = (msg.get("content") or "").strip()
    if not text:
        print("empty content (reasoning-only replies do not pass ping)", flush=True)
        return 1
    if text.strip() != "inkling-ok":
        print(f"unexpected ping reply: {text!r}", flush=True)
        return 2
    print("inkling-ok", flush=True)
    print("INKLING_PING_OK", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())