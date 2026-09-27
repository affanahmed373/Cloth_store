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
from cloth_store.services.library import list_images
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
    st.caption("Pick one dress photo and a suit code. Generate one 4:5 Instagram image, or the shop caption.")

    settings = render_sidebar()
    folder = resolve_folder(settings.folder_text)
    if not folder.is_dir():
        st.error(f"That folder does not exist: {folder}")
        st.stop()

    images = list_images(folder)
    if not images:
        st.info(f"No photos in {folder}. Add JPG, PNG, or WEBP files, then refresh this page.")
        st.stop()

    selected = render_gallery(images)
    image_prompt, text_prompt = _prompt_editors()
    suit_code = st.text_input("Suit code", placeholder="1005")
    extra = st.text_area(
        "Your notes",
        placeholder="Example: Eid launch, emerald and gold, lawn suit",
        height=80,
    )
    st.caption("Your notes are added to the saved prompt for this run only. The suit code is used in the caption and in the file name.")
    generate_image, generate_text = st.columns(2)
    with generate_image:
        make_photo = st.button("Generate image", type="primary")
    with generate_text:
        make_text = st.button("Generate text")

    if make_photo:
        _generate_photo(selected, settings, image_prompt, extra, suit_code)
    if make_text:
        _generate_text(selected, settings, text_prompt, extra, suit_code)

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


def _client(api_key: str, base_url: str, missing_message: str):
    if not api_key:
        st.error(missing_message)
        return None
    try:
        return make_client(api_key, base_url)
    except ValueError as error:
        st.error(str(error))
        return None


def _generate_photo(
    source: Path,
    settings: SidebarInput,
    general: str,
    extra: str,
    suit_code: str,
) -> None:
    if not suit_code.strip():
        st.error("Enter a suit code.")
        return
    client = _client(
        settings.api_key,
        settings.api_base_url,
        "Add an API key in the sidebar, or set API_KEY in a .env file.",
    )
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

    with st.spinner(f"Sending {source.name}..."):
        try:
            image_path, prompt_path = generate_mannequin_image(
                client,
                source,
                prompt,
                model=settings.image_model,
                output_dir=OUTPUT_DIR,
                suit_code=suit_code,
            )
            photo = GeneratedPhoto(
                source_name=source.name,
                image_path=str(image_path),
                prompt_path=str(prompt_path),
            )
        except Exception as error:
            photo = GeneratedPhoto(source_name=source.name, error=str(error))
    st.session_state["photos"] = [photo]


def _generate_text(
    source: Path,
    settings: SidebarInput,
    general: str,
    extra: str,
    suit_code: str,
) -> None:
    if not suit_code.strip():
        st.error("Enter a suit code.")
        return
    client = _client(
        settings.text_api_key,
        settings.text_api_base_url,
        "Add a DeepSeek API key in the sidebar, or set TEXT_API_KEY in a .env file.",
    )
    if client is None:
        return
    if not settings.text_model:
        st.error("Set a text model in the sidebar.")
        return
    try:
        prompt = compose_prompt(general, extra, suit_code)
    except ValueError as error:
        st.error(str(error))
        return

    with st.spinner(f"Writing text for {source.name}..."):
        try:
            text, text_path = generate_marketing_text(
                client,
                source,
                prompt,
                model=settings.text_model,
                output_dir=OUTPUT_DIR,
                suit_code=suit_code,
            )
            item = MarketingText(source_name=source.name, text=text, text_path=str(text_path))
        except Exception as error:
            item = MarketingText(source_name=source.name, error=str(error))
    st.session_state["texts"] = [item]
