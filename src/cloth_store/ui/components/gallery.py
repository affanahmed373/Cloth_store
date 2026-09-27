"""Photo picker for a local folder. One dress photo per run."""

from __future__ import annotations

from pathlib import Path

import streamlit as st


def render_gallery(images: list[Path]) -> Path:
    folder = images[0].parent
    st.write(f"**{len(images)}** photo{'s' if len(images) != 1 else ''} in `{folder}`")
    names = [path.name for path in images]
    choice = st.selectbox("Dress photo", names)
    selected = next(path for path in images if path.name == choice)
    st.image(str(selected), width=360)
    st.caption("One photo is used. The result is a single 4:5 Instagram image.")
    return selected
