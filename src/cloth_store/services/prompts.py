"""Saved prompts, plus the shop notes added for one run."""

from __future__ import annotations

from pathlib import Path

DEFAULT_IMAGE_PROMPT = """The uploaded photos are different views of the same outfit. Use every photo as the garment reference for an online clothing shop.
Keep the same Pakistani dress: colors, print, embroidery, fabric, and cut.
Show that full outfit front view, standing straight, as one realistic catalog photograph.
Do not make a collage or a grid. Show one person or mannequin, in one frame.
Use either a fashion mannequin or a generated catalog model wearing the outfit. A model is allowed. Do not force a mannequin.
The person or mannequin and the cloth must look photographic and real: natural fabric, real folds, and no plastic or illustrated look.
Copy the neckline exactly. Keep its shape, embroidery, buttons, collar, and opening. Do not invent a different neck.
Plain light studio background, soft even lighting.
No text, no watermark, no logo, no price. Do not copy a real person's face.
Match the pieces in the photo. Do not add or remove a garment.
If the bottom is a shalwar, keep a shalwar. If it is a trouser, keep a trouser.
A shalwar is loose through the leg. A trouser is a straighter pant. Do not turn one into the other.
Elastic gathered at the waist or abdomen is the trouser waist. It does not mean the ankles are elastic.
The opening at the leg is usually a plain hem, not an elastic cuff. Do not add elastic at the ankles unless the photos clearly show it there.
A three-piece outfit is a kameez or shirt, a bottom, and a dupatta. Show all three only when all three are in the photo.
A two-piece outfit has only two garments: the kameez or shirt, plus either a dupatta or a bottom (shalwar or trouser), whichever pair is actually in the photo.
Frame the shot as one vertical 4:5 Instagram portrait. Keep the full outfit inside the frame, with a little space above the head and below the feet."""

DEFAULT_TEXT_PROMPT = """Write one Instagram caption for the Pakistani outfit in the photos.
The photos are different views of the same outfit. Use all of them, and write a single caption, not one caption per photo.
This caption is for Instagram. It can also be reused on the related Facebook post.
Follow this layout. Change the description so it matches the photos, and use the suit code from the line that starts with "Suit code:".
Put that same code after "Code:" in the first line and again in "mention Code". Do not invent a different code.
Keep the shop name, the address, the emojis, and the closing line.

✨ **New Arrival | Code: CODE** ✨

DESCRIPTION

📍 Available at **Z.J. Mode**
Münzstr. 19, 47051 Duisburg, Deutschland

To order or ask about price, size, and availability:
💌 Send us a DM and mention **Code CODE**
📦 Delivery is also available — DM us for delivery details
🏬 Or visit us in store at **Z.J. Mode, Duisburg**

Apna style, Pardesi style ✨

HASHTAGS

Write DESCRIPTION as one paragraph in this style:
A rich maroon embroidered suit with delicate floral detailing, elegant embroidered sleeve cuffs, matching plain trousers, and a soft matching dupatta. The graceful tassel detail and subtle shimmer make this a beautiful choice for Eid, dawats, family gatherings, weddings, and special occasions. ❤️✨
Describe only what is visible. State the pieces you can see.
Say whether the bottom is a shalwar or a trouser. A shalwar is loose through the leg. A trouser is a straighter pant.
Elastic gathered at the waist or abdomen is the trouser waist. Do not call that elastic at the foot.
The opening at the leg is usually a plain hem. Mention an elastic cuff at the ankle only when the photos clearly show one.
Describe the neckline only as it appears.
Say whether the set is three-piece or two-piece.
A three-piece set is a kameez or shirt, a bottom, and a dupatta.
A two-piece set is the kameez or shirt plus one other garment. Say whether that other garment is a dupatta or a bottom (shalwar or trouser).
Do not call it three-piece when a dupatta or a bottom is missing, and do not mention a piece that is not in the photo.
Do not invent a price.
For HASHTAGS, keep #PardesiStyle #PakistaniFashionGermany #IndianFashionGermany #DuisburgFashion #DesiFashionGermany #PakistaniSuits #EidOutfit #WeddingWear #Duisburg #NRWFashion #PakistaniFashion #IndianEthnicWear and add a few that match the color and the outfit."""


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


def compose_prompt(general: str, extra: str, suit_code: str = "") -> str:
    base = general.strip()
    if not base:
        raise ValueError("The saved prompt is empty.")
    parts = [base]
    code = suit_code.strip()
    if code:
        parts.append(f"Suit code: {code}")
    notes = extra.strip()
    if notes:
        parts.append(f"Shop notes:\n{notes}")
    return "\n\n".join(parts)
