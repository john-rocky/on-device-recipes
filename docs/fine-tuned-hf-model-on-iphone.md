# How do I run a fine-tuned Hugging Face model on iPhone?

**Last verified: 2026-09-05** — hf-to-litertlm at 5ffe9ee (litert-torch 0.9.3, ai-edge-quantizer 0.8.0, transformers 5.14.1, litert-lm-builder 0.15.0); swift-litert-lm 0.2.0 (LiteRT-LM v0.15.0 xcframeworks) with Xcode 27.0 beta 5 and Xcode 26.1.1; litert-lm 0.16.0 and 0.17.0 CLI wheels; Mac Studio (M4 Max), macOS 27.0. No iPhone run yet.

## Direct answer

Convert the fine-tune to one `.litertlm` file with [hf-to-litertlm](https://github.com/john-rocky/hf-to-litertlm) (`python scripts/convert.py <org>/<model>`; LoRA adapters are merged into their base first; gated repositories, repository-local architectures and pre-quantized weights are refused at the entry gate), host the file where the app can download it, and load it with `LiteRTChat` from [swift-litert-lm](https://github.com/john-rocky/swift-litert-lm) (`LiteRTChat(huggingFaceRepo:fileName:)` to download, `LiteRTChat(modelFileURL:)` for a local file). Supported models are the dense architectures the stock exporter handles (Llama 3.x, Qwen 2/2.5/3, SmolLM3, OLMo-2, Phi, Ministral) plus the families with their own lanes in the converter, listed below.

Recipe 3 does this for one representative fine-tune, [suayptalha/Qwen3-0.6B-Code-Expert](https://huggingface.co/suayptalha/Qwen3-0.6B-Code-Expert) (Apache-2.0, a full fine-tune of Qwen3-0.6B): converted in 217 s, gate 7 of 8, and answered through `LiteRTChat` on a Mac Studio (M4 Max) at 142.7 tokens/s on the GPU. The converted bundle is published as [mlboydaisuke/Qwen3-0.6B-Code-Expert-LiteRT](https://huggingface.co/mlboydaisuke/Qwen3-0.6B-Code-Expert-LiteRT), so the verify command below needs no conversion. **No iPhone has run it yet**: the iPhone 17 Pro row is added when the device is available, and the iOS Simulator was not run either (the runtime xcframework ships an `ios-arm64-simulator` slice; nothing was tried on it). macOS is a supported platform of the same package, so the Mac rows are the same Swift call the iPhone app makes.

Two limits, up front: a second message on the same `LiteRTChat` fails for Qwen3-template bundles on the pinned runtime (upstream issue [google-ai-edge/LiteRT-LM#3443](https://github.com/google-ai-edge/LiteRT-LM/issues/3443); the recipe uses one `LiteRTChat` per turn), and tag 0.1.1 of the package does not compile for iOS with Xcode 26.1.1 or 27.0 beta 5, so use 0.2.0 or later.

## Supported models

Quoted from the hf-to-litertlm README at [5ffe9ee](https://github.com/john-rocky/hf-to-litertlm/blob/5ffe9ee/README.md#convert-a-finetune) through the recipe (Hub derivative counts recounted there on 2026-08-26). The converter routes by `config.json` `model_type`.

| base family | bases | Hub finetunes + adapters | toolchain | path |
|---|---|---|---:|---|
| any dense arch the stock exporter handles | llama 3.x, qwen 2/2.5/3, smollm3, olmo2, phi, ministral, … | open-ended | default stack | stock export |
| MiniCPM5 | 1B | 53 + 54 | default stack | stock export (plain llama rail) |
| granite-4.1 (dense) | 3b | 20 + 15 | default stack | stock export; spurious-BOS guard fires (bos == eos) |
| Hy-MT2 (hunyuan_v1_dense) | 1.8B | 10 + 1 | default stack | stock export after a bitwise-equal rope bake; duplicate-BOS guard fires |
| Qwen3.5 | 0.8B / 2B / 4B | 1,214 + 928 | litert-torch *main* | stock export; CPU gate |
| LFM2.5 | 350M / 1.2B / 2.6B | 210 + 94 | released 0.9.3/0.9.4 | stock export + ExecutorMetadata retrofit |
| granite-4.0-h | 350m / 1b | 24 + 4 | pinned checkout | family recipe (`HYBRID_RECIPE`) |
| Falcon-H1 | 0.5B / 1.5B / 1.5B-Deep / 3B | 14 + 2 | pinned checkout | family recipe (`HYBRID_RECIPE`) |
| Zamba2 | 1.2B / 2.7B | 3 + 0; the only real one is pre-port-serialized | pinned checkout | routed; pre-port checkpoints are refused with re-serialization instructions |
| Nemotron-H | Nemotron-H-4B / Nemotron-3-Nano-4B | 19 + 14 | pinned checkout | family recipe (`HYBRID_RECIPE`) |

Refused at the entry gate, with a JSON reason and exit code 2: gated repositories, architectures that live in repository code (`auto_map` with a `model_type` transformers does not register), pre-quantized weights (GPTQ, AWQ, bitsandbytes), and pre-port Zamba2 checkpoints. Not covered: mixture-of-experts models, diffusion language models, encoder-only or classifier heads. Vision-language derivatives use a separate script in the same repository.

Size decides more than architecture on a phone: the converter's default is int8 weights, about one byte per parameter plus the tokenizer (613,406,208 bytes for the 596,049,920-parameter model below). Models of 3B parameters and more get the embedding split out so the main section stays under the iOS mmap limit; that path is not exercised in Recipe 3.

## Decision table

| you have | route | why |
|---|---|---|
| a fine-tune of a family in the table above, an iOS or macOS app | hf-to-litertlm, then swift-litert-lm (Recipe 3) | one command to a bundle, one Swift package, one download pattern |
| a fine-tune of a family in the table above, an Android app | hf-to-litertlm, then Recipe 2's Kotlin files | same bundle file; [the Android page](litert-lm-models-other-than-gemma.md) |
| a model already on the litert-community list | skip the conversion; load the published bundle | [the Android page](litert-lm-models-other-than-gemma.md) lists them |
| a LoRA adapter repository | hf-to-litertlm merges it into the base first | the merged path is in the converter; not exercised in Recipe 3 |
| a model the converter refuses, or weights only in GGUF or MLX form | another runtime, see "When not to use" | no bundle can be made |
| no custom weights, iOS 26 or later | Apple's Foundation Models framework | the system model, no file to ship |

## Quick start

<!-- gen:recipe-answer:hf-finetune-iphone:start -->
**Run a fine-tuned Hugging Face model in an existing iPhone app (convert with hf-to-litertlm, load with swift-litert-lm).** Model: [mlboydaisuke/Qwen3-0.6B-Code-Expert-LiteRT](https://huggingface.co/mlboydaisuke/Qwen3-0.6B-Code-Expert-LiteRT) `model.litertlm` (613,406,208 bytes, apache-2.0, from [Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B)). Runtime: LiteRT-LM via swift-litert-lm (LiteRTChat) v0.15.0 (xcframeworks pinned by Package.swift), gpu. Verified: Mac Studio (Apple M4 Max, 128 GB), macOS 27.0 (26A5416b), 2026-09-05: GPU: 142.7 tokens/s decode, 469.2 tokens/s prefill, 2.2 s to the first answer, 1,411 MB footprint; CPU: 33.3 tokens/s decode, 95.2 tokens/s prefill, 11.4 s to the first answer, 1,107 MB footprint. Status: verified. Guide: https://github.com/john-rocky/swift-litert-lm/blob/main/docs/recipe-hf-finetune-to-iphone.md; machine-readable: https://raw.githubusercontent.com/john-rocky/swift-litert-lm/main/docs/recipe.json.
<!-- gen:recipe-answer:hf-finetune-iphone:end -->

**Convert** (once, on a Mac or Linux box):

```bash
git clone https://github.com/john-rocky/hf-to-litertlm && cd hf-to-litertlm
pip install litert-torch ai-edge-quantizer "transformers==5.14.*" huggingface_hub litert-lm
python scripts/convert.py suayptalha/Qwen3-0.6B-Code-Expert
# -> out/Qwen3-0.6B-Code-Expert/model.litertlm, gate.json, convert_report.json
```

Exit 0 means converted and gated, 1 converted but the gate failed, 2 refused at the entry gate.

**Add it to the app.** Xcode: File → Add Package Dependencies → `https://github.com/john-rocky/swift-litert-lm`, product `LiteRTFoundation` (tag 0.2.0 or later). Then:

```swift
import LiteRTFoundation

var chat: LiteRTChat? = try await LiteRTChat(
  huggingFaceRepo: "<your-org>/<your-model>-litertlm", fileName: "model.litertlm",
  modalities: [])                        // text-only bundle
let generation = Task {
  for try await delta in chat!.stream("What is 17 + 25? Answer briefly.") { transcript.append(delta) }
}
try chat?.cancel()                       // Stop: the model is idle within 0.5 s; the stream throws CANCELLED
chat = nil                               // Release: Engine and Conversation free their handles in deinit
```

Upload the `.litertlm` to a public, ungated Hugging Face repository you own; the downloader is chunked and resumable and sends no token. During development, copy the file into the app's Documents with `xcrun devicectl device copy to` and load it with `LiteRTChat(modelFileURL:modalities: [])`.

The package lines, the model file, the stop and release behaviour, the second-turn limit and the verify command, from `recipe.json`:

<!-- gen:recipe-conditions:hf-finetune-iphone:start -->
| | |
|---|---|
| model repository | [mlboydaisuke/Qwen3-0.6B-Code-Expert-LiteRT](https://huggingface.co/mlboydaisuke/Qwen3-0.6B-Code-Expert-LiteRT) |
| model file | `model.litertlm` |
| download URL | <https://huggingface.co/mlboydaisuke/Qwen3-0.6B-Code-Expert-LiteRT/resolve/main/model.litertlm> |
| sha256 | `b9f8587090b56934e4189a9d969193b5c2fcc120b44ae819692451c92e88f480` |
| size, bytes | 613,406,208 |
| license | apache-2.0 |
| base model | [Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B) |
| converted from | [suayptalha/Qwen3-0.6B-Code-Expert](https://huggingface.co/suayptalha/Qwen3-0.6B-Code-Expert) |
| source revision | 02c021dfc15bb3c2d4bd6d26671aba778fc4e840 |
| license note | apache-2.0 in the card metadata; the card's LICENSE link points at a file the repo does not contain |
| parameters | 596,049,920 |
| variant | int8 weights (converter default), context 4096 tokens, thought channel <think>/</think>, stop tokens 151645 and 151643 |
| published by | mlboydaisuke (own conversion of the fine-tune above); not gated |
| runtime | LiteRT-LM via swift-litert-lm (LiteRTChat) |
| runtime version | v0.15.0 (xcframeworks pinned by Package.swift) |
| Swift package | <https://github.com/john-rocky/swift-litert-lm> |
| Swift package tag | 0.2.0 (09f04f1), tagged 2026-09-05. Tag 0.1.1 and main before 09f04f1 do not compile for iOS with Xcode 26.1.1 or Xcode 27.0 beta 5; the Easy-mode sources used here are unchanged since e82e3b1 |
| accelerator | gpu |
| converter | hf-to-litertlm scripts/convert.py (litert-torch 0.9.3, ai-edge-quantizer 0.8.0, transformers 5.14.1, litert-lm-builder 0.15.0) |
| converter version | hf-to-litertlm@5ffe9ee |
| conversion script | `scripts/convert.py` |
| conversion command | `python scripts/convert.py suayptalha/Qwen3-0.6B-Code-Expert` |
| minimum OS | iOS 16 (Easy mode); macOS 13 |
<!-- gen:recipe-conditions:hf-finetune-iphone:end -->

<!-- gen:recipe-steps:hf-finetune-iphone:start -->
1. Dependency lines, exactly as they go into the build file:

   ```
   .package(url: "https://github.com/john-rocky/swift-litert-lm", from: "0.2.0")
   .product(name: "LiteRTFoundation", package: "swift-litert-lm")
   ```

   minimum OS iOS 16 (Easy mode); macOS 13.

2. Code:

   ```swift
   let chat = try await LiteRTChat(huggingFaceRepo: "mlboydaisuke/Qwen3-0.6B-Code-Expert-LiteRT", fileName: "model.litertlm", modalities: []); for try await delta in chat.stream(prompt) { ... }
   ```

3. Model delivery: public, ungated Hugging Face repo; LiteRTChat(huggingFaceRepo:fileName:) downloads the file once into Application Support/LiteRTModels (excluded from iCloud backup, chunked, resumable, no auth token). Development: devicectl copy into the app's Documents and LiteRTChat(modelFileURL:modalities: []).

4. Stop: chat.cancel(): model idle within 0.5 s (GPU and CPU); the stream throws CANCELLED and the conversation cannot take another message. Cancelling only the reading Task does not stop the model (it decoded the full 2,017-token essay after the reader left at 10 deltas).

5. Release: drop the last reference (chat = nil): Engine and Conversation free their native handles in deinit. GPU footprint 1,376 -> 226 MB two seconds later; CPU 1,105 -> 1,052 MB; fresh load 0.1 s.

6. Second turn: fails on the same conversation with failedToStartStream(status: 13), INTERNAL 'rendered template string does not start with the previous', thinking off and on, GPU and CPU: google-ai-edge/LiteRT-LM#3443 (Qwen3 template). Workaround: one LiteRTChat per turn, history carried in the prompt.

7. Verify:

   ```sh
   python3 -m venv lt && lt/bin/pip install "litert-lm==0.17.0" && lt/bin/litert-lm run --from-huggingface-repo mlboydaisuke/Qwen3-0.6B-Code-Expert-LiteRT model.litertlm --prompt "What is 17 + 25? Answer briefly." --thinking false --temperature 0 --top-k 1
   ```

   Expected, from the run recorded in recipe.json: 17 + 25 = 42 (litert-lm 0.17.0 on the local file: 1.1 s wall; 0.16.0: 1.0 s; Mac Studio M4 Max, 2026-09-05; repo form 67 s wall including the 613 MB download; one earlier attempt stalled in the download and was killed after 10 min, the retry went through). With thinking left on and greedy sampling the same prompt looped on '17 + 25.' inside the thought channel for 128 s with no answer; with the CLI's default sampler and thinking on (0.17.0) it thought one paragraph and answered 17 + 25 = 42.

   Device command: PENDING: Samples/LiteRTDemo local-model self-test (devicectl copy into Documents, launch with LITERT_LOCAL_TEST=1, read the LOCAL: lines); the sample does not build on 2026-09-05 (references LiteRTAudioSegment/LiteRTVideoSegment removed for Xcode 27 beta 5)
<!-- gen:recipe-steps:hf-finetune-iphone:end -->

## Real-device measurements

Mac Studio (Apple M4 Max, 128 GB), macOS 27.0, through this package's `LiteRTChat` on 2026-09-05; the iPhone row is pending. The conversion gate on the same machine: 7 of 8 questions correct, no degenerate answer, median decode 138.3 tokens/s on the GPU.

<!-- gen:recipe-measurements:hf-finetune-iphone:start -->
| device | OS | backend | runtime | decode tokens/s | prefill tokens/s | first answer s | footprint MB | output | date |
|---|---|---|---|---|---|---|---|---|---|
| Mac Studio (Apple M4 Max, 128 GB) | macOS 27.0 (26A5416b) | gpu | LiteRT-LM v0.15.0 via swift-litert-lm LiteRTChat (0.2.0 = 09f04f1, Xcode 27.0 beta 5 27A5237l) | 142.7 | 469.2 | 2.2 | 1,411 | 17 + 25 = 42 | 2026-09-05 |
| Mac Studio (Apple M4 Max, 128 GB) | macOS 27.0 (26A5416b) | cpu | LiteRT-LM v0.15.0 via swift-litert-lm LiteRTChat (0.2.0 = 09f04f1) | 33.3 | 95.2 | 11.4 | 1,107 | 17 + 25 = 42 | 2026-09-05 |

Conditions:

- Mac Studio (Apple M4 Max, 128 GB), gpu, 2026-09-05: prewarm false, maxTokens 2048, default sampler (top-k 40, top-p 0.95, temperature 0.8), fresh load with a warm compile cache; prebuilt verifier on the same file: 141.2 decode / 472.2 prefill tok/s. Source: this recipe's Swift lifecycle test, run on 2026-09-05.
- Mac Studio (Apple M4 Max, 128 GB), cpu, 2026-09-05: same test as the GPU row with backend: .cpu(). Source: this recipe's Swift lifecycle test, run on 2026-09-05.
<!-- gen:recipe-measurements:hf-finetune-iphone:end -->

Stop and release, same machine: after `cancel()` the model was idle within 0.5 s on both backends; cancelling only the reading `Task` did not stop it (it decoded the full 2,017-token essay). After `chat = nil` the GPU process footprint went from 1,376 MB to 226 MB two seconds later, and a fresh load took 0.1 s. Full lines: [recipe section 7](https://github.com/john-rocky/swift-litert-lm/blob/main/docs/recipe-hf-finetune-to-iphone.md#7-verified--unverified).

## When to use, when not to use, alternatives

Use this route when the model is your own fine-tune of a family in the table above and the same bundle should run on iOS, macOS and Android from one runtime. The bundle carries the tokenizer and the chat template, so the app ships no tokenizer files.

Not the better choice when:

- **The converter refuses the model.** Mixture-of-experts, repository-local architectures, pre-quantized weights and gated repositories are refused at the entry gate. llama.cpp (GGUF) and MLX cover more architectures on Apple silicon; the choice between them is not measured here.
- **You already have GGUF or MLX weights.** There is no path from those formats to `.litertlm`; the model stays on llama.cpp or MLX.
- **The app needs many turns on a Qwen3-template model today.** The second turn on one `LiteRTChat` fails on the pinned runtime (#3443); the recipe's workaround is one `LiteRTChat` per turn with the history in the prompt. Fine-tunes of non-thinking bases (Qwen2.5, SmolLM2, OLMo-2) do not carry that template shape; not measured in Recipe 3.
- **You do not need custom weights.** On iOS 26 and later, Apple's Foundation Models framework runs the system model with nothing to convert or download; swift-litert-lm carries a Foundation Models-compatible adapter for the case where you do (not exercised by Recipe 3).
- **The model is 3B parameters or more.** The converter splits the embedding out to stay under the iOS mmap limit; that path is not exercised here, and no phone number exists for it.

Not verified here: any iPhone, the Simulator, and any runtime other than LiteRT-LM. This page quotes no speed for llama.cpp, MLX or Core ML.

## Limits

<!-- gen:recipe-limits:hf-finetune-iphone:start -->
Not verified as of 2026-09-05:

- any iPhone: the iPhone 17 Pro row is added when the device is available; the sample app must build first
- iOS Simulator: the runtime xcframework ships an ios-arm64-simulator slice and the README says the Simulator falls back to CPU; nothing was run there
- runtime binaries other than v0.15.0 in the Swift package; Xcode versions other than 26.1.1 and 27.0 beta 5
- multi-turn through the litert-lm CLI: two prompts on stdin were answered in one run and not in another; not established
- convert.py --int4, LoRA adapter repos (merge path), and every fine-tune other than this one
- first-generation cost on a fresh engine on an iPhone (Mac: 2.2 s GPU, 11.4 s CPU with prewarm false)
<!-- gen:recipe-limits:hf-finetune-iphone:end -->

## Implementation links

- Recipe 3: [docs/recipe-hf-finetune-to-iphone.md](https://github.com/john-rocky/swift-litert-lm/blob/main/docs/recipe-hf-finetune-to-iphone.md) in swift-litert-lm, machine-readable [recipe.json](https://github.com/john-rocky/swift-litert-lm/blob/main/docs/recipe.json).
- hf-to-litertlm: https://github.com/john-rocky/hf-to-litertlm (`scripts/convert.py`, `scripts/verify_quality.py`).
- swift-litert-lm: https://github.com/john-rocky/swift-litert-lm (`LiteRTChat`, the downloader, the Foundation Models adapter).
- LiteRT-LM: https://github.com/google-ai-edge/LiteRT-LM

## Model links

- [suayptalha/Qwen3-0.6B-Code-Expert](https://huggingface.co/suayptalha/Qwen3-0.6B-Code-Expert): the fine-tune converted in Recipe 3 (Apache-2.0 in the card metadata; the card's LICENSE link points at a file the repository does not contain).
- [mlboydaisuke/Qwen3-0.6B-Code-Expert-LiteRT](https://huggingface.co/mlboydaisuke/Qwen3-0.6B-Code-Expert-LiteRT): the converted bundle (613,406,208 bytes, int8 weights, 4096-token context).
- [Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B): the base.

## FAQ

**Can the bundle be tested without Xcode?** Yes: `pip install "litert-lm==0.17.0"` and `litert-lm run --from-huggingface-repo mlboydaisuke/Qwen3-0.6B-Code-Expert-LiteRT model.litertlm --prompt "What is 17 + 25? Answer briefly." --thinking false --temperature 0 --top-k 1` printed `17 + 25 = 42` in 1.1 s on the local file (Mac Studio, 2026-09-05).

**Why `--thinking false`?** With thinking on and greedy sampling the same prompt looped inside the thought channel for 128 s without answering; the Qwen3 card says not to use greedy decoding in thinking mode. With the CLI's default sampler and thinking on, it answered after one paragraph of thought.

**Does the Simulator work?** Not tried. The xcframework ships an `ios-arm64-simulator` slice and the package README says the Simulator falls back to the CPU; nothing was run there.

**Which Xcode?** 26.1.1 and 27.0 beta 5 both compile tag 0.2.0 for iOS; both fail on 0.1.1 and on `main` before 09f04f1.

**How big is the process?** 1,411 MB on the GPU and 1,107 MB on the CPU backend for this 613 MB bundle on the Mac; no iPhone figure exists yet.

## Related

- [Can LiteRT-LM run models other than Gemma?](litert-lm-models-other-than-gemma.md)
- [Can I run a PyTorch model on Android without going through ONNX?](pytorch-model-on-android-without-onnx.md)

## Provenance

<!-- gen:provenance:hf-finetune-iphone:start -->
- Converted and verified by: john-rocky
- Recipe: https://github.com/john-rocky/swift-litert-lm/blob/main/docs/recipe-hf-finetune-to-iphone.md
- Measurements: https://github.com/john-rocky/swift-litert-lm/blob/main/docs/recipe-hf-finetune-to-iphone.md#7-verified--unverified
- Commit: john-rocky/swift-litert-lm@09f04f1 (tag 0.2.0); john-rocky/hf-to-litertlm@5ffe9ee
- Maintained at: https://github.com/john-rocky/swift-litert-lm/issues
<!-- gen:provenance:hf-finetune-iphone:end -->

This page is the canonical text. Article copies (dev.to, Zenn, Medium) are snapshots that link back here and are not edited after publishing; corrections land here first.
