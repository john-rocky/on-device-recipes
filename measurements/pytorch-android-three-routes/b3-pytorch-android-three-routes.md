# One PyTorch model, three Android converters: litert-torch, ExecuTorch, ONNX Runtime (measured 2026-09-05)

Model: `tasks/assets/T06/model.py` `TinyHybridNet` — conv stem (3 conv + BatchNorm + GELU) → 784 tokens → one `nn.MultiheadAttention` encoder block → mean pool → linear head. Input `1×3×224×224`, 10 logits. Weights: `torch.manual_seed(0)` plus randomised BatchNorm statistics and positional embedding (the same recipe as the probe's T06 ExecuTorch run), saved once and loaded by every route.

Machine: Apple M4 Max, macOS 27.0 (26A5416b). Python 3.12.13 and 3.14.6 (Homebrew), fresh venvs at `/private/tmp/odp-b3/venv312` and `venv314`. torch 2.13.0 in both.

Parity protocol (same as the probe's T06 ExecuTorch run): golden input + 8 random inputs at scales 1.0 / 3.0 / 0.1, `atol 1e-4`, `rtol 1e-3`, argmax must match. Reference = eager PyTorch fp32 on the same weights.

Scripts: `b3_routes.py` (three routes), `b3_attn4d.py` (4-D attention rewrite for the GPU delegate). Structured copy of every number: `b3-pytorch-android-three-routes.json`.

## Conversion and parity on the Mac (identical results on Python 3.12 and 3.14)

| Route | Converter call | Artifact | Convert time (3.12 / 3.14) | Parity vs PyTorch (worst max abs / rel) |
|---|---|---:|---:|---|
| litert-torch 0.9.4 → ai-edge-litert 2.2.0 | `litert_torch.convert(model, (x,)).export("model.tflite")` | 1,073,260 B `.tflite` | 1.0–2.4 s / 2.2 s | 6.9e-7 / 7.5e-4, argmax 9/9 (Interpreter and `CompiledModel` CPU give the same numbers) |
| ExecuTorch 1.4.1 (XNNPACK partitioner) | `to_edge_transform_and_lower(torch.export.export(model,(x,)), partitioner=[XnnpackPartitioner()]).to_executorch()` | 1,073,320 B `.pte` | 2.5 s / 2.5 s | 6.9e-7 / 6.0e-4, argmax 9/9 |
| torch.onnx.export (opset 18, TorchScript tracer) → onnxruntime 1.29.0 | `torch.onnx.export(model,(x,),"model.onnx",opset_version=18,dynamo=False)` | 1,065,628 B `.onnx` | 0.1 s / 0.1 s | 7.5e-7 / 2.9e-4, argmax 9/9 |

Notes per route:

- litert-torch: `torch.export` → FX passes → `litert_converter.exported_programs_to_flatbuffer` (MLIR). No ONNX, no TensorFlow graph. The flatbuffer contains builtin ops only (`CONV_2D` ×3, `FULLY_CONNECTED` ×5, `BATCH_MATMUL` ×2, `SOFTMAX`, `GELU` ×4, `TRANSPOSE` ×9, `RESHAPE` ×21, LayerNorm as `MEAN`/`SQUARED_DIFFERENCE`/`RSQRT`/`MUL`/`SUB`/`ADD`, `PAD` ×3, `SLICE` ×3, `SUM`); no Flex, no custom ops. `pip install ai-edge-litert litert-torch` pulled torch 2.13.0, jax 0.11.1, transformers 5.16.1 and `litert-converter` 0.4.0 (native wheel, cp310–cp314); no TensorFlow. venv size 2.0 GB, 93 packages.
- ExecuTorch: 9 XNNPACK delegate calls. Not delegated in 1.4.1: `native_layer_norm` ×3 and the `nn.MultiheadAttention` mask glue (`eq`/`logical_not`/`any`/`where`, `select`/`expand`/`mul.Scalar`) — the same set the probe's T06 run reported for 1.4.0.
- ONNX: eval-mode `nn.MultiheadAttention` takes a fused fast path (`aten::_native_multi_head_attention`) that the TorchScript exporter does not support; `torch.backends.mha.set_fastpath_enabled(False)` before export avoids it (found by the probe's T06 Codex run).

## litert `.tflite` on the LiteRT `CompiledModel` GPU (macOS Metal backend, ai-edge-litert 2.2.0 Python API)

| Model graph | `CompiledModel` GPU result | Parity vs fp32 PyTorch | Median latency (Mac) |
|---|---|---|---:|
| unmodified (`nn.MultiheadAttention`) | refused: `RESHAPE: Tensor dimensions must be less than 5` ×2, `TRANSPOSE: Permutation for transpose is invalid`; "54 operations will run on the GPU, and the remaining 30 operations will run on the CPU" → `RuntimeError` (no CPU fallback under `CompiledModel`) | — | — |
| attention re-expressed in 4-D `(B, heads, N, head_dim)`, same weights (PyTorch max abs diff vs original 1.6e-7), max tensor rank 4 | compiles, `is_fully_accelerated() == True`, default precision (fp16) | 2.8e-3 max abs, argmax 9/9, fails the 1e-4 gate | 0.77 ms |
| same 4-D graph, `GpuOptions(enforce_f32=True)` | compiles, fully accelerated | 3.6e-7 / 1.1e-4, passes | 0.65 ms |
| same 4-D graph, `CompiledModel` CPU | — | 6.9e-7, passes | 2.29 ms |

The rank rule is the same one the LiteRT-Models conversion guide documents for the Android GPU delegate (4-D tensors only). The rewrite is `b3_attn4d.py`: split q/k/v with `reshape(B, N, heads, head_dim).transpose(1, 2)`, `matmul` → `softmax` → `matmul`, no 5-D tensor anywhere.

Mac latencies are each stack's Python runtime on the M4 Max with default threads; they are not Android numbers and are not compared across rows.

## Android side (from the probe's T06 runs, 2026-09-04)

Three independent implementations of the same task on the same emulator image (Pixel, API 36, arm64-v8a), by three different coding agents, no shared harness. Timings are what each run reported; they are not a controlled comparison.

| Route | Android dependency | Accelerator used | On-device parity | Latency reported | Notes |
|---|---|---|---|---:|---|
| ExecuTorch | `org.pytorch:executorch-android:1.4.0`, minSdk 28 | XNNPACK (`[XnnpackBackend]`, the only backend in the prebuilt AAR) | 4.5e-7 (instrumented test vs PyTorch golden) | 21.5 ms median / 8.2 ms min (10 random inputs); 166.4 ms with the undelegated `.pte` | `.pte` must be `noCompress`; Vulkan needs a source build |
| ONNX Runtime | `com.microsoft.onnxruntime:onnxruntime-android:1.24.3`, minSdk 27 | NNAPI EP (loaded on the emulator), XNNPACK / CPU fallback chain | 7.15e-7 (instrumented test) | ~23 ms | NNAPI is deprecated from Android 15; run also verified 7.3e-7 on the Mac CPU EP |
| ONNX Runtime | `com.microsoft.onnxruntime:onnxruntime-android:1.29.0`, minSdk 27 | NNAPI EP ("NNAPI execution provider enabled") | 5.4e-7 on the Mac CPU EP (no instrumented test) | not reported | — |
| litert-torch | `com.google.ai.edge.litert:litert:2.2.0`, minSdk 23 | `CompiledModel.Options(Accelerator.GPU)` / `.NPU` | not run on Android in this measurement | not measured | Mac Metal results above; the 4-D rule applies to the Android GPU delegate as well |

Registry versions on 2026-09-05: `executorch` 1.4.1 on PyPI, `executorch-android` 1.4.0 on Maven Central; `onnxruntime` / `onnxruntime-android` 1.29.0; `com.google.ai.edge.litert:litert` 2.2.0 on Google Maven.
