"""Settings sidebar."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from cloth_store.config import (
    IMAGES_DIR,
    api_base_url,
    env_api_key,
    image_model,
    read_api_key,
    text_api_base_url,
    text_api_key,
    text_model,
)


@dataclass
class SidebarInput:
    folder_text: str
    api_base_url: str
    api_key: str
    image_model: str
    text_api_base_url: str
    text_api_key: str
    text_model: str


def render_sidebar() -> SidebarInput:
    with st.sidebar:
        st.header("Settings")
        folder_text = st.text_input("Image folder", value=str(IMAGES_DIR))
        st.subheader("Image")
        base_url = st.text_input("Image API base URL", value=api_base_url())
        typed_key = ""
        if env_api_key():
            st.caption("Image API key loaded from the environment.")
        else:
            typed_key = st.text_input("Image API key", type="password", key="api_key_input")
        image_name = st.text_input("Image model", value=image_model())

        st.subheader("Text")
        text_base_url = st.text_input("Text API base URL", value=text_api_base_url())
        typed_text_key = ""
        if text_api_key():
            st.caption("DeepSeek API key loaded from the environment.")
        else:
            typed_text_key = st.text_input("DeepSeek API key", type="password", key="text_api_key_input")
        text_name = st.text_input("Text model", value=text_model())
        st.caption("Images use the image server. Captions use DeepSeek unless you change the text server.")
    return SidebarInput(
        folder_text=folder_text,
        api_base_url=base_url.strip(),
        api_key=read_api_key(typed_key),
        image_model=image_name.strip(),
        text_api_base_url=text_base_url.strip(),
        text_api_key=typed_text_key.strip() or text_api_key(),
        text_model=text_name.strip(),
    )
