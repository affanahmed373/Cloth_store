"""Load the page stylesheet."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

CSS_PATH = Path(__file__).with_name("styles.css")


def apply_styles() -> None:
    st.markdown(f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
