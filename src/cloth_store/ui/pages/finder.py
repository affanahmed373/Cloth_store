"""Main page: a dress photo in, a mannequin shot and shop text out."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
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
from cloth_store.services.library import MAX_REFERENCE_PHOTOS, list_images
from cloth_store.services.prompts import DEFAULT_IMAGE_PROMPT, DEFAULT_TEXT_PROMPT, compose_prompt
from cloth_store.ui.components.gallery import render_gallery
from cloth_store.ui.components.prompts import render_saved_prompt
from cloth_store.ui.components.results import render_post
from cloth_store.ui.components.sidebar import SidebarInput, render_sidebar
from cloth_store.ui.styles import apply_styles


def render_page() -> None:
    st.set_page_config(page_title="Dress catalog", page_icon="🧵", layout="wide")
    apply_styles()
    st.title("Dress catalog")
    st.caption(
        f"Select up to {MAX_REFERENCE_PHOTOS} photos of one outfit and a suit code. "
        "Generate image makes one 4:5 Instagram photo. Generate text writes the caption."
    )

    busy = bool(st.session_state.get("image_job"))
    settings = render_sidebar(disabled=busy)
    folder = resolve_folder(settings.folder_text)
    if not folder.is_dir():
        st.error(f"That folder does not exist: {folder}")
        st.stop()

    images = list_images(folder)
    if not images:
        st.info(f"No photos in {folder}. Add JPG, PNG, or WEBP files, then refresh this page.")
        st.stop()

    selected = render_gallery(images, disabled=busy)
    image_prompt, text_prompt = _prompt_editors(disabled=busy)
    suit_code = st.text_input("Suit code", placeholder="1005", disabled=busy, key="suit_code")
    extra = st.text_area(
        "Your notes",
        placeholder="Example: Eid launch, emerald and gold, lawn suit",
        height=80,
        disabled=busy,
        key="shop_notes",
    )
    st.caption("Your notes are added to the saved prompt for this run only. The suit code is used in the caption and in the file name.")
    needs_code = not suit_code.strip()
    if needs_code:
        st.caption("Enter a suit code before generating an image.")
    generate_image, generate_text = st.columns(2)
    with generate_image:
        make_photo = st.button("Generate image", type="primary", disabled=busy or needs_code)
    with generate_text:
        make_text = st.button("Generate text", disabled=busy)

    if make_photo and not needs_code and _ready(selected, suit_code) and _image_ready(settings):
        st.session_state["image_job"] = True
        st.rerun()
    if busy and needs_code:
        st.session_state["image_job"] = False
        st.error("Enter a suit code.")
    elif busy:
        _generate_photo(selected, settings, image_prompt, extra, suit_code)
        st.session_state["image_job"] = False
        st.rerun()
    if make_text:
        _generate_text(selected, settings, text_prompt, extra, suit_code)

    photos = st.session_state.get("photos") or []
    texts = st.session_state.get("texts") or []
    if photos or texts:
        render_post(photos[0] if photos else None, texts[0] if texts else None)


def _prompt_editors(*, disabled: bool = False) -> tuple[str, str]:
    image_column, text_column = st.columns(2)
    with image_column:
        image_prompt = render_saved_prompt(
            "Image prompt",
            IMAGE_PROMPT_PATH,
            DEFAULT_IMAGE_PROMPT,
            "image_prompt_model",
            disabled=disabled,
        )
    with text_column:
        text_prompt = render_saved_prompt(
            "Text prompt",
            TEXT_PROMPT_PATH,
            DEFAULT_TEXT_PROMPT,
            "text_prompt_disclaimer",
            disabled=disabled,
        )
    return image_prompt, text_prompt


def _image_ready(settings: SidebarInput) -> bool:
    if not settings.api_key:
        st.error("Add an API key in the sidebar, or set API_KEY in a .env file.")
        return False
    if not settings.image_model:
        st.error("Set an image model in the sidebar.")
        return False
    return True


def _client(api_key: str, base_url: str, missing_message: str):
    if not api_key:
        st.error(missing_message)
        return None
    try:
        return make_client(api_key, base_url)
    except ValueError as error:
        st.error(str(error))
        return None


def _ready(sources: list[Path], suit_code: str) -> bool:
    if not sources:
        st.error("Select at least one photo.")
        return False
    if len(sources) > MAX_REFERENCE_PHOTOS:
        st.error(f"Select at most {MAX_REFERENCE_PHOTOS} photos.")
        return False
    if not suit_code.strip():
        st.error("Enter a suit code.")
        return False
    return True


def _generate_photo(
    sources: list[Path],
    settings: SidebarInput,
    general: str,
    extra: str,
    suit_code: str,
) -> None:
    if not _ready(sources, suit_code):
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

    names = ", ".join(path.name for path in sources)
    holder: dict[str, object] = {}

    def work() -> None:
        try:
            holder["image_path"] = generate_mannequin_image(
                client,
                sources,
                prompt,
                model=settings.image_model,
                output_dir=OUTPUT_DIR,
                suit_code=suit_code,
            )
        except Exception as error:
            holder["error"] = error

    elapsed = _tick("Creating the Instagram image…", work)
    if "error" in holder:
        photo = GeneratedPhoto(source_name=names, error=str(holder["error"]), elapsed_seconds=elapsed)
    else:
        photo = GeneratedPhoto(
            source_name=names,
            image_path=str(holder["image_path"]),
            elapsed_seconds=elapsed,
        )
    st.session_state["photos"] = [photo]


def _generate_text(
    sources: list[Path],
    settings: SidebarInput,
    general: str,
    extra: str,
    suit_code: str,
) -> None:
    if not _ready(sources, suit_code):
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

    names = ", ".join(path.name for path in sources)
    holder: dict[str, object] = {}

    def work() -> None:
        try:
            holder["result"] = generate_marketing_text(
                client,
                sources,
                prompt,
                model=settings.text_model,
                output_dir=OUTPUT_DIR,
                suit_code=suit_code,
            )
        except Exception as error:
            holder["error"] = error

    elapsed = _tick("Writing the Instagram caption…", work)
    if "error" in holder:
        item = MarketingText(source_name=names, error=str(holder["error"]), elapsed_seconds=elapsed)
    else:
        text, text_path = holder["result"]
        item = MarketingText(
            source_name=names,
            text=str(text),
            text_path=str(text_path),
            elapsed_seconds=elapsed,
        )
    st.session_state["texts"] = [item]


def _tick(label: str, work: Callable[[], None]) -> float:
    """Run work off the main thread and show the seconds already spent."""
    thread = threading.Thread(target=work, daemon=True)
    thread.start()
    started = time.perf_counter()
    status = st.empty()
    while thread.is_alive():
        seconds = int(time.perf_counter() - started)
        status.info(f"{label} {seconds} s")
        thread.join(timeout=1)
    status.empty()
    return time.perf_counter() - started
