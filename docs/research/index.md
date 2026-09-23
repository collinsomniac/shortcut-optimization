# Research home base

Snapshot: 2026-09-22/23. This directory is the durable research layer for Shortcut Optimization. The active phase is intentionally research-first: collect capabilities, examples, constraints, and composition patterns before committing to a runtime or beginning device benchmarks.

Read this page before treating a conversation summary as project state. Use [research methodology](methodology.md) to add findings consistently and [capability record template](capability-record-template.md) for substantial new surfaces. Claims still follow [the evidence policy](../evidence.md): documented, artifact-inspected, reproduced, reported, hypothesis, or unknown.

## What the project is becoming

The repository began as a phone-first collection of reusable Shortcuts and trustworthy handoff patterns. The research now supports a broader thesis: Apple Shortcuts can act as a typed workflow and execution layer inside a hybrid agent harness, while deterministic actions, app intents, specialized decision models, generative models, browser/shell tools, and cloud services are selected only where each adds value.

A useful north-star is not unrestricted UI control. It is a versioned capability system in which a planner can discover narrow tools, pass typed state, receive explicit results, and escalate from cheap deterministic computation to probabilistic or remote computation only when necessary. Frontier escalation should itself be optional and learnable rather than a mandatory inference stage. See [Capability stack](capability-stack.md), [System-One decision models](system-one-decision-models.md), and [CourierGrid benchmark](game-policy-benchmark.md).

## Research map

| Layer | What we are studying | Representative surfaces | Evidence now |
|---|---|---|---|
| Workflow language | typed dataflow, branching, loops, filtering, prompts | Shortcuts variables, List, If, Repeat, Find/Filter | documented |
| App capability layer | app-defined actions, entities, queries and system integrations | App Intents, Shortcuts actions, Siri/Spotlight entry points | documented; compatibility varies by app |
| Context and transport | move state into/out of workflows | Share Sheet, onscreen input, URL schemes, x-callback-url, Get Contents of URL, JSON | documented; client round trips untested here |
| Extension providers | typed third-party actions, code runners, remote execution | Actions, Scriptable, a-Shell, Pyto, Toolbox Pro, Pushcut | provider-documented; project recipes not reproduced |
| Web and shell extension | arbitrary-but-bounded programmable work | Run JavaScript on Webpage, a-Shell commands/WASM/files | documented; project recipes not reproduced |
| Persistent state | context across invocations | Shortcuts Storage/global values, files, Data Jar candidates | documented/reported depending on backend |
| Fast learned decisions | bounded classification, scoring, zero-shot labels and calibration | Jev, Laya, GLiClass, SetFit-style specialists | model/provider-documented; no project phone result |
| Generative inference | interpretation, synthesis, planning | Use Model, Gemma, wllama, remote providers | documented/model-documented; no project benchmark |
| Native AI integration | bring custom/local/remote models into Apple model sessions | Foundation Models LanguageModel/Executor, Dynamic Profiles, Core AI | documented for app developers; no project app |
| External control plane | durable coordination, builds, training, optional inference | GitHub, Supabase, Colab, OpenRouter | plan-documented; account/device measurements separate |

Primary platform references include Apple's [Shortcuts User Guide](https://support.apple.com/guide/shortcuts/welcome/ios), [WWDC26 Shortcuts session](https://developer.apple.com/videos/play/wwdc2026/310/), [Foundation Models provider session](https://developer.apple.com/videos/play/wwdc2026/339/), [agentic Foundation Models session](https://developer.apple.com/videos/play/wwdc2026/242/), and [Core AI overview](https://developer.apple.com/videos/play/wwdc2026/324/). The broader source inventory is in [source ledger](source-ledger.md).

## Current architectural hypotheses

1. **Use the smallest adequate primitive.** A deterministic Shortcuts action should beat an LLM for known arithmetic, date logic, filtering, fixed transformations and direct app actions. A specialized decision model is interesting when the output is bounded but semantics are fuzzy. A generative model earns its cost only when the output space or reasoning really requires generation.
2. **Treat model routing as part of the program.** Rules, typed decision models, zero-shot classifiers, Apple on-device models, local generative models and cloud models can be interchangeable implementations behind typed contracts rather than independent demos. See [System-One decision models](system-one-decision-models.md) and [Model routing](model-routing.md).
3. **Treat a Shortcut as a program, not a screenshot.** A useful optimizer eventually needs a graph/IR view of actions, typed edges, side effects, permissions and costs. See [Shortcut as program](shortcut-as-program.md).
4. **Separate planner, decision, executor and transport.** A conversation agent can plan without pretending it directly controls iOS; Shortcuts/App Intents remain execution authorities, while explicit receipts close the loop.
5. **Compose capabilities into skills.** The most valuable workflows are likely to combine context collection, state, bounded decisions, app/API actions, verification and recovery rather than expose hundreds of raw actions directly to a model. See [Use-case atlas](use-cases.md) and [Extension ecosystem](extension-ecosystem.md).

These are hypotheses and design directions, not device-verified performance claims.

## How future agents should use this repository

Start with [agents/research-brief.md](../../agents/research-brief.md), then this page, [research methodology](methodology.md), [evidence policy](../evidence.md), and the relevant topical guide. Prefer primary Apple/developer/model documentation; use community posts as leads and examples. Date release-specific findings. Preserve contradictions instead of silently resolving them. Add a source once, then cross-link it rather than repeatedly copying claims into unrelated files.

During the current research phase, optimize for breadth plus traceability: discover new capability surfaces, identify interfaces between them, and turn promising combinations into explicit hypotheses. Do not convert a plausible architecture into a claim that it works on the target phone until a later experiment records it.

## Questions that organize the next research passes

- Which Shortcuts action types and App Intent entity types form the most useful stable semantic vocabulary for an agent?
- How much of shortcut creation, refinement, organization and export can be composed from Shortcuts itself on released iOS 27, versus hidden/prototype actions or macOS-only tooling?
- Can Jev/Laya-style typed decision models become reusable learned branch nodes, and when should GLiClass/SetFit-style zero-shot or distilled classifiers be preferred?
- Can a frontier model act mainly as schema teacher, choice-elevation engine and active-learning labeler while a small classifier handles the hot loop?
- Can the local policy learn `frontier_assist` as a cost-sensitive defer action from counterfactual outcomes instead of relying on a permanent cascade or hard confidence threshold?
- Can a background App Intent make a warm typed classifier feel like a native sub-second Shortcuts primitive?
- Which local model runtime boundary is best for each workload: browser ONNX/WebGPU, wllama, a native Core AI model, or a remote provider?
- Which workflows become substantially more capable when persistent Storage, notification/screenshot triggers, onscreen input and model sessions are combined?
- What representation would let an optimizer reason about latency, energy, quota, privacy, determinism, permissions and expected error without knowing every app implementation?
- Which existing community tools already solve compilation, signing, catalogs, updates or action metadata well enough that this project should integrate instead of rebuild?
- Can machine-readable third-party action catalogs be normalized into a portable capability ontology that future agents can retrieve from safely?

Testing is deliberately deferred, but every research note should make eventual falsification easier.