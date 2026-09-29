"""Saved prompts, plus the shop notes added for one run."""

from __future__ import annotations

from pathlib import Path

DEFAULT_IMAGE_PROMPT = """Use all uploaded images as garment references. They show different views of the same Pakistani outfit.

Keep the same generated female catalog model from the current image. Preserve her exact face, hairstyle, skin tone, body proportions, age appearance, and overall identity. Do not replace the model, create a new face, use a mannequin, or copy the face of any person in the garment-reference images.

Recreate the outfit exactly as shown in the uploaded garment-reference images. Preserve the exact colors, fabric, floral print, embroidery, stitching, neckline, collar, buttons, front opening, sleeve design, sleeve length, shirt length, borders, hem, bottom, and dupatta. Do not redesign, simplify, recolor, or reinterpret any part of the outfit.

Copy the neckline exactly from the references. Keep its original shape, embroidery, collar, buttons, front slit or opening, and finishing. Do not invent a different neckline.

Keep the same number of pieces shown in the reference images. A three-piece outfit must include the kameez or shirt, bottom, and dupatta. A two-piece outfit must include only the two pieces actually shown.

Keep the bottom type exactly as shown. If it is a shalwar, keep it loose through the legs. If it is a trouser, keep it straight and tailored. Do not turn a shalwar into trousers or trousers into a shalwar. Do not add elastic ankle cuffs unless they are clearly visible in the reference. A gathered elastic waist does not mean the ankle is elastic.

Keep the dupatta exactly as shown, including its color, print, transparency, border, embroidery, width, and fabric. Drape it naturally without hiding the neckline, sleeves, shirt embroidery, bottom shape, or important details of the garment.

Create one realistic, premium Pakistani clothing e-commerce catalog photograph. Show one full outfit, on one female model, in one single frame. The model must stand naturally facing the camera, with a relaxed straight posture. Use a simple natural pose with both arms and both feet visible.

Safe full-body framing is mandatory. Use a slightly wide camera distance, not a zoomed-in view. Center the model horizontally and vertically. Show the entire body from the top of her hair to the soles of both shoes. Leave generous empty background space above her head and visible floor beneath her shoes. Keep at least 8 to 10 percent of the image height as empty space above the head and at least 6 to 8 percent as visible floor below the shoes. Keep comfortable space on both sides of the model and dupatta. Nothing may touch or be cropped by the edges of the frame.

The entire hairstyle, head, shoulders, hands, sleeves, shirt hem, trouser or shalwar hem, dupatta, ankles, shoes, and both feet must be fully visible. Ensure the trailing end and border of the dupatta remain inside the frame.

Use one vertical 4:5 Instagram portrait composition. Use a realistic professional photo studio with a warm soft off-white seamless wall that curves naturally into a light floor. Add soft even daylight, natural shadows, and a gentle contact shadow beneath both feet. Use high-end fashion catalog photography with a sharp, realistic camera look.

The model and fabric must look truly photographic and realistic. Show natural cloth drape, realistic folds, detailed stitching, accurate embroidery, visible textile texture, correct garment proportions, realistic hands, and natural feet. Avoid plastic-looking fabric, overly smooth skin, illustration style, 3D render style, or artificial shine.

No collage, no grid, no multiple models, no mannequin, no duplicate person, no changed face, no different outfit, no invented neckline, no missing garment piece, no extra garment piece, no wrong bottom type, no changed sleeve length, no extra pockets, no added ankle cuffs, no cropped head, no cut-off hair, no cropped hands, no cropped feet, no missing shoes, no feet touching the bottom edge, no head touching the top edge, no cropped dupatta, no clothing touching side borders, no close-up framing, no partial body shot, no flat pure-white cutout background, no busy room, no text, no watermark, no logo, no label, and no price."""

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
Say whether the bottom is a shalwar or a trouser. A shalwar is loose through the leg. A trouser is a straighter pant.
Elastic gathered at the waist or abdomen is the trouser waist. Do not call that elastic at the foot.
The opening at the leg is usually a plain hem. Mention an elastic cuff at the ankle only when the photos clearly show one.
Describe the neckline only as it appears.
Say whether the set is three-piece or two-piece.
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
