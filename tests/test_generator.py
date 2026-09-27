import base64
from pathlib import Path
from types import SimpleNamespace

import pytest

from cloth_store.services.generator import generate_mannequin_image
from tests.fakes import FakeImageClient, FakeImages


def test_sends_the_dress_and_saves_the_prompt(image_file: Path, tmp_path: Path) -> None:
    images = FakeImages(edit_b64=base64.b64encode(b"png-bytes").decode("ascii"))
    image_path, prompt_path = generate_mannequin_image(
        FakeImageClient(images),
        image_file,
        "Show this dress on a mannequin.\n\nShop notes:\nEid launch",
        model="gpt-image-1-mini",
        output_dir=tmp_path,
        index=1,
    )

    assert image_path.name == "01-swatch.png"
    assert image_path.read_bytes() == b"png-bytes"
    assert "Eid launch" in prompt_path.read_text(encoding="utf-8")
    assert images.edit_kwargs["image"].name == "reference.jpg"
    assert images.edit_kwargs["prompt"].startswith("Show this dress")
    assert images.generate_kwargs is None


def test_edit_errors_are_not_replaced_with_a_text_only_image(image_file: Path, tmp_path: Path) -> None:
    images = FakeImages(edit_error=RuntimeError("edit down"))
    with pytest.raises(RuntimeError, match="edit down"):
        generate_mannequin_image(
            FakeImageClient(images),
            image_file,
            "Show the dress.",
            model="gpt-image-1-mini",
            output_dir=tmp_path,
            index=1,
        )


def test_rejects_an_empty_image_response(image_file: Path, tmp_path: Path) -> None:
    images = FakeImages(edit_data=[])
    with pytest.raises(RuntimeError, match="no photos"):
        generate_mannequin_image(
            FakeImageClient(images),
            image_file,
            "Show the dress.",
            model="gpt-image-1-mini",
            output_dir=tmp_path,
            index=1,
        )


def test_downloads_a_url_when_the_api_does_not_return_bytes(
    image_file: Path, tmp_path: Path, monkeypatch
) -> None:
    images = FakeImages(edit_data=[SimpleNamespace(b64_json=None, url="http://example.test/dress.png")])

    class Response:
        def read(self) -> bytes:
            return b"from-url"

        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *args: object) -> bool:
            return False

    monkeypatch.setattr("cloth_store.services.generator.urllib.request.urlopen", lambda url, timeout=0: Response())
    image_path, _prompt_path = generate_mannequin_image(
        FakeImageClient(images),
        image_file,
        "Show the dress.",
        model="compatible-image",
        output_dir=tmp_path,
        index=2,
    )
    assert image_path.read_bytes() == b"from-url"
