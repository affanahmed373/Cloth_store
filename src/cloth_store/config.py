"""Paths and environment settings."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
IMAGES_DIR = DATA_DIR / "images"
OUTPUT_DIR = DATA_DIR / "output"

load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_VISION_MODEL = "gpt-4o-mini"
DEFAULT_IMAGE_MODEL = "gpt-image-1-mini"


def vision_model() -> str:
    return os.getenv("OPENAI_VISION_MODEL", DEFAULT_VISION_MODEL)


def image_model() -> str:
    return os.getenv("OPENAI_IMAGE_MODEL", DEFAULT_IMAGE_MODEL)


def env_api_key() -> str:
    return os.getenv("OPENAI_API_KEY", "").strip()


def read_api_key(typed: str) -> str:
    if typed.strip():
        return typed.strip()
    return env_api_key()


def resolve_folder(raw: str, root: Path = PROJECT_ROOT) -> Path:
    folder = Path(raw).expanduser()
    if not folder.is_absolute():
        folder = root / folder
    return folder.resolve()
