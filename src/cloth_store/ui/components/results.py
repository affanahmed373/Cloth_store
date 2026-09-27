"""The finished Instagram post: photo on the left, caption on the right."""

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


def render_post(photo: GeneratedPhoto | None, text: MarketingText | None) -> None:
    st.subheader("Instagram post")
    with st.container(border=True):
        image_col, caption_col = st.columns([2, 3], gap="large")
        with image_col:
            _render_image(photo)
        with caption_col:
            _render_caption(text)


def _render_image(photo: GeneratedPhoto | None) -> None:
    if photo and photo.image_path and Path(photo.image_path).is_file():
        st.image(photo.image_path, width="stretch")
        st.caption("1080×1350, 4:5, ready for Instagram.")
    elif photo is None or not photo.error:
        st.info("Image not created yet.")
    if photo and photo.error:
        st.warning(photo.error)
    elapsed = format_elapsed(photo.elapsed_seconds if photo else None)
    if elapsed:
        st.caption(elapsed)


def _render_caption(text: MarketingText | None) -> None:
    if text and text.text:
        st.markdown(text.text)
    elif text is None or not text.error:
        st.info("Caption not written yet.")
    if text and text.text_path:
        st.caption(f"Text saved to {text.text_path}")
    if text and text.error:
        st.warning(text.error)
    elapsed = format_elapsed(text.elapsed_seconds if text else None)
    if elapsed:
        st.caption(elapsed)
