from pathlib import Path

import pytest

from cloth_store.config import IMAGE_PROMPT_PATH, TEXT_PROMPT_PATH
from cloth_store.services.prompts import (
    DEFAULT_IMAGE_PROMPT,
    DEFAULT_TEXT_PROMPT,
    compose_prompt,
    load_prompt,
    save_prompt,
)


def test_checked_in_prompts_keep_the_piece_rules() -> None:
    image_prompt = load_prompt(IMAGE_PROMPT_PATH, DEFAULT_IMAGE_PROMPT)
    text_prompt = load_prompt(TEXT_PROMPT_PATH, DEFAULT_TEXT_PROMPT)
    assert image_prompt == DEFAULT_IMAGE_PROMPT
    assert text_prompt == DEFAULT_TEXT_PROMPT
    for prompt in (image_prompt, text_prompt):
        assert "shalwar" in prompt
        assert "elastic" in prompt
        assert "two-piece" in prompt
        assert "dupatta" in prompt


def test_compose_prompt_appends_shop_notes() -> None:
    assert compose_prompt("Show the dress.", "  ") == "Show the dress."
    assert compose_prompt("Show the dress.", "Eid launch") == "Show the dress.\n\nShop notes:\nEid launch"


def test_compose_prompt_rejects_an_empty_general_prompt() -> None:
    with pytest.raises(ValueError, match="empty"):
        compose_prompt("  ", "notes")


def test_save_prompt_writes_a_file_and_rejects_blank_text(tmp_path: Path) -> None:
    path = tmp_path / "prompts" / "image_prompt.txt"
    save_prompt(path, "  Keep the embroidery.  ")
    assert path.read_text(encoding="utf-8") == "Keep the embroidery.\n"
    with pytest.raises(ValueError, match="empty"):
        save_prompt(path, "   ")
