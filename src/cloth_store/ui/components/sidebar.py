"""Settings sidebar."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from cloth_store.config import IMAGES_DIR, env_api_key, read_api_key

AUDIENCES = ["Women", "Men", "Any"]
OCCASIONS = ["Any", "Casual", "Eid", "Wedding", "Party", "Formal"]


@dataclass
class SidebarInput:
    folder_text: str
    audience: str
    occasion: str
    count: int
    make_images: bool
    api_key: str


def render_sidebar() -> SidebarInput:
    with st.sidebar:
        st.header("Settings")
        folder_text = st.text_input("Image folder", value=str(IMAGES_DIR))
        audience = st.selectbox("Who is it for?", AUDIENCES)
        occasion = st.selectbox("Occasion", OCCASIONS)
        count = st.slider("How many dresses", min_value=1, max_value=3, value=3)
        make_images = st.checkbox("Also create dress photos", value=True)
        typed_key = ""
        if env_api_key():
            st.caption("API key loaded from the environment.")
        else:
            typed_key = st.text_input("OpenAI API key", type="password", key="api_key_input")
        st.caption(
            "Photos are sent to OpenAI. Dress photos use extra image calls and are saved in the output folder."
        )
    return SidebarInput(
        folder_text=folder_text,
        audience=audience,
        occasion=occasion,
        count=int(count),
        make_images=bool(make_images),
        api_key=read_api_key(typed_key),
    )
