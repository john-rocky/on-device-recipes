# On-device recipes

Step-by-step guides for adding one AI feature to an iOS or Android app you already have, running on the device with LiteRT or LiteRT-LM, Google's on-device runtimes. There are three so far: background removal on the Android GPU, an offline chat on Android, and a fine-tuned Hugging Face model for iPhone, which has run on a Mac but not yet on an iPhone.

Each recipe lists what to add and which model file to download, and gives a command that runs the model to check it.

## Recipes

<!-- gen:recipes-summary:start -->
| Recipe | Runtime | Ran on |
|---|---|---|
| [Background removal (ormbg) in an existing Android app, on the GPU](https://github.com/john-rocky/LiteRT-Models/blob/main/ormbg/INTEGRATION.md) | LiteRT CompiledModel 2.2.0, GPU | Pixel 8a, 2026-09-05 |
| [Offline chat with Qwen2.5-1.5B-Instruct in an existing Android app (LiteRT-LM)](https://github.com/john-rocky/on-device-recipes/blob/main/android-llm-chat/INTEGRATION.md) | LiteRT-LM 0.16.1, CPU | Pixel 8a, 2026-09-05 |
| [A fine-tuned Hugging Face model in an existing iPhone app (hf-to-litertlm + swift-litert-lm)](https://github.com/john-rocky/swift-litert-lm/blob/main/docs/recipe-hf-finetune-to-iphone.md) | LiteRT-LM v0.15.0, GPU | Mac Studio (Apple M4 Max, 128 GB), 2026-09-05 |
<!-- gen:recipes-summary:end -->

[The full table](docs/index.md) has the timings on each device. If the recipe you need is missing, [ask for one](https://github.com/john-rocky/on-device-recipes/issues/new?template=recipe-request.yml).

## Guides

- [A PyTorch model on Android without ONNX](docs/pytorch-model-on-android-without-onnx.md), with litert-torch
- [LiteRT-LM with models other than Gemma](docs/litert-lm-models-other-than-gemma.md)
- [A fine-tuned Hugging Face model on iPhone](docs/fine-tuned-hf-model-on-iphone.md), with hf-to-litertlm and swift-litert-lm

These guides are also at https://john-rocky.github.io/on-device-recipes/, and [`recipes.json`](recipes.json) has the index as data. To add a recipe, see [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Related repositories

- [LiteRT-Models](https://github.com/john-rocky/LiteRT-Models): more than 120 models converted to run on Android with LiteRT, with the conversion guide and toolkit
- [swift-litert-lm](https://github.com/john-rocky/swift-litert-lm): LiteRT-LM Swift SDK for iOS and macOS
- [hf-to-litertlm](https://github.com/john-rocky/hf-to-litertlm): converts Hugging Face fine-tunes to `.litertlm` bundles
- [apple-silicon-llm-bench](https://github.com/john-rocky/apple-silicon-llm-bench): speed measurements of LLM runtimes on Apple silicon

## License

Apache-2.0. Model files keep their own licenses, stated in each recipe.
