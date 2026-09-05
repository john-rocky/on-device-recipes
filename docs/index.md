# On-device recipes

Device-verified answers to developer questions about adding on-device AI to an existing iOS or Android app. Each page answers one question in its first 300 words, then leads to a recipe: the dependency line, the one file to copy, the model file with its sha256, a verify command with its expected output, and the devices it was verified on, with dates.

**Last verified: 2026-09-05.** Source and issues: https://github.com/john-rocky/on-device-recipes

## Questions

- [Can I run a PyTorch model on Android without going through ONNX?](pytorch-model-on-android-without-onnx.md) — yes. litert-torch, ExecuTorch and ONNX Runtime measured on one conv + transformer model, the LiteRT GPU rank-4 and fp16 rules, quick start for all three.
- Can LiteRT-LM run models other than Gemma? — in progress: yes, with the ungated bundle list and Recipe 2 being written.
- How do I run a fine-tuned Hugging Face model on iPhone? — in progress: Recipe 3.

## Recipes

<!-- gen:recipes-table:start -->
| Recipe | Question it answers | Runtime | Verified on | Status |
|---|---|---|---|---|
| [Background removal (ormbg) in an existing Android app, GPU](https://github.com/john-rocky/LiteRT-Models/blob/main/ormbg/INTEGRATION.md) (`ormbg-android-gpu`) | PyTorch model on Android without ONNX | LiteRT 2.2.0, `CompiledModel` GPU | Pixel 8a (Android 16), GPU: 246 ms per image for the model, 361 ms end to end, 246/246 ops on the GPU, 2026-09-05 | verified |
| [Offline chat with Qwen2.5-1.5B-Instruct in an existing Android app](https://github.com/john-rocky/on-device-recipes/blob/main/android-llm-chat/INTEGRATION.md) (`android-llm-chat`) | LiteRT-LM models other than Gemma | LiteRT-LM 0.16.1 (`litertlm-android`) | Pixel 8a (Android 16): 10.5 tokens/s decode on CPU, 13.8 on GPU, 0.7 s to first token; Stop, Release and reload checked by the instrumented test, 2026-09-05 | verified |
| A fine-tuned Hugging Face model in an existing iPhone app (`hf-finetune-iphone`) | fine-tuned HF model on iPhone | swift-litert-lm 0.1.1 + hf-to-litertlm | none yet | planned |
<!-- gen:recipes-table:end -->

Status: **verified** means the guide is published and the verify command was run on the listed device on the listed date. **in progress** means the code exists and the guide or the dated run is pending. **planned** means there is nothing to run yet.

## For agents

- [recipes.json](https://github.com/john-rocky/on-device-recipes/blob/main/recipes.json): every recipe, machine-readable; schema in [recipe.schema.json](https://github.com/john-rocky/on-device-recipes/blob/main/schemas/recipe.schema.json).
- [llms.txt](https://github.com/john-rocky/on-device-recipes/blob/main/llms.txt) and [AGENTS.md](https://github.com/john-rocky/on-device-recipes/blob/main/AGENTS.md): the same index for language models and coding agents.

## Attribution

- [Provenance block](provenance.md): the five lines every recipe, model card and page carries, and where they go.

Part of the john-rocky on-device AI ecosystem: models, runtimes, benchmarks and production examples for iOS and Android. Related: [LiteRT-Models](https://github.com/john-rocky/LiteRT-Models), [swift-litert-lm](https://github.com/john-rocky/swift-litert-lm), [hf-to-litertlm](https://github.com/john-rocky/hf-to-litertlm), [apple-silicon-llm-bench](https://github.com/john-rocky/apple-silicon-llm-bench).
