#!/usr/bin/env python
"""Same TinyHybridNet weights, nn.MultiheadAttention re-expressed as explicit 4-D attention
(B, heads, N, head_dim) so no tensor exceeds rank 4. Checks equality with the original in
PyTorch, converts with litert-torch, then tries CompiledModel CPU and GPU (Mac Metal)."""
import json, os, sys, time
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from model import TinyHybridNet
from b3_routes import load_model, parity, latency, sample_input

class Attn4D(nn.Module):
    """Drop-in for nn.MultiheadAttention(batch_first=True) using its own in_proj/out_proj weights."""
    def __init__(self, mha: nn.MultiheadAttention):
        super().__init__()
        self.h, self.d = mha.num_heads, mha.embed_dim // mha.num_heads
        self.in_w, self.in_b = mha.in_proj_weight, mha.in_proj_bias
        self.out = mha.out_proj
    def forward(self, x):
        B, N, C = x.shape
        qkv = F.linear(x, self.in_w, self.in_b)                       # (B, N, 3C)
        q, k, v = qkv.split(C, dim=-1)
        q = q.reshape(B, N, self.h, self.d).transpose(1, 2)           # (B, h, N, d)
        k = k.reshape(B, N, self.h, self.d).transpose(1, 2)
        v = v.reshape(B, N, self.h, self.d).transpose(1, 2)
        a = torch.matmul(q * (self.d ** -0.5), k.transpose(-1, -2)).softmax(-1)   # (B, h, N, N)
        y = torch.matmul(a, v).transpose(1, 2).reshape(B, N, C)       # (B, N, C)
        return self.out(y)

class Block4D(nn.Module):
    def __init__(self, blk):
        super().__init__(); self.norm1, self.norm2, self.mlp = blk.norm1, blk.norm2, blk.mlp; self.attn = Attn4D(blk.attn)
    def forward(self, x):
        x = x + self.attn(self.norm1(x)); return x + self.mlp(self.norm2(x))

class TinyHybridNet4D(nn.Module):
    def __init__(self, m: TinyHybridNet):
        super().__init__(); self.stem, self.pos, self.block, self.norm, self.head = m.stem, m.pos, Block4D(m.block), m.norm, m.head
    def forward(self, x):
        x = self.stem(x).flatten(2).transpose(1, 2) + self.pos
        x = self.block(x); return self.head(self.norm(x).mean(dim=1))

def main():
    import litert_torch
    from ai_edge_litert.interpreter import Interpreter
    from ai_edge_litert.compiled_model import CompiledModel
    from ai_edge_litert.hardware_accelerator import HardwareAccelerator
    orig = load_model(); m4 = TinyHybridNet4D(orig).eval()
    torch.manual_seed(7); xs = [torch.randn(1, 3, 224, 224) * s for s in (1.0, 3.0, 0.1)]
    with torch.no_grad():
        eq = max((orig(x) - m4(x)).abs().max().item() for x in xs)
    print(f"PyTorch: original vs 4-D rewrite max|diff| = {eq:.3e}")
    out_path = os.path.join(HERE, "tinyhybridnet_attn4d.tflite")
    t0 = time.perf_counter(); litert_torch.convert(m4, (sample_input(),)).export(out_path); conv_s = time.perf_counter() - t0
    it = Interpreter(model_path=out_path); it.allocate_tensors()
    ops = {}
    for d in it._get_ops_details(): ops[d["op_name"]] = ops.get(d["op_name"], 0) + 1
    max_rank = max(len(it.get_tensor_details()[i]["shape"]) for i in range(len(it.get_tensor_details())))
    res = dict(route="litert-torch (attention re-expressed in 4-D)", torch_equivalence_max_abs=eq, artifact=os.path.basename(out_path),
               artifact_bytes=os.path.getsize(out_path), convert_seconds=conv_s, ops=ops, max_tensor_rank=max_rank)
    for accel in ("CPU", "GPU"):
        key = f"compiled_model_{accel.lower()}"
        try:
            cm = CompiledModel.from_file(out_path, getattr(HardwareAccelerator, accel))
            ins, outs = cm.create_input_buffers(0), cm.create_output_buffers(0)
            def run_cm(a, ins=ins, outs=outs, cm=cm):
                ins[0].write(np.ascontiguousarray(a, dtype=np.float32)); cm.run_by_index(0, ins, outs); return outs[0].read(10, np.float32)
            print(f"--- CompiledModel {accel} (fully accelerated: {cm.is_fully_accelerated()}) ---")
            res[key] = dict(fully_accelerated=bool(cm.is_fully_accelerated()), parity=parity(orig, run_cm), latency=latency(run_cm))
        except Exception as e:
            res[key] = f"not run: {type(e).__name__}: {e}"; print(f"--- CompiledModel {accel}: {res[key]}")
    print(json.dumps({k: v for k, v in res.items() if not k.startswith("compiled_model")}, indent=1))
    for k in ("compiled_model_cpu", "compiled_model_gpu"):
        v = res[k]; print(k, "->", (v["fully_accelerated"], v["parity"]["ok"], f"{v['parity']['worst_abs']:.3e}", f"{v['latency']['median_ms']:.2f} ms") if isinstance(v, dict) else v)
    json.dump(res, open(os.path.join(HERE, "..", "res-312-litert-attn4d.json"), "w"), indent=1, default=str)

if __name__ == "__main__":
    main()
