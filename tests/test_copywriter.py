from pathlib import Path

from PIL import Image

from cloth_store.services.copywriter import generate_marketing_text
from tests.fakes import FakeChatClient


def test_sends_the_dress_photo_and_saves_the_text(image_file: Path, tmp_path: Path) -> None:
    client = FakeChatClient("Emerald lawn suit\nSoft green cotton.")
    text, text_path = generate_marketing_text(
        client,
        [image_file],
        "Write the listing.\n\nShop notes:\nEid launch",
        model="deepseek-flash",
        output_dir=tmp_path,
        suit_code="1005",
    )

    content = client.completions.kwargs["messages"][0]["content"]
    assert text_path.name == "instaimage-1005.txt"
    assert text.startswith("Emerald lawn suit")
    assert text_path.read_text(encoding="utf-8").startswith("Emerald lawn suit")
    assert content[0]["text"].endswith("Eid launch")
    assert content[1]["image_url"]["url"].startswith("data:image/jpeg;base64,")


def test_sends_every_selected_photo_with_the_caption(tmp_path: Path) -> None:
    sources = []
    for index in range(10):
        path = tmp_path / f"view-{index}.png"
        Image.new("RGB", (24, 24), "green").save(path)
        sources.append(path)
    client = FakeChatClient("Caption")
    generate_marketing_text(
        client,
        sources,
        "Write the listing.",
        model="deepseek-flash",
        output_dir=tmp_path / "out",
        suit_code="1005",
    )

    content = client.completions.kwargs["messages"][0]["content"]
    assert content[0]["type"] == "text"
    assert len([part for part in content if part["type"] == "image_url"]) == 10
