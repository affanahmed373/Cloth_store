"""Ask a chat API for shop text about a dress photo."""

from __future__ import annotations

from pathlib import Path

from openai import OpenAI

from cloth_store.services.library import slug, to_data_url


def generate_marketing_text(
    client: OpenAI,
    source: Path,
    prompt: str,
    *,
    model: str,
    output_dir: Path,
    index: int,
) -> tuple[str, Path]:
    if not prompt.strip():
        raise ValueError("The saved prompt is empty.")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": to_data_url(source), "detail": "low"},
                    },
                ],
            }
        ],
    )
    text = (response.choices[0].message.content or "").strip()
    if not text:
        raise RuntimeError("The text API returned an empty reply.")

    output_dir.mkdir(parents=True, exist_ok=True)
    text_path = output_dir / f"{index:02d}-{slug(source.stem)}.txt"
    text_path.write_text(text + "\n", encoding="utf-8")
    return text, text_path
