"""Create catalog photos for suggested Pakistani outfits."""

from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path

from openai import OpenAI

from cloth_store.models import Dress
from cloth_store.services.library import MAX_REFERENCE_IMAGES, slug, to_jpeg_buffer


def dress_prompt(dress: Dress) -> str:
    color_text = ", ".join(dress.colors)
    return (
        "Create a new photorealistic fashion catalog photo of a modest Pakistani outfit. "
        f"Name: {dress.name}. Category: {dress.category}. "
        f"Fabric: {dress.fabric}. Colors: {color_text}. "
        f"Occasion: {dress.occasion}. {dress.description} "
        "Use the colors, pattern, and mood of the reference photo. "
        "Show the full outfit clearly on a plain studio background. "
        "No text, no watermark, no logo."
    )


def write_image(raw: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(base64.b64decode(raw))
    return destination


def generate_dress_image(
    client: OpenAI,
    dress: Dress,
    reference_paths: list[Path],
    *,
    model: str,
    output_dir: Path,
    index: int,
) -> Path:
    prompt = dress_prompt(dress)
    uploads = [to_jpeg_buffer(path, max_side=1536) for path in reference_paths[:MAX_REFERENCE_IMAGES]]
    if not uploads:
        raise ValueError("Choose at least one image.")
    image_arg: BytesIO | list[BytesIO] = uploads[0] if len(uploads) == 1 else uploads
    try:
        result = client.images.edit(
            model=model,
            image=image_arg,
            prompt=prompt,
            size="1024x1024",
            quality="low",
            output_format="png",
        )
    except Exception as edit_error:
        try:
            result = client.images.generate(
                model=model,
                prompt=prompt,
                size="1024x1024",
                quality="low",
                output_format="png",
            )
        except Exception as generate_error:
            raise RuntimeError(
                f"Could not create a dress photo. Edit failed: {edit_error}. "
                f"Generate failed: {generate_error}."
            ) from generate_error

    images = result.data or []
    if not images:
        raise RuntimeError("The image model returned no photos.")
    encoded = getattr(images[0], "b64_json", None)
    if not encoded:
        raise RuntimeError("The image model did not return image data.")
    filename = f"{index:02d}-{slug(dress.name)}.png"
    return write_image(encoded, output_dir / filename)
