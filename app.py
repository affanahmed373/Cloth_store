"""Streamlit entry point. Run with: streamlit run app.py"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cloth_store.ui.pages.finder import render_page

render_page()
