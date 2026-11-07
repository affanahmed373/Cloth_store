# Roadmap

Planned improvements. Each item lists the skill it proves and what "done" means.
Add the skill to the CV only after the item is pushed.

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

## 4. Repo hygiene (priority: high)
- [ ] GitHub Actions: lint + pytest on every push (tests already exist).
- [ ] Before/after example images in the README (with the shop's permission).
- [ ] Decide on this repo vs `instagram-catalog-posts`: merge or archive one so the CV links a single repo.
