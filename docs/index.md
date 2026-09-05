# On-device recipes

Device-verified answers to developer questions about adding on-device AI to an existing iOS or Android app. Each page answers one question in its first 300 words, then leads to a recipe: the dependency line, the one file to copy, the model file with its sha256, a verify command with its expected output, and the devices it was verified on, with dates.

**Last verified: 2026-09-05.** Source and issues: https://github.com/john-rocky/on-device-recipes

## Questions

- [Can I run a PyTorch model on Android without going through ONNX?](pytorch-model-on-android-without-onnx.md) — yes. litert-torch, ExecuTorch and ONNX Runtime measured on one conv + transformer model, the LiteRT GPU rank-4 and fp16 rules, quick start for all three.
- [Can LiteRT-LM run models other than Gemma?](litert-lm-models-other-than-gemma.md) — yes. The ungated litert-community bundles other than Gemma, read from the Hugging Face API; Recipe 2, an offline Qwen2.5-1.5B-Instruct chat in an existing Android app, verified on a Pixel 8a; when another runtime fits better.
- [How do I run a fine-tuned Hugging Face model on iPhone?](fine-tuned-hf-model-on-iphone.md) — convert with hf-to-litertlm, load with swift-litert-lm. Supported families and what is refused; Recipe 3 on one representative fine-tune, verified on a Mac (M4 Max), iPhone row pending.

## Recipes

<!-- gen:recipes-table:start -->
| Recipe | Question it answers | Runtime | Verified on | Status |
|---|---|---|---|---|
| [Background removal (ormbg) in an existing Android app, on the GPU](https://github.com/john-rocky/LiteRT-Models/blob/main/ormbg/INTEGRATION.md) (`ormbg-android-gpu`) | [Can I run a PyTorch model on Android without going through ONNX?](pytorch-model-on-android-without-onnx.md) | LiteRT CompiledModel 2.2.0 (`com.google.ai.edge.litert:litert`), gpu | Pixel 8a, Android 16, build CP1A.260505.005 (SDK 36), 2026-09-05: GPU: 246 ms per frame for the model, 361 ms end to end, 246/246 ops on the GPU | verified |
| [Offline chat with Qwen2.5-1.5B-Instruct in an existing Android app (LiteRT-LM)](https://github.com/john-rocky/on-device-recipes/blob/main/android-llm-chat/INTEGRATION.md) (`android-llm-chat`) | [Can LiteRT-LM run models other than Gemma?](litert-lm-models-other-than-gemma.md) | LiteRT-LM 0.16.1 (`com.google.ai.edge.litertlm:litertlm-android`), cpu | Pixel 8a, Android 16, build CP1A.260505.005 (SDK 36), 2026-09-05: CPU: 10.48 tokens/s decode, 55.4 tokens/s prefill, 0.67 s to the first token; GPU: 13.8 tokens/s decode, 71.5 tokens/s prefill, 0.5 s to the first token | verified |
| [A fine-tuned Hugging Face model in an existing iPhone app (hf-to-litertlm + swift-litert-lm)](https://github.com/john-rocky/swift-litert-lm/blob/main/docs/recipe-hf-finetune-to-iphone.md) (`hf-finetune-iphone`) | [How do I run a fine-tuned Hugging Face model on iPhone?](fine-tuned-hf-model-on-iphone.md) | LiteRT-LM via swift-litert-lm (LiteRTChat) v0.15.0 (xcframeworks pinned by Package.swift), gpu | Mac Studio (Apple M4 Max, 128 GB), macOS 27.0 (26A5416b), 2026-09-05: GPU: 142.7 tokens/s decode, 469.2 tokens/s prefill, 2.2 s to the first answer, 1,411 MB footprint; CPU: 33.3 tokens/s decode, 95.2 tokens/s prefill, 11.4 s to the first answer, 1,107 MB footprint | verified |
<!-- gen:recipes-table:end -->

Status: **verified** means the guide is published and the verify command was run on the listed device on the listed date. **in progress** means the code exists and the guide or the dated run is pending. **planned** means there is nothing to run yet.

## For agents

- [recipes.json](https://github.com/john-rocky/on-device-recipes/blob/main/recipes.json): every recipe, machine-readable; schema in [recipe.schema.json](https://github.com/john-rocky/on-device-recipes/blob/main/schemas/recipe.schema.json).
- [llms.txt](https://github.com/john-rocky/on-device-recipes/blob/main/llms.txt) and [AGENTS.md](https://github.com/john-rocky/on-device-recipes/blob/main/AGENTS.md): the same index for language models and coding agents.

## Attribution

- [Provenance block](provenance.md): the five lines every recipe, model card and page carries, and where they go.

Part of the john-rocky on-device AI ecosystem: models, runtimes, benchmarks and production examples for iOS and Android. Related: [LiteRT-Models](https://github.com/john-rocky/LiteRT-Models), [swift-litert-lm](https://github.com/john-rocky/swift-litert-lm), [hf-to-litertlm](https://github.com/john-rocky/hf-to-litertlm), [apple-silicon-llm-bench](https://github.com/john-rocky/apple-silicon-llm-bench).
