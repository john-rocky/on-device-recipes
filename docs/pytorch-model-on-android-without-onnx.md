# Can I run a PyTorch model on Android without going through ONNX?

**Last verified: 2026-09-05** — litert-torch 0.9.4, ai-edge-litert 2.2.0, LiteRT Android 2.2.0; ExecuTorch 1.4.1 (Android AAR 1.4.0); ONNX Runtime 1.29.0; torch 2.13.0; Python 3.12.13 and 3.14.6 on an M4 Max, macOS 27.

## Direct answer

Yes. **litert-torch** (the converter formerly named ai-edge-torch) takes a PyTorch `nn.Module` through `torch.export` and writes a `.tflite` flatbuffer directly; no ONNX file and no TensorFlow graph are involved. The `.tflite` runs in an Android app through LiteRT's `CompiledModel` API on the CPU, the GPU or an NPU. Two conditions decide whether the GPU path works: every op must have a GPU kernel (there is no per-op CPU fallback under `CompiledModel`), and every tensor must have rank 4 or less. Standard CNNs pass as-is; `nn.MultiheadAttention` needs its 5-D head split rewritten in 4-D. **ExecuTorch** is the other ONNX-free route. **ONNX Runtime** is the right choice when one artifact must also run on iOS, Windows or the browser, or when you already ship ORT.

There are three maintained routes from a PyTorch model to an Android app. None of them passes through ONNX unless you pick ONNX Runtime itself, and none of them builds a TensorFlow graph.

1. **litert-torch** (formerly ai-edge-torch) → `.tflite` → LiteRT `CompiledModel` (`com.google.ai.edge.litert:litert:2.2.0`). `torch.export` → MLIR → flatbuffer. GPU or NPU is an option on `CompiledModel`.
2. **ExecuTorch** → `.pte` → `org.pytorch:executorch-android:1.4.0`. `torch.export` → `to_edge_transform_and_lower` with the XNNPACK partitioner.
3. **torch.onnx.export** → `.onnx` → `com.microsoft.onnxruntime:onnxruntime-android:1.29.0` with the NNAPI, XNNPACK or QNN execution provider.

On 2026-09-05 all three converted the unmodified model below (a conv stem plus an `nn.MultiheadAttention` encoder block) and matched PyTorch within 7.5e-7, on Python 3.12 and on Python 3.14. What differs is the accelerator story on the phone, and one rule about tensor rank on the LiteRT GPU.

The "PyTorch → ONNX → TensorFlow → TFLite" chain in older tutorials is not how litert-torch works. Its old name, `ai-edge-torch`, still shows up in search results; the package is a deprecation stub that points to `litert-torch`.

