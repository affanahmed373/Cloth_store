# Roadmap

Planned improvements. Each item lists the skill it proves and what "done" means.
Add the skill to the CV only after the item is pushed.

## 0. Go public and live demo (priority: highest)
Proves: a multimodal app anyone can open from the CV link.
- [x] Make this repo public. The CV already links `github.com/affanahmed373/Cloth_store`.
- [x] Make `instagram-catalog-posts` private. Its README already points here.
- [x] Update this README, the profile README (`affanahmed373`), and the catalog copy's README to name this as the maintained repo.
- [x] Set the GitHub description to Clothing Store Catalog Studio.
- [ ] Pin order on the profile (GitHub UI only; no API): 1 retail agent, 2 Cloth_store, 3 spice shop, 4 evals, 5 governance, 6 GNNxEval.
- [x] Remove the tracked `.DS_Store`.
- [ ] Deploy to Streamlit Community Cloud (free, deploys from GitHub).
- [ ] Hosted mode: `st.file_uploader` instead of the folder picker (the desktop folder window cannot open on a server). Keep the folder picker for local use.
- [ ] Visitors paste their own OpenAI key in the sidebar (already supported); no shared key on the public app. Never store uploaded photos.
- [ ] Before/after gallery from `examples/` so visitors see the result without a key (with the shop's permission).
Done when: the app link is in the README and the profile README, and a visitor without a key still sees example output.

## 1. Background job queue (priority: medium)
Proves: task queues (Celery + Redis), long-running AI jobs.
- [ ] Run image and caption generation as Celery tasks with Redis as broker; the Streamlit UI polls job status.
- [ ] Move the existing cancel logic to task revocation.
- [ ] Batch mode: generate a whole folder of outfits overnight.
Done when: several outfits can be queued and the UI stays responsive.

## 2. Quality checks on generated images (priority: medium)
Proves: multimodal evaluation, vision-LLM-as-judge.
- [ ] Vision-model check that compares the generated image to the source photos (colour, sleeves, embroidery) and flags mismatches.
- [ ] Track cost per image and per model in a small table (CSV or SQLite) and show it in the sidebar.

## 3. Structured listing output (priority: low)
Proves: structured outputs.
- [ ] Return caption, hashtags, fabric, colours and suggested price as a Pydantic model; export as CSV for the shop catalog.
- [ ] Feed the same fields into `multi-cloud-retail-agent`'s `products.json`.

## 4. Offer posts for the spice shop (priority: medium)
Proves: the same multimodal pipeline serves a second business through prompts, not new code.
- [ ] Prompt sets per shop in `prompts/` (`clothing/`, `spice/`) and a shop selector in the sidebar.
- [ ] Spice shop post: product photos plus offer text (product, price, dates) into one 1080x1350 image, for Eid, Ramadan and weekly offers.
- [ ] Caption in Urdu, German and English.
Done when: one app makes posts for both shops and the README shows one example of each.

## 5. Google review replies (priority: low)
Proves: human-in-the-loop drafting.
- [ ] Paste a review, get a short reply draft in the reviewer's language; the owner edits and copies it. Nothing is posted automatically.

## 6. Repo hygiene (priority: high)
- [ ] GitHub Actions: lint + pytest on every push (tests already exist).
- [ ] Before/after example images in the README (with the shop's permission).
- [x] Decide on this repo vs `instagram-catalog-posts`: keep this one (the CV links it, longer history), archive the other.
