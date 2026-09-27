# Cloth store

Small Streamlit app for an online clothing shop. Put a dress photo in a folder, press **Generate image**, and an OpenAI-compatible API returns a catalog photo of that outfit, on a mannequin or a generated model. **Generate text** writes the listing copy. The general prompts are saved in `prompts/`, and your own notes are added for that run only.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Put the API key in `.env`. To use another OpenAI-compatible server later, change the base URL and model names:

```bash
API_KEY=sk-...
API_BASE_URL=https://api.openai.com/v1
IMAGE_MODEL=gpt-image-1-mini
TEXT_MODEL=gpt-4o-mini
```

The same fields are in the sidebar, so you can switch servers without editing code.

## Run

```bash
streamlit run app.py
```

`data/images/` includes a green placeholder, `sample_fabric.png`. Replace it with JPG, PNG, or WEBP dress photos, or type another folder path in the sidebar. Select a photo, edit the saved prompt if you want, add notes, then press **Generate image** or **Generate text**.

Created photos, the exact prompt used, and the marketing text are saved under `data/output/`.

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
