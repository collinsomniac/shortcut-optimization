# Roadmap and acceptance gates

## 0. Research consolidation — active

The project is currently in a deliberate research-first phase. Before running the phone/runtime experiments below, make this repository the durable source of truth for relevant Shortcuts surfaces, App Intents, Apple Intelligence/Foundation Models/Core AI, local/browser inference, shell/web extensions, existing compilers/catalogs, community examples and optional compute/control-plane services.

Work in this phase should:

- widen the source-backed capability map rather than prematurely selecting one implementation;
- distinguish documented primitive, first-person/community report and project hypothesis;
- capture how multiple primitives might compound into workflows/skills;
- identify existing open-source tools that should be integrated or learned from rather than rebuilt;
- turn promising architectures into explicit questions and eventual falsification criteria;
- keep volatile OS/model/plan facts dated and traceable through the [research source ledger](research/source-ledger.md);
- improve the future-agent handoff in [agents/research-brief.md](../agents/research-brief.md).

**Done when:** the major architecture choices have a well-cited comparison, unknowns are explicit, representative use cases are mapped to candidate primitives, and entering the experiment phase no longer requires reconstructing research from old conversations.

See [research home base](research/index.md), [capability stack](research/capability-stack.md), [model routing](research/model-routing.md), [Shortcut as program](research/shortcut-as-program.md), and [use-case atlas](research/use-cases.md).

The execution phases below are intentionally deferred, not canceled.

## 1. Establish the real handoff

Release SO Echo from an Apple-device export. Verify installation, text fidelity, ChatGPT/Safari launch, user cancellation and explicit return to chat. Pass ASCII, emoji, multiline text, ampersands, literal percent signs and JSON. Record failures by client/build.

**Done when:** a newcomer can install it, run a fixture and return a matching result without recreating actions.

## 2. Explain the builder boundary

Run the native/third-party creation/edit matrix. Inspect before/after graphs and execute fixtures. Publish a short compatibility table with exact actions and builds.

**Done when:** recommendations describe reproducible conditions, including failures, rather than “third-party support works/doesn't work.”

## 3. Add local memory

Prototype the same get/put interface with Shortcuts Storage/global values and a JSON-file adapter; compare other backends only where they add a concrete property. Test offline behavior, restart, simultaneous invocations, export/restore and data exposure when sharing.

**Done when:** state survives the stated lifecycle and failures cannot silently corrupt it.

## 4. Add bounded decision/model adapters

Compare a native rule/If decision with a task-specific Laya adapter on a labeled fixture. Check accuracy, confusion, calibration, abstention, cold start, battery and lifecycle overhead, not only inference latency. Separately measure a small browser generative model before attempting Gemma 4 E4B.

**Done when:** the repository can explain which decision/generation class deserves which runtime on the target device using measured evidence.

## 5. Make discovery useful

Populate the agent catalog only with real installation links and evidence. Add filters for dependencies, offline behavior, permissions, model/runtime needs and evidence level. A launch is not a completed task.

## 6. Publish the documentation/catalog

Use GitHub Pages for the documentation and explicit launch links. Begin with this Markdown knowledge base; add an interactive catalog once actual packages exist. See [Pages preparation](pages.md).

## Later architecture tracks

- Canonical Shortcut graph/IR and structural optimizer passes.
- Vetted compilation/signing and optional macOS build backend.
- Browser result callbacks and durable local web state.
- Native Foundation Models/Core AI provider bridge.
- Agent action loop with correlated receipts, read-only tools first and scoped/reversible writes later.
- Cross-device control plane only where local-first execution cannot satisfy the requirement.

Every later track should inherit the same evidence labels and source/date discipline established during phase 0.