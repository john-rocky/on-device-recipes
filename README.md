# On-device recipes

**What this solves.** You have an existing iOS or Android app and want to add one on-device AI feature: a PyTorch vision model on the phone GPU, a chat that works offline, a fine-tuned Hugging Face model. Samples show a new app. A recipe here is for an existing one: the dependency line, the one file to copy, the exact model file with its sha256, the verify command with its expected output, and the devices it was verified on, with dates.

**Who this is for.** App developers adding a feature, and coding agents that get asked to. Everything on the pages is also in [`recipes.json`](recipes.json) (schema: [`schemas/recipe.schema.json`](schemas/recipe.schema.json)), [`llms.txt`](llms.txt) and [`AGENTS.md`](AGENTS.md).

**Fastest way to try it.** Open the question that matches yours; the answer is in the first 300 words and links the recipe. To run a recipe, follow its INTEGRATION guide top to bottom and run its verify command. Pages: https://john-rocky.github.io/on-device-recipes/

## Questions

- [Can I run a PyTorch model on Android without going through ONNX?](docs/pytorch-model-on-android-without-onnx.md) — yes. litert-torch, ExecuTorch and ONNX Runtime measured on one conv + transformer model, the LiteRT GPU rank-4 and fp16 rules, quick start for all three. Last verified 2026-09-05.
- [Can LiteRT-LM run models other than Gemma?](docs/litert-lm-models-other-than-gemma.md) — yes. The ungated litert-community bundles other than Gemma, read from the Hugging Face API (base model, license, files); Recipe 2, an offline Qwen2.5-1.5B-Instruct chat in an existing Android app, verified on a Pixel 8a; when another runtime fits better. Last verified 2026-09-05.
- [How do I run a fine-tuned Hugging Face model on iPhone?](docs/fine-tuned-hf-model-on-iphone.md) — convert with hf-to-litertlm, load with swift-litert-lm. Supported families and what is refused; Recipe 3 on one representative fine-tune, verified on a Mac (M4 Max) through the same Swift call, iPhone row pending. Last verified 2026-09-05.

## Recipes

<!-- gen:recipes-table:start -->
| Recipe | Question it answers | Runtime | Verified on | Status |
|---|---|---|---|---|
| [Background removal (ormbg) in an existing Android app, on the GPU](https://github.com/john-rocky/LiteRT-Models/blob/main/ormbg/INTEGRATION.md) (`ormbg-android-gpu`) | [Can I run a PyTorch model on Android without going through ONNX?](docs/pytorch-model-on-android-without-onnx.md) | LiteRT CompiledModel 2.2.0 (`com.google.ai.edge.litert:litert`), gpu | Pixel 8a, Android 16, build CP1A.260505.005 (SDK 36), 2026-09-05: GPU: 246 ms per frame for the model, 361 ms end to end, 246/246 ops on the GPU | verified |
| [Offline chat with Qwen2.5-1.5B-Instruct in an existing Android app (LiteRT-LM)](https://github.com/john-rocky/on-device-recipes/blob/main/android-llm-chat/INTEGRATION.md) (`android-llm-chat`) | [Can LiteRT-LM run models other than Gemma?](docs/litert-lm-models-other-than-gemma.md) | LiteRT-LM 0.16.1 (`com.google.ai.edge.litertlm:litertlm-android`), cpu | Pixel 8a, Android 16, build CP1A.260505.005 (SDK 36), 2026-09-05: CPU: 10.48 tokens/s decode, 55.4 tokens/s prefill, 0.67 s to the first token; GPU: 13.8 tokens/s decode, 71.5 tokens/s prefill, 0.5 s to the first token | verified |
| [A fine-tuned Hugging Face model in an existing iPhone app (hf-to-litertlm + swift-litert-lm)](https://github.com/john-rocky/swift-litert-lm/blob/main/docs/recipe-hf-finetune-to-iphone.md) (`hf-finetune-iphone`) | [How do I run a fine-tuned Hugging Face model on iPhone?](docs/fine-tuned-hf-model-on-iphone.md) | LiteRT-LM via swift-litert-lm (LiteRTChat) v0.15.0 (xcframeworks pinned by Package.swift), gpu | Mac Studio (Apple M4 Max, 128 GB), macOS 27.0 (26A5416b), 2026-09-05: GPU: 142.7 tokens/s decode, 469.2 tokens/s prefill, 2.2 s to the first answer, 1,411 MB footprint; CPU: 33.3 tokens/s decode, 95.2 tokens/s prefill, 11.4 s to the first answer, 1,107 MB footprint | verified |
<!-- gen:recipes-table:end -->

Status: **verified** means the guide is published and the verify command was run on the listed device on the listed date. **in progress** means the code exists and the guide or the dated run is pending. **planned** means there is nothing to run yet.

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

## Related repositories

Part of the john-rocky on-device AI ecosystem: models, runtimes, benchmarks and production examples for iOS and Android.

- [LiteRT-Models](https://github.com/john-rocky/LiteRT-Models): PyTorch vision models converted for the LiteRT `CompiledModel` GPU, with the conversion guide and toolkit
- [swift-litert-lm](https://github.com/john-rocky/swift-litert-lm): LiteRT-LM Swift SDK for iOS and macOS
- [hf-to-litertlm](https://github.com/john-rocky/hf-to-litertlm): converts Hugging Face fine-tunes to `.litertlm` bundles
- [apple-silicon-llm-bench](https://github.com/john-rocky/apple-silicon-llm-bench): measurements, including the Android companions

## License

Apache-2.0. Model files keep their own licenses, stated in each recipe.
