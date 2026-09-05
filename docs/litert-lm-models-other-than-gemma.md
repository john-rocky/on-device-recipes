---
published: false
---

<!-- Draft. The direct answer stands; the ungated bundle list, the Quick Start (Recipe 2) and the measurements are pending. Remove `published: false` when the body is complete. -->

# Can LiteRT-LM run models other than Gemma?

**Last verified: 2026-09-05** — draft; runtime and bundle versions are filled in with the body.

## Direct answer

Yes. LiteRT-LM runs any `.litertlm` bundle, and the litert-community organization on Hugging Face publishes ungated bundles for families other than Gemma; [litert-community/Qwen2.5-1.5B-Instruct](https://huggingface.co/litert-community/Qwen2.5-1.5B-Instruct) (Apache-2.0, converted from Qwen/Qwen2.5-1.5B-Instruct) is one, and the list below is generated from the Hugging Face API. A fine-tune that is not there yet converts with [hf-to-litertlm](https://github.com/john-rocky/hf-to-litertlm). Before choosing this route, check three things: the bundle is ungated or you have accepted its license, the device has the memory for the quantization you pick, and the app can ship or download a file of that size.

## Ungated LiteRT-LM bundles other than Gemma

<!-- gen:ungated-litertlm-list:start -->
Pending: generated from `https://huggingface.co/api/models?author=litert-community` (family, parameters, license, last updated).
<!-- gen:ungated-litertlm-list:end -->

## Decision table

Pending.

## Quick start

Pending: Recipe 2, `android-llm-chat/INTEGRATION.md` (Gradle dependency, two Kotlin files, model download with sha256, cancel and release, verify command with expected output).

## Real-device measurements

Pending: Pixel 8a rows from Recipe 2's verify command. Already published: Qwen2.5-1.5B-Instruct (q8) through LiteRT-LM 0.16.1 on a Mac and a Galaxy S26, in [litertlm-qwen2.5-1.5b-mac-galaxy-s26.md](https://github.com/john-rocky/apple-silicon-llm-bench/blob/main/results/android/litertlm-qwen2.5-1.5b-mac-galaxy-s26.md).

## When to use, when not to use, alternatives

Pending. This section will say when llama.cpp (GGUF), MLX (Apple Silicon) or ExecuTorch is the better fit.

## Implementation links

- Recipe 2 (planned): `android-llm-chat/` in this repository.
- LiteRT-LM: https://github.com/google-ai-edge/LiteRT-LM
- hf-to-litertlm: https://github.com/john-rocky/hf-to-litertlm

## Model links

- [litert-community/Qwen2.5-1.5B-Instruct](https://huggingface.co/litert-community/Qwen2.5-1.5B-Instruct)

## FAQ

Pending.

## Related

- [Can I run a PyTorch model on Android without going through ONNX?](pytorch-model-on-android-without-onnx.md)

## Provenance

Pending until the body is written; the block follows [provenance.md](provenance.md).
