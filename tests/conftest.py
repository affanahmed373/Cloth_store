"""Shared fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image


@pytest.fixture
def image_file(tmp_path: Path) -> Path:
    path = tmp_path / "swatch.png"
    Image.new("RGB", (32, 48), (18, 92, 72)).save(path)
    return path
