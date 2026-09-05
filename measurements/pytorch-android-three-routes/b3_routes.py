#!/usr/bin/env python
"""B3: TinyHybridNet (tasks/assets/T06/model.py) through three PyTorch -> Android converters,
each checked against eager PyTorch on the Mac with one shared weight file and one protocol.

Weights: seed 0 + randomised BatchNorm / pos (same recipe as the probe's T06 Fable run).
Parity protocol (same as that run): golden input + 8 random inputs at scales 1.0 / 3.0 / 0.1,
atol 1e-4, rtol 1e-3, argmax must match.

Usage: python b3_routes.py --route litert|executorch|onnx [--out results.json]
"""
import argparse, json, os, platform, statistics, sys, time
import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from model import TinyHybridNet  # noqa: E402

INPUT_SHAPE = (1, 3, 224, 224)
WEIGHTS = os.path.join(HERE, "tinyhybridnet_weights.pt")


def make_weights():
    torch.manual_seed(0)
    m = TinyHybridNet(num_classes=10)
    with torch.no_grad():
        m.pos.normal_(std=0.02)
        for bn in (m.stem.bn1, m.stem.bn2, m.stem.bn3):
            bn.weight.uniform_(0.5, 1.5)
            bn.bias.normal_(std=0.1)
            bn.running_mean.normal_(std=0.5)
            bn.running_var.uniform_(0.5, 2.0)
    torch.save(m.state_dict(), WEIGHTS)


def load_model():
    if not os.path.exists(WEIGHTS):
        make_weights()
    m = TinyHybridNet(num_classes=10)
    m.load_state_dict(torch.load(WEIGHTS, map_location="cpu"))
    return m.eval()


def sample_input():
    torch.manual_seed(1234)
    return torch.randn(*INPUT_SHAPE)


def parity(model, run_fn, n=8, atol=1e-4, rtol=1e-3, seed=42):
    torch.manual_seed(seed)
    cases = [("golden", sample_input())] + [
        (f"random[{i}]", torch.randn(*INPUT_SHAPE) * [1.0, 3.0, 0.1][i % 3]) for i in range(n)
    ]
    rows, ok, worst_abs, worst_rel = [], True, 0.0, 0.0
    for tag, x in cases:
        with torch.no_grad():
            ref = model(x)
        out = torch.from_numpy(np.asarray(run_fn(x.numpy().astype(np.float32))).reshape(ref.shape).copy())
        diff = (out - ref).abs()
        ma = diff.max().item()
        mr = (diff / ref.abs().clamp_min(1e-6)).max().item()
        close = torch.allclose(out, ref, atol=atol, rtol=rtol)
        same = out.argmax(1).item() == ref.argmax(1).item()
        ok &= bool(close and same)
        worst_abs, worst_rel = max(worst_abs, ma), max(worst_rel, mr)
        rows.append(dict(case=tag, max_abs=ma, max_rel=mr, argmax_ref=ref.argmax(1).item(),
                         argmax_out=out.argmax(1).item(), ok=bool(close and same)))
        print(f"{tag:>10}: max|diff|={ma:.3e} max rel={mr:.3e} argmax {ref.argmax(1).item()}/{out.argmax(1).item()} {'OK' if close and same else 'FAIL'}")
    return dict(ok=ok, worst_abs=worst_abs, worst_rel=worst_rel, atol=atol, rtol=rtol, cases=rows)


def latency(run_fn, iters=50, warmup=10):
    x = sample_input().numpy().astype(np.float32)
    for _ in range(warmup):
        run_fn(x)
    ts = []
    for _ in range(iters):
        t0 = time.perf_counter(); run_fn(x); ts.append((time.perf_counter() - t0) * 1e3)
    return dict(median_ms=statistics.median(ts), min_ms=min(ts), iters=iters, note="Mac CPU, Python runtime of the converter's own stack; not an Android number")


def route_litert(model):
    import litert_torch
    from ai_edge_litert.interpreter import Interpreter
    out_path = os.path.join(HERE, "tinyhybridnet.tflite")
    x = sample_input()
    t0 = time.perf_counter()
    edge = litert_torch.convert(model, (x,))
    edge.export(out_path)
    conv_s = time.perf_counter() - t0
    it = Interpreter(model_path=out_path)
    it.allocate_tensors()
    inp, outp = it.get_input_details()[0], it.get_output_details()[0]
    ops = {}
    for d in it._get_ops_details():
        ops[d["op_name"]] = ops.get(d["op_name"], 0) + 1

    def run(a):
        it.set_tensor(inp["index"], a); it.invoke(); return it.get_tensor(outp["index"])

    res = dict(route="litert-torch", converter=f"litert-torch {litert_torch.__version__}",
               converter_call="litert_torch.convert(model, (x,)).export('model.tflite')",
               runtime=f"ai-edge-litert {__import__('ai_edge_litert').__version__} Interpreter (CPU)",
               artifact=os.path.basename(out_path), artifact_bytes=os.path.getsize(out_path),
               convert_seconds=conv_s, input_shape=list(inp["shape"]), ops=ops,
               parity=parity(model, run), latency=latency(run))
    # Also run the CompiledModel API on the Mac, which is the API the Android side uses (CPU, then GPU/Metal if it loads).
    from ai_edge_litert.compiled_model import CompiledModel
    from ai_edge_litert.hardware_accelerator import HardwareAccelerator
    for accel in ("CPU", "GPU"):
        key = f"compiled_model_{accel.lower()}"
        try:
            cm = CompiledModel.from_file(out_path, getattr(HardwareAccelerator, accel))
            ins, outs = cm.create_input_buffers(0), cm.create_output_buffers(0)
            n_out = int(np.prod(outp["shape"]))
            def run_cm(a, ins=ins, outs=outs, cm=cm, n_out=n_out):
                ins[0].write(np.ascontiguousarray(a, dtype=np.float32)); cm.run_by_index(0, ins, outs)
                return outs[0].read(n_out, np.float32)
            print(f"--- CompiledModel {accel} (fully accelerated: {cm.is_fully_accelerated()}) ---")
            res[key] = dict(fully_accelerated=bool(cm.is_fully_accelerated()), parity=parity(model, run_cm), latency=latency(run_cm))
        except Exception as e:
            res[key] = f"not run: {type(e).__name__}: {e}"
            print(f"--- CompiledModel {accel}: {res[key]}")
    return res


