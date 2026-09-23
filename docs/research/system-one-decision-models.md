# System-One decision models: Jev, Laya, GLiClass, SetFit and fast typed inference

Reviewed 2026-09-23. This page studies models whose useful output is a bounded decision rather than an open-ended generated string. It separates published measurements from project hypotheses. No iPhone result on this page is a project benchmark.

## 1. The design space is broader than one architecture

"System One" is TypeSafe's product/research framing for fast machine-native decisions. The useful technical category is broader:

| Family | Examples | Runtime shape | Label flexibility | Main tradeoff |
|---|---|---|---|---|
| Typed decision encoder/head | Laya; Jev conceptually, though Jev's exact architecture is closed | Encode state + question/options; score bounded outputs without ordinary token-by-token prose generation | Options supplied per request | Excellent software interface; specialization/calibration matter |
| Dynamic zero-shot classifier | GLiClass and related GLiNER-style classifiers | Encode text and candidate labels in a single classification-oriented forward path | Dynamic labels | Strong zero-shot flexibility without full causal decoding |
| Embedding/prototype classifier | SetFit / sentence-transformer classifiers | Embed text, compare/train a small head or prototypes | Usually trained/derived per task | Tiny inference cost; less expressive than typed workflow models |
| NLI/cross-encoder zero-shot | BART-MNLI/DeBERTa-style pipelines | Score text against each candidate/hypothesis | Dynamic labels | Simple and general, but compute often grows with number of labels |
| Generative router/classifier | small causal LM routers such as Arch-Router | Generate or score a constrained answer | Flexible | Still pays autoregressive/model overhead; useful comparison but not the same class |
| Frontier structured-output model | cloud LLM with JSON/schema constraints | Full generative reasoning then typed parse/constraint | Extremely flexible | Best semantic breadth, highest latency/cost; ideal teacher/escalation path |

The important distinction for this repository is not "LLM versus classifier." It is **how much computation and freedom does the operation actually need?**

## 2. Jev: the closed frontier-style reference point

TypeSafe introduced Jev on 2026-09-15 as a "System One Model": unstructured/structured state in, typed probabilistic decisions out. Its public primitives are `choice`, `score`, and `noul`; multiple independent questions can be evaluated against the same state in one request. TypeSafe says outputs are sampled/scored in parallel rather than generated as ordinary prose tokens.

