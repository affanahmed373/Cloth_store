# Cloth store

Small Streamlit app for an online clothing shop. Put a dress photo in a folder, press **Generate image**, and an OpenAI-compatible API returns a catalog photo of that outfit, on a mannequin or a generated model. **Generate text** writes the listing copy. The general prompts are saved in `prompts/`, and your own notes are added for that run only.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Put the API keys in `.env`. The image call stays on an OpenAI-compatible server. Captions use DeepSeek:

```bash
API_KEY=sk-...
API_BASE_URL=https://api.openai.com/v1
IMAGE_MODEL=gpt-image-1-mini
TEXT_API_KEY=sk-...
TEXT_API_BASE_URL=https://api.deepseek.com
TEXT_MODEL=deepseek-flash
```

The same fields are in the sidebar, so you can switch servers without editing code.

## Run

```bash
streamlit run app.py
```

Put JPG, PNG, or WEBP dress photos in `data/images/`, or type another folder path in the sidebar. Select up to 10 photos of the same outfit, enter the suit code, then press **Generate image** or **Generate text**.

**Generate image** sends those photos in one call and saves one portrait, `instaimage-<code>.png`, at 1080×1350 (4:5) for Instagram. **Generate text** is a separate call. It sends the same photos to DeepSeek with the text prompt and writes one caption, which can also be reused on Facebook. Both files land in `data/output/`.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Layout

```text
app.py                         Streamlit entry point
prompts/                       saved image and text prompts
src/cloth_store/
  config.py                    paths and API settings
  models.py                    generated photo and text results
  services/                    client, prompts, image call, text call
  ui/
    styles.css
    components/                sidebar, gallery, prompt editors, results
    pages/                     the catalog screen
data/images/                   dress photos you send
data/output/                   catalog photos and marketing text
tests/                         pytest, no live API key required
```
