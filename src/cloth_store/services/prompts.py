"""Saved prompts, plus the shop notes added for one run."""

from __future__ import annotations

from pathlib import Path

DEFAULT_IMAGE_PROMPT = """Use the uploaded photo as the garment reference for an online clothing shop.
Keep the same Pakistani dress: colors, print, embroidery, fabric, and cut.
Show that full outfit front view, standing straight, as a catalog product photo.
Use either a fashion mannequin or a generated catalog model wearing the outfit. A model is allowed. Do not force a mannequin.
Plain light studio background, soft even lighting.
No text, no watermark, no logo, no price. Do not copy a real person's face.
Match the pieces in the photo. Do not add or remove a garment.
If the bottom is a shalwar, keep a shalwar. If it is a trouser, keep a trouser.
Keep the opening near the foot as it is: a free open hem, or an elastic gathered cuff. Do not change one into the other.
A three-piece outfit is a kameez or shirt, a bottom, and a dupatta. Show all three only when all three are in the photo.
A two-piece outfit has only two garments: the kameez or shirt, plus either a dupatta or a bottom (shalwar or trouser), whichever pair is actually in the photo."""

DEFAULT_TEXT_PROMPT = """Write marketing text for an online shop listing of the Pakistani dress in the photo.
Describe only what is visible: outfit type, colors, pattern, and fabric when it is clear.
Return a short product title, two sentences for the product page, and five hashtags.
Do not invent a price, a brand name, or details that are not in the photo.
State the pieces you can see.
Say whether the bottom is a shalwar or a trouser.
Say whether the opening near the foot is free (an open hem) or elastic (a gathered cuff).
Say whether the set is three-piece or two-piece.
A three-piece set is a kameez or shirt, a bottom, and a dupatta.
A two-piece set is the kameez or shirt plus one other garment. Say whether that other garment is a dupatta or a bottom (shalwar or trouser).
Do not call it three-piece when a dupatta or a bottom is missing, and do not mention a piece that is not in the photo."""


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
