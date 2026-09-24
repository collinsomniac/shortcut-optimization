# From decoding display to a feature atlas

For the streaming semantic-map design, 2026 natural-language-activation research, model hooks and validation criteria, see [Semantic atlas design](semantic-atlas-design.md).

Research snapshot: 22 September 2026. This document distinguishes what Latent Scope already measures from hypotheses about the model's internal computations. The current running model is WebLLM's quantized `Llama-3.2-1B-Instruct-q4f16_1-MLC` in an iPhone browser; the shader sees streamed token log probabilities, **not** weights, attention, neurons, or residual activations. “Save trace” now exports one run's conversation, sampled token, returned top-five log probabilities, and elapsed times as JSON on the device. It makes no network request. The file includes private chat text. Browser downloads and run-time responsiveness on the owner's phone still need confirmation.

Progress: a token scrubber now pins any of the 64 latest decoding steps for exact candidate inspection. An [offline Qwen forward-hook probe](../research/README.md) captures a chosen block's final-position residual stream and optionally matching sparse features. That probe is prepared but has **not** been run against model weights in this environment; its JSON cannot be mixed with live Llama measurements.

## What can be measured

| Signal | Meaning | Access path | Interpretation boundary |
| --- | --- | --- | --- |
| Chosen-token log probability, top candidates, remaining mass | Next-token distribution at an output step | Already exposed by WebLLM | One-token alternatives; omitted tail and no internal feature attribution |
| Residual stream at named layer and position | Model's current state between blocks | PyTorch forward hook; instrumented inference runtime | Coordinates have no inherent human labels |
| Attention pattern and output | Which positions a head reads and what it writes | Named hooks | Attention weight is not itself a causal explanation |
| MLP activation or neuron contribution | Intermediate computation at a layer | Named hooks, optionally top-k/reduced on GPU | A neuron can be polysemantic; its input, sign, and output matter |
| SAE feature at layer | Projection of a residual state onto a trained sparse dictionary | Exact-model SAE encoder | A learned basis and a provisional label, not a ground-truth thought |
| Logit lens / tuned lens | An intermediate state's projection into vocabulary logits | Output unembedding or trained calibrated probe | Probe predictions may differ from the model's final computation |
| MoE expert ID and gate weight | Which experts execute and their mixing weights | Router hook | Selection is a routing decision, not an expert's semantic label |
| Ablation or activation patch | Change in target logits/output under controlled intervention | Re-run model with hook | Stronger evidence of causal involvement for that specific prompt and target |

A reasoning transcript is additional **output text**. It can help construct hypotheses, but does not verify how internal computation produced an answer. We should compare traces and interventions instead of presenting fluent reasoning text as a direct readout of hidden state.

## Model and tooling choice

**Immediate baseline: keep the working Llama browser experience.** Anthropic's open-source circuit-tracing release explicitly demonstrates graphs on Llama-3.2-1B and Gemma-2-2B. Its tooling is an unusually close way to study a model in this size class. A desktop replica must confirm the exact base/instruct revision, tokenizer, hook points, and quantization relationship before overlaying a graph on phone traces. The release supports feature interventions and an interactive explorer. This is a parallel offline research harness, not something the current WebLLM build exposes.

**Most promising sparse-feature research target: Qwen3-1.7B-Base.** The model card lists Apache-2.0. Qwen-Scope supplies a residual-stream TopK sparse autoencoder for all 28 transformer layers: width 32,768, hidden size 2,048, and 50 selected features per position. It documents a PyTorch forward hook and encoder calculation. The SAE artifacts are separately marked with a custom `qwen` license and usage restriction; inspect these terms before any distribution or product use. Its base-model dictionary does not automatically validate feature labels on an instruct, quantized, or differently implemented version. Qwen's card says cross-checking a post-trained checkpoint can be reasonable; we still need paired calibration rather than assume identity.

