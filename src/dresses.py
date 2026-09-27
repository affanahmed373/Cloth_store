"""Turn local reference photos into Pakistani dress suggestions."""

from __future__ import annotations

import base64
import json
import re
from io import BytesIO
from pathlib import Path

from openai import OpenAI
from PIL import Image

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_REFERENCE_IMAGES = 4

SYSTEM_PROMPT = """You are a stylist for a Pakistani clothing store.
Study the reference photo(s): colors, pattern, fabric feel, formality, and mood.
Suggest ready-to-wear Pakistani outfits that fit what you see.

Return only JSON with this shape:
{
  "image_summary": "one or two sentences about the reference photos",
  "dresses": [
    {
      "name": "short product name",
      "category": "one of: lawn suit, chiffon suit, cotton shalwar kameez, anarkali, lehenga, saree, gharara, sharara, kurta, sherwani, waistcoat",
      "occasion": "casual, eid, wedding, party, or formal",
      "fabric": "fabric name",
      "colors": ["color", "color"],
      "description": "two sentences a shopper can picture",
      "why_it_matches": "one sentence tying it to the reference photos"
    }
  ]
}

Rules:
- Respect the requested count, audience, and occasion.
- If the audience is women, suggest women's outfits. If men, suggest men's outfits. If any, mix both.
- Keep every outfit modest and traditional or contemporary Pakistani fashion.
- Do not invent prices, shop names, or links.
- Do not describe the people in the photos beyond clothing, color, and style.
"""


def list_images(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def _jpeg_bytes(path: Path, max_side: int) -> BytesIO:
    with Image.open(path) as image:
        converted = image.convert("RGB")
        converted.thumbnail((max_side, max_side))
        buffer = BytesIO()
        buffer.name = "reference.jpg"
        converted.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        return buffer


def _data_url(path: Path) -> str:
    encoded = base64.b64encode(_jpeg_bytes(path, max_side=1024).getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def _clean_dress(item: object) -> dict[str, str | list[str]] | None:
    if not isinstance(item, dict):
        return None
    colors = item.get("colors") or []
    if isinstance(colors, str):
        colors = [colors]
    if not isinstance(colors, list):
        colors = []
    return {
        "name": str(item.get("name") or "Pakistani outfit").strip(),
        "category": str(item.get("category") or "shalwar kameez").strip(),
        "occasion": str(item.get("occasion") or "").strip(),
        "fabric": str(item.get("fabric") or "").strip(),
        "colors": [str(color).strip() for color in colors if str(color).strip()],
        "description": str(item.get("description") or "").strip(),
        "why_it_matches": str(item.get("why_it_matches") or "").strip(),
    }


def parse_suggestions(payload: str) -> dict[str, object]:
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("ChatGPT did not return a JSON object.")
    dresses = [_clean_dress(item) for item in data.get("dresses") or []]
    return {
        "image_summary": str(data.get("image_summary") or "").strip(),
        "dresses": [dress for dress in dresses if dress],
    }


def suggest_dresses(
    client: OpenAI,
    image_paths: list[Path],
    *,
    model: str,
    count: int,
    audience: str,
    occasion: str,
    notes: str,
) -> dict[str, object]:
    paths = image_paths[:MAX_REFERENCE_IMAGES]
    if not paths:
        raise ValueError("Choose at least one image.")

    instruction = (
        f"Suggest exactly {count} Pakistani outfits. "
        f"Audience: {audience}. Occasion focus: {occasion}."
    )
    if notes.strip():
        instruction += f" Shopper notes: {notes.strip()}"

    content: list[dict[str, object]] = [{"type": "text", "text": instruction}]
    for path in paths:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": _data_url(path), "detail": "low"},
            }
        )

    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        temperature=0.7,
    )
    message = response.choices[0].message.content or ""
    return parse_suggestions(message)


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:40] or "dress"


def _dress_prompt(dress: dict[str, object]) -> str:
    colors = dress.get("colors") or []
    color_text = ", ".join(colors) if isinstance(colors, list) else str(colors)
    return (
        "Create a new photorealistic fashion catalog photo of a modest Pakistani outfit. "
        f"Name: {dress.get('name')}. Category: {dress.get('category')}. "
        f"Fabric: {dress.get('fabric')}. Colors: {color_text}. "
        f"Occasion: {dress.get('occasion')}. {dress.get('description')} "
        "Use the colors, pattern, and mood of the reference photo. "
        "Show the full outfit clearly on a plain studio background. "
        "No text, no watermark, no logo."
    )


def _write_image(raw: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(base64.b64decode(raw))
    return destination


def generate_dress_image(
    client: OpenAI,
    dress: dict[str, object],
    reference_paths: list[Path],
    *,
    model: str,
    output_dir: Path,
    index: int,
) -> Path:
    prompt = _dress_prompt(dress)
    uploads = [_jpeg_bytes(path, max_side=1536) for path in reference_paths[:MAX_REFERENCE_IMAGES]]
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
    data = images[0]
    encoded = getattr(data, "b64_json", None)
    if not encoded:
        raise RuntimeError("The image model did not return image data.")
    filename = f"{index:02d}-{_slug(str(dress.get('name') or 'dress'))}.png"
    return _write_image(encoded, output_dir / filename)