If the model is a vision CNN and the goal is an existing Android app on the GPU, [Recipe 1](#implementation-links) (background removal with ormbg) is the worked example of the litert-torch route: dependency line, one Kotlin file, model file with sha256, verify command, verified devices.

## The model

`TinyHybridNet`: three `Conv2d` + `BatchNorm2d` + `GELU` layers (stride 2 each) → 784 tokens of width 96 → one transformer block (`LayerNorm`, `nn.MultiheadAttention` with 4 heads, `LayerNorm`, MLP) → mean pool → `Linear` head. Input `1×3×224×224`, output 10 logits, random weights saved once and shared by every route. Source: [model.py](https://github.com/john-rocky/apple-silicon-llm-bench/blob/main/results/android/tinyhybridnet-three-runtimes/model.py).

Parity protocol: one fixed input plus 8 random inputs at three scales (1.0, 3.0, 0.1), `atol 1e-4`, `rtol 1e-3`, argmax must agree. Reference is eager PyTorch fp32.

## Which route? (by use case)

| Situation | Route | Basis |
|---|---|---|
| GPU on Android with one dependency; model is a CNN or a standard ViT (tensors of rank ≤ 4) | litert-torch → `CompiledModel(Accelerator.GPU)` | Fully accelerated once attention is expressed in 4-D. fp16 by default (2.8e-3 vs fp32); `enforce_f32` restores 3.6e-7 (Metal measurement below). |
| NPU (Qualcomm, MediaTek, Google Tensor, Samsung, Intel) | litert-torch → `Accelerator.NPU`; or ExecuTorch QNN / MediaTek backends; or the ONNX Runtime QNN provider | Documented paths; not measured here. |
| Stay in the PyTorch toolchain; CPU is enough | ExecuTorch + XNNPACK | 21.5 ms median on an API 36 arm64 emulator; `LayerNorm` and the attention-mask glue run on portable kernels in 1.4. |
| One artifact for Android, iOS, Windows and the browser | ONNX Runtime | NNAPI provider loaded on the emulator (~23 ms); NNAPI is deprecated from Android 15, XNNPACK and QNN providers remain. |
| Dynamic control flow in `forward` | ONNX (TorchScript tracer) or ExecuTorch with `torch.cond` | litert-torch lists dynamic control flow under "avoid". |

## Quick start, all three

Convert (Python, any of 3.10–3.14):

```python
import torch
x = torch.randn(1, 3, 224, 224)
model = model.eval()

# 1. litert-torch → model.tflite
import litert_torch
litert_torch.convert(model, (x,)).export("model.tflite")

# 2. ExecuTorch → model.pte (XNNPACK)
from executorch.backends.xnnpack.partition.xnnpack_partitioner import XnnpackPartitioner
from executorch.exir import to_edge_transform_and_lower
ep = torch.export.export(model, (x,))
pte = to_edge_transform_and_lower(ep, partitioner=[XnnpackPartitioner()]).to_executorch()
open("model.pte", "wb").write(pte.buffer)

# 3. ONNX → model.onnx
torch.backends.mha.set_fastpath_enabled(False)   # eval-mode MHA fast path is not exportable
torch.onnx.export(model, (x,), "model.onnx", input_names=["input"], output_names=["logits"],
                  opset_version=18, dynamo=False)
```

Android dependencies (`build.gradle.kts`):

```kotlin
implementation("com.google.ai.edge.litert:litert:2.2.0")            // Google Maven; minSdk 23
implementation("org.pytorch:executorch-android:1.4.0")              // Maven Central; minSdk 28
implementation("com.microsoft.onnxruntime:onnxruntime-android:1.29.0") // Maven Central; minSdk 27
// keep model assets uncompressed: android { androidResources { noCompress += listOf("tflite", "pte", "onnx") } }
```

Load and run (Kotlin):

```kotlin
// LiteRT CompiledModel (GPU; NPU with GPU fallback = Options(Accelerator.NPU, Accelerator.GPU))
val lm = CompiledModel.create(context.assets, "model.tflite", CompiledModel.Options(Accelerator.GPU), null)
val li = lm.createInputBuffers(); val lo = lm.createOutputBuffers()
li[0].writeFloat(input); lm.run(li, lo); val logits1 = lo[0].readFloat()

// ExecuTorch (copy the asset to filesDir first; the runtime wants a file path)
val module = Module.load(pteFile.path, Module.LOAD_MODE_MMAP, numThreads)
val out = module.forward(EValue.from(Tensor.fromBlob(input, longArrayOf(1, 3, 224, 224))))
val logits2 = out[0].toTensor().dataAsFloatArray

// ONNX Runtime (NNAPI provider; drop addNnapi() for CPU, or use addXnnpack(emptyMap()))
val env = OrtEnvironment.getEnvironment()
val session = env.createSession(modelBytes, OrtSession.SessionOptions().apply { addNnapi() })
OnnxTensor.createTensor(env, FloatBuffer.wrap(input), longArrayOf(1, 3, 224, 224)).use { t ->
    session.run(mapOf("input" to t)).use { r -> val logits3 = (r[0].value as Array<FloatArray>)[0] }
}
```

## Measured on the Mac: convert, then compare with PyTorch

Same results on Python 3.12.13 and 3.14.6.

| Route | Converter call | Artifact | Convert time | Worst max abs / rel diff vs PyTorch |
|---|---|---:|---:|---|
| litert-torch 0.9.4 → ai-edge-litert 2.2.0 | `litert_torch.convert(model, (x,)).export("model.tflite")` | 1,073,260 B | 1.0–2.4 s | 6.9e-7 / 7.5e-4, argmax 9/9 (Interpreter and `CompiledModel` CPU identical) |
| ExecuTorch 1.4.1, XNNPACK partitioner | `to_edge_transform_and_lower(torch.export.export(model, (x,)), partitioner=[XnnpackPartitioner()]).to_executorch()` | 1,073,320 B | 2.5 s | 6.9e-7 / 6.0e-4, argmax 9/9 |
| torch.onnx.export (opset 18) → onnxruntime 1.29.0 | `torch.onnx.export(model, (x,), "model.onnx", opset_version=18, dynamo=False)` | 1,065,628 B | 0.1 s | 7.5e-7 / 2.9e-4, argmax 9/9 |

What each converter did with the attention block:

- litert-torch emitted builtin ops only: `CONV_2D` ×3, `FULLY_CONNECTED` ×5, `BATCH_MATMUL` ×2, `SOFTMAX`, `GELU` ×4, `TRANSPOSE` ×9, `RESHAPE` ×21, LayerNorm as `MEAN` / `SQUARED_DIFFERENCE` / `RSQRT` / `MUL` / `SUB` / `ADD`. No Flex ops, no custom ops.
- ExecuTorch produced 9 XNNPACK delegate calls. Left on portable kernels in 1.4.1: `native_layer_norm` ×3 and the mask glue that `nn.MultiheadAttention` traces to (`eq`, `logical_not`, `any`, `where`, `select`, `expand`, `mul.Scalar`).
- torch.onnx.export needs `torch.backends.mha.set_fastpath_enabled(False)` first. In eval mode `nn.MultiheadAttention` takes a fused fast path (`aten::_native_multi_head_attention`) that the TorchScript exporter rejects.

`pip install ai-edge-litert litert-torch` pulled torch 2.13.0, jax 0.11.1, transformers 5.16.1 and the native `litert-converter` 0.4.0 (wheels cp310–cp314). 2.0 GB, 93 packages, no TensorFlow. `pip install executorch onnx onnxruntime` also installed and ran on 3.14.

## The LiteRT GPU rule: rank 4, and fp16 by default

`CompiledModel` with `Accelerator.GPU` compiles the whole graph for the GPU or fails; there is no per-op CPU fallback. The unmodified model failed on the macOS Metal backend of the same runtime:

```
RESHAPE: Tensor dimensions must be less than 5   (MultiheadAttention, twice)
TRANSPOSE: Permutation for transpose is invalid.
54 operations will run on the GPU, and the remaining 30 operations will run on the CPU.
```

`nn.MultiheadAttention` reshapes to a 5-D tensor when it splits heads. Re-expressing the same weights as explicit 4-D attention (`reshape(B, N, heads, head_dim).transpose(1, 2)`, `matmul`, `softmax`, `matmul`) keeps every tensor at rank 4 and is numerically the same model in PyTorch (max diff 1.6e-7). Results on the Metal GPU, same protocol:

| Graph | `CompiledModel` GPU | vs fp32 PyTorch | Median latency (Mac) |
|---|---|---|---:|
| unmodified `nn.MultiheadAttention` | refused (above) | — | — |
| 4-D attention, default precision (fp16) | compiles, fully accelerated | 2.8e-3, argmax 9/9, fails the 1e-4 gate | 0.77 ms |
| 4-D attention, `GpuOptions(enforce_f32=True)` | compiles, fully accelerated | 3.6e-7 / 1.1e-4, passes | 0.65 ms |
| 4-D attention, CPU | — | 6.9e-7, passes | 2.29 ms |

The rank rule is the same one the Android GPU delegate enforces, so the rewrite is what you would do before shipping the LiteRT route. The Mac latencies are for this comparison only; they are not Android numbers.

## Measured on Android (emulator, from three independent implementations)

These rows come from three separate implementations of the same task on the same emulator image (Pixel, API 36, arm64-v8a), written by three different coding agents in a separate experiment. They share the emulator but not a harness, so the timings are what each run reported, not a controlled comparison.

| Route | Android dependency | Accelerator | On-device parity vs PyTorch | Latency reported | Notes |
|---|---|---|---|---:|---|
| ExecuTorch | `org.pytorch:executorch-android:1.4.0`, minSdk 28 | XNNPACK (`[XnnpackBackend]` is the only backend in the prebuilt AAR) | 4.5e-7 (instrumented test) | 21.5 ms median, 8.2 ms min over 10 inputs; 166.4 ms with the undelegated `.pte` | `.pte` assets must be `noCompress`; Vulkan needs a source build |
| ONNX Runtime | `com.microsoft.onnxruntime:onnxruntime-android:1.24.3`, minSdk 27 | NNAPI provider loaded; XNNPACK → CPU fallback chain | 7.15e-7 (instrumented test) | ~23 ms | NNAPI deprecated from Android 15 |
| ONNX Runtime | `com.microsoft.onnxruntime:onnxruntime-android:1.29.0`, minSdk 27 | NNAPI provider enabled | 5.4e-7 on the Mac CPU provider | not reported | — |
| litert-torch | `com.google.ai.edge.litert:litert:2.2.0`, minSdk 23 | `Accelerator.GPU` / `NPU` | not run on Android for this article | not measured | Mac Metal results above; the rank-4 rule applies on Android too |

A controlled run of the same model, one instrumented-test process per device with 5 warm-up and 30 timed runs, on a Galaxy S26 (Snapdragon SM8850, Android 16) and the same API 36 emulator image, measured 2026-09-05, is published in [tinyhybridnet-three-runtimes.md](https://github.com/john-rocky/apple-silicon-llm-bench/blob/main/results/android/tinyhybridnet-three-runtimes.md). It adds the LiteRT CPU rows (XNNPACK; on the S26, 8.77 ms median with default threads and 5.42 ms with 4 threads) and reproduces the GPU refusal of the unmodified attention block on a real phone: `CompiledModel.create` fails with "Failed to compile model" on the S26, with the same "Tensor dimensions must be less than 5" in logcat as on the Mac. Its emulator numbers are host-CPU numbers and are not compared with the phone column.

## When to use which, and when not

Use litert-torch when the GPU or NPU matters and the graph fits the rank-4 rule; the payoff is a single dependency and a fully accelerated graph. Do not use it for a graph with 5-D tensors you cannot rewrite, or if you need per-op CPU fallback inside the same session.

Use ExecuTorch when you want to stay inside PyTorch's toolchain and CPU XNNPACK is enough. Do not expect GPU from the prebuilt AAR; Vulkan and vendor NPU backends need a source build and the matching device.

Use ONNX Runtime when the same file must run on several platforms or you already ship ORT elsewhere. Do not rely on NNAPI going forward; plan on XNNPACK or a vendor provider.

## Alternatives

TensorFlow Lite's own converter (`tf.lite.TFLiteConverter`) still exists for TensorFlow and Keras models. onnx2tf converts ONNX to `.tflite` for CNNs but transposes NCHW to NHWC on the way, which breaks attention layers. PyTorch Mobile (`.ptl`) is deprecated in favour of ExecuTorch. MediaPipe Tasks wraps LiteRT with pre- and post-processing for its own model families.

## Things the docs do not tell you

- `ai-edge-torch` on PyPI is a stub: "This package is now deprecated. The project has been officially renamed to litert-torch". Searches still return the old name.
- The `executorch-android` 1.4.0 AAR registers only `XnnpackBackend` (checked with `ExecuTorchRuntime.getRegisteredBackends()` on device).
- `nn.MultiheadAttention` needs the fast path disabled before `torch.onnx.export`, and lowers to a 5-D reshape that the LiteRT GPU rejects. Explicit 4-D attention fixes both.
- The LiteRT GPU computes in fp16 unless you set `enforce_f32`; on this model that is the difference between 2.8e-3 and 3.6e-7.
- Assets that are compressed by AAPT fail to mmap; add `noCompress` for `tflite`, `pte`, `onnx`.
- `pip install ai-edge-litert litert-torch` is 2 GB of dependencies. Python 3.14 works; the native `litert-converter` wheel exists for cp314.

## Implementation links

- **Recipe 1: add background removal (ormbg, an ISNet CNN) to an existing Android app, on the GPU.** [ormbg/INTEGRATION.md](https://github.com/john-rocky/LiteRT-Models/blob/main/ormbg/INTEGRATION.md) in LiteRT-Models: the dependency line, one Kotlin file to copy, the model file with its sha256, the verify command with its expected output, and the devices it was verified on. Conversion script: [ormbg/scripts/build_ormbg.py](https://github.com/john-rocky/LiteRT-Models/blob/main/ormbg/scripts/build_ormbg.py) (litert-torch, one `align_corners` patch, 246/246 ops on the GPU). Machine-readable entry: `ormbg-android-gpu` in [recipes.json](https://github.com/john-rocky/on-device-recipes/blob/main/recipes.json).
- The GPU op rules and the attention rewrites, with one section per model that needed one: [LITERT_CONVERSION_GUIDE.md](https://github.com/john-rocky/LiteRT-Models/blob/main/docs/LITERT_CONVERSION_GUIDE.md) (sections "GPU-Incompatible Ops" and "4D Tensor Limit").
- `litert_gpu_toolkit`: `convert_for_gpu(model, dummy_input, output_path)` with the patch catalog: [litert_gpu_toolkit/](https://github.com/john-rocky/LiteRT-Models/tree/main/litert_gpu_toolkit).
- The Android instrumented test that runs all three runtimes on one model (Kotlin, Gradle): [tinyhybridnet-three-runtimes/android](https://github.com/john-rocky/apple-silicon-llm-bench/tree/main/results/android/tinyhybridnet-three-runtimes/android).
- The scripts and JSON behind the Mac numbers on this page: [measurements/pytorch-android-three-routes/](https://github.com/john-rocky/on-device-recipes/tree/main/measurements/pytorch-android-three-routes).

## Model links

- `TinyHybridNet`, the model measured here: [model.py](https://github.com/john-rocky/apple-silicon-llm-bench/blob/main/results/android/tinyhybridnet-three-runtimes/model.py).
- `ormbg.tflite` for Recipe 1: [litert-community/ormbg-LiteRT](https://huggingface.co/litert-community/ormbg-LiteRT) (176,240,148 bytes, Apache-2.0, input `[1, 3, 1024, 1024]` NCHW, output `[1, 1, 1024, 1024]` alpha), converted from [schirrmacher/ormbg](https://huggingface.co/schirrmacher/ormbg).

## FAQ

**Does PyTorch → TFLite still go through ONNX?** No. litert-torch calls `torch.export` and writes the flatbuffer through MLIR. ONNX only appears if you choose ONNX Runtime.

**Which one is fastest on the phone?** Not answered here. The emulator rows come from separate implementations, and the litert route was not run on Android for this article.

**Do all three support `nn.MultiheadAttention`?** Yes, as-is for CPU parity. For the LiteRT GPU, rewrite it in 4-D.

**Which Python version?** 3.12 and 3.14 both worked for all three routes on 2026-09-05.

**Which Maven artifacts, and what is the latest version of each?** On 2026-09-05: `com.google.ai.edge.litert:litert:2.2.0` on Google Maven; `org.pytorch:executorch-android:1.4.0` and `com.microsoft.onnxruntime:onnxruntime-android:1.29.0` on Maven Central. The registries are the source; the "Last verified" line above says when this page last checked them.

## Related

- litert-torch: https://github.com/google-ai-edge/litert-torch
- ExecuTorch Android: https://docs.pytorch.org/executorch/stable/using-executorch-android.html
- ONNX Runtime Android: https://onnxruntime.ai/docs/get-started/with-java.html
- Vision models converted with litert-torch for `CompiledModel` GPU, with a conversion guide that lists the GPU op rules and the attention rewrites: https://github.com/john-rocky/LiteRT-Models
<!-- TODO(lane B): add the LiteRT vs TensorFlow Lite article (B1) here once it is published. -->

## Provenance

- Converted and verified by: john-rocky
- Recipe: this page covers the route; the worked recipe is [ormbg/INTEGRATION.md](https://github.com/john-rocky/LiteRT-Models/blob/main/ormbg/INTEGRATION.md) in LiteRT-Models
- Measurements: [measurements/pytorch-android-three-routes/](https://github.com/john-rocky/on-device-recipes/tree/main/measurements/pytorch-android-three-routes) (Mac, 2026-09-05) and [tinyhybridnet-three-runtimes.md](https://github.com/john-rocky/apple-silicon-llm-bench/blob/main/results/android/tinyhybridnet-three-runtimes.md) (Galaxy S26 and API 36 emulator, 2026-09-05)
- Commit: john-rocky/apple-silicon-llm-bench@b7b7cfd94c856f4a65c1e5160d1cbad312455815 (model.py and the Android harness)
- Maintained at: https://github.com/john-rocky/on-device-recipes/issues

This page is the canonical text. Article copies (dev.to, Zenn, Medium) are snapshots that link back here and are not edited after publishing; corrections land here first.