Primary sources:
- [Introducing System One Models & Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- [TypeSafe workflow evals](https://evals.typesafe.ai/)
- [TypeSafe OpenAPI](https://api.typesafe.ai/docs)

TypeSafe currently advertises roughly 70–500 ms end-to-end latency and $0.042 per million input tokens, with output too cheap to meter. Its launch post says the largest workflow comparison reached 193.6x lower time and 444.6x lower cost than the comparison setup, while explicitly warning that these are high-end gains and that the workflows were built by its model-capabilities team.

**Do not infer Jev's hidden architecture or parameter count.** TypeSafe publicly names a new architecture, parallel sampler, and Reinforcement Learning for Calibrated Decisions (RLCD), but has not published enough implementation detail to reproduce Jev. Open projects that call their training "RLCD-like" are useful experiments, not evidence of Jev's internal algorithm.

### Public workflow pattern

TypeSafe's workflow evals are more valuable architecturally than the headline benchmark. Their examples decompose a policy into:
1. deterministic arithmetic/date/status logic in code;
2. many small independent semantic questions;
3. probability-aware program rules;
4. a final discrete action.

The customer-service example asks many independent questions about intent, frustration, urgency, fraud/legal/person-request flags, then runs deterministic policy sections. The invoice example similarly leaves sums/dates/statuses to code and asks semantic questions only where fuzzy judgment is needed.

That is almost exactly the programming model this repository should investigate.


### Independent Jev measurement

[DecisionEval](https://decisioneval.dev/models/typesafe-jev/) reports an independent run of Jev 1.13.0 on the frozen `LocalLLaMA/typed-decisions` test split: 400 requests / 2,000 decisions, all requests successful.

| Metric | Independent result |
|---|---:|
| Accuracy | 0.740 [0.721, 0.759] |
| Brier | 0.148 [0.139, 0.156] |
| ECE, 10 bins | 0.045 [0.037, 0.066] |
| Score MAE | 0.389 |
| Request latency | p50 687 ms / p95 777 ms, client/network included, five decisions/request |
| Total input cost reported | $0.0159 for the 2,000-decision run |

The most useful result for autonomy is **accuracy at coverage** rather than raw accuracy: DecisionEval reports 57.6% coverage / 0.864 accuracy at confidence ≥0.7, and 24.5% coverage / 0.937 accuracy at confidence ≥0.9.

There is a calibration discrepancy worth preserving. Laya's comparison card cites Jev ECE 0.144, while DecisionEval obtains 0.045 and says it cannot reproduce 0.144; different binning/definitions are a plausible explanation but are not published. Do not compare ECE values without matching the exact computation.

DecisionEval also points out that 40.6% of the benchmark decisions lack teacher-ensemble argmax agreement. Jev scores 0.841 where teachers agree and 0.591 where they disagree in that run. This makes the dataset useful for system comparison but not equivalent to human ground truth.

## 3. Laya: open typed-decision implementation

[Laya](https://github.com/NandhaKishorM/laya) is currently the most directly useful open implementation for this project.

Published checkpoints:

| Checkpoint | Encoder | Params | Context | Intended role |
|---|---:|---:|---:|---|
| `laya` | ModernBERT-large | 421M | 512 | English |
| `laya-multilingual` | mmBERT-base | 322M | 1024 | multilingual |
| `laya-typed-decisions` | ModernBERT-large | 421M | 1024 | typed-decisions specialization |

Laya places option markers into the encoded sequence and scores the bounded options at those marker positions. The SDK returns a selected choice or score plus probabilities/confidence; `noul` returns P(true). It reports zero output tokens because it is not generating an answer string.

### Minimal Laya example

```python
import laya

agent = laya.load("convaiinnovations/laya")

state = {
    "message": "I was charged twice and need this fixed before rent is due.",
    "account": {"plan": "pro", "duplicate_charge": True},
}

questions = {
    "department": {
        "type": "choice",
        "instructions": "Which department should handle this request?",
        "criteria": {
            "billing": "payments, refunds, duplicate charges",
            "technical": "bugs, outages, broken product behavior",
            "sales": "pricing, upgrades, new contracts",
            "other": "none of the above",
        },
    },
    "urgency": {
        "type": "score",
        "instructions": "How urgent is the request?",
        "criteria": [
            "not time-sensitive",
            "should be handled soon",
            "blocking or deadline-critical",
        ],
    },
    "refund_requested": {
        "type": "noul",
        "instructions": "Does the user explicitly request money back?",
    },
}

result = agent.predict(state, questions)

print(result["answers"]["department"]["choice"])
print(result["answers"]["department"]["probabilities"])
print(result["answers"]["urgency"]["score"])
print(result["answers"]["refund_requested"]["noul"])
```

The result shape is defined in Laya's public implementation. A `choice` answer includes `choice`, probabilities and confidence; a `score` includes expected score, level probabilities and confidence; a `noul` includes a probability and confidence.

### Published Laya benchmark

Laya's current `typed-decisions` report uses 400 cases / 2,000 decisions across four workflow domains.

| Model | Accuracy | Soft acc. | Brier | ECE | Score MAE |
|---|---:|---:|---:|---:|---:|
| Laya typed-decisions | 0.766 | 0.471 | 0.061 | 0.213 | 0.242 |
| Laya base English | 0.361 | 0.332 | 0.316 | 0.175 | 0.694 |
| Laya multilingual | 0.342 | 0.326 | 0.439 | 0.285 | 0.687 |
| Jev 1.13.0 comparison published by Laya | 0.727 | 0.580 | 0.148 | 0.144 | 0.391 |
| Per-question majority | 0.461 | — | — | — | — |
| Random | 0.318 | — | — | — | — |

Source: [Laya BENCHMARKS.md](https://github.com/NandhaKishorM/laya/blob/main/BENCHMARKS.md).

The central lesson is that **fine-tuning, not the base checkpoint, creates most of the typed-workflow value**. The base checkpoints are below the majority baseline on this benchmark.

Laya's measured Tesla T4 latency:

| Questions in request | English | Multilingual |
|---:|---:|---:|
| 1 | 39.5 ms | 32.8 ms |
| 5 | 84.5 ms | 40.1 ms |
| 10 | 158.6 ms | 72.3 ms |
| 50 | 771.3 ms | 337.4 ms |

Those are local T4 measurements, not API round trips and not iPhone measurements.

### Calibration and cardinality are first-class constraints

Laya reports substantial calibration improvement from fitting one temperature per (question type, option-count) bucket: mean ECE 0.466 → 0.081 for English and 0.314 → 0.106 for multilingual on its calibration setup.

The current implementation also degrades on very large option sets because its fixed option/head token budget must represent every criterion. The maintainers recommend keeping ordinary choice sets modest, increasing the budget, using embedding shortlisting, or coarse→fine classification. This is directly relevant to an agent capability registry: do not pass 180 installed actions as one flat Laya choice question.

## 4. GLiClass: dynamic zero-shot labels without a typed workflow API

[GLiClass](https://github.com/Knowledgator/GLiClass) is a useful comparison because it is explicitly designed for dynamic zero-shot sequence classification and scores candidate labels in a classification-oriented forward pass rather than using a general chat model. Its maintainers report roughly 10x faster classification than traditional cross-encoder approaches in their setup.

```python
from gliclass import GLiClassModel, ZeroShotClassificationPipeline
from transformers import AutoTokenizer

model_id = "knowledgator/gliclass-small-v1.0"
model = GLiClassModel.from_pretrained(model_id)
tokenizer = AutoTokenizer.from_pretrained(model_id)

classifier = ZeroShotClassificationPipeline(
    model,
    tokenizer,
    classification_type="multi-label",
    device="cuda:0",
)

result = classifier(
    "The battery only lasts five miles and I want a refund.",
    ["battery issue", "refund request", "shipping", "sales"],
    threshold=0.5,
)[0]
```

Recent GLiClass versions support hierarchical labels. That makes the family particularly interesting for **coarse capability family → fine action** classification.

GLiClass is not a drop-in substitute for Laya's `choice/score/noul` schema, but it may be a stronger zero-shot label matcher in places where Laya would otherwise need domain fine-tuning.


### GLiClass V3 scale/speed spectrum

Current GLiClass V3 model cards publish a useful edge→large spectrum on an A6000. The detailed zero-shot benchmark table reports average F1 values of roughly 0.490 (32.7M edge), 0.558 (151M modern-base), 0.620 (399M modern-large), 0.676 (187M base), and 0.719 (439M large). The accompanying speed table averages about 97.3, 54.5, 43.8, 51.6 and 25.2 examples/s respectively across 64–512-token inputs and 1–128 labels.

Source: [GLiClass large v3 model card](https://huggingface.co/knowledgator/gliclass-large-v3.0).

The card itself contains a small reporting inconsistency: its summary table lists a lower "Average Benchmark" value for several variants than the detailed zero-shot table. Preserve the individual/detailed table when doing comparisons and re-check the model revision before eventual benchmarking.

The striking systems result is label scaling: GLiClass edge stays around 103.8 examples/s at one label and 82.6 at 128 labels in the published A6000 table, while the DeBERTa cross-encoder baselines collapse toward sub-1 example/s at 64–128 labels. That is precisely why dynamic single-pass label encoders deserve a place beside Laya in our capability-router research.

## 5. SetFit: teacher-generated data and very cheap specialists

SetFit is useful less because it resembles Jev's interface and more because it demonstrates a powerful system pattern: **use class semantics or a larger teacher to cheaply manufacture enough data to train a small specialist**.

Hugging Face's current zero-shot tutorial trains a small SetFit classifier from templated examples derived only from class names. On its published emotion example, BGE-small SetFit reaches 0.591 accuracy versus 0.3765 for the demonstrated BART-MNLI zero-shot baseline, with 0.46 ms versus 31.18 ms per sentence on the authors' GPU benchmark. Those numbers are task/hardware specific, but the architecture is relevant.

SetFit also documents teacher→student knowledge distillation over unlabeled data using `DistillationTrainer`.

Sources:
- [SetFit zero-shot classification](https://huggingface.co/docs/setfit/how_to/zero_shot)
- [SetFit knowledge distillation](https://huggingface.co/docs/setfit/how_to/knowledge_distillation)

## 6. Fine-tuning Laya-style specialists

Laya publishes a Kaggle 2×T4 notebook that performs the complete loop: dataset construction, RLCD-style training with proper-scoring-rule rewards and a GRPO-style policy-gradient method, temperature fitting, evaluation, and Hub publishing. The README estimates roughly 4–5 hours for four epochs over about 30,000 questions.

Source: [Laya fine-tuning material](https://github.com/NandhaKishorM/laya/blob/main/README.md).

A project-specific pipeline should be broader than simply "generate 30k labels":

### Dataset unit

Store the **state**, **question definition**, **answer target/distribution**, **provenance**, and **split/group identity**.

```json
{
  "state": {
    "source": "share_sheet",
    "text": "...",
    "recent_receipts": []
  },
  "question": {
    "id": "primary_intent",
    "type": "choice",
    "instructions": "Which capability family best matches the user's desired outcome?",
    "criteria": {
      "capture": "save or organize for later",
      "task": "something the user needs to do",
      "research": "needs investigation or comparison",
      "communicate": "send or draft a communication",
      "unknown": "none is sufficiently supported"
    }
  },
  "target": {
    "choice": "research",
    "distribution": {
      "capture": 0.08,
      "task": 0.15,
      "research": 0.72,
      "communicate": 0.02,
      "unknown": 0.03
    }
  },
  "provenance": "frontier_teacher_v3+human_review",
  "scenario_group": "purchase_research"
}
```

### Training-data quality matters more than raw volume

Include:
- ordinary positive examples;
- near-boundary examples between easily confused choices;
- hard negatives;
- counterfactual edits that should flip one decision but preserve others;
- paraphrases and noisy real input;
- option-order permutations;
- missing-context cases;
- novel/OOD examples where `unknown` or escalation is correct;
- examples where several independent questions read the same state differently.

Keep scenario families together when splitting train/eval so paraphrases of one synthetic case do not leak across the boundary.

## 7. Frontier model + fast classifier: a symbiotic architecture

The frontier model should be a **teacher/compiler/escalation engine**, not automatically the hot-path controller.

### Offline / training-time roles

1. **Schema induction.** Give the teacher a workflow corpus and capability catalog; ask it to propose stable semantic dimensions and candidate labels.
2. **Synthetic case generation.** Generate balanced examples, boundary cases, counterfactuals and adversarial ambiguity.
3. **Soft labeling.** Ask one or more frontier teachers for probability distributions, not only argmax labels.
4. **Choice critique.** Detect overlapping labels, missing cases, criteria that encode multiple concepts, or unstable wording.
5. **Hard-negative mining.** Feed the teacher the specialist's mistakes and ask for similar-but-distinct cases.
6. **Distillation.** Train the fast model against teacher probabilities plus gold/human outcomes.
7. **Calibration set creation.** Reserve independently generated or real cases for temperature/threshold fitting; do not calibrate on training examples.

### Online roles

1. Fast classifier evaluates the routine state.
2. Deterministic policy acts only above calibrated thresholds.
3. Low confidence, high entropy, OOD signals, repeated failure, or `unknown` trigger **choice elevation**.
4. Frontier model may propose up to N candidate subchoices, rewrite criteria, request missing fields, or generate a structured artifact.
5. The classifier re-scores the bounded candidates when possible.
6. Executor performs only an allowed capability.
7. A post-action classifier verifies completion/recovery state.
8. Interesting failures are logged for the next training round.

### Choice elevation versus choice mutation

**Elevation** adds a temporary finer choice underneath a stable category. Example:

```text
research
  ├─ compare_purchase_options
  ├─ fact_check_claim
  ├─ investigate_technical_issue
  └─ find_local_service
```

The frontier model may propose these subchoices from context, but a stable top-level specialist still controls the route.

**Mutation** edits the durable schema itself: split one overloaded label, merge duplicates, rewrite ambiguous criteria, or add a new recurring class. Mutation should be an offline/reviewed process because changing labels invalidates calibration and potentially the training distribution.

### Active-learning trigger

A useful queue score could combine:

```text
priority =
    low_calibrated_confidence
  + small_top1_top2_margin
  + teacher_student_disagreement
  + repeated_fallback
  + failed_postcondition
  + novelty/OOD_signal
```

Those are exactly the expensive examples worth sending to a frontier teacher or human instead of labeling random traffic.

## 8. iOS execution surfaces

No single surface gives "a model inside every app." iOS provides several bounded integration surfaces with different authority.

| Surface | Can run local model code? | Reach | Best role |
|---|---|---|---|
| Safari/PWA page | Yes in principle: Safari 26 ships WebGPU; WebKit explicitly names ONNX Runtime and Transformers.js | Browser/web app | Fastest zero-install research route |
| Safari Web Extension | JavaScript/web extension plus native containing app; model execution in a specific extension context still needs validation | Safari pages | Contextual page classifier/overlay |
| Share/Action extension | Native extension receives shared content from many host apps | User-invoked cross-app | "Analyze/route this" from nearly any shareable content |
| App Intents | Native app capabilities exposed to system experiences | Siri, Shortcuts, Apple Intelligence/system surfaces | Stable semantic capability API |
| Shortcuts | Orchestration/automation layer; can call app intents/web APIs and hand off to helper apps | Broad user workflows | Trigger/state/policy/execution composition |
| Custom keyboard | Systemwide where third-party keyboards are permitted | Text fields | Narrow text suggestion/classification UI, not general agent control |
| Native app + Core AI/MLX/custom runtime | Yes | App + intents/extensions it exposes | Best long-term local inference owner |
| Foundation Models custom provider | `LanguageModel`/`LanguageModelExecutor` can wrap local or server models | Native apps using Foundation Models | Unified Apple-native provider abstraction |

### Browser

WebKit states that WebGPU has shipped in Safari 26 on iOS and that ONNX Runtime and Transformers.js work with Safari's WebGPU implementation:
[WebKit Features in Safari 26](https://webkit.org/blog/17333/webkit-features-in-safari-26-0/).

This makes an ONNX-converted Laya/GLiClass/SetFit-style model far more plausible on iPhone than a large GGUF LLM. The remaining unknowns are model conversion fidelity, Safari memory, initial compilation/load, cache residency, background eviction and actual target-device latency.

### Safari extension

Apple's [Safari Web Extensions](https://developer.apple.com/documentation/safariservices/safari-web-extensions) can read/modify page content and are packaged as an iOS app extension. Apple also documents [native messaging and app groups](https://developer.apple.com/documentation/safariservices/messaging-between-the-app-and-javascript-in-a-safari-web-extension): a background/extension page can send a message to the native extension; content scripts cannot call native messaging directly and must route through extension JavaScript. The containing iOS app cannot proactively send messages back to web-extension JavaScript the same way the macOS app can.

A plausible architecture is:

```text
content script
   ↓ selected/page state
extension background/page
   ├─ run small ONNX classifier in JS/WebGPU  [needs extension-context validation]
   └─ nativeMessaging
          ↓
     native app extension / shared App Group
          ↓
     Core AI/MLX/custom local runtime
```

Do not yet claim WebGPU works inside every Safari extension execution context; WebKit documents Safari web-page support, not this project's extension topology.

### Chrome on iOS

Google's Chrome Web Store help currently says extensions/themes can only be used on computers; "Add to Desktop" from a phone installs for the desktop later. So **Chrome iOS is not an extension deployment route**. A normal webpage/PWA, Share extension, Shortcut, or native app still works independently of the browser.

### Cross-app surfaces

For "use this from almost any application," the highest-value native front doors are:
- Share extension for selected/shareable content;
- Shortcuts/App Intents for semantic system operations;
- optional custom keyboard for text-field-only interactions.

App Intents are particularly important because Apple defines them as app-specific actions made available to Siri, Shortcuts, Apple Intelligence and other system experiences. They are the cleaner long-term bridge from a native classifier service to the rest of iOS.

## 9. Foundation Models/Core AI: long-term native bridge

iOS 27's Foundation Models framework materially changes the architecture. Apple now says its `LanguageModel` abstraction can represent the system model, Private Cloud Compute, Core AI, MLX, or another local/server provider. `LanguageModelExecutor` is explicitly the bridge to the actual local inference engine or server API.

Sources:
- [Bring an LLM provider to Foundation Models](https://developer.apple.com/videos/play/wwdc2026/339/)
- [LanguageModel](https://developer.apple.com/documentation/foundationmodels/languagemodel)
- [LanguageModelExecutor](https://developer.apple.com/documentation/foundationmodels/languagemodelexecutor)
- [Meet Core AI](https://developer.apple.com/videos/play/wwdc2026/324/)

A Laya-like classifier is not naturally a token-streaming language model, so wrapping it as a `LanguageModel` may be semantically awkward unless the provider adapter maps typed decision requests into the framework's transcript/output conventions. An **App Intent such as `EvaluateDecisionSchema` may be cleaner initially**. The Foundation Models provider route becomes more valuable when one app wants to compose the classifier alongside generative models and Dynamic Profiles.

## 10. ChatGPT surfaces

The cleanest integration is not to run the model secretly inside ChatGPT's model process. It is to expose the classifier as a **tool**.

OpenAI's current plugin platform packages skills and MCP servers, with optional UI. A remote MCP server can expose narrow tools such as:
- `decision.evaluate`
- `schema.elevate`
- `classifier.feedback`
- `training_case.append`

Sources:
- [Build for ChatGPT](https://developers.openai.com/chatgpt)
- [Plugins](https://developers.openai.com/plugins)
- [Plugin quickstart](https://developers.openai.com/plugins/quickstart)

This is ideal for a server-hosted Laya/Jev/GLiClass service. A classifier running only on an iPhone cannot be directly reached by ChatGPT's cloud execution without an authorized bridge. The phone-first options are therefore:
1. ChatGPT → user opens/approves a Shortcut/App Intent handoff;
2. ChatGPT plugin/MCP → durable control plane → iPhone worker;
3. eventual native app plus system surfaces, with ChatGPT remaining the planner.

A plugin UI is also an interesting **research** place to attempt client-side ONNX inference, but the platform docs do not promise WebGPU, memory lifetime or model caching in every ChatGPT UI/webview. Treat it as an experiment, not a supported deployment assumption.

## 11. Research questions this opens

- How small can the state/question representation become before accuracy falls?
- Does a domain-specialized Laya beat GLiClass zero-shot once real workflow labels exist?
- When does hierarchical GLiClass-style routing outperform Laya's fixed option head?
- Can a frontier teacher improve calibration by emitting soft labels, or does it merely transfer teacher overconfidence?
- What combination of entropy, margin, OOD detection and postcondition failure best predicts when frontier escalation is worth its cost?
- Can the same classifier checkpoint serve notification, Share Sheet and onscreen contexts after normalizing them into one semantic state?
- Is Safari WebGPU startup/lifecycle overhead larger than the classifier forward pass?
- Is a native App Intent decision service a better universal iOS primitive than wrapping a non-generative classifier as a Foundation Models `LanguageModel`?
- Can an action/capability catalog itself be dynamically shortlisted by embeddings before a typed decision pass?

See [Adaptive Capture Router](../../examples/adaptive-capture-router/) for the first concrete architecture example.
