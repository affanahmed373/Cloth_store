from pathlib import Path

import pytest

from cloth_store.config import IMAGE_PROMPT_PATH, TEXT_PROMPT_PATH
from cloth_store.services.prompts import (
    DEFAULT_IMAGE_PROMPT,
    DEFAULT_TEXT_PROMPT,
    OutfitDetails,
    compose_prompt,
    format_outfit_details,
    load_prompt,
    save_prompt,
)


def test_checked_in_prompts_keep_the_piece_rules() -> None:
    image_prompt = load_prompt(IMAGE_PROMPT_PATH, DEFAULT_IMAGE_PROMPT)
    text_prompt = load_prompt(TEXT_PROMPT_PATH, DEFAULT_TEXT_PROMPT)
    assert image_prompt == DEFAULT_IMAGE_PROMPT
    assert text_prompt == DEFAULT_TEXT_PROMPT
    assert "The actual item may differ slightly from the photo." in text_prompt
    assert "12 to 15 percent" in image_prompt
    assert "subject overflowing the frame" in image_prompt
    assert "First decide whether a dupatta exists" in image_prompt
    assert "Decide the neck design only from the reference photos" in image_prompt
    assert "Do not invent a dupatta" in text_prompt
    assert "Describe the neck design only as it appears" in text_prompt
    assert "Never assume a dupatta by default" in image_prompt
    assert "fashion mannequin" in image_prompt
    assert "not on a real person" in image_prompt
    assert "no real person" in image_prompt
    assert "Sleeves are usually full long sleeves" in image_prompt
    assert "Sleeves are usually full long sleeves" in text_prompt
    assert "never assume a dupatta by default" in text_prompt
    for prompt in (image_prompt, text_prompt):
        assert "shalwar" in prompt
        assert "elastic" in prompt
        assert "two-piece" in prompt
        assert "dupatta" in prompt


def test_compose_prompt_adds_the_suit_code() -> None:
    text = compose_prompt("Write the listing.", "Eid launch", "1005")
    assert "Write the listing." in text
    assert "Suit code: 1005" in text
    assert "Shop notes:\nEid launch" in text
    assert "Pieces: information not available" not in text
    assert "How many pieces: information not available" in text
    assert "Dupatta: information not available" in text
    assert "Bottom: information not available" in text


def test_compose_prompt_uses_chosen_outfit_details() -> None:
    text = compose_prompt(
        "Show the dress.",
        "",
        outfit=OutfitDetails(dupatta="No", pieces="2 pieces", bottom="Trouser"),
    )
    assert "Dupatta: no." in text
    assert "How many pieces: 2." in text
    assert "Bottom: trouser." in text
    assert "Do not invent a dupatta" in text
    text3 = compose_prompt(
        "Show the dress.",
        "",
        outfit=OutfitDetails(pieces="3 pieces"),
    )
    assert "How many pieces: 3." in text3
    assert "3-piece set in the caption" in text3


def test_unset_outfit_details_are_not_a_yes() -> None:
    text = format_outfit_details(OutfitDetails())
    assert "Dupatta: information not available" in text
    assert "Do not assume a dupatta by default" in text
    assert "Dupatta: yes" not in text


def test_compose_prompt_appends_shop_notes() -> None:
    assert "Shop notes:\nEid launch" in compose_prompt("Show the dress.", "Eid launch")
    bare = compose_prompt("Show the dress.", "  ")
    assert bare.startswith("Show the dress.")
    assert "Shop notes:" not in bare
    assert "information not available" in bare


def test_compose_prompt_rejects_an_empty_general_prompt() -> None:
    with pytest.raises(ValueError, match="empty"):
        compose_prompt("  ", "notes")


def test_save_prompt_writes_a_file_and_rejects_blank_text(tmp_path: Path) -> None:
    path = tmp_path / "prompts" / "image_prompt.txt"
    save_prompt(path, "  Keep the embroidery.  ")
    assert path.read_text(encoding="utf-8") == "Keep the embroidery.\n"
    with pytest.raises(ValueError, match="empty"):
        save_prompt(path, "   ")
