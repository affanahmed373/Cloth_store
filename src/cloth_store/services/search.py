"""Run a stylist request and optionally create dress photos."""

from __future__ import annotations

from pathlib import Path

from openai import OpenAI

from cloth_store.models import SuggestionResult
from cloth_store.services.generator import generate_dress_image
from cloth_store.services.stylist import suggest_dresses


def find_dresses(
    client: OpenAI,
    image_paths: list[Path],
    *,
    vision_model: str,
    image_model: str,
    count: int,
    audience: str,
    occasion: str,
    notes: str,
    make_images: bool,
    output_dir: Path,
) -> SuggestionResult:
    result = suggest_dresses(
        client,
        image_paths,
        model=vision_model,
        count=count,
        audience=audience,
        occasion=occasion,
        notes=notes,
    )
    if not make_images:
        return result

    for index, dress in enumerate(result.dresses, start=1):
        try:
            dress.image_path = str(
                generate_dress_image(
                    client,
                    dress,
                    image_paths,
                    model=image_model,
                    output_dir=output_dir,
                    index=index,
                )
            )
        except Exception as error:
            dress.image_error = str(error)
    return result
