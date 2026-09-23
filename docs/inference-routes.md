# Local inference: which model does which job?

Research snapshot 2026-09-23. **No model below has been run on the project owner's phone or in this repo's Pages site.** A checkpoint, a format, a runtime, and an execution surface are four different compatibility questions.

| Candidate | Documented shape | Useful role | Hard question before release |
|---|---|---|---|
| [Laya](https://huggingface.co/convaiinnovations/laya) | 421M-parameter ModernBERT decision model; English root, separate multilingual and typed-decisions checkpoints; Apache 2.0 | Typed classification/score of a compact state and options | Can it run locally on iPhone through a suitable encoder runtime, and is it accurate on *our* labels? |
| [Gemma 4 E4B](https://huggingface.co/google/gemma-4-E4B) | Pretrained multimodal generative model, 4.5B effective / 8B total including embeddings, 128K specified context | Fine-tuning or comparisons | Pretrained is not the default conversational assistant. |
| [Gemma 4 E4B-it](https://huggingface.co/google/gemma-4-E4B-it) | Instruction-tuned model of the same family | Generative interpretation, drafts, constrained tool proposals | Device memory and correct output parsing at a practical context size. |
| [Unsloth E4B-it QAT GGUF](https://huggingface.co/unsloth/gemma-4-E4B-it-qat-GGUF) | Quantized distribution for llama.cpp; includes multiple quantizations and an optional MTP drafter | Candidate artifact for GGUF runtimes | Exact variant size, modality support, current wllama build compatibility, and phone memory. |
| [wllama](https://github.com/ngxson/wllama) | Browser llama.cpp binding; WASM and recent WebGPU support | Optional local inference in a browser page | iOS Safari WebGPU availability, performance, CORS/isolation headers, cache and tab lifetime. |

**Important correction:** Laya's authors report ~33–40 ms per question on a *T4 GPU*, with substantial CPU and cold-load differences. They explicitly report base English/multilingual checkpoints near chance on their typed-decision benchmark (0.362/0.352; majority-class baseline 0.461); 0.766 belongs to the checkpoint fine-tuned on that benchmark. Its 512-token English budget also constrains large dictionaries and many choices. A model card's calibrated probabilities are not a calibrated guarantee for a new workflow. [Laya card](https://huggingface.co/convaiinnovations/laya)

## Proposed `SO Decide` interface

Model-neutral input is a JSON object containing `schema_version`, `request_id`, redacted `state`, a finite `choices` map with one-line descriptions, and an allowed `default`. Output is `choice`, `score` (if used), `confidence`, `model_id`, `status`, and `request_id`. The Shortcuts wrapper validates types, the choice against the declared set, threshold, and timeout before a `Choose from Menu`/`If` branch. Return `default` on invalid output, low confidence, timeout or canceled user action; require user approval for irreversible branches. Example values are illustrative, not model-tested:

```json
{"schema_version":1,"request_id":"demo-001","state":{"text":"Invoice billed twice"},"choices":{"billing":"refunds and invoices","other":"all other cases"},"default":"other"}
```

Start with deterministic Shortcuts rules for unambiguous decisions. Evaluate Laya only on ambiguous classification where it improves measured accuracy. Its Python SDK and ModernBERT architecture are **not GGUF**; wllama's ability to run Gemma GGUF does not run Laya. A server/Colab inference endpoint would add connectivity and availability dependencies, so it is a research control rather than the default phone path. A native app could expose Laya via an App Intent if someone implements and measures the encoder runtime; no such integration is demonstrated here.

## Browser versus native

wllama V3 documents WASM, WebGPU, multimodal and tool calls, a 2 GB per-file limit with model splitting, and cross-origin isolation headers for multithreading. GPU support is not a promise of fast iOS Safari generation; static GitHub Pages may require a separate header strategy to enable threaded WASM. Start with single-thread or WebGPU detection and test the actual origin. A large GGUF can exceed the web process budget even when physical iPhone RAM is larger. [wllama README](https://github.com/ngxson/wllama)

The [WebKit memory discussion](https://www.catchmetrics.io/blog/deep-dive-ram-internals-webkit) provides directional estimates for browsers, not an Apple-supported per-device heap limit. A [first-person iPhone 17 Pro comparison](https://rockyshikoku.medium.com/local-llm-on-iphone-which-runtime-is-actually-fastest-58096685481e) reports Gemma 4 **E2B** at 55.4 tok/s in LiteRT-LM, 47.5 in MLX and 37.8 in llama.cpp (median of three cold runs on iOS 26.4.2); formats, output lengths and runtimes differ, and this is neither E4B nor browser wllama. The [llamas-on-the-web project](https://reeselevine.github.io/llamas-on-the-web/) is a browser GPU/WASM research lead; its site did not expose benchmark data in this review, so we derive no phone throughput from it.

## Measurement contract

Record phone/iOS/browser/app versions, exact model revision and GGUF file hashes/sizes, WASM/WebGPU feature detection, cold/warm download and load time, first-token latency, prompt tokens/s, decode tokens/s, context length, peak memory or crash, battery/thermal state, offline reload, 3+ repetitions, and comparable prompt/output lengths. A model's theoretical 128K context is not a measured feasible mobile context. Include deterministic baseline and a small model before E4B. Do not publish an unqualified tokens/day capacity from one burst benchmark.
