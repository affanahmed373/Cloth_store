import base64
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image

from cloth_store.services.generator import generate_mannequin_image
from tests.fakes import FakeImageClient, FakeImages


def _png_b64(width: int = 90, height: int = 160) -> str:
    buffer = BytesIO()
    Image.new("RGB", (width, height), (120, 20, 40)).save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def test_sends_the_dress_and_saves_the_prompt(image_file: Path, tmp_path: Path) -> None:
    images = FakeImages(edit_b64=_png_b64())
    image_path = generate_mannequin_image(
        FakeImageClient(images),
        [image_file],
        "Show this dress on a mannequin.\n\nShop notes:\nEid launch",
        model="gpt-image-1-mini",
        output_dir=tmp_path,
        suit_code="1005",
    )

    assert image_path.name == "instaimage-1005.png"
    with Image.open(image_path) as saved:
        assert saved.size == (1080, 1350)
    assert "Eid launch" in images.edit_kwargs["prompt"]
    assert images.edit_kwargs["quality"] == "high"
    assert "input_fidelity" not in images.edit_kwargs
    assert not (tmp_path / "instaimage-1005.prompt.txt").exists()
    assert images.edit_kwargs["image"].name == "reference-1.jpg"
    assert images.edit_kwargs["size"] == "1024x1536"
    assert images.edit_kwargs["n"] == 1
    assert images.edit_kwargs["prompt"].startswith("Show this dress")
    assert images.generate_kwargs is None


def test_stronger_models_ask_for_high_input_fidelity(image_file: Path, tmp_path: Path) -> None:
    images = FakeImages(edit_b64=_png_b64())
    generate_mannequin_image(
        FakeImageClient(images),
        [image_file],
        "Show this dress.",
        model="gpt-image-1.5",
        output_dir=tmp_path,
        suit_code="1005",
    )
    assert images.edit_kwargs["input_fidelity"] == "high"
    assert images.edit_kwargs["model"] == "gpt-image-1.5"


def test_edit_errors_are_not_replaced_with_a_text_only_image(image_file: Path, tmp_path: Path) -> None:
    images = FakeImages(edit_error=RuntimeError("edit down"))
    with pytest.raises(RuntimeError, match="edit down"):
        generate_mannequin_image(
            FakeImageClient(images),
            [image_file],
            "Show the dress.",
            model="gpt-image-1-mini",
            output_dir=tmp_path,
            suit_code="1005",
        )


def test_rejects_an_empty_image_response(image_file: Path, tmp_path: Path) -> None:
    images = FakeImages(edit_data=[])
    with pytest.raises(RuntimeError, match="no photos"):
        generate_mannequin_image(
            FakeImageClient(images),
            [image_file],
            "Show the dress.",
            model="gpt-image-1-mini",
            output_dir=tmp_path,
            suit_code="1005",
        )


def test_downloads_a_url_when_the_api_does_not_return_bytes(
    image_file: Path, tmp_path: Path, monkeypatch
) -> None:
    images = FakeImages(edit_data=[SimpleNamespace(b64_json=None, url="http://example.test/dress.png")])

    class Response:
        def read(self) -> bytes:
            return base64.b64decode(_png_b64(width=200, height=200))

        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *args: object) -> bool:
            return False

    monkeypatch.setattr("cloth_store.services.generator.urllib.request.urlopen", lambda url, timeout=0: Response())
    image_path = generate_mannequin_image(
        FakeImageClient(images),
        [image_file],
        "Show the dress.",
        model="compatible-image",
        output_dir=tmp_path,
        suit_code="1005",
    )
    assert image_path.name == "instaimage-1005.png"
    with Image.open(image_path) as saved:
        assert saved.size == (1080, 1350)


def test_sends_ten_reference_photos_and_asks_for_one_result(tmp_path: Path) -> None:
    sources = []
    for index in range(10):
        path = tmp_path / f"view-{index}.png"
        Image.new("RGB", (40, 60), (index * 40, 20, 30)).save(path)
        sources.append(path)
    images = FakeImages(edit_b64=_png_b64())
    image_path = generate_mannequin_image(
        FakeImageClient(images),
        sources,
        "Show the dress.",
        model="gpt-image-1-mini",
        output_dir=tmp_path / "out",
        suit_code="1005",
    )

    uploaded = images.edit_kwargs["image"]
    assert [item.name for item in uploaded] == [f"reference-{index}.jpg" for index in range(1, 11)]
    assert images.edit_kwargs["n"] == 1
    assert image_path.name == "instaimage-1005.png"