def route_executorch(model):
    import executorch, importlib.metadata as _md; ET_VERSION = _md.version("executorch")
    from executorch.backends.xnnpack.partition.xnnpack_partitioner import XnnpackPartitioner
    from executorch.exir import EdgeCompileConfig, to_edge_transform_and_lower
    from executorch.runtime import Runtime
    out_path = os.path.join(HERE, "tinyhybridnet_xnnpack.pte")
    x = sample_input()
    t0 = time.perf_counter()
    ep = torch.export.export(model, (x,), strict=True)
    et = to_edge_transform_and_lower(ep, partitioner=[XnnpackPartitioner()],
                                     compile_config=EdgeCompileConfig(_check_ir_validity=False)).to_executorch()
    with open(out_path, "wb") as f:
        f.write(et.buffer)
    conv_s = time.perf_counter() - t0
    gm = et.exported_program().graph_module
    ops, delegates = {}, 0
    for node in gm.graph.nodes:
        if node.op == "call_function":
            name = getattr(node.target, "__name__", str(node.target))
            if name.startswith("executorch_call_delegate"):
                delegates += 1
            else:
                ops[name] = ops.get(name, 0) + 1
    method = Runtime.get().load_program(out_path).load_method("forward")

    def run(a):
        return method.execute([torch.from_numpy(a)])[0].numpy()

    return dict(route="executorch", converter=f"executorch {ET_VERSION} (torch.export -> to_edge_transform_and_lower, XnnpackPartitioner)",
                converter_call="to_edge_transform_and_lower(torch.export.export(model,(x,)), partitioner=[XnnpackPartitioner()]).to_executorch()",
                runtime=f"executorch {ET_VERSION} Python runtime (XNNPACK delegate, CPU)",
                artifact=os.path.basename(out_path), artifact_bytes=os.path.getsize(out_path),
                convert_seconds=conv_s, delegate_calls=delegates, non_delegated_ops=ops,
                parity=parity(model, run), latency=latency(run))


def route_onnx(model):
    import onnx, onnxruntime as ort
    out_path = os.path.join(HERE, "tinyhybridnet.onnx")
    x = sample_input()
    torch.backends.mha.set_fastpath_enabled(False)  # eval-mode MHA fast path is not exportable (probe T06 Codex finding)
    t0 = time.perf_counter()
    torch.onnx.export(model, (x,), out_path, input_names=["input"], output_names=["logits"],
                      opset_version=18, do_constant_folding=True, dynamo=False)
    conv_s = time.perf_counter() - t0
    m = onnx.load(out_path); onnx.checker.check_model(m)
    ops = {}
    for n in m.graph.node:
        ops[n.op_type] = ops.get(n.op_type, 0) + 1
    sess = ort.InferenceSession(out_path, providers=["CPUExecutionProvider"])
    name = sess.get_inputs()[0].name

    def run(a):
        return sess.run(None, {name: a})[0]

    return dict(route="onnx-runtime", converter=f"torch.onnx.export (torch {torch.__version__}, opset 18, TorchScript tracer, MHA fastpath disabled)",
                converter_call="torch.onnx.export(model, (x,), 'model.onnx', opset_version=18, dynamo=False)",
                runtime=f"onnxruntime {ort.__version__} CPUExecutionProvider",
                artifact=os.path.basename(out_path), artifact_bytes=os.path.getsize(out_path),
                convert_seconds=conv_s, ops=ops, parity=parity(model, run), latency=latency(run))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--route", required=True, choices=["litert", "executorch", "onnx"])
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    model = load_model()
    env = dict(python=platform.python_version(), torch=torch.__version__, machine=platform.machine(),
               macos=platform.mac_ver()[0], date=time.strftime("%Y-%m-%d"))
    res = {"litert": route_litert, "executorch": route_executorch, "onnx": route_onnx}[args.route](model)
    res["env"] = env
    print(json.dumps({k: v for k, v in res.items() if k not in ("parity", "compiled_model_cpu_parity")}, indent=1, default=str))
    p = res["parity"]
    print(f"\nPARITY {'OK' if p['ok'] else 'FAILED'}: worst max|diff| {p['worst_abs']:.3e}, worst rel {p['worst_rel']:.3e}")
    if args.out:
        with open(args.out, "w") as f:
            json.dump(res, f, indent=1, default=str)


if __name__ == "__main__":
    main()
