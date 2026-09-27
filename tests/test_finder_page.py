"""Page checks that do not call the API."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


def _app() -> AppTest:
    app = AppTest.from_file("app.py", default_timeout=20)
    app.run()
    return app


def _folder(app: AppTest):
    return next(field for field in app.text_input if field.label == "Image folder")


def _clear_keys(monkeypatch) -> None:
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


def test_page_lists_photos_and_both_actions(monkeypatch) -> None:
    _clear_keys(monkeypatch)
    app = _app()
    labels = [button.label for button in app.button]

    assert app.title[0].value == "Dress catalog"
    assert app.checkbox
    assert any(field.label == "Suit code" for field in app.text_input)
    assert "Select all" in labels
    assert "Generate image" in labels
    assert "Generate text" in labels
    assert "Save image prompt" in labels
    assert "Save text prompt" in labels


def test_select_all_checks_every_photo(monkeypatch) -> None:
    _clear_keys(monkeypatch)
    app = _app()
    next(button for button in app.button if button.label == "Select all").click()
    app.run()

    assert app.checkbox
    assert all(box.value for box in app.checkbox)


def _image_button(app: AppTest):
    return next(button for button in app.button if button.label == "Generate image")


def test_generate_image_is_disabled_without_a_suit_code(monkeypatch) -> None:
    _clear_keys(monkeypatch)
    app = _app()
    assert _image_button(app).disabled


def test_generate_image_without_a_key_asks_for_one(monkeypatch) -> None:
    _clear_keys(monkeypatch)
    app = _app()
    app.checkbox[0].check()
    next(field for field in app.text_input if field.label == "Suit code").set_value("1005")
    app.run()
    _image_button(app).click()
    app.run()

    assert app.error[0].value.startswith("Add an API key")


def test_missing_folder_shows_an_error(tmp_path: Path) -> None:
    app = _app()
    _folder(app).set_value(str(tmp_path / "missing"))
    app.run()

    assert "does not exist" in app.error[0].value


def test_empty_folder_shows_instructions(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    app = _app()
    _folder(app).set_value(str(empty))
    app.run()

    assert "No photos in" in app.info[0].value
