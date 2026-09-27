from pathlib import Path

import pytest
from PIL import Image

from cloth_store.services.stylist import build_instruction, suggest_dresses
from tests.fakes import SAMPLE_JSON, FakeChatClient


def test_build_instruction_includes_notes_only_when_present() -> None:
    plain = build_instruction(2, "women", "eid", "  ")
    noted = build_instruction(2, "women", "eid", " prefer gold ")
    assert "Shopper notes" not in plain
    assert "Shopper notes: prefer gold" in noted


def test_suggest_dresses_requires_an_image() -> None:
    with pytest.raises(ValueError, match="at least one"):
        suggest_dresses(
            FakeChatClient(),
            [],
            model="gpt-4o-mini",
            count=1,
            audience="women",
            occasion="any",
            notes="",
        )


def test_suggest_dresses_sends_at_most_four_photos(tmp_path: Path) -> None:
    paths = []
    for index in range(5):
        path = tmp_path / f"{index}.png"
        Image.new("RGB", (8, 8), (index, 20, 40)).save(path)
        paths.append(path)

    client = FakeChatClient(SAMPLE_JSON)
    result = suggest_dresses(
        client,
        paths,
        model="gpt-4o-mini",
        count=3,
        audience="women",
        occasion="wedding",
        notes="maroon",
    )

    content = client.completions.kwargs["messages"][1]["content"]
    assert result.dresses[0].name == "Emerald Lawn"
    assert content[0]["text"].endswith("Shopper notes: maroon")
    assert len([part for part in content if part["type"] == "image_url"]) == 4
    assert content[1]["image_url"]["url"].startswith("data:image/jpeg;base64,")
