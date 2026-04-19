import os
from pathlib import Path


def atomic_write(path: Path, content: str) -> None:
    """Write content to a .tmp file, verify it, then replace the target atomically."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    if tmp.stat().st_size == 0:
        tmp.unlink()
        raise RuntimeError(f"atomic_write: temp file for {path} is empty, aborting")
    os.replace(tmp, path)
