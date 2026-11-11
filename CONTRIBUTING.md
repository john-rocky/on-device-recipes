# Contributing

## Want a recipe? Say what you want to add.

Open a [recipe request](https://github.com/john-rocky/on-device-recipes/issues/new?template=recipe-request.yml):
the feature and the platform, one sentence. The recipe comes back on the issue, verified on a
named device with a date, or the reason it cannot be done yet. A request to convert a specific
model belongs in [hf-to-litertlm](https://github.com/john-rocky/hf-to-litertlm/issues/new?template=model-request.yml).

## A recipe broke for you

File it where the recipe's code lives: the `Maintained at` line of its provenance block
(Recipe 1: LiteRT-Models, Recipe 2: here, Recipe 3: swift-litert-lm). Include the runtime
version, your device and OS build, and the verify command's output.

## Pull requests

- **A run on a device we don't have.** Follow a recipe's INTEGRATION guide to the end, run its
  verify command, and post device, OS build, date and the output on an issue. Rows are added
  from posted runs; nothing is extrapolated.
- **Docs and tools.** A clearer page, a check in `tools/validate.py`, a skill under `skills/`
  that resolves its versions from `recipe.json`.
- **A new recipe.** The code and its `recipe.json` live in the repository that ships the code.
  Here it is vendored with `python tools/vendor.py <id> <path or raw URL> --status verified`,
  then `python tools/validate.py`, `python tools/check_drift.py`, `python tools/render.py`.
  CI runs the same three.

Issues labeled [good first issue](https://github.com/john-rocky/on-device-recipes/labels/good%20first%20issue)
are scoped for a first PR.

Rules that keep the pages honest ([AGENTS.md](AGENTS.md) has the full list):

- Every number is a dated run on a named device with the report linked. No estimates, no "best".
- Never edit text between `gen:` markers; `tools/render.py` regenerates it and CI fails on drift.
- Model files stay out of git; a recipe points at the Hugging Face file and its sha256.
- Each page says when another runtime is the better choice.
- Code and comments in English. Apache-2.0; model files keep their own licenses.

## How this repository is kept honest

- **One source of truth per recipe.** The INTEGRATION guide and its `recipe.json` live in the repository that ships the code: LiteRT-Models for Recipe 1, this repository for Recipe 2, swift-litert-lm for Recipe 3. `recipes.json` mirrors them, and CI (`tools/check_drift.py`) fails when a mirrored entry differs from its source.
- **Generated, not retyped.** The recipe tables, the bundle list, the per-recipe facts on the pages and the `llms.txt` lines sit between `gen:` markers and are written by `tools/render.py` from `recipes.json`; CI fails when they drift. The same generator writes, per recipe, the addendum for the model author's card and the lines for LiteRT-side lists, so every surface quotes the same numbers.
- **Canonical text.** The pages under `docs/` are the canonical version of each answer. Article copies (dev.to, Zenn, Medium) are snapshots that link back here and are not edited after publishing; corrections land in `docs/` first.
- **Numbers.** Every number comes from a dated run on a named device, with the report linked. No estimates, and no "best".
- **Neutral.** Each page says when another runtime is the better choice.
- **Attribution.** Every recipe, card and page ends with the same five-line block: who converted and verified, recipe URL, measurement report, commit, where to file issues. Format and placement: [`docs/provenance.md`](docs/provenance.md).

## Layout

| path | what |
|---|---|
| `docs/` | question pages; published with GitHub Pages from this folder |
| `recipes.json`, `schemas/recipe.schema.json` | machine-readable index and its schema |
| `llms.txt`, `AGENTS.md` | the same index for language models and coding agents |
| `measurements/` | measurement records quoted by the pages that have no other public home |
| `android-llm-chat/` | Recipe 2: code, instrumented test, `INTEGRATION.md`, `recipe.json` |
| `skills/` | step-by-step procedures for coding agents applying a recipe; versions resolved from `recipe.json` |
| `data/` | `litert-community-litertlm.json`: the Hugging Face listing behind the bundle list, dated (`tools/render.py --fetch`) |
| `tools/` | `vendor.py` (copy a recipe.json into the index), `validate.py` (schema and docs checks), `check_drift.py` (index against each source), `render.py` (regenerates every `gen:` region, `llms.txt` lines and `out/<id>/` addenda from `recipes.json`; `--check` in CI) |

## Status words

Status: **verified** means the guide is published and the verify command was run on the listed device on the listed date. **in progress** means the code exists and the guide or the dated run is pending. **planned** means there is nothing to run yet.
