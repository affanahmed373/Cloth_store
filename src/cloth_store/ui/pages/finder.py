"""Main page: local photos in, Pakistani dress ideas out."""

from __future__ import annotations

from pathlib import Path

import streamlit as st
from openai import OpenAI

from cloth_store.config import OUTPUT_DIR, image_model, resolve_folder, vision_model
from cloth_store.services.library import list_images
from cloth_store.services.search import find_dresses
from cloth_store.ui.components.gallery import render_gallery
from cloth_store.ui.components.results import render_results
from cloth_store.ui.components.sidebar import render_sidebar
from cloth_store.ui.styles import apply_styles


def render_page() -> None:
    st.set_page_config(page_title="Pakistani Dress Finder", page_icon="🧵", layout="wide")
    apply_styles()
    st.title("Pakistani Dress Finder")
    st.caption("Pick photos from a folder. ChatGPT reads them and suggests Pakistani outfits.")

    settings = render_sidebar()
    folder = resolve_folder(settings.folder_text)
    notes = st.text_input("Notes for the stylist", placeholder="Example: prefer green and gold, summer lawn")

    if not folder.is_dir():
        st.error(f"That folder does not exist: {folder}")
        st.stop()

    images = list_images(folder)
    if not images:
        st.info(f"No photos in {folder}. Add JPG, PNG, or WEBP files, then refresh this page.")
        st.stop()

    selected = render_gallery(images)
    find = st.button("Find Pakistani dresses", type="primary", disabled=not selected)
    if find:
        _search(selected, settings.api_key, settings.audience, settings.occasion, settings.count, settings.make_images, notes)

    result = st.session_state.get("result")
    if result:
        render_results(result)


def _search(
    selected: list[Path],
    api_key: str,
    audience: str,
    occasion: str,
    count: int,
    make_images: bool,
    notes: str,
) -> None:
    if not api_key:
        st.error("Add an OpenAI API key in the sidebar, or set OPENAI_API_KEY in a .env file.")
        return

    client = OpenAI(api_key=api_key, timeout=180)
    message = "Reading your photos and creating dress pictures..." if make_images else "Reading your photos..."
    try:
        with st.spinner(message):
            result = find_dresses(
                client,
                selected,
                vision_model=vision_model(),
                image_model=image_model(),
                count=count,
                audience=audience.lower(),
                occasion=occasion.lower(),
                notes=notes,
                make_images=make_images,
                output_dir=OUTPUT_DIR,
            )
        st.session_state["result"] = result
    except Exception as error:
        st.error(f"ChatGPT request failed: {error}")
