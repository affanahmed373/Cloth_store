from pathlib import Path

from cloth_store.services.copywriter import generate_marketing_text
from tests.fakes import FakeChatClient


def test_sends_the_dress_photo_and_saves_the_text(image_file: Path, tmp_path: Path) -> None:
    client = FakeChatClient("Emerald lawn suit\nSoft green cotton.")
    text, text_path = generate_marketing_text(
        client,
        image_file,
        "Write the listing.\n\nShop notes:\nEid launch",
        model="gpt-4o-mini",
        output_dir=tmp_path,
        index=1,
    )

    content = client.completions.kwargs["messages"][0]["content"]
    assert text.startswith("Emerald lawn suit")
    assert text_path.read_text(encoding="utf-8").startswith("Emerald lawn suit")
    assert content[0]["text"].endswith("Eid launch")
    assert content[1]["image_url"]["url"].startswith("data:image/jpeg;base64,")
