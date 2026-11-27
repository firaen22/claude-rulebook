"""Start Inkling 2 Mini (GGUF) OpenAI-compatible server on Colab VM.

Run via: colab exec -s SESSION -f scripts/colab_vm_start_inkling_25_mini.py

Exposes http://127.0.0.1:8092/v1 — model id inkling-2.5-mini (alias for coding helpers).
"""
from __future__ import annotations

import glob
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.error
import urllib.request

os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"

# Pinned 2026-11-27 after live Colab sm_75 download; override with INKLING_LLAMA_TAG=.
PINNED_TAG = os.environ.get("INKLING_LLAMA_TAG", "b12757-mix-ef2df21")
FALLBACK_TAG = PINNED_TAG
RELEASES_API = "https://api.github.com/repos/unslothai/llama.cpp/releases/latest"
ASSET_PREFIX = "https://github.com/unslothai/llama.cpp/releases/download"
REQUIRED_SM = "75"
ROOT = "/content" if os.path.isdir("/content") else "/tmp"
BIN_DIR = os.path.join(ROOT, "llama.cpp")
ARCHIVE = os.path.join(ROOT, "llama-unsloth-cuda12.tgz")

REPO_ID = "unsloth/Inkling-2-Mini-GGUF"
MODEL_FILE = "Inkling-2-Mini-UD-Q3_K_XL.gguf"
MMPROJ_FILE = "mmproj-F16.gguf"
LOCAL_DIR = os.path.join(ROOT, "Inkling-2-Mini-GGUF")
HOST = os.environ.get("INKLING_HOST", os.environ.get("ELKO_INKLING_HOST", "127.0.0.1"))
PORT = int(os.environ.get("INKLING_PORT", os.environ.get("ELKO_INKLING_PORT", "8092")))
MODEL_ALIAS = os.environ.get("INKLING_MODEL", os.environ.get("ELKO_INKLING_MODEL", "inkling-2.5-mini"))
N_CTX = int(os.environ.get("INKLING_CTX", os.environ.get("ELKO_INKLING_CTX", "8192")))
N_GPU_LAYERS = 99
N_CPU_MOE = int(os.environ.get("ELKO_INKLING_N_CPU_MOE", "4"))
LOG = os.path.join(ROOT, "inkling-llama-server.log")
PID_FILE = os.path.join(ROOT, "inkling-llama-server.pid")
TAG_STAMP = os.path.join(ROOT, "inkling_llama_bundle.tag")


