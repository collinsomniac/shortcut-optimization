# Capability stack: composing Shortcuts into an agent harness

Status: architecture synthesis based on documented platform surfaces and external projects. This is a design map, not an implemented harness.

## One stack, several execution authorities

A future harness becomes easier to reason about if capabilities are separated by semantics rather than by app. The planner should not need to know whether a particular implementation is an Apple action, JavaScript, a shell command or a model call.

| Semantic capability | Lowest-level candidates | Why it matters |
|---|---|---|
| `context.collect` | Shortcut input, Share Sheet, Receive What's On Screen, notification/screenshot automation | Normalize surrounding user/device context before reasoning |
| `state.get` / `state.set` | Shortcuts Storage/global values, files, optional Data Jar | Durable memory without forcing a remote database |
| `decision.evaluate` | If/Choose from Menu/rules, later Laya | Bounded decisions should not default to free-form generation |
| `model.generate` | Use Model, local provider, wllama, remote API | Open-ended interpretation/generation when needed |
| `app.invoke` | native Shortcuts actions and App Intents | Prefer semantic app actions to UI coordinates |
| `web.request` | Get Contents of URL + Dictionary/JSON | Typed service/API access |
| `web.dom` | Run JavaScript on Webpage | Read or modify the current Safari page when a web API is unavailable |
| `shell.exec` | a-Shell Execute Command / WASM ecosystem | File transforms and CLI-style work beyond stock actions |
| `shortcut.run` | Run Shortcut / URL schemes | Composition and modular reuse |
| `user.confirm` | Ask for Input, Choose from Menu, Show Alert | Preserve authority at irreversible/ambiguous boundaries |
| `result.verify` | typed return envelope, artifact/state checks | Distinguish attempted launch from completed work |

Apple documents web API calls with GET/POST/PUT/PATCH/DELETE and JSON request bodies in [Get Contents of URL](https://support.apple.com/guide/shortcuts/request-your-first-api-apd58d46713f/ios), JSON as dictionaries/lists in [Using JSON](https://support.apple.com/guide/shortcuts/use-json-apd0f2e057df/ios), URL schemes in [Intro to URL schemes](https://support.apple.com/guide/shortcuts/intro-to-url-schemes-apd621a1ad7a/ios), and Safari scripting in [Run JavaScript on a webpage](https://support.apple.com/guide/shortcuts/run-javascript-on-a-webpage-apdb71a01d93/ios). a-Shell documents Shortcuts actions for Execute Command, Put File and Get File in its [maintainer README](https://github.com/holzschu/a-shell#shortcuts).

## Apple-native layers should stay distinct

### 1. Shortcuts

Shortcuts is the user-facing workflow/dataflow layer: typed action outputs, variables, lists, dictionaries, conditionals, repeat loops, filtering, prompts, triggers and app actions. iOS 27 additionally brings automations into the editor and Apple documents new trigger/context surfaces in [What's new in Shortcuts](https://developer.apple.com/videos/play/wwdc2026/310/).

### 2. App Intents

App Intents is the semantic capability surface apps expose to system experiences such as Shortcuts, Siri and Spotlight. A future harness should prefer these intent/entity contracts over simulated taps whenever an app exposes them. Apple's [App Intents documentation](https://developer.apple.com/documentation/AppIntents) is the primary reference; [App Intents Testing](https://developer.apple.com/documentation/AppIntentsTesting) is notable because it exercises intents/entities/queries out of process, closer to how system clients invoke them.

### 3. Foundation Models and Core AI

These are native app-development layers, not ordinary Shortcut actions. In iOS 27-era Foundation Models, Apple documents the `LanguageModel` protocol plus `LanguageModelExecutor` for integrating a provider, including local or server models, while Dynamic Profiles can change model, instructions and tools within a session. See [Bring an LLM provider to Foundation Models](https://developer.apple.com/videos/play/wwdc2026/339/) and [Build agentic app experiences with Foundation Models](https://developer.apple.com/videos/play/wwdc2026/242/).

Core AI provides model conversion/optimization and an on-device Swift runtime across Apple silicon. Apple's [Meet Core AI](https://developer.apple.com/videos/play/wwdc2026/324/) explicitly positions a Core AI language model as usable through Foundation Models. This creates a plausible later bridge for a custom local model provider; it does not mean a Shortcut can directly load any arbitrary model today.

## The composition rule

Prefer a semantic escalation ladder:

1. direct native action or deterministic expression;
2. deterministic branch/filter/lookup;
3. bounded learned decision if evidence supports it;
4. local generative model;
5. Apple/cloud or third-party remote model;
6. explicit user decision when risk or ambiguity remains.

This is both an efficiency strategy and a reliability strategy. An optimizer can later treat each implementation as a candidate carrying costs such as latency, memory, energy, quota, monetary cost, network dependency, privacy exposure, determinism and expected error.

## A candidate capability envelope

A portable tool call should eventually be describable with fields such as capability ID, schema version, request ID, typed inputs, allowed side effects, permission requirements, timeout, idempotency, implementation candidates and evidence level. The caller should receive a typed status such as proposed, launched, permission_denied, canceled, timed_out, executed or verified_output.

This extends the bounded action loop in [agent harness](../agent-harness.md). It deliberately avoids giving the planner arbitrary URL schemes, file paths, shell text or action identifiers supplied by untrusted content.

## Compound patterns worth researching

- **Context → decision → action:** notification/screenshot/onscreen context becomes a dictionary, rules or Laya choose a bounded route, then an App Intent or Shortcut performs it.
- **Capture → enrich → store:** Share Sheet content is parsed locally, optionally enriched by a model, then persisted in Storage/files and later recalled.
- **API → local transform → app:** Get Contents of URL fetches structured data, a-Shell or deterministic actions transform it, and an app action writes the result.
- **Fast/slow model pair:** a classifier handles ordinary routing; only ambiguous or generative cases activate a larger model.
- **Planner → skill → receipt:** a conversational planner selects a versioned Shortcut skill, user/device authorizes execution, and a typed result comes back before the planner continues.
- **Generated workflow → compiler pass:** Apple's natural-language Shortcut builder supplies a draft, while a later optimizer replaces avoidable model/network operations with cheaper deterministic equivalents and verifies semantic preservation.

These combinations are research hypotheses. Keep each underlying documented capability separate from the inferred value of combining them.