**MoE second track:** OLMoE-1B-7B has approximately 1B active and 7B total parameters. An instrumented native or desktop run can record per-layer expert IDs, gate scores, and contributions, and build a routing atlas. Qwen3-30B-A3B has Qwen-Scope SAEs too, but its total weights are a poor first phone-browser target. Quantized 7B at an ideal 4 bits requires 3.5 GB for weights alone; quantization metadata, embeddings, KV cache, inference scratch space and browser/GPU allocations increase that figure. Neither fit nor sustained speed has been verified on the iPhone. CPU/GPU offload or expert caching trades throughput for residency. iPhone CPU and GPU share system memory, so “CPU offload” cannot increase the total physical RAM budget; disk paging may further reduce throughput. llama.cpp exposes `--cpu-moe`, `--n-cpu-moe`, and tensor placement, but it does not thereby expose a stable browser router telemetry API. Native Metal or a desktop sidecar is a distinct architecture that must be tested rather than silently substituted for browser-local inference.

**Dictionary memory arithmetic.** One Qwen-Scope 32,768 × 2,048 f16 encoder is 134,217,728 bytes (128 MiB) before bias/overhead. Encoder and decoder together are about 256 MiB per layer; 28 layers are about 7 GiB. A browser demo should begin with *one* chosen layer and GPU top-k reduction, or a validated restricted feature subset. Compute overhead and extra model residency still require a device benchmark. A visual network of 1.7 billion weight cells would dwarf any mobile canvas and would not disclose which parameters were causally important. A weight map can instead show a named, selectable tensor tile with stable parameter coordinates and measured contribution overlay.

## An evidence-bearing feature atlas

1. Pin the model revision, tokenizer, quantization, probe/SAE revision, precise hook, layer and token position. Record all generated positions **and selected prompt positions** if we want to discuss where a concept first appears. Prefill can be instrumented offline even if mobile streaming only exposes decoded tokens.
2. Run matched contrasts, e.g. “The sky is” versus an altered context, while capturing the residual vector at a small set of named layers. Store sparse top feature IDs, strengths, normalized baseline scores, and reconstruction error. Separate processing time, telemetry time, and render time. Avoid full GPU-to-CPU tensor transfers per token.
3. For each feature, inspect top-activating examples, low/negative examples and held-out prompts. Generate a plain-language label as a **hypothesis**; record the examples and failure cases. If the dictionary does not reconstruct the hidden state adequately on our prompt distribution, label the feature view incomplete.
4. Test claims by ablating or patching that feature or source activation between matched prompts; report change in a *predeclared* target logit and in the distribution, with controls. Re-run across paraphrases and seeds. Attribution edges from a graph are model-dependent approximations until these tests support them.
5. Store the catalog locally as versioned records: `model_rev / tokenizer_rev / quantization / hook / layer / dictionary_rev / feature_id`, proposed label, examples, counterexamples, activation counts, reconstruction quality and intervention results. Store occurrences separately by `run_id / position / strength / baseline`. Graph edges need an explicit type: co-occurrence, temporal succession, attribution estimate, or causal test result. Counts describe a chosen test corpus, not a universal meaning.

### Proposed instrumented event

```json
{
  "schemaVersion": 2,
  "runId": "local-id",
  "source": { "modelRevision": "exact-revision", "runtime": "harness-version", "quantization": "none", "probeRevision": "dictionary-revision" },
  "position": { "index": 17, "phase": "decode", "tokenId": 123, "tokenText": " example" },
  "measurements": [
    { "kind": "sae_feature", "hook": "residual_after_block", "layer": 12, "id": 402, "value": 1.2, "baselineZ": 2.1 },
    { "kind": "reconstruction_error", "hook": "residual_after_block", "layer": 12, "value": 0.08 }
  ],
  "sampling": { "captured": true, "droppedEvents": 0 }
}
```

This is a **future contract**, not data present in today's exported v1 traces. Each numeric field needs a documented normalization and tested hook semantics. Prefix `phase` with prefill/decode to avoid attributing a prompt activation to generated reasoning.

## Visual design

