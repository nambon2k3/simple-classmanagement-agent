"""Class rail avatars: an uploaded image, or the first two characters of the name."""

from __future__ import annotations

import base64
import os
import tempfile
from pathlib import Path

_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}
_MAX_BYTES = 512_000


def class_initials(name: str) -> str:
    """Return the two-character label shown when a class has no image."""
    compact = "".join(name.split())
    if not compact:
        return "?"
    return compact[:2].upper()


def icon_dir() -> Path:
    """Directory that stores uploaded class icons."""
    configured = os.environ.get("CLASS_ICON_DIR")
    if configured:
        path = Path(configured)
    else:
        path = Path(__file__).resolve().parents[2] / "data" / "class-icons"
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError:
        path = Path(tempfile.gettempdir()) / "class-icons"
        path.mkdir(parents=True, exist_ok=True)
    return path


def class_icon_data_uri(class_id: int, *, directory: Path | None = None) -> str | None:
    """Return a data URI for the class icon, if one has been uploaded."""
    folder = directory or icon_dir()
    for suffix, mime in _MIME.items():
        path = folder / f"{class_id}{suffix}"
        if path.is_file():
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            return f"data:{mime};base64,{encoded}"
    return None


def save_class_icon(
    class_id: int,
    filename: str,
    data: bytes,
    *,
    directory: Path | None = None,
) -> None:
    """Replace any existing icon for this class with the uploaded file."""
    suffix = Path(filename).suffix.lower()
    if suffix not in _MIME:
        raise ValueError("Please upload a PNG, JPEG, WEBP or GIF image.")
    if len(data) > _MAX_BYTES:
        raise ValueError("Please keep the class icon under 512 KB.")
    folder = directory or icon_dir()
    folder.mkdir(parents=True, exist_ok=True)
    for old_suffix in _MIME:
        old = folder / f"{class_id}{old_suffix}"
        if old.exists():
            old.unlink()
    (folder / f"{class_id}{suffix}").write_bytes(data)
