"""Photo picker. Up to ten views of one outfit, sent together."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from cloth_store.services.library import MAX_REFERENCE_PHOTOS


def render_gallery(images: list[Path]) -> list[Path]:
    folder = images[0].parent
    st.write(f"**{len(images)}** photo{'s' if len(images) != 1 else ''} in `{folder}`")
    st.caption(
        "Select up to 10 photos of the same outfit. They are sent together as context. "
        "You still get one Instagram image and, separately, one caption."
    )

    selected: list[Path] = []
    columns = st.columns(4)
    for index, path in enumerate(images):
        with columns[index % 4]:
            st.image(str(path), width="stretch")
            if st.checkbox(path.name, key=f"pick_{path}"):
                selected.append(path)

    if len(selected) > MAX_REFERENCE_PHOTOS:
        st.error(f"Select at most {MAX_REFERENCE_PHOTOS} photos of this outfit.")
    elif selected:
        count = len(selected)
        st.caption(f"{count} photo{'s' if count != 1 else ''} selected for this post.")
    return selected
