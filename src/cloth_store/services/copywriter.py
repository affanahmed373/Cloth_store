"""Ask DeepSeek for one Instagram caption from the outfit photos."""

from __future__ import annotations

from pathlib import Path

from openai import OpenAI

from cloth_store.services.library import MAX_REFERENCE_PHOTOS, instagram_stem, to_data_url


def generate_marketing_text(
    client: OpenAI,
    sources: list[Path],
    prompt: str,
    *,
    model: str,
    output_dir: Path,
    suit_code: str,
) -> tuple[str, Path]:
    if not prompt.strip():
        raise ValueError("The saved prompt is empty.")
    if not sources:
        raise ValueError("Select at least one photo.")
    if len(sources) > MAX_REFERENCE_PHOTOS:
        raise ValueError(f"Select at most {MAX_REFERENCE_PHOTOS} photos.")
    content: list[dict[str, object]] = [{"type": "text", "text": prompt}]
    for source in sources:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": to_data_url(source), "detail": "low"},
            }
        )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": content}],
    )
    text = (response.choices[0].message.content or "").strip()
    if not text:
        raise RuntimeError("The text API returned an empty reply.")

    output_dir.mkdir(parents=True, exist_ok=True)
    text_path = output_dir / f"{instagram_stem(suit_code)}.txt"
    text_path.write_text(text + "\n", encoding="utf-8")
    return text, text_path
