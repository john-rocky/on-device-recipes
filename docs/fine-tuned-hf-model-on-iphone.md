---
published: false
---

<!-- Draft. The body follows Recipe 3, docs/recipe-hf-finetune-to-iphone.md in swift-litert-lm. Remove `published: false` when the body is complete. -->

# How do I run a fine-tuned Hugging Face model on iPhone?

**Last verified: 2026-09-05** — draft; converter, SDK and device rows are filled in with the body.

## Direct answer

Convert the fine-tune to a `.litertlm` bundle with [hf-to-litertlm](https://github.com/john-rocky/hf-to-litertlm) (`python scripts/convert.py <org>/<model>`; LoRA merge included; gated and remote-code repositories are refused at the entry gate), then load the bundle in the app with [swift-litert-lm](https://github.com/john-rocky/swift-litert-lm) (`LiteRTChat(modelFileURL:)`, or `LiteRTChat(huggingFaceRepo:fileName:)` to download). Supported models are the dense architectures the stock exporter handles plus the families with their own lanes in the converter's README; the exact list goes here with the body. The simulator cannot run the bundle: verification is on a physical iPhone, or on a Mac with the `litert-lm` CLI. The representative fine-tune, its conversion report and the device rows are being added (Recipe 3).

## Supported models

Pending: quoted from the hf-to-litertlm README at a named commit, with the unsupported cases.

## Decision table

Pending.

## Quick start

Pending: one Swift package dependency, five lines of Swift, one model distribution pattern, cancel (`Task` cancellation) and release.

## Real-device measurements

Pending: Mac host run (M4 Max, date) and iPhone 17 Pro rows when available.

## When to use, when not to use, alternatives

Pending. This section will say when llama.cpp (GGUF), MLX, Core ML or Apple's Foundation Models are the better fit.

## Implementation links

- Recipe 3 (planned): `docs/recipe-hf-finetune-to-iphone.md` in swift-litert-lm.

## Model links

Pending.

## FAQ

Pending.

## Related

- [Can I run a PyTorch model on Android without going through ONNX?](pytorch-model-on-android-without-onnx.md)

## Provenance

Pending until the body is written; the block follows [provenance.md](provenance.md).
