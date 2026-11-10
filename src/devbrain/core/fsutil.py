"""Filesystem helpers shared across devbrain modules."""

import json
import os
from pathlib import Path
import tempfile
from typing import Any


def atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    """Write text to a temp file in the same directory, then replace the target.

    A crash or concurrent reader never observes a half-written file.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(text)
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def atomic_write_json(path: Path, data: Any, indent: int = 2) -> None:
    """Serialize data as JSON and write it atomically."""
    atomic_write_text(path, json.dumps(data, indent=indent, ensure_ascii=False))