def _http_json(url: str) -> dict:
    req = urllib.request.Request(
        url, headers={"Accept": "application/vnd.github+json", "User-Agent": "elko-inkling-setup"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def _download(url: str, dest: str) -> None:
    print(f"downloading {url}", flush=True)
    part = f"{dest}.part"
    try:
        urllib.request.urlretrieve(url, part)
        os.replace(part, dest)
    finally:
        if os.path.isfile(part):
            try:
                os.remove(part)
            except OSError:
                pass


def _server_bundle_ok(server: str) -> bool:
    lib_dir = os.path.dirname(server)
    return os.path.isfile(os.path.join(lib_dir, "libllama-server-impl.so"))


def resolve_cuda12_sm75_asset(tag: str) -> tuple[str, str]:
    manifest_url = f"{ASSET_PREFIX}/{tag}/llama-prebuilt-manifest.json"
    manifest = _http_json(manifest_url)
    candidates = []
    for art in manifest.get("artifacts") or []:
        if art.get("install_kind") != "linux-cuda" or art.get("runtime_line") != "cuda12":
            continue
        sms = [str(s) for s in (art.get("supported_sms") or [])]
        if REQUIRED_SM not in sms:
            continue
        name = art.get("asset_name") or ""
        if not name.endswith(".tar.gz"):
            continue
        rank = 0 if art.get("coverage_class") == "portable" else 1
        candidates.append((rank, name))
    if not candidates:
        raise SystemExit(f"No CUDA12 sm_{REQUIRED_SM} asset in {manifest_url}")
    candidates.sort()
    name = candidates[0][1]
    return name, f"{ASSET_PREFIX}/{tag}/{name}"


def _find_llama_servers() -> list[str]:
    return sorted(
        p for p in glob.glob(os.path.join(ROOT, "**/llama-server"), recursive=True) if os.path.isfile(p)
    )


def _read_stamp() -> tuple[str, str] | None:
    if not os.path.isfile(TAG_STAMP):
        return None
    lines = open(TAG_STAMP, encoding="utf-8").read().splitlines()
    if len(lines) < 2:
        return None
    return lines[0].strip(), lines[1].strip()


def _write_stamp(tag: str, server: str) -> None:
    with open(TAG_STAMP, "w", encoding="utf-8") as f:
        f.write(f"{tag}\n{server}\n")


def _bundle_root() -> str:
    return os.path.join(ROOT, "inkling-llama-bundle")


def _path_inside_bundle(path: str) -> bool:
    bundle_real = os.path.realpath(_bundle_root())
    try:
        target_real = os.path.realpath(path)
    except OSError:
        return False
    return target_real == bundle_real or target_real.startswith(bundle_real + os.sep)


def _pick_server(tag: str) -> str | None:
    if not tag or tag in {".", ".."}:
        return None
    stamped = _read_stamp()
    if not stamped or stamped[0] != tag:
        return None
    path = stamped[1]
    if not _path_inside_bundle(path):
        return None
    if os.path.isfile(path) and _server_bundle_ok(path):
        return path
    return None


def ensure_llama_server() -> str:
    track_latest = os.environ.get("INKLING_LLAMA_TRACK_LATEST", "").strip() == "1"
    if track_latest:
        try:
            latest = _http_json(RELEASES_API)
            tag = latest.get("tag_name") or FALLBACK_TAG
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            tag = FALLBACK_TAG
    else:
        tag = PINNED_TAG
        print(f"using pinned llama.cpp tag {tag} (set INKLING_LLAMA_TRACK_LATEST=1 to follow releases/latest)", flush=True)
    stale = os.path.join(BIN_DIR, "llama-server")
    if os.path.isfile(stale) and not _server_bundle_ok(stale):
        try:
            os.remove(stale)
        except OSError:
            pass
    server = _pick_server(tag)
    if server is None:
        _, asset_url = resolve_cuda12_sm75_asset(tag)
        if os.path.isfile(TAG_STAMP):
            try:
                os.remove(TAG_STAMP)
            except OSError:
                pass
        if os.path.isfile(ARCHIVE):
            try:
                os.remove(ARCHIVE)
            except OSError:
                pass
        safe_tag = re.sub(r"[^a-zA-Z0-9._-]", "_", tag)
        if not safe_tag or safe_tag in {".", ".."}:
            raise SystemExit(f"invalid llama tag for extract dir: {tag!r}")
        bundle_root = _bundle_root()
        extract_dir = os.path.join(bundle_root, safe_tag)
        os.makedirs(bundle_root, exist_ok=True)
        bundle_real = os.path.realpath(bundle_root)
        extract_real = os.path.realpath(extract_dir)
        if extract_real != bundle_real and not extract_real.startswith(bundle_real + os.sep):
            raise SystemExit(f"refusing extract outside bundle root: {extract_dir}")
        os.makedirs(extract_dir, exist_ok=True)
        _download(asset_url, ARCHIVE)
        with tarfile.open(ARCHIVE, "r:gz") as tar:
            tar.extractall(extract_dir, filter="data")
        candidates = [
            p
            for p in glob.glob(os.path.join(extract_dir, "**/llama-server"), recursive=True)
            if os.path.isfile(p) and _path_inside_bundle(p) and _server_bundle_ok(p)
        ]
        if not candidates:
            raise SystemExit(
                f"llama-server bundle missing libllama-server-impl.so under {extract_dir} after extract"
            )
        server = sorted(candidates)[0]
        if not _path_inside_bundle(server):
            raise SystemExit(f"refusing llama-server outside bundle: {server}")
        _write_stamp(tag, server)
    if server is None:
        raise SystemExit("llama-server bundle missing libllama-server-impl.so beside binary — re-download or fix extract")
    if stale != server and os.path.isfile(stale):
        try:
            os.remove(stale)
        except OSError:
            pass
    os.chmod(server, os.stat(server).st_mode | 0o111)
    print(f"llama-server: {server}", flush=True)
    return server


def ensure_model() -> tuple[str, str]:
    os.makedirs(LOCAL_DIR, exist_ok=True)
    model_path = os.path.join(LOCAL_DIR, MODEL_FILE)
    mmproj_path = os.path.join(LOCAL_DIR, MMPROJ_FILE)
    if os.path.isfile(model_path) and os.path.isfile(mmproj_path):
        return model_path, mmproj_path
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-q", "huggingface_hub>=0.34"],
    )
    hf = shutil.which("hf") or shutil.which("huggingface-cli")
    if not hf:
        raise SystemExit("hf CLI missing")
    subprocess.check_call(
        [hf, "download", REPO_ID, MODEL_FILE, MMPROJ_FILE, "--local-dir", LOCAL_DIR],
        env={**os.environ, "HF_HUB_DISABLE_IMPLICIT_TOKEN": "1"},
    )
    if not os.path.isfile(model_path) or not os.path.isfile(mmproj_path):
        raise SystemExit("GGUF download failed")
    print(f"model {model_path} ({os.path.getsize(model_path) / 1024**3:.2f} GB)", flush=True)
    return model_path, mmproj_path


def ld_env(server: str) -> dict:
    libs: list[str] = []
    for pattern in (
        "/usr/local/cuda*/lib64",
        "/usr/lib/x86_64-linux-gnu",
        "/usr/local/lib/python*/dist-packages/nvidia/cuda_runtime/lib",
        "/usr/local/lib/python*/dist-packages/nvidia/cublas/lib",
    ):
        libs.extend(p for p in glob.glob(pattern) if os.path.isdir(p))
    for pkg_name in ("nvidia.cuda_runtime", "nvidia.cublas"):
        try:
            pkg = importlib.import_module(pkg_name)
            lib_dir = os.path.join(pkg.__path__[0], "lib")
            if os.path.isdir(lib_dir):
                libs.append(lib_dir)
        except ImportError:
            pass
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = ":".join([os.path.dirname(server), BIN_DIR, *libs, env.get("LD_LIBRARY_PATH", "")])
    env["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
    return env


def stop_existing() -> None:
    if os.path.isfile(PID_FILE):
        try:
            pid = int(open(PID_FILE, encoding="utf-8").read().strip())
            os.kill(pid, 15)
            time.sleep(2)
        except (OSError, ValueError):
            pass
        try:
            os.remove(PID_FILE)
        except OSError:
            pass


def wait_ready(url: str, proc: subprocess.Popen, timeout: float = 600.0) -> None:
    import urllib.request

    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            raise SystemExit(f"llama-server exited rc={proc.returncode} — see {LOG}")
        try:
            with urllib.request.urlopen(f"{url}/v1/models", timeout=5) as resp:
                if resp.status == 200:
                    if proc.poll() is not None:
                        raise SystemExit(f"llama-server exited rc={proc.returncode} after /v1/models — see {LOG}")
                    return
        except Exception:
            time.sleep(3)
    raise SystemExit(f"server not ready at {url} after {timeout}s — see {LOG}")


def main() -> int:
    try:
        import torch

        if not torch.cuda.is_available():
            raise SystemExit("Need T4 GPU runtime (colab new --gpu T4)")
        print("GPU:", torch.cuda.get_device_name(0), flush=True)
    except ImportError:
        raise SystemExit("torch missing — refuse to provision on unverified runtime (need T4 GPU VM)")

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-q", "nvidia-cuda-runtime-cu12", "nvidia-cublas-cu12"],
    )

    server_bin = ensure_llama_server()
    model_path, mmproj_path = ensure_model()
    env = ld_env(server_bin)
    stop_existing()

    cmd = [
        server_bin,
        "--model",
        model_path,
        "--mmproj",
        mmproj_path,
        "--jinja",
        "-ngl",
        str(N_GPU_LAYERS),
        "--n-cpu-moe",
        str(N_CPU_MOE),
        "-c",
        str(N_CTX),
        "-fa",
        "auto",
        "--parallel",
        "1",
        "--temp",
        "1.0",
        "--top-p",
        "1.0",
        "--top-k",
        "0",
        "--min-p",
        "0.0",
        "--host",
        HOST,
        "--port",
        str(PORT),
        "--alias",
        MODEL_ALIAS,
    ]
    print("starting:", " ".join(cmd), flush=True)
    log_f = open(LOG, "w", encoding="utf-8")
    proc = subprocess.Popen(cmd, env=env, stdout=log_f, stderr=subprocess.STDOUT)
    with open(PID_FILE, "w", encoding="utf-8") as f:
        f.write(str(proc.pid))

    base = f"http://127.0.0.1:{PORT}"
    wait_ready(base, proc)
    print(f"READY {base}/v1 model={MODEL_ALIAS} pid={proc.pid} log={LOG}", flush=True)
    print("Set on VM: INKLING_BASE_URL=http://127.0.0.1:{}/v1".format(PORT), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())