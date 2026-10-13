"""Main page: a dress photo in, a mannequin shot and shop text out."""

from __future__ import annotations

import threading
import time
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
from cloth_store.services.prompts import (
    DEFAULT_IMAGE_PROMPT,
    DEFAULT_TEXT_PROMPT,
    DUPATTA_OPTIONS,
    NOT_SET,
    PIECE_OPTIONS,
    OutfitDetails,
    compose_prompt,
)
from cloth_store.ui.components.gallery import render_gallery
from cloth_store.ui.components.prompts import render_saved_prompt
from cloth_store.ui.components.results import render_post
from cloth_store.ui.components.sidebar import SidebarInput, render_sidebar
from cloth_store.ui.styles import apply_styles

CANCEL_NOTICE = (
    "Stopped. Change the settings and try again. "
    "The previous API call may still finish in the background, and you may still be charged for it."
)


def render_page() -> None:
    st.set_page_config(page_title="Dress catalog", page_icon="🧵", layout="wide")
    apply_styles()
    st.title("Dress catalog")
    st.caption(
        f"Select up to {MAX_REFERENCE_PHOTOS} photos of one outfit and a suit code. "
        "Generate image makes one 4:5 Instagram photo. Generate text writes the caption."
    )

    if st.session_state.pop("cancel_notice", None):
        st.warning(CANCEL_NOTICE)

    _collect_finished_job()
    busy = _job_busy()
    settings = render_sidebar(disabled=busy)
    folder = resolve_folder(settings.folder_text)
    if not folder.is_dir():
        st.error(f"That folder does not exist: {folder}")
        st.stop()

    images = list_images(folder)
    photos = st.session_state.get("photos") or []
    texts = st.session_state.get("texts") or []
    if not images:
        st.info(f"No photos in {folder}. Add JPG, PNG, or WEBP files, then refresh this page.")
        if photos or texts:
            render_post(photos[0] if photos else None, texts[0] if texts else None)
        st.stop()

    selected = render_gallery(images, disabled=busy)
    image_prompt, text_prompt = _prompt_editors(disabled=busy)
    suit_code = st.text_input("Suit code", placeholder="1005", disabled=busy, key="suit_code")
    outfit = _outfit_details(disabled=busy)
    extra = st.text_area(
        "Your notes",
        placeholder="Example: Eid launch, emerald and gold, lawn suit",
        height=80,
        disabled=busy,
        key="shop_notes",
    )
    st.caption(
        "Your notes are added to the saved prompt for this run only. "
        "The suit code is used in the caption and in the file name. "
        "Outfit details stay Not set until you choose them; then they are added to the prompt."
    )
    needs_code = not suit_code.strip()
    if needs_code:
        st.caption("Enter a suit code before generating an image.")

    generate_image, generate_text = st.columns(2)
    with generate_image:
        make_photo = st.button("Generate image", type="primary", disabled=busy or needs_code)
    with generate_text:
        make_text = st.button("Generate text", disabled=busy)

    _render_job_status()

    if make_photo and not needs_code and _ready(selected, suit_code) and _image_ready(settings):
        if _start_photo_job(selected, settings, image_prompt, extra, suit_code, outfit):
            st.rerun()
    if make_text and _start_text_job(selected, settings, text_prompt, extra, suit_code, outfit):
        st.rerun()

    photos = st.session_state.get("photos") or []
    texts = st.session_state.get("texts") or []
    if photos or texts:
        render_post(photos[0] if photos else None, texts[0] if texts else None)

    if busy and _thread_is_alive():
        time.sleep(1)
        st.rerun()


def _job_busy() -> bool:
    return st.session_state.get("active_job") is not None


def _thread_is_alive() -> bool:
    job = st.session_state.get("active_job")
    if job is None:
        return False
    thread = job.get("thread")
    return bool(thread is not None and thread.is_alive())


def cancel_active_job(session: dict) -> None:
    """Free the page. Any in-flight API call is left running but its result is ignored."""
    job = session.get("active_job")
    if job is not None:
        cancel = job.get("cancel")
        if cancel is not None:
            cancel.set()
    session.pop("active_job", None)
    session["image_job"] = False
    session["cancel_notice"] = True


def _collect_finished_job() -> None:
    """Move a finished background job into the result panels."""
    job = st.session_state.get("active_job")
    if job is None:
        return
    thread = job.get("thread")
    if thread is not None and thread.is_alive():
        return
    _finish_active_job(job)
    st.session_state.pop("active_job", None)
    st.session_state["image_job"] = False


def _render_job_status() -> None:
    """Progress and cancel stay under the generate buttons."""
    job = st.session_state.get("active_job")
    if job is None:
        return
    st.info(f"{job['label']} {int(time.perf_counter() - job['started'])} s")
    st.caption("Cancel frees the page so you can fix the settings and try again.")
    st.warning(
        "Careful: you may still be charged for the API call that already started, "
        "even if you cancel here."
    )
    if st.button("Cancel and free the page", type="secondary"):
        cancel_active_job(st.session_state)
        st.rerun()


