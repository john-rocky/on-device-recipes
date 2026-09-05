# On-device recipes

**What this solves.** You have an existing iOS or Android app and want to add one on-device AI feature: a PyTorch vision model on the phone GPU, a chat that works offline, a fine-tuned Hugging Face model. Samples show a new app. A recipe here is for an existing one: the dependency line, the one file to copy, the exact model file with its sha256, the verify command with its expected output, and the devices it was verified on, with dates.

**Who this is for.** App developers adding a feature, and coding agents that get asked to. Everything on the pages is also in [`recipes.json`](recipes.json) (schema: [`schemas/recipe.schema.json`](schemas/recipe.schema.json)), [`llms.txt`](llms.txt) and [`AGENTS.md`](AGENTS.md).

**Fastest way to try it.** Open the question that matches yours; the answer is in the first 300 words and links the recipe. To run a recipe, follow its INTEGRATION guide top to bottom and run its verify command. Pages: https://john-rocky.github.io/on-device-recipes/

## Questions

- [Can I run a PyTorch model on Android without going through ONNX?](docs/pytorch-model-on-android-without-onnx.md) — yes. litert-torch, ExecuTorch and ONNX Runtime measured on one conv + transformer model, the LiteRT GPU rank-4 and fp16 rules, quick start for all three. Last verified 2026-09-05.
- [Can LiteRT-LM run models other than Gemma?](docs/litert-lm-models-other-than-gemma.md) — draft: yes, with the ungated bundle list and Recipe 2 being written.
- [How do I run a fine-tuned Hugging Face model on iPhone?](docs/fine-tuned-hf-model-on-iphone.md) — draft: Recipe 3.

## Recipes

<!-- gen:recipes-table:start -->
| Recipe | Question it answers | Runtime | Verified on | Status |
|---|---|---|---|---|
| [Background removal (ormbg) in an existing Android app, GPU](https://github.com/john-rocky/LiteRT-Models/blob/main/ormbg/INTEGRATION.md) (`ormbg-android-gpu`) | PyTorch model on Android without ONNX | LiteRT 2.2.0, `CompiledModel` GPU | Pixel 8a (Android 16), GPU: 246 ms per image for the model, 361 ms end to end, 246/246 ops on the GPU, 2026-09-05 | verified |
| [Offline chat with Qwen2.5-1.5B-Instruct in an existing Android app](android-llm-chat/INTEGRATION.md) (`android-llm-chat`) | LiteRT-LM models other than Gemma | LiteRT-LM 0.16.1 (`litertlm-android`) | Pixel 8a (Android 16): 10.5 tokens/s decode on CPU, 13.8 on GPU, 0.7 s to first token; Stop, Release and reload checked by the instrumented test, 2026-09-05 | verified |
| A fine-tuned Hugging Face model in an existing iPhone app (`hf-finetune-iphone`) | fine-tuned HF model on iPhone | swift-litert-lm 0.1.1 + hf-to-litertlm | none yet | planned |
<!-- gen:recipes-table:end -->

Status: **verified** means the guide is published and the verify command was run on the listed device on the listed date. **in progress** means the code exists and the guide or the dated run is pending. **planned** means there is nothing to run yet.

## How this repository is kept honest

- **One source of truth per recipe.** The INTEGRATION guide and its `recipe.json` live in the repository that ships the code: LiteRT-Models for Recipe 1, this repository for Recipe 2, swift-litert-lm for Recipe 3. `recipes.json` mirrors them, and CI (`tools/check_drift.py`) fails when a mirrored entry differs from its source.
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
| `android-llm-chat/` | Recipe 2 code (planned) |
| `tools/` | `validate.py` (schema and docs checks), `check_drift.py` (mirror against source); `render.py` (planned) regenerates the `gen:` regions from `recipes.json` |

## Related repositories

Part of the john-rocky on-device AI ecosystem: models, runtimes, benchmarks and production examples for iOS and Android.

- [LiteRT-Models](https://github.com/john-rocky/LiteRT-Models): PyTorch vision models converted for the LiteRT `CompiledModel` GPU, with the conversion guide and toolkit
- [swift-litert-lm](https://github.com/john-rocky/swift-litert-lm): LiteRT-LM Swift SDK for iOS and macOS
- [hf-to-litertlm](https://github.com/john-rocky/hf-to-litertlm): converts Hugging Face fine-tunes to `.litertlm` bundles
- [apple-silicon-llm-bench](https://github.com/john-rocky/apple-silicon-llm-bench): measurements, including the Android companions

## License

Apache-2.0. Model files keep their own licenses, stated in each recipe.
