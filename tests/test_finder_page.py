"""Page checks that do not call OpenAI."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


def _app() -> AppTest:
    app = AppTest.from_file("app.py", default_timeout=20)
    app.run()
    return app


def _folder(app: AppTest):
    return next(field for field in app.text_input if field.label == "Image folder")


def test_page_lists_the_sample_photo(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    app = _app()

    assert app.title[0].value == "Pakistani Dress Finder"
    assert {box.label for box in app.checkbox} == {"sample_fabric.png", "Also create dress photos"}
    assert "Find Pakistani dresses" in [button.label for button in app.button]


def test_search_without_a_key_asks_for_one(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    app = _app()
    next(box for box in app.checkbox if box.label == "sample_fabric.png").check()
    next(button for button in app.button if button.label == "Find Pakistani dresses").click()
    app.run()

    assert app.error[0].value.startswith("Add an OpenAI API key")


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
