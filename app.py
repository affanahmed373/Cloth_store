"""Minimal Streamlit UI: local photos in, Pakistani dress ideas out."""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from src.dresses import generate_dress_image, list_images, suggest_dresses

ROOT = Path(__file__).resolve().parent
DEFAULT_FOLDER = ROOT / "images"
OUTPUT_DIR = ROOT / "output"

load_dotenv(ROOT / ".env")

st.set_page_config(page_title="Pakistani Dress Finder", page_icon="🧵", layout="wide")
st.markdown(
    """
    <style>
      .block-container { padding-top: 1.5rem; max-width: 1100px; }
      div[data-testid="stCaption"] { margin-top: -0.4rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_key() -> str:
    typed = st.session_state.get("api_key_input", "")
    if isinstance(typed, str) and typed.strip():
        return typed.strip()
    return os.getenv("OPENAI_API_KEY", "").strip()


def resolve_folder(raw: str) -> Path:
    folder = Path(raw).expanduser()
    if not folder.is_absolute():
        folder = ROOT / folder
    return folder.resolve()


st.title("Pakistani Dress Finder")
st.caption("Pick photos from a folder. ChatGPT reads them and suggests Pakistani outfits.")

with st.sidebar:
    st.header("Settings")
    folder_text = st.text_input("Image folder", value=str(DEFAULT_FOLDER))
    audience = st.selectbox("Who is it for?", ["Women", "Men", "Any"])
    occasion = st.selectbox("Occasion", ["Any", "Casual", "Eid", "Wedding", "Party", "Formal"])
    count = st.slider("How many dresses", min_value=1, max_value=3, value=3)
    make_images = st.checkbox("Also create dress photos", value=True)
    if not os.getenv("OPENAI_API_KEY"):
        st.text_input("OpenAI API key", type="password", key="api_key_input")
    else:
        st.caption("API key loaded from the environment.")
    st.caption("Photos are sent to OpenAI. Dress photos use extra image calls and are saved in the output folder.")

folder = resolve_folder(folder_text)
notes = st.text_input("Notes for the stylist", placeholder="Example: prefer green and gold, summer lawn")

if not folder.is_dir():
    st.error(f"That folder does not exist: {folder}")
    st.stop()

images = list_images(folder)
if not images:
    st.info(f"No photos in {folder}. Add JPG, PNG, or WEBP files, then refresh this page.")
    st.stop()

st.write(f"**{len(images)}** photo{'s' if len(images) != 1 else ''} in `{folder}`")

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

if len(selected) > 4:
    st.warning("Only the first 4 selected photos are sent.")

find = st.button("Find Pakistani dresses", type="primary", disabled=not selected)

if find:
    key = api_key()
    if not key:
        st.error("Add an OpenAI API key in the sidebar, or set OPENAI_API_KEY in a .env file.")
    else:
        client = OpenAI(api_key=key, timeout=180)
        vision_model = os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini")
        image_model = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1-mini")
        try:
            with st.spinner("Reading your photos..."):
                result = suggest_dresses(
                    client,
                    selected,
                    model=vision_model,
                    count=count,
                    audience=audience.lower(),
                    occasion=occasion.lower(),
                    notes=notes,
                )
            dresses = result["dresses"]
            if make_images:
                for index, dress in enumerate(dresses, start=1):
                    with st.spinner(f"Creating photo {index} of {len(dresses)}..."):
                        try:
                            dress["image_path"] = str(
                                generate_dress_image(
                                    client,
                                    dress,
                                    selected,
                                    model=image_model,
                                    output_dir=OUTPUT_DIR,
                                    index=index,
                                )
                            )
                        except Exception as error:
                            dress["image_error"] = str(error)
            st.session_state["result"] = result
        except Exception as error:
            st.error(f"ChatGPT request failed: {error}")

result = st.session_state.get("result")
if result:
    st.divider()
    if result.get("image_summary"):
        st.write(result["image_summary"])
    for dress in result.get("dresses") or []:
        photo, details = st.columns([1, 2])
        with photo:
            image_path = dress.get("image_path")
            if image_path and Path(image_path).is_file():
                st.image(image_path, width="stretch")
            elif dress.get("image_error"):
                st.warning(dress["image_error"])
        with details:
            st.subheader(dress["name"])
            meta = " · ".join(
                part for part in (dress.get("category"), dress.get("occasion"), dress.get("fabric")) if part
            )
            if meta:
                st.caption(meta)
            if dress.get("colors"):
                st.write("Colors: " + ", ".join(dress["colors"]))
            if dress.get("description"):
                st.write(dress["description"])
            if dress.get("why_it_matches"):
                st.write(dress["why_it_matches"])
