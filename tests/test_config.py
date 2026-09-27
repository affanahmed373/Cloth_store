from pathlib import Path

from cloth_store.config import IMAGES_DIR, OUTPUT_DIR, PROJECT_ROOT, read_api_key, resolve_folder


def test_data_folders_live_under_the_project() -> None:
    assert IMAGES_DIR == PROJECT_ROOT / "data" / "images"
    assert OUTPUT_DIR == PROJECT_ROOT / "data" / "output"


def test_read_api_key_prefers_typed_value(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "from-env")
    assert read_api_key("  typed-key  ") == "typed-key"
    assert read_api_key("   ") == "from-env"


def test_resolve_folder_accepts_relative_and_absolute_paths(tmp_path: Path) -> None:
    assert resolve_folder("data/images") == (PROJECT_ROOT / "data" / "images").resolve()
    assert resolve_folder(str(tmp_path)) == tmp_path.resolve()
