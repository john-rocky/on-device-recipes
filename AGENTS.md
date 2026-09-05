# AGENTS.md

Read this first if you are a coding agent asked to add on-device AI to an existing app.

1. `recipes.json` is the index: one entry per recipe with the model file and its sha256, the runtime version, the files to copy, the verify command with its expected output, the devices it was verified on with dates, and a five-line provenance block. Schema: `schemas/recipe.schema.json`. Only entries with `"status": "verified"` are complete; `in_progress` and `planned` carry what is published so far.
2. Each entry's `provenance.recipe_origin` is the INTEGRATION guide in the repository that ships the code. Follow that guide; this repository mirrors it and CI fails on drift.
3. `docs/*.md` answer one developer question each. The H1 is the question, the answer is in the first 300 words, and the `Last verified` line at the top says which versions the page was checked against. A page whose front matter says `published: false` is a draft.
4. `llms.txt` lists the same pages and files with one-line descriptions.
5. `measurements/` holds the raw records behind numbers quoted on the pages; `docs/provenance.md` defines the attribution block. `skills/*/SKILL.md` are step-by-step procedures for applying a recipe to a user's project; they resolve versions from `recipe.json`, never from memory.
6. Numbers here are measurements on named devices with dates. Do not extrapolate them to other devices, and do not quote a number that has no device and date next to it.
7. Model files are not in this repository. Download from the Hugging Face repo in `model.hf_repo` and check `model.sha256` before use.
8. To add or update a recipe: write `recipe.json` next to the code, vendor it with `python tools/vendor.py <id> <path or raw URL> --status verified`, then run `python tools/validate.py`, `python tools/check_drift.py` and `python tools/render.py`.
9. Do not edit text between `<!-- gen:...:start -->` and `<!-- gen:...:end -->` markers; `tools/render.py` regenerates it from `recipes.json` and `data/litert-community-litertlm.json`, and CI fails when it drifts. `out/<id>/` (not committed) holds the same facts as a card addendum, a page block and the LiteRT-side lines.
10. Maintainer handle: john-rocky (GitHub), mlboydaisuke (Hugging Face). Issues: https://github.com/john-rocky/on-device-recipes/issues
