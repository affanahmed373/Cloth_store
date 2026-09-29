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
INSTAGRAM_PAD_COLOR = (245, 240, 232)
MAX_REFERENCE_PHOTOS = 10


def instagram_stem(suit_code: str) -> str:
    cleaned = re.sub(r"[^\w.-]+", "-", suit_code.strip()).strip(".-")
    if not cleaned:
        raise ValueError("Enter a suit code.")
    return f"instaimage-{cleaned}"


def to_instagram_png(raw: bytes) -> bytes:
    """Fit the full photo inside 4:5 without cropping the model."""
    try:
        with Image.open(BytesIO(raw)) as image:
            frame = image.convert("RGB")
    except Exception as error:
        raise RuntimeError("The image API did not return a photo that could be sized for Instagram.") from error

    width, height = frame.size
    if width < 1 or height < 1:
        raise RuntimeError("The image API did not return a photo that could be sized for Instagram.")

    target_width, target_height = INSTAGRAM_SIZE
    scale = min(target_width / width, target_height / height)
    new_width = max(1, int(round(width * scale)))
    new_height = max(1, int(round(height * scale)))
    fitted = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", INSTAGRAM_SIZE, INSTAGRAM_PAD_COLOR)
    left = (target_width - new_width) // 2
    top = (target_height - new_height) // 2
    canvas.paste(fitted, (left, top))

    buffer = BytesIO()
    canvas.save(buffer, format="PNG")
    return buffer.getvalue()
