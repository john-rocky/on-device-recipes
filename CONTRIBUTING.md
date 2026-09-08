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
