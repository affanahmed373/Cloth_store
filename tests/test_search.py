from pathlib import Path

from cloth_store.services.search import find_dresses
from tests.fakes import FakeChatClient


def _search(image_file: Path, tmp_path: Path, **overrides: object):
    settings = {
        "vision_model": "gpt-4o-mini",
        "image_model": "gpt-image-1-mini",
        "count": 1,
        "audience": "women",
        "occasion": "casual",
        "notes": "",
        "make_images": False,
        "output_dir": tmp_path,
    }
    settings.update(overrides)
    return find_dresses(FakeChatClient(), [image_file], **settings)


def test_find_dresses_returns_text_without_creating_photos(image_file: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    result = _search(image_file, output_dir)

    assert result.image_summary == "Green fabric"
    assert result.dresses[0].name == "Emerald Lawn"
    assert result.dresses[0].image_path is None
    assert not output_dir.exists()


def test_find_dresses_keeps_the_suggestion_when_a_photo_fails(
    image_file: Path, tmp_path: Path, monkeypatch
) -> None:
    def fail(*args: object, **kwargs: object) -> Path:
        raise RuntimeError("quota")

    monkeypatch.setattr("cloth_store.services.search.generate_dress_image", fail)
    result = _search(image_file, tmp_path, make_images=True)

    assert result.dresses[0].name == "Emerald Lawn"
    assert result.dresses[0].image_error == "quota"
