"""Paths and environment settings."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
IMAGES_DIR = DATA_DIR / "images"
OUTPUT_DIR = DATA_DIR / "output"
PROMPTS_DIR = PROJECT_ROOT / "prompts"
IMAGE_PROMPT_PATH = PROMPTS_DIR / "image_prompt.txt"
TEXT_PROMPT_PATH = PROMPTS_DIR / "text_prompt.txt"

load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_API_BASE_URL = "https://api.openai.com/v1"
DEFAULT_TEXT_API_BASE_URL = "https://api.deepseek.com"
DEFAULT_TEXT_MODEL = "deepseek-flash"
DEFAULT_IMAGE_MODEL = "gpt-image-1-mini"


def api_base_url() -> str:
    return os.getenv("API_BASE_URL", DEFAULT_API_BASE_URL).strip() or DEFAULT_API_BASE_URL


def text_api_base_url() -> str:
    return os.getenv("TEXT_API_BASE_URL", DEFAULT_TEXT_API_BASE_URL).strip() or DEFAULT_TEXT_API_BASE_URL


def text_model() -> str:
    return os.getenv("TEXT_MODEL") or DEFAULT_TEXT_MODEL


def text_api_key() -> str:
    return os.getenv("TEXT_API_KEY", "").strip() or os.getenv("DEEPSEEK_API_KEY", "").strip()


def image_model() -> str:
    return os.getenv("IMAGE_MODEL") or os.getenv("OPENAI_IMAGE_MODEL") or DEFAULT_IMAGE_MODEL


def env_api_key() -> str:
    return os.getenv("API_KEY", "").strip() or os.getenv("OPENAI_API_KEY", "").strip()


def read_api_key(typed: str) -> str:
    if typed.strip():
        return typed.strip()
    return env_api_key()


def resolve_folder(raw: str, root: Path = PROJECT_ROOT) -> Path:
    folder = Path(raw).expanduser()
    if not folder.is_absolute():
        folder = root / folder
    return folder.resolve()
