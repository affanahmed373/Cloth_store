# Cloth store

Small Streamlit app that reads outfit or fabric photos from a local folder, sends them to ChatGPT, and returns Pakistani dress ideas. With image generation turned on, it also saves catalog-style photos in `output/`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Put your OpenAI API key in `.env`:

```bash
OPENAI_API_KEY=sk-...
```

Optional model overrides:

```bash
OPENAI_VISION_MODEL=gpt-4o-mini
OPENAI_IMAGE_MODEL=gpt-image-1-mini
```

## Run

```bash
streamlit run app.py
```

`images/` includes a green placeholder, `sample_fabric.png`. Replace it with JPG, PNG, or WEBP outfit or fabric photos, or type another folder path in the sidebar. Select the photos, then choose **Find Pakistani dresses**.

The vision call reads color, pattern, and mood. The image call uses those photos as reference and saves new dress photos under `output/`. Uncheck **Also create dress photos** if you only want the written suggestions.
