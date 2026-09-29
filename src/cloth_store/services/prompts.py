"""Saved prompts, plus the shop notes added for one run."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DEFAULT_IMAGE_PROMPT = """Use all uploaded images as garment references. They show different views of the same Pakistani outfit.

Display the outfit on a realistic female fashion mannequin, not on a real person and not on a generated human model. Use one full-body store-display mannequin with a neutral mannequin face, no living skin texture, no real human identity, and no face copied from anyone in the garment-reference images. Keep the mannequin standing straight and facing the camera.

Recreate the outfit exactly as shown in the uploaded garment-reference images. Preserve the exact colors, fabric, floral print, embroidery, stitching, neck design, neckline shape, collar, buttons, front opening, sleeve design, sleeve length, shirt length, borders, hem, bottom, and any dupatta only if a dupatta is actually present. Do not redesign, simplify, recolor, or reinterpret any part of the outfit.

Decide the neck design only from the reference photos. Copy that neck design exactly: depth, width, shape (round, V, square, boat, keyhole, high collar, or whatever is shown), embroidery or lace around the neck, collar, buttons, placket, front slit or opening, and finishing. Do not invent a different neckline, do not deepen or close the neck, and do not add or remove neck embroidery that is not in the photos.

First decide whether a dupatta exists in the reference photos. Check every uploaded photo. If the shop outfit details say Dupatta: yes or Dupatta: no, follow that. If they say information not available, decide only from the photos. If any photo clearly shows a dupatta, include it. If no photo shows a dupatta, do not invent one and do not drape any scarf, shawl, or extra fabric over the shoulders. Keep only the pieces that are actually shown. Never assume a dupatta by default.

Keep the same number of pieces shown in the reference images. If the shop outfit details name how many pieces (2 or 3), follow that exact count. If they say information not available, decide from the photos. A three-piece outfit is a kameez or shirt, a bottom, and a dupatta, and must be used only when all three are visible. A two-piece outfit must include only the two pieces actually shown. Never turn a two-piece set into a three-piece set by adding a dupatta.

Keep the bottom type exactly as shown. If the shop outfit details name shalwar or trouser, follow that. If they say information not available, decide from the photos. If it is a shalwar, keep it loose through the legs. If it is a trouser, keep it straight and tailored. Do not turn a shalwar into trousers or trousers into a shalwar. Do not add elastic ankle cuffs unless they are clearly visible in the reference. A gathered elastic waist does not mean the ankle is elastic. Never assume shalwar or trouser by default.

When a dupatta is present in the references, keep it exactly as shown, including its color, print, transparency, border, embroidery, width, length, and fabric. Drape it naturally on the mannequin without covering or changing the neck design, sleeves, shirt embroidery, bottom shape, or important garment details. When no dupatta is present, leave the neck, shoulders, and chest clear of any extra fabric.

Create one realistic, premium Pakistani clothing e-commerce catalog photograph. Show one full outfit on one female fashion mannequin in one single frame. The mannequin must stand facing the camera with a simple straight display pose, with both arms and both feet visible.

Safe full-body framing is mandatory. Pull the camera farther back so the whole mannequin and outfit fit comfortably inside the picture with clear empty margin on every side. Do not use a zoomed-in, tight, or cropped fashion crop. Center the mannequin horizontally and vertically. Show the entire mannequin from the top of the head to the soles of both shoes or feet. Leave generous empty background space above the head and visible floor beneath the feet. Keep at least 12 to 15 percent of the image height as empty space above the head and at least 10 to 12 percent as visible floor below the feet. Keep at least 10 percent empty background on the left and right of the mannequin and of any dupatta. The mannequin, outfit, hands, feet, shoes, and any dupatta must sit fully inside the safe area. Nothing may touch, cross, or be cut by the edges of the frame.

The entire mannequin head, neck design, shoulders, hands, sleeves, shirt hem, trouser or shalwar hem, ankles, shoes or feet must be fully visible inside the frame with margin around them. If a dupatta is present, its trailing end and border must also remain well inside the frame, not near the sides.

Use one vertical 4:5 Instagram portrait composition. Use a realistic professional photo studio with a warm soft off-white seamless wall that curves naturally into a light floor. Add soft even daylight, natural shadows, and a gentle contact shadow beneath both feet. Use high-end fashion catalog photography with a sharp, realistic camera look.

The fabric must look truly photographic and realistic. Show natural cloth drape, realistic folds, detailed stitching, accurate embroidery, visible textile texture, and correct garment proportions on the mannequin. The support must clearly read as a mannequin, not a real person. Avoid plastic-looking fabric, illustration style, 3D render style, or artificial shine.

No collage, no grid, no multiple mannequins, no real person, no living model, no generated human face, no human skin, no duplicate subject, no different outfit, no invented neckline, no changed neck design, no invented dupatta, no missing dupatta when one is shown, no missing garment piece, no extra garment piece, no wrong bottom type, no changed sleeve length, no extra pockets, no added ankle cuffs, no cropped head, no cropped hands, no cropped feet, no missing shoes or feet, no feet near or touching the bottom edge, no head near or touching the top edge, no cropped dupatta, no clothing near or touching side borders, no tight framing, no close-up framing, no partial body shot, no subject overflowing the frame, no flat pure-white cutout background, no busy room, no text, no watermark, no logo, no label, and no price."""

DEFAULT_TEXT_PROMPT = """Write one Instagram caption for the Pakistani outfit in the photos.
The photos are different views of the same outfit. Use all of them, and write a single caption, not one caption per photo.
This caption is for Instagram. It can also be reused on the related Facebook post.
Follow this layout. Change the description so it matches the photos, and use the suit code from the line that starts with "Suit code:".
Put that same code after "Code:" in the first line and again in "mention Code". Do not invent a different code.
Keep the shop name, the address, the emojis, the closing line, and the disclaimer.

