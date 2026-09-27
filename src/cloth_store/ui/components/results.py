"""Generated mannequin photos and marketing text."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from cloth_store.models import GeneratedPhoto, MarketingText


def format_elapsed(seconds: float | None) -> str | None:
    if seconds is None:
        return None
    if seconds < 60:
        return f"Took {seconds:.1f} s"
    minutes, rest = divmod(int(round(seconds)), 60)
    return f"Took {minutes} min {rest} s"


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
            if photo.image_path:
                st.caption("1080×1350, 4:5, ready for Instagram.")
            elapsed = format_elapsed(photo.elapsed_seconds)
            if elapsed:
                st.caption(elapsed)
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
        elapsed = format_elapsed(item.elapsed_seconds)
        if elapsed:
            st.caption(elapsed)
        if item.error:
            st.warning(item.error)
