"""Suggested outfit cards."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from cloth_store.models import SuggestionResult


def render_results(result: SuggestionResult) -> None:
    st.divider()
    if result.image_summary:
        st.write(result.image_summary)
    for dress in result.dresses:
        photo, details = st.columns([1, 2])
        with photo:
            if dress.image_path and Path(dress.image_path).is_file():
                st.image(dress.image_path, width="stretch")
            elif dress.image_error:
                st.warning(dress.image_error)
        with details:
            st.subheader(dress.name)
            meta = " · ".join(part for part in (dress.category, dress.occasion, dress.fabric) if part)
            if meta:
                st.caption(meta)
            if dress.colors:
                st.write("Colors: " + ", ".join(dress.colors))
            if dress.description:
                st.write(dress.description)
            if dress.why_it_matches:
                st.write(dress.why_it_matches)
