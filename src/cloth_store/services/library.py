"""Local photo folder helpers."""

from __future__ import annotations

import base64
import re
from io import BytesIO
from pathlib import Path

from PIL import Image

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


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


INSTAGRAM_SIZE = (1080, 1350)


def instagram_stem(suit_code: str) -> str:
    cleaned = re.sub(r"[^\w.-]+", "-", suit_code.strip()).strip(".-")
    if not cleaned:
        raise ValueError("Enter a suit code.")
    return f"instaimage-{cleaned}"


def to_instagram_png(raw: bytes) -> bytes:
    """Center-crop to 4:5 and resize to the Instagram portrait size."""
    try:
        with Image.open(BytesIO(raw)) as image:
            frame = image.convert("RGB")
    except Exception as error:
        raise RuntimeError("The image API did not return a photo that could be sized for Instagram.") from error

    width, height = frame.size
    if width < 1 or height < 1:
        raise RuntimeError("The image API did not return a photo that could be sized for Instagram.")

    target_ratio = 4 / 5
    if width / height > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        frame = frame.crop((left, 0, left + new_width, height))
    else:
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        frame = frame.crop((0, top, width, top + new_height))

    frame = frame.resize(INSTAGRAM_SIZE, Image.Resampling.LANCZOS)
    buffer = BytesIO()
    frame.save(buffer, format="PNG")
    return buffer.getvalue()
