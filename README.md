# Clothing Store Catalog Studio

Multimodal Streamlit app for a Pakistani clothing store in Germany. Select up to 10 outfit photos, press **Generate image**, and an OpenAI-compatible image model returns one Instagram catalog portrait (1080×1350, 4:5) of that outfit on a fashion mannequin. **Generate text** writes the caption with DeepSeek from the same photos.

This is the maintained repo (CV name: Clothing Store Catalog Studio). An older public copy lived at `instagram-catalog-posts` and is no longer updated.

```text
Photos of one outfit
        |
        +-- Generate image --> OpenAI-compatible image edit --> Instagram portrait
        |
        +-- Generate text  --> DeepSeek (or another chat model) --> caption
```

Shop name, address and tagline in `prompts/text_prompt.txt` are the placeholders `SHOP_NAME`, `SHOP_ADDRESS` and `SHOP_TAGLINE`. Notes typed in the app are added for that run only. API keys and shop photos stay local (`.env`, `data/images/`, `data/output/` are not committed).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

```bash
API_KEY=sk-...
API_BASE_URL=https://api.openai.com/v1
IMAGE_MODEL=gpt-image-1-mini

TEXT_API_KEY=sk-...
TEXT_API_BASE_URL=https://api.deepseek.com
TEXT_MODEL=deepseek-flash
```

In the sidebar you can switch image models (`gpt-image-1`, `gpt-image-1.5`, `gpt-image-2`, `chatgpt-image-latest`) without editing code. Stronger models follow the suit photos more closely and cost more.

## Run

```bash
streamlit run app.py
```

Put JPG, PNG or WEBP photos in `data/images/`, or type another folder path in the sidebar. Enter the suit code, then press **Generate image** or **Generate text**. Outputs land in `data/output/`.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Tests use stand-in API clients, so no key or photo is required.

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
data/images/                   dress photos you send (local)
data/output/                   catalog photos and marketing text (local)
tests/                         pytest, no live API key required
```

## Related

- Shop assistant: [multi-cloud-retail-agent](https://github.com/affanahmed373/multi-cloud-retail-agent)
- Planned: Streamlit Community Cloud demo (see `ROADMAP.md`)
