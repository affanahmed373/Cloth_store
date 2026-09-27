"""Ask ChatGPT for Pakistani outfits that match reference photos."""

from __future__ import annotations

from pathlib import Path

from openai import OpenAI

from cloth_store.models import SuggestionResult
from cloth_store.services.library import MAX_REFERENCE_IMAGES, to_data_url

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


def build_instruction(count: int, audience: str, occasion: str, notes: str) -> str:
    instruction = (
        f"Suggest exactly {count} Pakistani outfits. "
        f"Audience: {audience}. Occasion focus: {occasion}."
    )
    if notes.strip():
        instruction += f" Shopper notes: {notes.strip()}"
    return instruction


def suggest_dresses(
    client: OpenAI,
    image_paths: list[Path],
    *,
    model: str,
    count: int,
    audience: str,
    occasion: str,
    notes: str,
) -> SuggestionResult:
    paths = image_paths[:MAX_REFERENCE_IMAGES]
    if not paths:
        raise ValueError("Choose at least one image.")

    content: list[dict[str, object]] = [
        {"type": "text", "text": build_instruction(count, audience, occasion, notes)}
    ]
    for path in paths:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": to_data_url(path), "detail": "low"},
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
    return SuggestionResult.from_payload(message)
