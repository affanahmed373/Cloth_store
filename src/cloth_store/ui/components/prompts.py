"""Editors for the prompts stored in the prompts folder."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from cloth_store.services.prompts import load_prompt, save_prompt


def render_saved_prompt(label: str, path: Path, default: str, key: str, *, disabled: bool = False) -> str:
    if key not in st.session_state:
        st.session_state[key] = load_prompt(path, default)
    st.text_area(label, key=key, height=160, disabled=disabled)
    if st.button(f"Save {label.lower()}", key=f"save_{key}", disabled=disabled):
        try:
            save_prompt(path, st.session_state[key])
        except ValueError as error:
            st.error(str(error))
        else:
            st.success(f"Saved {path.name}.")
    return str(st.session_state[key])
