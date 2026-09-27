import base64
from pathlib import Path

import pytest

from cloth_store.models import Dress
from cloth_store.services.generator import generate_dress_image
from tests.fakes import FakeImageClient, FakeImages


def _dress() -> Dress:
    return Dress(
        name="Emerald Lawn",
        category="lawn suit",
        occasion="casual",
        fabric="lawn",
        colors=["emerald"],
        description="A light summer suit.",
        why_it_matches="It keeps the green.",
    )


def test_edit_writes_a_png_and_skips_generate(image_file: Path, tmp_path: Path) -> None:
    images = FakeImages(edit_b64=base64.b64encode(b"png-bytes").decode("ascii"))
    saved = generate_dress_image(
        FakeImageClient(images),
        _dress(),
        [image_file],
        model="gpt-image-1-mini",
        output_dir=tmp_path,
        index=1,
    )

    assert saved.name == "01-emerald-lawn.png"
    assert saved.read_bytes() == b"png-bytes"
    assert images.generate_kwargs is None
    assert "Emerald Lawn" in images.edit_kwargs["prompt"]
    assert images.edit_kwargs["image"].name == "reference.jpg"


def test_falls_back_to_generate_when_edit_fails(image_file: Path, tmp_path: Path) -> None:
    images = FakeImages(
        edit_error=RuntimeError("edit down"),
        generate_b64=base64.b64encode(b"generated").decode("ascii"),
    )
    saved = generate_dress_image(
        FakeImageClient(images),
        _dress(),
        [image_file],
        model="gpt-image-1-mini",
        output_dir=tmp_path,
        index=2,
    )

    assert saved.read_bytes() == b"generated"
    assert images.generate_kwargs["prompt"] == images.edit_kwargs["prompt"]


def test_reports_both_failures(image_file: Path, tmp_path: Path) -> None:
    images = FakeImages(edit_error=RuntimeError("edit down"))
    with pytest.raises(RuntimeError, match="Edit failed: edit down"):
        generate_dress_image(
            FakeImageClient(images),
            _dress(),
            [image_file],
            model="gpt-image-1-mini",
            output_dir=tmp_path,
            index=1,
        )


def test_rejects_an_empty_image_response(image_file: Path, tmp_path: Path) -> None:
    images = FakeImages(edit_data=[])
    with pytest.raises(RuntimeError, match="no photos"):
        generate_dress_image(
            FakeImageClient(images),
            _dress(),
            [image_file],
            model="gpt-image-1-mini",
            output_dir=tmp_path,
            index=1,
        )