✨ **New Arrival | Code: CODE** ✨

DESCRIPTION

📍 Available at **Z.J. Mode**
Münzstr. 19, 47051 Duisburg, Deutschland

To order or ask about price, size, and availability:
💌 Send us a DM and mention **Code CODE**
📦 Delivery is also available — DM us for delivery details
🏬 Or visit us in store at **Z.J. Mode, Duisburg**

Apna style, Pardesi style ✨

⚠️ The actual item may differ slightly from the photo.

HASHTAGS

Write DESCRIPTION as one paragraph in this style:
A rich maroon embroidered suit with delicate floral detailing, elegant embroidered sleeve cuffs, matching plain trousers, and a soft matching dupatta. The graceful tassel detail and subtle shimmer make this a beautiful choice for Eid, dawats, family gatherings, weddings, and special occasions. ❤️✨
Describe only what is visible. State the pieces you can see.
Say whether the bottom is a shalwar or a trouser. A shalwar is loose through the leg. A trouser is a straighter pant. If the shop outfit details name shalwar or trouser, follow that. If they say information not available, decide only from the photos and never assume either by default.
Elastic gathered at the waist or abdomen is the trouser waist. Do not call that elastic at the foot.
The opening at the leg is usually a plain hem. Mention an elastic cuff at the ankle only when the photos clearly show one.
Describe the neck design only as it appears in the photos. Do not invent a different neckline.
First check whether a dupatta is visible in any photo. Mention a dupatta only when one is shown, or when the shop outfit details say Dupatta: yes. Do not invent a dupatta. If the shop outfit details say Dupatta: no, do not mention a dupatta. If they say information not available, decide only from the photos and never assume a dupatta by default.
Say whether the set is three-piece or two-piece, and include that piece count in the DESCRIPTION (for example "2-piece" or "3-piece"). If the shop outfit details name how many pieces, follow that and state it clearly. If they say information not available, decide only from the photos and still say the piece count.
A three-piece set is a kameez or shirt, a bottom, and a dupatta.
A two-piece set is the kameez or shirt plus one other garment. Say whether that other garment is a dupatta or a bottom (shalwar or trouser).
Do not call it three-piece when a dupatta or a bottom is missing, and do not mention a piece that is not in the photo.
Do not invent a price.
Keep the disclaimer exactly as written: "The actual item may differ slightly from the photo." Do not drop it, rewrite it, or move it.
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


NOT_SET = "Not set"
DUPATTA_OPTIONS = (NOT_SET, "Yes", "No")
PIECE_OPTIONS = (NOT_SET, "2 pieces", "3 pieces")
BOTTOM_OPTIONS = (NOT_SET, "Shalwar", "Trouser")


@dataclass(frozen=True)
class OutfitDetails:
    dupatta: str = NOT_SET
    pieces: str = NOT_SET
    bottom: str = NOT_SET


def format_outfit_details(details: OutfitDetails | None) -> str:
    """Shop overrides for the run. Unset fields stay information not available."""
    chosen = details or OutfitDetails()
    lines = ["Outfit details from the shop:"]

    if chosen.dupatta == "Yes":
        lines.append(
            "Dupatta: yes. This outfit has a dupatta. Include the dupatta exactly as shown."
        )
    elif chosen.dupatta == "No":
        lines.append(
            "Dupatta: no. This outfit has no dupatta. Do not invent a dupatta, scarf, or shawl."
        )
    else:
        lines.append(
            "Dupatta: information not available. Decide only from the photos. "
            "Do not assume a dupatta by default."
        )

    if chosen.pieces == "2 pieces":
        lines.append(
            "How many pieces: 2. This is a two-piece outfit. Keep only the two garments shown. "
            "Do not add a third piece. State that it is a 2-piece set in the caption."
        )
    elif chosen.pieces == "3 pieces":
        lines.append(
            "How many pieces: 3. This is a three-piece outfit. Include the kameez or shirt, "
            "the bottom, and the dupatta when the dupatta field allows it. "
            "State that it is a 3-piece set in the caption."
        )
    else:
        lines.append(
            "How many pieces: information not available. Decide two-piece or three-piece "
            "only from the photos, then state that piece count in the caption."
        )

    if chosen.bottom == "Shalwar":
        lines.append(
            "Bottom: shalwar. Keep a loose shalwar through the legs. Do not turn it into trousers."
        )
    elif chosen.bottom == "Trouser":
        lines.append(
            "Bottom: trouser. Keep a straighter trouser. Do not turn it into a shalwar."
        )
    else:
        lines.append(
            "Bottom: information not available. Decide shalwar or trouser only from the photos. "
            "Do not assume either by default."
        )

    lines.append(
        "When a field above is definite, follow it. When it says information not available, "
        "use only what is visible in the photos."
    )
    return "\n".join(lines)


def compose_prompt(
    general: str,
    extra: str,
    suit_code: str = "",
    outfit: OutfitDetails | None = None,
) -> str:
    base = general.strip()
    if not base:
        raise ValueError("The saved prompt is empty.")
    parts = [base]
    code = suit_code.strip()
    if code:
        parts.append(f"Suit code: {code}")
    parts.append(format_outfit_details(outfit))
    notes = extra.strip()
    if notes:
        parts.append(f"Shop notes:\n{notes}")
    return "\n\n".join(parts)
