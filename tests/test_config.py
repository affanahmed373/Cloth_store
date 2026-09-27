from pathlib import Path

from cloth_store.config import (
    IMAGE_PROMPT_PATH,
    IMAGES_DIR,
    OUTPUT_DIR,
    PROJECT_ROOT,
    TEXT_PROMPT_PATH,
    read_api_key,
    resolve_folder,
)


def test_data_folders_live_under_the_project() -> None:
    assert IMAGES_DIR == PROJECT_ROOT / "data" / "images"
    assert OUTPUT_DIR == PROJECT_ROOT / "data" / "output"
    assert IMAGE_PROMPT_PATH == PROJECT_ROOT / "prompts" / "image_prompt.txt"
    assert TEXT_PROMPT_PATH == PROJECT_ROOT / "prompts" / "text_prompt.txt"


def test_read_api_key_prefers_typed_value(monkeypatch) -> None:
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "from-env")
    assert read_api_key("  typed-key  ") == "typed-key"
    assert read_api_key("   ") == "from-env"


def test_api_key_setting_wins_over_the_openai_name(monkeypatch) -> None:
    monkeypatch.setenv("API_KEY", "primary")
    monkeypatch.setenv("OPENAI_API_KEY", "legacy")
    assert read_api_key("") == "primary"


def test_resolve_folder_accepts_relative_and_absolute_paths(tmp_path: Path) -> None:
    assert resolve_folder("data/images") == (PROJECT_ROOT / "data" / "images").resolve()
    assert resolve_folder(str(tmp_path)) == tmp_path.resolve()
