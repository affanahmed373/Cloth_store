"""Generated mannequin photos and marketing text."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from cloth_store.models import GeneratedPhoto, MarketingText


def render_photos(photos: list[GeneratedPhoto]) -> None:
    st.subheader("Catalog photos")
    for photo in photos:
        image, details = st.columns([1, 2])
        with image:
            if photo.image_path and Path(photo.image_path).is_file():
                st.image(photo.image_path, width="stretch")
            elif photo.error:
                st.warning(photo.error)
        with details:
            st.write(photo.source_name)
            if photo.prompt_path:
                st.caption(f"Prompt saved to {photo.prompt_path}")
            if photo.error and photo.image_path:
                st.warning(photo.error)


def render_texts(texts: list[MarketingText]) -> None:
    st.subheader("Marketing text")
    for item in texts:
        st.write(item.source_name)
        if item.text:
            st.write(item.text)
        if item.text_path:
            st.caption(f"Text saved to {item.text_path}")
        if item.error:
            st.warning(item.error)
