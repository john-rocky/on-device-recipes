# One PyTorch model through three Android converters (measured 2026-09-05)

Public copy of record for the Mac-side measurements quoted on
[Can I run a PyTorch model on Android without going through ONNX?](../../docs/pytorch-model-on-android-without-onnx.md):
conversion, parity against eager PyTorch, and the LiteRT `CompiledModel` GPU rank-4 / fp16 rule.

| file | what it is |
|---|---|
| `b3-pytorch-android-three-routes.md` | the measurement record, written as the runs finished |
| `b3-pytorch-android-three-routes.json` | every number in the record, structured |
| `b3_routes.py` | the three routes (litert-torch, ExecuTorch, torch.onnx.export) with the shared parity protocol |
| `b3_attn4d.py` | the 4-D attention rewrite and the `CompiledModel` GPU / CPU runs (Mac Metal backend) |

The scripts import `model.py` (`TinyHybridNet`) from the same directory. That file is the one published in
[apple-silicon-llm-bench/results/android/tinyhybridnet-three-runtimes/model.py](https://github.com/john-rocky/apple-silicon-llm-bench/blob/main/results/android/tinyhybridnet-three-runtimes/model.py)
(sha256 `6f71090bba653f4d0559c4d926487d9d42e77c2101bd703586ed6b6f58bc9d25`); copy it next to the scripts to rerun.
`tasks/assets/T06/model.py` in the record is its path in the private harness the runs came from.

The Android-side rows in the record are from that harness's earlier emulator runs. A controlled run of the same
model on a Galaxy S26 and the same emulator image, one process per device, is published separately:
[tinyhybridnet-three-runtimes.md](https://github.com/john-rocky/apple-silicon-llm-bench/blob/main/results/android/tinyhybridnet-three-runtimes.md).

Provenance: measured by john-rocky on an Apple M4 Max, macOS 27.0, 2026-09-05; litert-torch 0.9.4, ai-edge-litert 2.2.0,
ExecuTorch 1.4.1, ONNX Runtime 1.29.0, torch 2.13.0, Python 3.12.13 and 3.14.6. Issues: this repository.
