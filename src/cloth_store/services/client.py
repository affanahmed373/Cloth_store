"""OpenAI-compatible client. Point the base URL at another server later."""

from __future__ import annotations

from openai import OpenAI


def make_client(api_key: str, base_url: str) -> OpenAI:
    cleaned = base_url.strip().rstrip("/")
    if cleaned and not cleaned.startswith(("http://", "https://")):
        raise ValueError("API base URL must start with http:// or https://")
    kwargs: dict[str, object] = {"api_key": api_key, "timeout": 180.0}
    if cleaned:
        kwargs["base_url"] = cleaned
    return OpenAI(**kwargs)