| View | Graphic | Human-readable inspection |
| --- | --- | --- |
| Token futures (available now) | Chosen token and top alternatives with residual probability mass; select a step on the timeline | Exact candidate strings, percentages, and warning that a candidate is not a full reply |
| Feature atlas (proposed) | Layer × feature sparse activity over time; stable feature IDs grouped by layer; animated only on new events | Tap a node for a provisional label, strongest examples, counterexamples, strength and causal evidence level |
| Circuit replay (proposed, offline initially) | A small token-specific directed graph of features, source positions and target token logits | Distinguish co-activation, attribution estimate, and tested causal edges by labels and legend |
| Expert routes (proposed, MoE only) | Layer × token paths between expert IDs; line thickness gate weight; optional playback | Router score, observed frequency and contrast across prompts; expert names remain provisional |
| Weight tile (optional) | A bounded slice of one tensor, with quantized weight value and signed measured activity overlay | Tap reveals tensor name and indices; no claim that one pixel is one idea |

On mobile, retain the current shader as a continuously visible backdrop and compact chat sheet. A trace scrubber can pin one token, showing its alternatives and feature panel together. Disable continuous animation while idle; batch sparse data to one small GPU buffer or texture per token; cap canvas resolution and update the DOM only for the selected event. Cache compiled shader/program and existing tiles. During slow prefill or thermal throttling, drop **visual** frames before inference, and surface telemetry gaps explicitly. Compare p50/p95 token latency, total token throughput, time-to-first-token, memory and responsiveness to the current uninstrumented build on the same phone.

## Experiments and acceptance gates

- **A, current browser baseline:** run the three built-in prompts 3 times each, save each trace, record phone/browser build, generation rate, time to first token, thermal behavior and any stalls. Check trace token count against on-screen count per run (the on-screen counter is cumulative), token alternatives against the inspector, stopped/error status, and file openability. The existing v1 trace records token event times relative to the start of generation; the time to first returned token includes prompt processing. It does not record frame timings, GPU memory, hidden activations or a full-vocabulary distribution.
- **B, exact-model desktop pilot:** run the open circuit-tracing demo on the supported Llama family and trace two contrasting prompts. Record exact model match and whether selected features have reproducible labels and intervention effects. If revisions differ, do not attach those labels to mobile traces.
- **C, Qwen sparse pilot:** reproduce one layer's SAE feature extraction with the original unquantized Qwen3-1.7B-Base. Report reconstruction and activation sparsity, 20 top examples for three candidate features, controls and held-out detection. Only then test a quantized/instruct runtime and measured phone fit.
- **D, router pilot:** choose a small, license-appropriate MoE, instrument a named router on desktop, compare IDs and weights across prompts, and benchmark a *native* phone build only after a real peak-memory estimate. Do not equate an active-parameter count with an installed model size.

## Primary sources

- [Anthropic, Towards Monosemanticity (2023)](https://transformer-circuits.pub/2023/monosemantic-features/index.html); [Circuit Tracing methods (2025)](https://transformer-circuits.pub/2025/attribution-graphs/methods.html); [open-source circuit tracing and Llama-3.2-1B demo](https://www.anthropic.com/research/open-source-circuit-tracing).
- [Anthropic, measuring chain-of-thought faithfulness](https://www.anthropic.com/research/measuring-faithfulness-in-chain-of-thought-reasoning).
- [Qwen3-1.7B-Base model card](https://huggingface.co/Qwen/Qwen3-1.7B-Base); [Qwen-Scope SAE model card and hook code](https://huggingface.co/Qwen/SAE-Res-Qwen3-1.7B-Base-W32K-L0_50); [Qwen-Scope paper](https://arxiv.org/abs/2605.11887).
- [Gemma Scope 2 model information](https://huggingface.co/google/gemma-scope-2-1b-it), a second pretrained dictionary ecosystem whose model and tooling terms need separate review.
- [llama.cpp server configuration](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md); [OLMoE-1B-7B model card](https://huggingface.co/allenai/OLMoE-1B-7B-0125).
