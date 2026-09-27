"""Local photo folder helpers."""

from __future__ import annotations

import base64
import re
from io import BytesIO
from pathlib import Path

from PIL import Image

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_REFERENCE_IMAGES = 4


def list_images(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def to_jpeg_buffer(path: Path, max_side: int) -> BytesIO:
    with Image.open(path) as image:
        converted = image.convert("RGB")
        converted.thumbnail((max_side, max_side))
        buffer = BytesIO()
        buffer.name = "reference.jpg"
        converted.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        return buffer


def to_data_url(path: Path) -> str:
    encoded = base64.b64encode(to_jpeg_buffer(path, max_side=1024).getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cleaned[:40] or "dress"