def _finish_active_job(job: dict) -> None:
    if job.get("cancel") is not None and job["cancel"].is_set():
        return
    holder = job["holder"]
    names = job["names"]
    elapsed = time.perf_counter() - job["started"]
    if job["kind"] == "image":
        if "error" in holder:
            photo = GeneratedPhoto(
                source_name=names,
                error=str(holder["error"]),
                elapsed_seconds=elapsed,
            )
        else:
            photo = GeneratedPhoto(
                source_name=names,
                image_path=str(holder.get("image_path")),
                elapsed_seconds=elapsed,
            )
        st.session_state["photos"] = [photo]
        return
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


def _prompt_editors(*, disabled: bool = False) -> tuple[str, str]:
    image_column, text_column = st.columns(2)
    with image_column:
        image_prompt = render_saved_prompt(
            "Image prompt",
            IMAGE_PROMPT_PATH,
            DEFAULT_IMAGE_PROMPT,
            "image_prompt_white_shalwar",
            disabled=disabled,
        )
    with text_column:
        text_prompt = render_saved_prompt(
            "Text prompt",
            TEXT_PROMPT_PATH,
            DEFAULT_TEXT_PROMPT,
            "text_prompt_shalwar_on_request",
            disabled=disabled,
        )
    return image_prompt, text_prompt


def _outfit_details(*, disabled: bool = False) -> OutfitDetails:
    st.subheader("Outfit details")
    st.caption(
        f"Leave a field on {NOT_SET} when you are unsure. "
        "That sends information not available in the prompt, not a yes. "
        "How many pieces can be 1, 2, or 3 when you know it. "
        "A one-piece shirt shows a white shalwar in the photo. The caption says shalwar is not included "
        "by default and white or black can be added on request."
    )
    dupatta_col, pieces_col = st.columns(2)
    with dupatta_col:
        dupatta = st.radio("Dupatta", DUPATTA_OPTIONS, horizontal=True, disabled=disabled, key="outfit_dupatta")
    with pieces_col:
        pieces = st.radio(
            "How many pieces",
            PIECE_OPTIONS,
            horizontal=True,
            disabled=disabled,
            key="outfit_pieces",
        )
    return OutfitDetails(dupatta=dupatta, pieces=pieces)


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


def _start_photo_job(
    sources: list[Path],
    settings: SidebarInput,
    general: str,
    extra: str,
    suit_code: str,
    outfit: OutfitDetails,
) -> bool:
    if not _ready(sources, suit_code):
        return False
    client = _client(
        settings.api_key,
        settings.api_base_url,
        "Add an API key in the sidebar, or set API_KEY in a .env file.",
    )
    if client is None:
        return False
    if not settings.image_model:
        st.error("Set an image model in the sidebar.")
        return False
    try:
        prompt = compose_prompt(general, extra, outfit=outfit)
    except ValueError as error:
        st.error(str(error))
        return False

    cancel = threading.Event()
    holder: dict[str, object] = {}
    names = ", ".join(path.name for path in sources)

    def work() -> None:
        if cancel.is_set():
            return
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

    thread = threading.Thread(target=work, daemon=True)
    st.session_state["active_job"] = {
        "kind": "image",
        "label": "Creating the Instagram image…",
        "thread": thread,
        "cancel": cancel,
        "holder": holder,
        "started": time.perf_counter(),
        "names": names,
    }
    st.session_state["image_job"] = True
    thread.start()
    return True


def _start_text_job(
    sources: list[Path],
    settings: SidebarInput,
    general: str,
    extra: str,
    suit_code: str,
    outfit: OutfitDetails,
) -> bool:
    if not _ready(sources, suit_code):
        return False
    client = _client(
        settings.text_api_key,
        settings.text_api_base_url,
        "Add a DeepSeek API key in the sidebar, or set TEXT_API_KEY in a .env file.",
    )
    if client is None:
        return False
    if not settings.text_model:
        st.error("Set a text model in the sidebar.")
        return False
    try:
        prompt = compose_prompt(general, extra, suit_code, outfit=outfit)
    except ValueError as error:
        st.error(str(error))
        return False

    cancel = threading.Event()
    holder: dict[str, object] = {}
    names = ", ".join(path.name for path in sources)

    def work() -> None:
        if cancel.is_set():
            return
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

    thread = threading.Thread(target=work, daemon=True)
    st.session_state["active_job"] = {
        "kind": "text",
        "label": "Writing the Instagram caption…",
        "thread": thread,
        "cancel": cancel,
        "holder": holder,
        "started": time.perf_counter(),
        "names": names,
    }
    st.session_state["image_job"] = True
    thread.start()
    return True
