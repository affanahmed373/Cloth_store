"""Dress suggestions returned by the stylist."""

from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass
class Dress:
    name: str
    category: str
    occasion: str
    fabric: str
    colors: list[str]
    description: str
    why_it_matches: str
    image_path: str | None = None
    image_error: str | None = None

    @classmethod
    def from_payload(cls, item: object) -> Dress | None:
        if not isinstance(item, dict):
            return None
        colors = item.get("colors") or []
        if isinstance(colors, str):
            colors = [colors]
        if not isinstance(colors, list):
            colors = []
        return cls(
            name=str(item.get("name") or "Pakistani outfit").strip(),
            category=str(item.get("category") or "shalwar kameez").strip(),
            occasion=str(item.get("occasion") or "").strip(),
            fabric=str(item.get("fabric") or "").strip(),
            colors=[str(color).strip() for color in colors if str(color).strip()],
            description=str(item.get("description") or "").strip(),
            why_it_matches=str(item.get("why_it_matches") or "").strip(),
        )


@dataclass
class SuggestionResult:
    image_summary: str
    dresses: list[Dress] = field(default_factory=list)

    @classmethod
    def from_payload(cls, payload: str) -> SuggestionResult:
        data = json.loads(payload)
        if not isinstance(data, dict):
            raise ValueError("ChatGPT did not return a JSON object.")
        dresses = [Dress.from_payload(item) for item in data.get("dresses") or []]
        return cls(
            image_summary=str(data.get("image_summary") or "").strip(),
            dresses=[dress for dress in dresses if dress],
        )
