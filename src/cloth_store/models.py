"""Results saved after an API call."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GeneratedPhoto:
    source_name: str
    image_path: str | None = None
    prompt_path: str | None = None
    error: str | None = None


@dataclass
class MarketingText:
    source_name: str
    text: str = ""
    text_path: str | None = None
    error: str | None = None
