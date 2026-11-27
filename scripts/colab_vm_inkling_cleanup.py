"""Remove Colab VM artifacts listed in INKLING_RM_PATHS (comma-separated)."""
import os

paths = os.environ.get("INKLING_RM_PATHS", "").split(",")
for path in paths:
    path = path.strip()
    if not path:
        continue
    try:
        os.remove(path)
        print(f"removed {path}", flush=True)
    except FileNotFoundError:
        pass
    except OSError as exc:
        print(f"could not remove {path}: {exc}", flush=True)