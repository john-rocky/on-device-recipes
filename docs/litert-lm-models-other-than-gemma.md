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

Recipe 2 adds Qwen2.5-1.5B-Instruct as an offline chat to an app that already exists:
[android-llm-chat/INTEGRATION.md](https://github.com/john-rocky/on-device-recipes/blob/main/android-llm-chat/INTEGRATION.md).

```kotlin
// app/build.gradle.kts, minSdk 24
implementation("com.google.ai.edge.litertlm:litertlm-android:0.16.1")
implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.11.0")   // required pin
```

Copy `ChatEngine.kt` and `ModelProvisioner.kt` from the recipe, then:

```kotlin
val modelFile = ModelProvisioner.provision(context, MODEL_URL, MODEL_SHA256, MODEL_BYTES) { status -> }
val engine = ChatEngine(modelFile.absolutePath, cacheDir = context.cacheDir.path)
engine.initialize()                                           // seconds; Dispatchers.IO inside
engine.send("Hello").collect { chunk -> transcript.append(chunk) }
engine.cancel()   // Stop: ends the reply being generated; the next send() continues the chat
engine.close()    // Release: frees the model; initialize() loads it again with the chat kept
```

The model file (1.6 GB, sha256 in the recipe) is downloaded once into the app's `filesDir`;
`INTERNET` is needed for that download only. The verify command is
`./gradlew :app:connectedDebugAndroidTest` after pushing the model to the device; it checks the
stream, the cancel (process CPU time flat afterwards), and close() followed by initialize().

## Real-device measurements

Recipe 2's instrumented test on a Pixel 8a (Tensor G3, Android 16), LiteRT-LM 0.16.1, the q8 bundle, phone idle, 2026-09-05. Tokens/s are the runtime's own numbers, median of three turns of the same prompt.

| backend | decode tokens/s | prefill tokens/s | first token | model load / reload | process memory loaded, after release |
|---|---|---|---|---|---|
| CPU | 10.5 | 55 | 0.67 s | 8.8 s / 1.4 s | 1,929 MB, 89 MB |
| GPU | 13.8 (shorter replies, 30 to 39 tokens) | 72 | 0.50 s | 6.7 s / 5.5 s | 2,585 MB, 480 MB |

Stop and release are measured too: after a cancel the process used 80 ms of CPU time in the next 1.5 s on CPU (2,020 ms per 0.5 s while generating) and 60 ms on GPU; `close()` freed the model in 535 ms during a reply on CPU. Full lines and conditions: [INTEGRATION.md section 7](https://github.com/john-rocky/on-device-recipes/blob/main/android-llm-chat/INTEGRATION.md#7-verified--unverified). The same bundle through the litert-lm CLI on a Mac and a Galaxy S26, with a different harness: [litertlm-qwen2.5-1.5b-mac-galaxy-s26.md](https://github.com/john-rocky/apple-silicon-llm-bench/blob/main/results/android/litertlm-qwen2.5-1.5b-mac-galaxy-s26.md).

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
