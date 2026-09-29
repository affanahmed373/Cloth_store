"""Settings sidebar."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from cloth_store.services.folder_picker import pick_folder
from cloth_store.config import (
    IMAGES_DIR,
    OUTPUT_DIR,
    api_base_url,
    env_api_key,
    image_model,
    image_model_choices,
    read_api_key,
    resolve_folder,
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


def _choose_image_folder() -> None:
    chosen = pick_folder(str(st.session_state.get("image_folder", IMAGES_DIR)))
    if chosen:
        st.session_state["image_folder"] = chosen


def render_sidebar(*, disabled: bool = False) -> SidebarInput:
    with st.sidebar:
        st.header("Settings")
        if "image_folder" not in st.session_state:
            st.session_state["image_folder"] = str(IMAGES_DIR)
        folder_text = st.text_input("Image folder", key="image_folder", disabled=disabled)
        st.button(
            "Choose folder",
            on_click=_choose_image_folder,
            disabled=disabled,
        )
        folder = resolve_folder(folder_text)
        st.caption(f"Photos are read from this folder on this computer: {folder}")
        st.caption(f"The caption and the generated image stay in {OUTPUT_DIR}.")
        st.subheader("Image")
        base_url = st.text_input("Image API base URL", value=api_base_url(), disabled=disabled)
        typed_key = ""
        if env_api_key():
            st.caption("Image API key loaded from the environment.")
        else:
            typed_key = st.text_input("Image API key", type="password", key="api_key_input", disabled=disabled)
        choices = image_model_choices()
        current = image_model()
        image_name = st.selectbox(
            "Image model",
            choices,
            index=choices.index(current) if current in choices else 0,
            disabled=disabled,
        )
        st.caption(
            "mini is cheapest. gpt-image-1 / 1.5 / 2 follow the suit photos more closely and cost more."
        )

        st.subheader("Text")
        text_base_url = st.text_input("Text API base URL", value=text_api_base_url(), disabled=disabled)
        typed_text_key = ""
        if text_api_key():
            st.caption("DeepSeek API key loaded from the environment.")
        else:
            typed_text_key = st.text_input(
                "DeepSeek API key",
                type="password",
                key="text_api_key_input",
                disabled=disabled,
            )
        text_name = st.text_input("Text model", value=text_model(), disabled=disabled)
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
