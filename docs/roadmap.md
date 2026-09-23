# Roadmap and acceptance gates

The [ecosystem comparison](ecosystem.md) favors reusing authoring/validation tooling. The [next experiments](next-experiments.md) prioritize preservation and install receipts, using synthetic specimens rather than a personal collection.

The [research landscape](research-landscape.md) now adds model and subscription work. These are optional tracks after the basic handoff; their benchmarks must use the same fixture and target device before choosing a runtime.

## 1. Establish the real handoff

Release SO Echo from an Apple-device export. Verify installation, text fidelity, ChatGPT/Safari launch, user cancellation, and explicit return to chat. Pass ASCII, emoji, multiline text, ampersands, literal percent signs, and JSON. Record failures by client/build.

**Done when:** a newcomer can install it, run a fixture, and return a matching result without recreating actions.

## 2. Explain the builder boundary

Run the native/third-party creation/edit matrix. Inspect before/after graphs and execute fixtures. Publish a short compatibility table with exact actions and builds.

**Done when:** recommendations describe reproducible conditions, including failures, rather than “third-party support works/doesn't work.”

## 3. Add local memory

Prototype the same get/put interface with Native Storage and a JSON-file adapter. Test no network, restart, simultaneous invocations, export/restore, and data exposure when sharing. Escalate to SQLite only for a requirement the simple backends cannot meet.

**Done when:** state survives the stated lifecycle and failures cannot silently corrupt it.

## 4. Make discovery useful

Populate the agent catalog only with real installation links and evidence. Add filters for dependencies, offline behavior, permissions, and evidence level. A launch is not a completed task.

## 5. Publish the documentation

Use GitHub Pages for the documentation and explicit launch links. Begin with this Markdown collection; add an interactive catalog once actual packages exist. See [Pages preparation](pages.md).

Future: vetted compilation/signing, installer-assisted organization, browser result callbacks, and a browser database. These need experiments before architecture commitments.

## Parallel research gates

- Compare a native rule/If decision with a Laya classification adapter on a labeled, redacted fixture. Check confusion, confidence calibration, abstention, cold start, and battery as well as latency; do not expose this as a universal router before task-specific evaluation.
- Measure one small browser GGUF before trying Gemma 4 E4B; test iOS Safari tab survival, first download, cache, peak memory, prompt and decode time, WebGPU versus WASM, and multi-thread availability on the actual Pages origin.
- Run an agent action loop only after SO Echo produces an explicit correlated result. Add read-only capabilities first, then scoped writes with permission and a reversible outcome.
