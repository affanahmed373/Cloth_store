"""Main page: a dress photo in, a mannequin shot and shop text out."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from cloth_store.config import (
    IMAGE_PROMPT_PATH,
    OUTPUT_DIR,
    TEXT_PROMPT_PATH,
    resolve_folder,
)
from cloth_store.models import GeneratedPhoto, MarketingText
from cloth_store.services.client import make_client
from cloth_store.services.copywriter import generate_marketing_text
from cloth_store.services.generator import generate_mannequin_image
from cloth_store.services.library import MAX_REFERENCE_IMAGES, list_images
from cloth_store.services.prompts import DEFAULT_IMAGE_PROMPT, DEFAULT_TEXT_PROMPT, compose_prompt
from cloth_store.ui.components.gallery import render_gallery
from cloth_store.ui.components.prompts import render_saved_prompt
from cloth_store.ui.components.results import render_photos, render_texts
from cloth_store.ui.components.sidebar import SidebarInput, render_sidebar
from cloth_store.ui.styles import apply_styles


def render_page() -> None:
    st.set_page_config(page_title="Dress catalog", page_icon="🧵", layout="wide")
    apply_styles()
    st.title("Dress catalog")
    st.caption("Add a dress photo. One button makes a mannequin shot. The other writes the shop text.")

    settings = render_sidebar()
    folder = resolve_folder(settings.folder_text)
    if not folder.is_dir():
        st.error(f"That folder does not exist: {folder}")
        st.stop()

    images = list_images(folder)
    if not images:
        st.info(f"No photos in {folder}. Add JPG, PNG, or WEBP files, then refresh this page.")
        st.stop()

    selected = render_gallery(images)[:MAX_REFERENCE_IMAGES]
    image_prompt, text_prompt = _prompt_editors()
    extra = st.text_area(
        "Your notes",
        placeholder="Example: Eid launch, emerald and gold, lawn suit",
        height=80,
    )
    st.caption("Your notes are added to the saved prompt for this run only.")
    generate_image, generate_text = st.columns(2)
    with generate_image:
        make_photo = st.button("Generate image", type="primary", disabled=not selected)
    with generate_text:
        make_text = st.button("Generate text", disabled=not selected)

    if make_photo:
        _generate_photos(selected, settings, image_prompt, extra)
    if make_text:
        _generate_texts(selected, settings, text_prompt, extra)

    photos = st.session_state.get("photos")
    texts = st.session_state.get("texts")
    if photos:
        render_photos(photos)
    if texts:
        render_texts(texts)


def _prompt_editors() -> tuple[str, str]:
    image_column, text_column = st.columns(2)
    with image_column:
        image_prompt = render_saved_prompt(
            "Image prompt",
            IMAGE_PROMPT_PATH,
            DEFAULT_IMAGE_PROMPT,
            "image_prompt",
        )
    with text_column:
        text_prompt = render_saved_prompt(
            "Text prompt",
            TEXT_PROMPT_PATH,
            DEFAULT_TEXT_PROMPT,
            "text_prompt",
        )
    return image_prompt, text_prompt


def _client(settings: SidebarInput):
    if not settings.api_key:
        st.error("Add an API key in the sidebar, or set API_KEY in a .env file.")
        return None
    try:
        return make_client(settings.api_key, settings.api_base_url)
    except ValueError as error:
        st.error(str(error))
        return None


def _generate_photos(selected: list[Path], settings: SidebarInput, general: str, extra: str) -> None:
    client = _client(settings)
    if client is None:
        return
    if not settings.image_model:
        st.error("Set an image model in the sidebar.")
        return
    try:
        prompt = compose_prompt(general, extra)
    except ValueError as error:
        st.error(str(error))
        return

    photos: list[GeneratedPhoto] = []
    for index, path in enumerate(selected, start=1):
        with st.spinner(f"Sending {path.name}..."):
            try:
                image_path, prompt_path = generate_mannequin_image(
                    client,
                    path,
                    prompt,
                    model=settings.image_model,
                    output_dir=OUTPUT_DIR,
                    index=index,
                )
                photos.append(
                    GeneratedPhoto(
                        source_name=path.name,
                        image_path=str(image_path),
                        prompt_path=str(prompt_path),
                    )
                )
            except Exception as error:
                photos.append(GeneratedPhoto(source_name=path.name, error=str(error)))
    st.session_state["photos"] = photos


def _generate_texts(selected: list[Path], settings: SidebarInput, general: str, extra: str) -> None:
    client = _client(settings)
    if client is None:
        return
    if not settings.text_model:
        st.error("Set a text model in the sidebar.")
        return
    try:
        prompt = compose_prompt(general, extra)
    except ValueError as error:
        st.error(str(error))
        return

    texts: list[MarketingText] = []
    for index, path in enumerate(selected, start=1):
        with st.spinner(f"Writing text for {path.name}..."):
            try:
                text, text_path = generate_marketing_text(
                    client,
                    path,
                    prompt,
                    model=settings.text_model,
                    output_dir=OUTPUT_DIR,
                    index=index,
                )
                texts.append(MarketingText(source_name=path.name, text=text, text_path=str(text_path)))
            except Exception as error:
                texts.append(MarketingText(source_name=path.name, error=str(error)))
    st.session_state["texts"] = texts
