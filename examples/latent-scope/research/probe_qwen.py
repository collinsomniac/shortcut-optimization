"""Offline Qwen3 Base probe: one named residual hook, optional matching SAE.

Requires an exact model revision and locally acquired SAE checkpoint. Never uploads prompts.
Captured state is the last *input* position used to predict the next token.
"""
import argparse
import json
import time
from pathlib import Path


def summarize_sae(hidden, sae, torch, topk=50):
    """Project one residual vector and return a small sparse feature record."""
    w_enc, b_enc = sae["W_enc"], sae["b_enc"]
    if w_enc.ndim != 2 or w_enc.shape[1] != hidden.numel() or b_enc.shape != w_enc.shape[:1]:
        raise ValueError("SAE encoder dimensions do not match the hooked residual")
    activations = hidden.to(dtype=w_enc.dtype) @ w_enc.T + b_enc
    values, indices = activations.topk(min(topk, activations.numel()))
    result = [{"id": int(i), "value": float(v)} for i, v in zip(indices.tolist(), values.tolist())]
    # Reconstruct with precisely the selected features, if the decoder is present.
    error = None
    if "W_dec" in sae and "b_dec" in sae:
        reconstruction = values @ sae["W_dec"][:, indices].T + sae["b_dec"]
        denominator = hidden.norm().clamp_min(1e-8)
        error = float(((hidden - reconstruction.to(hidden.dtype)).norm() / denominator).item())
    return result, error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", default="Qwen/Qwen3-1.7B-Base")
    parser.add_argument("--revision", required=True, help="Pinned Hugging Face commit hash")
    parser.add_argument("--layer", type=int, required=True, help="0-indexed transformer block")
    parser.add_argument("--sae", type=Path, help="Local matching layerN.sae.pt from Qwen-Scope")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--tokens", type=int, default=16)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if args.tokens < 1 or args.tokens > 256:
        parser.error("--tokens must be between 1 and 256")
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    tokenizer = AutoTokenizer.from_pretrained(args.model_id, revision=args.revision)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, revision=args.revision, torch_dtype=dtype,
        trust_remote_code=False, low_cpu_mem_usage=True
    ).to(device).eval()
    layers = model.model.layers
    if not 0 <= args.layer < len(layers):
        parser.error(f"layer must be between 0 and {len(layers)-1}")
    sae = None
    if args.sae:
        raw = torch.load(args.sae, map_location="cpu", weights_only=True)
        names = ("W_enc", "b_enc", "W_dec", "b_dec")
        if not all(name in raw for name in names):
            raise ValueError("SAE checkpoint is missing one of W_enc, b_enc, W_dec, b_dec")
        sae = {name: raw[name].to(device=device, dtype=dtype) for name in names}
    captured = []

    def hook(module, inputs, output):
        state = output[0] if isinstance(output, tuple) else output
        captured.append(state[0, -1].detach())

    handle = layers[args.layer].register_forward_hook(hook)
    ids = tokenizer(args.prompt, return_tensors="pt")["input_ids"].to(device)
    records = []
    cache = None
    first = ids
    started = time.perf_counter()
    try:
        with torch.inference_mode():
            for step in range(args.tokens):
                # Prefill on step 0; thereafter send only the previously chosen token.
                result = model(input_ids=first, past_key_values=cache, use_cache=True)
                cache = result.past_key_values
                if len(captured) != step + 1:
                    raise RuntimeError("hook was not invoked exactly once for this decoding step")
                state = captured.pop()
                logits = result.logits[0, -1].float()
                logprobs = logits.log_softmax(-1)
                token_id = int(logprobs.argmax().item())
                values, indices = logprobs.topk(5)
                features, error = summarize_sae(state, sae, torch) if sae else (None, None)
                records.append({
                    "step": step, "phase": "prefill_last_position" if step == 0 else "decode_previous_token",
                    "elapsedMs": round((time.perf_counter() - started) * 1000, 2),
                    "inputLastTokenId": int(first[0, -1]),
                    "predictedTokenId": token_id,
                    "predictedToken": tokenizer.decode([token_id]),
                    "chosenLogprob": float(logprobs[token_id].item()),
                    "topLogprobs": [
                        {"tokenId": int(i), "token": tokenizer.decode([int(i)]), "logprob": float(v)}
                        for v, i in zip(values.tolist(), indices.tolist())
                    ],
                    "residualNorm": float(state.float().norm().item()),
                    "features": features,
                    "relativeReconstructionError": error,
                })
                first = torch.tensor([[token_id]], device=device)
                if token_id == tokenizer.eos_token_id:
                    break
    finally:
        handle.remove()
    payload = {
        "schemaVersion": 2, "source": "offline-qwen3-forward-hook", "model": args.model_id,
        "revision": args.revision, "layer": args.layer, "hook": "model.model.layers[N].output",
        "saeFile": args.sae.name if args.sae else None, "dtype": str(dtype),
        "prompt": args.prompt, "sampling": "greedy", "records": records,
        "note": "One residual per prediction step; no causal feature attribution or validated label."
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(records)} prediction steps to {args.out}")


if __name__ == "__main__":
    main()
