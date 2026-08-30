"""Class image helpers: initials fallback and upload validation.

Image bytes themselves are stored on the ``classes`` row in PostgreSQL, so they
survive container rebuilds with the existing ``postgres-data`` volume.
"""

from __future__ import annotations

from pathlib import Path

_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}
_MAX_BYTES = 10_485_760  # 10 MB


def class_initials(name: str) -> str:
    """Return the two-character label shown when a class has no image."""
    compact = "".join(name.split())
    if not compact:
        return "?"
    return compact[:2].upper()


def validate_class_image(filename: str, data: bytes) -> str:
    """Return the MIME type for a valid class image upload.

    Raises:
        ValueError: If the type is unsupported, empty, or larger than 10 MB.
    """
    suffix = Path(filename).suffix.lower()
    mime = _MIME.get(suffix)
    if mime is None:
        raise ValueError("Please upload a PNG, JPEG, WEBP or GIF image.")
    if not data:
        raise ValueError("Please upload a non-empty image.")
    if len(data) > _MAX_BYTES:
        raise ValueError("Please keep the image under 10 MB.")
    return mime
