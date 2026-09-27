"""Send a dress photo to an image API and save the mannequin shot."""

from __future__ import annotations

import base64
import urllib.request
from pathlib import Path

from openai import OpenAI

from cloth_store.services.library import instagram_stem, to_instagram_png, to_jpeg_buffer


def image_bytes(image: object) -> bytes:
    encoded = getattr(image, "b64_json", None)
    if encoded:
        return base64.b64decode(encoded)
    url = getattr(image, "url", None)
    if not url:
        raise RuntimeError("The image API did not return a photo.")
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


def generate_mannequin_image(
    client: OpenAI,
    source: Path,
    prompt: str,
    *,
    model: str,
    output_dir: Path,
    suit_code: str,
) -> tuple[Path, Path]:
    if not prompt.strip():
        raise ValueError("The saved prompt is empty.")
    stem = instagram_stem(suit_code)
    upload = to_jpeg_buffer(source, max_side=1536)
    result = client.images.edit(
        model=model,
        image=upload,
        prompt=prompt,
        size="1024x1536",
        n=1,
    )
    images = result.data or []
    if not images:
        raise RuntimeError("The image API returned no photos.")

    output_dir.mkdir(parents=True, exist_ok=True)
    image_path = output_dir / f"{stem}.png"
    prompt_path = output_dir / f"{stem}.prompt.txt"
    image_path.write_bytes(to_instagram_png(image_bytes(images[0])))
    prompt_path.write_text(prompt.strip() + "\n", encoding="utf-8")
    return image_path, prompt_path
