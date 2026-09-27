from pathlib import Path

from PIL import Image

from cloth_store.services.library import list_images, slug, to_jpeg_buffer


def test_list_images_keeps_photos_and_sorts_them(tmp_path: Path) -> None:
    Image.new("RGB", (8, 8), "red").save(tmp_path / "b.PNG")
    Image.new("RGB", (8, 8), "blue").save(tmp_path / "a.jpg")
    (tmp_path / "notes.txt").write_text("skip", encoding="utf-8")
    nested = tmp_path / "more"
    nested.mkdir()
    Image.new("RGB", (8, 8), "green").save(nested / "hidden.webp")

    found = list_images(tmp_path)

    assert [path.name for path in found] == ["a.jpg", "b.PNG"]


def test_list_images_on_a_missing_folder_is_empty(tmp_path: Path) -> None:
    assert list_images(tmp_path / "missing") == []


def test_to_jpeg_buffer_is_a_named_jpeg(image_file: Path) -> None:
    buffer = to_jpeg_buffer(image_file, max_side=16)
    assert buffer.name == "reference.jpg"
    assert buffer.getvalue()[:2] == b"\xff\xd8"


def test_slug_cleans_and_limits_names() -> None:
    assert slug("Emerald Lawn!!") == "emerald-lawn"
    assert slug("   ") == "dress"
    assert len(slug("a" * 80)) == 40
