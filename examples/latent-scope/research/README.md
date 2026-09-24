# Offline activation probe

`probe_qwen.py` records one named residual-stream hook from an **exact revision** of the Apache-2.0 Qwen3-1.7B-Base model. It runs locally in PyTorch/Transformers and captures a single residual vector per prediction step, a norm, token scores, and optionally the top 50 matching Qwen-Scope SAE features and reconstruction error. It writes JSON locally and does not contact the Latent Scope website. The script does not download or redistribute SAE files.

On a machine with model access, install a compatible PyTorch build for its CPU/GPU and `transformers>=4.51,<5` plus `accelerate` and `safetensors`. Pin a model commit hash from the model repository and run:

```sh
python research/probe_qwen.py --revision MODEL_COMMIT_HASH --layer 12 --prompt 'The sky is' --tokens 16 --out probe.json
```

For sparse features, obtain `layer12.sae.pt` separately from [Qwen-Scope](https://huggingface.co/Qwen/SAE-Res-Qwen3-1.7B-Base-W32K-L0_50), inspect its terms, and add `--sae /path/to/layer12.sae.pt`. The checkpoint must match the selected hook and layer. The optional projection is done on the selected PyTorch device; only top features and summary values are copied into JSON. The script performs greedy generation so two runs with the same model and prompt are easier to compare. Position 0 captures the final **prompt** position used to predict the first output token. Later records capture the previous generated token's position. There is no activation record for the last output token unless another prediction step follows. The first record does not include activations for all earlier prompt positions.

**Status:** prepared and syntax checked; a model-backed run is pending. This workspace has no PyTorch, Transformers, cached model weights, or approved access to the external model host. Do not interpret this as a completed feature extraction result or substitute its output for the mobile app's Llama inference. The checkpoints differ; align them only after a model and runtime match is verified. The tool's activation magnitudes, selected feature IDs and decoder error are observations, while semantic names and causal edges require the contrast/intervention protocol in [the roadmap](../docs/interpretability-roadmap.md).
