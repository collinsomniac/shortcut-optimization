# Local inference: which model does which job?

Research snapshot 2026-09-23. **No model below has been run by this repository on the target phone or Pages origin.** A checkpoint, artifact format, runtime and execution surface are four different compatibility questions.

| Candidate | Documented shape | Useful role | Hard question before release |
|---|---|---|---|
| [Laya](https://huggingface.co/convaiinnovations/laya) | ~421M ModernBERT decision model for English/typed-decision variants; separate multilingual and typed-decisions checkpoints | Typed classification/score/probability over compact state and options | Which task-specific checkpoint/calibration is actually accurate enough, and which iPhone runtime keeps latency/load worthwhile? |
| [Upstream laya-ts](https://github.com/NandhaKishorM/laya/blob/main/laya-ts/README.md) | Split encoder/head ONNX export; browser WebGPU with WASM fallback and hooks, as of 2026-09-24 | First-party browser typed-decision runtime lead | Specific checkpoint fit, export parity and iPhone memory/latency still require reproduction. |\n| Independent Laya ONNX ports | [laya-onnx](https://huggingface.co/Mattepiu/laya-onnx), [receptron/laya](https://github.com/receptron/laya), [mizchi browser/WebGPU port](https://huggingface.co/mizchi/laya-multilingual-onnx) | Possible browser/JS decision runtime | Do exports preserve upstream outputs closely enough on target browser, and what are cold/warm retention costs? |
| [Gemma 4 E4B](https://huggingface.co/google/gemma-4-E4B) | Pretrained multimodal generative model; ~4.5B effective / 8B total including embeddings, 128K specified context | Fine-tuning/base-model comparisons | Pretrained is not the default conversational assistant and theoretical context is not mobile-feasible context. |
| [Gemma 4 E4B-it](https://huggingface.co/google/gemma-4-E4B-it) | Instruction-tuned model of the family | Generative interpretation, drafting, constrained tool proposals | Device memory, cold load and structured-output correctness. |
| [Unsloth E4B-it QAT GGUF](https://huggingface.co/unsloth/gemma-4-E4B-it-qat-GGUF) | Current QAT GGUF distribution includes ~3.22 GB Q2_K_XL and ~4.22 GB Q4_K_XL files, ~990 MB multimodal projector and optional small MTP drafter | Candidate GGUF artifact for llama.cpp-style runtimes | Combined memory/load behavior, modality support and wllama compatibility on iPhone. |
| [wllama](https://github.com/ngxson/wllama) | Browser llama.cpp binding with WASM/WebGPU, splitting, multimodal/tool-call and worker support | Optional local generative inference in a browser/PWA | Safari memory, WebGPU stability, cache/tab lifetime and isolation/header constraints. |
| Foundation Models custom provider + Core AI | Apple documents `LanguageModel`/`LanguageModelExecutor`, Dynamic Profiles and Core AI native model deployment | Later native app bridge exposing local/remote providers behind one Apple session/tool abstraction | Requires an app implementation; not a stock Shortcut-only path. |

## Laya: specialization matters more than headline latency

Laya's authors report roughly 33–40 ms per single question on a **T4 GPU**, with substantial CPU/cold-load differences. On the project's typed-decisions benchmark, the base English and multilingual checkpoints score about **0.362 and 0.342**, while the task-fine-tuned checkpoint reaches **0.766**. Its English budget is 512 tokens and the docs recommend keeping ordinary choice sets relatively small. A model card's calibration on its benchmark is not a guarantee for a new workflow. [Laya card](https://huggingface.co/convaiinnovations/laya)

The published training material describes specialization as where most value appears; one recipe is roughly 30,000 questions and about 4–5 hours on free Kaggle 2×T4. [Training README](https://github.com/NandhaKishorM/laya/blob/main/README.md) This makes small domain specialists more plausible than one universal zero-shot router.

## Proposed `SO Decide` contract

Model-neutral input can contain `schema_version`, `request_id`, redacted `state`, a finite `choices` map with one-line descriptions, and an allowed `default`. Output can contain `choice`, optional `score`, `confidence`, `model_id`, `status` and `request_id`. The Shortcuts wrapper validates types, declared choices, confidence/abstention and timeout before an If/Menu branch; irreversible actions retain user approval.

Start with deterministic Shortcuts rules for unambiguous decisions. Laya is interesting for fuzzy bounded classification only when later evidence shows an advantage. Its ModernBERT architecture is **not GGUF**; wllama's support for Gemma GGUF does not run Laya.

## Browser classifier route

Independent ONNX ports materially lower the barrier to a future browser experiment. [ONNX Runtime Web](https://github.com/microsoft/onnxruntime/tree/main/js/web) supports browser-side WASM/GPU inference, while the Laya ports above demonstrate that the architecture can be exported by third parties. These are implementation leads, not upstream compatibility guarantees.

A useful later experiment is therefore Shortcuts → compact JSON state → local Laya PWA/JS runtime → typed result → Shortcut continuation. The important unknown may be lifecycle overhead—page/app handoff, model compilation, cache residency and WebKit process eviction—rather than forward-pass time.

## Browser generative route

wllama V3 documents WASM, WebGPU, multimodal/tool calls, model splitting and an individual ArrayBuffer limit around 2 GB; multithreaded WASM requires cross-origin isolation headers. GPU support does not imply fast or stable iOS Safari generation. [wllama README](https://github.com/ngxson/wllama)

The [WebKit memory analysis](https://www.catchmetrics.io/blog/deep-dive-ram-internals-webkit) is directional rather than an Apple-supported per-device heap guarantee. [Llamas on the Web](https://reeselevine.github.io/llamas-on-the-web/) is another useful independent browser-GPU lead and explicitly treats smartphone memory as a constraint.

A [first-person iPhone 17 Pro comparison](https://rockyshikoku.medium.com/local-llm-on-iphone-which-runtime-is-actually-fastest-58096685481e) reports Gemma 4 **E2B** at about 55.4 tok/s in LiteRT-LM, 47.5 in MLX and 37.8 in llama.cpp (median of three cold runs on the author's iOS 26.4.2 setup), with large runtime-dependent memory differences. It is neither E4B nor browser wllama; its value here is evidence that runtime choice can dominate model choice.

## Native Apple provider route

Apple now documents a more integrated long-term path. [Bring an LLM provider to Foundation Models](https://developer.apple.com/videos/play/wwdc2026/339/) describes `LanguageModel` plus `LanguageModelExecutor`; the executor handles prewarming, transcript conversion, context/generation options and streamed events. [Dynamic Profiles](https://developer.apple.com/documentation/updates/foundationmodels) can vary models, tools and instructions in a session. [Meet Core AI](https://developer.apple.com/videos/play/wwdc2026/324/) describes native model conversion/runtime and integration with Foundation Models.

A later companion app could therefore expose `LayaLanguageModel`, `GemmaLanguageModel` or remote providers and surface selected operations to Shortcuts through App Intents. That architecture could reduce custom orchestration glue, but it requires native development and remains a hypothesis until implemented.

## Measurement contract for the later experiment phase

Record phone/iOS/browser/app versions; exact model revision and artifact hashes/sizes; runtime/backend; WASM/WebGPU/ANE/GPU feature path; cold/warm download/load; first-token latency; prompt/decode throughput; context length; peak memory/crash; battery/thermal state; offline reload; at least three repetitions; and comparable prompts/outputs. For classifiers also record confusion, calibration, abstention and cost of errors.

A model's theoretical context or one burst decode number is not a usable mobile capacity claim. Include deterministic and small-model baselines before E4B. See [model-routing synthesis](research/model-routing.md).