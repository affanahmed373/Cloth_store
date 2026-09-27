"""Saved prompts, plus the shop notes added for one run."""

from __future__ import annotations

from pathlib import Path

DEFAULT_IMAGE_PROMPT = """Use the uploaded photo as the garment reference for an online clothing shop.
Keep the same Pakistani dress: colors, print, embroidery, fabric, and cut.
Show that full outfit on a headless fashion mannequin (dress dummy), front view, standing straight.
Plain light studio background, soft even lighting, catalog product photo.
No person, no face, no hands, no text, no watermark, no logo, no price."""

DEFAULT_TEXT_PROMPT = """Write marketing text for an online shop listing of the Pakistani dress in the photo.
Describe only what is visible: outfit type, colors, pattern, and fabric when it is clear.
Return a short product title, two sentences for the product page, and five hashtags.
Do not invent a price, a brand name, or details that are not in the photo."""


def load_prompt(path: Path, default: str) -> str:
    if not path.is_file():
        save_prompt(path, default)
    return path.read_text(encoding="utf-8").strip()


def save_prompt(path: Path, text: str) -> None:
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("The prompt is empty.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(cleaned + "\n", encoding="utf-8")


def compose_prompt(general: str, extra: str) -> str:
    base = general.strip()
    notes = extra.strip()
    if not base:
        raise ValueError("The saved prompt is empty.")
    if not notes:
        return base
    return f"{base}\n\nShop notes:\n{notes}"
