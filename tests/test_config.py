from pathlib import Path

from cloth_store.config import (
    IMAGE_MODELS,
    IMAGE_PROMPT_PATH,
    IMAGES_DIR,
    OUTPUT_DIR,
    PROJECT_ROOT,
    TEXT_PROMPT_PATH,
    image_model_choices,
    read_api_key,
    resolve_folder,
    supports_input_fidelity,
    text_api_base_url,
    text_model,
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


def test_text_defaults_to_deepseek(monkeypatch) -> None:
    monkeypatch.delenv("TEXT_MODEL", raising=False)
    monkeypatch.delenv("TEXT_API_BASE_URL", raising=False)
    assert text_model() == "deepseek-flash"
    assert text_api_base_url() == "https://api.deepseek.com"


def test_image_model_choices_include_openai_edit_models(monkeypatch) -> None:
    monkeypatch.delenv("IMAGE_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_IMAGE_MODEL", raising=False)
    choices = image_model_choices()
    assert choices == list(IMAGE_MODELS)
    assert "gpt-image-1" in choices
    assert "gpt-image-1.5" in choices
    assert "gpt-image-2" in choices
    assert supports_input_fidelity("gpt-image-1")
    assert not supports_input_fidelity("gpt-image-1-mini")


def test_image_model_choices_keep_a_custom_env_value(monkeypatch) -> None:
    monkeypatch.setenv("IMAGE_MODEL", "my-custom-image")
    assert image_model_choices()[0] == "my-custom-image"


def test_resolve_folder_accepts_relative_and_absolute_paths(tmp_path: Path) -> None:
    assert resolve_folder("data/images") == (PROJECT_ROOT / "data" / "images").resolve()
    assert resolve_folder(str(tmp_path)) == tmp_path.resolve()
