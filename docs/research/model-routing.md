# Model routing and learned decision nodes

Status: research synthesis. No model/runtime in this page has been benchmarked by this repository on the target phone.

## The useful distinction: decision versus generation

Many Shortcut branches do not need generated language. They need one choice, an ordinal score, or a probability from a declared set. That is the niche where Laya-like decision models are more interesting than treating every semantic operation as an LLM prompt.

A practical hierarchy to investigate is: deterministic action/rule → specialized bounded decision model → small local generative model → larger local/Apple cloud/remote model → user confirmation.

## Laya as a learned branch primitive

[Laya](https://huggingface.co/convaiinnovations/laya) is built on ModernBERT and exposes typed questions including choice, score and `noul`/probability-style decisions over supplied state. Its model card reports about 421M parameters for the English/typed-decision variants, a compact 512-token English budget, and T4 timings around 39.5 ms for an English single question and 32.8 ms for multilingual, with higher throughput under batching.

The critical qualification is specialization. On Laya's own typed-decisions benchmark, the base English and multilingual checkpoints score about 0.362 and 0.342 while the task-fine-tuned checkpoint reaches 0.766. The project documentation describes fine-tuning as the source of most value; one published training recipe uses roughly 30,000 questions and about 4–5 hours on free Kaggle 2×T4. The model card also recommends relatively small choice sets and shows domain temperature fitting can materially improve expected-calibration error. Sources: [Laya model card](https://huggingface.co/convaiinnovations/laya), [typed-decisions checkpoint](https://huggingface.co/convaiinnovations/laya-typed-decisions), and [training README](https://github.com/NandhaKishorM/laya/blob/main/README.md).

Therefore the current hypothesis is not one universal zero-shot Laya router. It is a shared runtime plus task/domain specialists: notification route, intent route, file/category route, safety/approval gate, error recovery route, or model-route selector. Every specialist would need its own labeled corpus, calibration and abstention policy.

## Browser/ONNX leads for Laya\n\nAs of 2026-09-24, the upstream [laya-ts browser package](https://github.com/NandhaKishorM/laya/blob/main/laya-ts/README.md) documents a split `encoder.onnx` + `head.onnx` export, browser WebGPU with WASM fallback, PyTorch-to-ONNX parity checking, and prediction hooks. This is a stronger integration lead than relying solely on independent exports. Browser support is upstream documented; artifact residency, iPhone latency and particular model fidelity are not reproduced in this repository. The [Latent Scope example](../../examples/latent-scope/) keeps token and typed-decision displays separate.\n

Laya is not a GGUF/llama.cpp model, so wllama is not its runtime. Independent ports show that ONNX is a plausible web path worth later validation. [Mattepiu/laya-onnx](https://huggingface.co/Mattepiu/laya-onnx) publishes an ONNX conversion; [receptron/laya](https://github.com/receptron/laya) implements a TypeScript/ONNX Runtime path; and [mizchi/laya-multilingual-onnx](https://huggingface.co/mizchi/laya-multilingual-onnx) reports browser WebGPU parity tests for selected answers. These are independent projects, not upstream guarantees.

[ONNX Runtime Web](https://github.com/microsoft/onnxruntime/tree/main/js/web) supports client-side execution through WebAssembly and GPU-capable browser backends. That makes a zero-server classifier PWA a credible research route, but iOS memory, compilation, warm retention and Shortcut↔browser handoff costs remain unknown.

## Generative companion: Gemma 4 and wllama

Google's [Gemma 4 overview](https://huggingface.co/blog/gemma4) describes E4B as about 4.5B effective parameters and 8B total including embeddings, with 128K specified context and multimodality. The [Unsloth QAT GGUF distribution](https://huggingface.co/unsloth/gemma-4-E4B-it-qat-GGUF) currently includes roughly 3.22 GB Q2_K_XL and 4.22 GB Q4_K_XL files, plus an approximately 990 MB multimodal projector and a small MTP drafter artifact.

[wllama](https://github.com/ngxson/wllama) is a browser llama.cpp binding with WASM and WebGPU support, OpenAI-compatible interfaces, model splitting, multimodal/tool-call support and worker execution. Its documentation notes the browser's 2 GB individual ArrayBuffer constraint and the need for cross-origin isolation for multithreaded WASM. [Llamas on the Web](https://reeselevine.github.io/llamas-on-the-web/) is a useful independent implementation/benchmark lead and warns that memory remains especially problematic on smartphones.

A first-person [iPhone 17 Pro runtime comparison](https://rockyshikoku.medium.com/local-llm-on-iphone-which-runtime-is-actually-fastest-58096685481e) reports Gemma 4 E2B—not E4B—running substantially differently across LiteRT-LM, MLX, llama.cpp and Core ML. This is evidence that runtime choice matters; it is not a forecast of E4B browser performance.

## Native Apple route

Apple's current Foundation Models APIs materially widen the design space. [Bring an LLM provider to Foundation Models](https://developer.apple.com/videos/play/wwdc2026/339/) describes implementing `LanguageModel` and `LanguageModelExecutor`, while [Dynamic Profiles](https://developer.apple.com/documentation/updates/foundationmodels) can vary models, tools and instructions. [Core AI](https://developer.apple.com/videos/play/wwdc2026/324/) provides a native model conversion/runtime path and Apple separately describes curated/on-device model workflows in [Integrate on-device AI models into your app](https://developer.apple.com/videos/play/wwdc2026/326/).

This suggests a later native bridge in which Laya, Gemma or another runtime is exposed behind one provider/session abstraction and App Intents expose selected operations back to Shortcuts. It is a prospective app architecture, not a current Shortcut-only capability.

## Router objective

A future router should minimize total cost subject to reliability and safety rather than merely maximize model quality. Candidate dimensions include latency, cold-start cost, energy, memory, network dependency, privacy, quota, money, output determinism, task accuracy/calibration and reversibility of the side effect.

The most interesting research question is whether specialization lets a small decision node remove a meaningful fraction of generative calls without reducing task success. That can later be evaluated using Apple's [Evaluations framework](https://developer.apple.com/videos/play/wwdc2026/298/) concepts—datasets, metrics and model-driven judges—alongside ordinary deterministic labels and calibration metrics.

See [inference routes](../inference-routes.md) for the current runtime inventory and [compute inventory](../compute-inventory.md) for external resource boundaries.