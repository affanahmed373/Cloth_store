"""Photo picker for a local folder."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

def render_gallery(images: list[Path]) -> list[Path]:
    st.write(f"**{len(images)}** photo{'s' if len(images) != 1 else ''} in `{images[0].parent}`")

    if st.button("Select all"):
        for path in images:
            st.session_state[f"pick_{path}"] = True
        st.rerun()

    selected: list[Path] = []
    columns = st.columns(4)
    for index, path in enumerate(images):
        with columns[index % 4]:
            st.image(str(path), width="stretch")
            if st.checkbox(path.name, key=f"pick_{path}"):
                selected.append(path)

    return selected
