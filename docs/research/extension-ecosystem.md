# Extension ecosystem: third-party capability providers

Status: research map. These apps expand what Shortcuts can express, but each adds a dependency and its own lifecycle/version/permission boundary. The goal is not to require all of them; it is to understand which capabilities are already packaged well enough that a future harness should discover or wrap them instead of rebuilding them.

## Why this matters for an agent harness

Third-party Shortcuts actions behave like small semantic APIs. They often expose typed parameters and outputs directly inside the workflow graph, which is preferable to screen-coordinate automation. A future capability catalog can therefore normalize selected third-party actions behind stable project contracts while retaining the app/action provenance.

An especially useful precedent is Sindre Sorhus's [Actions](https://sindresorhus.com/actions): the current catalog advertises 180+ extra actions and explicitly publishes [AI-readable source data](https://gist.githubusercontent.com/sindresorhus/fbba65a774fb9da915e624807a02a6d2/raw/7be21a65977b6dd82d1a6cc34be4476df057ea06/actions.md) containing action descriptions, parameter types and return types. That is close to the metadata format this project eventually needs for capability discovery and retrieval.

## Candidate providers

| Provider | Documented surface | Research value | Boundary/caution |
|---|---|---|---|
| [Actions](https://sindresorhus.com/actions) | 180+ Shortcuts actions across data, URLs, device state, files, networking, UI helpers and more; AI-readable action source data | Excellent corpus for typed capability discovery; includes useful primitives such as atomic Counter, Manage Shortcut Lock, Keychain, extended HTTP, JSONPath and deterministic transforms | Third-party dependency; its own page notes actions can temporarily fail to appear due to an iOS/macOS issue; some platform gaps listed by the app may become outdated as Apple adds native features |
| [Data Jar](https://datajar.app/) | JSON-compatible data store for Shortcuts, offline with iCloud synchronization | Mature state backend/reference implementation for dictionaries/lists and cross-shortcut data | Native iOS 27 Storage may replace it for simpler cases; Data Jar remains useful where inspection/iCloud file integration or established workflows matter |
| [Scriptable](https://docs.scriptable.app/) | JavaScriptCore automation environment; Shortcut parameters can be text/list/dictionary/file and scripts can return text/number/boolean/dictionary/file path; URL scheme/universal-link execution | Programmable adapter between Shortcuts and JS libraries/services; explicit typed input/output makes it skill-friendly | Scriptable is JavaScript, not browser DOM; memory/lifecycle constraints apply and some scripts may need to run in the app |
| [a-Shell](https://github.com/holzschu/a-shell#shortcuts) | Execute Command, Put File and Get File actions; Unix-like tools, scripting and WASM command ecosystem | Strong CLI/file-processing executor and bridge to existing command-line patterns | Extension vs full-app execution differs; dynamic native extensions are constrained; dependency must be declared |
| [Pyto](https://pyto.app/) | Python 3.10/C/C++ environment on iOS with scientific packages and Shortcuts support for running scripts/custom code | Rich Python/scientific/image-processing option for workflows whose logic is awkward in visual actions | Paid app/current compatibility must be rechecked before relying on it; heavier runtime than a narrow native action |
| [Toolbox Pro](https://toolboxpro.app/) | Current site advertises 130 Shortcuts actions including OCR, NFC, global variables, file/device utilities and advanced UI/notification helpers | Broad precedent for typed extension actions and app-like Shortcut UI; useful comparison for what should remain a dependency rather than project code | Some functions overlap newer Apple/Actions features; action coverage/version behavior should be checked per device |
| [Pushcut Automation Server](https://www.pushcut.io/support/automation-server) | Dedicated always-on iOS device can expose installed shortcuts/HomeKit scenes through schedules, API/webhooks and response handling | Important remote-execution precedent: Shortcuts can become a network-addressable executor if a dedicated device is acceptable | Requires a dedicated iOS server device, internet and provider/service assumptions; sequential queue/timeouts and plan features matter |
| [AI Actions](https://sindresorhus.com/ai-actions) | Shortcuts actions for OpenAI/Anthropic and additional providers such as Ollama/Groq; user API keys stored in Keychain | Existing provider-adapter precedent and secret-handling pattern | ChatGPT/Anthropic subscriptions do not imply API credit; cloud/provider costs and privacy remain separate |

## Actions as a capability-catalog precedent

The Actions source data is notable beyond the app itself. Entries include human descriptions, typed parameters, typed return values, caveats and platform restrictions. Examples visible in the current catalog include:

- `Counter`: atomic counter intended for races, progress and rate limits;
- `Manage Shortcut Lock`: prevents multiple instances from running simultaneously;
- `Get Contents of URL (Extended)`: returns fuller HTTP response details and timeout control;
- `Keychain`: stores sensitive values in the device keychain;
- JSONPath get/set helpers;
- device/thermal/storage/connectivity predicates;
- deterministic list, URL, text and file transforms.

This suggests a research methodology: ingest third-party action metadata into a normalized **capability ontology**, then compare each action against Apple's native equivalent and our own semantic vocabulary. The project should not mirror hundreds of actions one-for-one. It should identify reusable capabilities such as `state.atomic_increment`, `runtime.lock`, `secret.get`, `http.request`, `file.transform`, `device.query`, or `ui.choose` and record which providers can implement them.

## Native-versus-extension replacement analysis

iOS 27 changes the dependency calculus. Apple now documents persistent/global Storage and notification/screenshot automation additions in [What's new in Shortcuts](https://developer.apple.com/videos/play/wwdc2026/310/), reducing the need for some older third-party workarounds. A useful research table for each extension feature is therefore:

| Question | Meaning |
|---|---|
| Is there a native equivalent now? | Prefer the native path when capability/behavior is adequate and portability matters |
| Does the extension add a semantic property? | Atomicity, richer return metadata, secure storage, timeout, UI, scheduling, code execution, etc. may justify it |
| Can the action execute in the background? | App-switch requirements can dominate UX and automation reliability |
| Is its schema discoverable? | Typed metadata makes it far easier for agents/builders to use safely |
| Can it be distributed without secrets/personal state? | Shared artifacts must not embed credentials or private data |
| What is the failure mode if the app is absent/offloaded? | Dependency checks and recovery belong in the capability contract |

## Remote execution and scheduling

Pushcut is a useful architectural comparison even if it never becomes a project dependency. Its Automation Server makes a dedicated iOS device network-addressable through an API, queues shortcut runs sequentially and can return structured responses. That demonstrates one existing way to turn iOS/Shortcuts into a remote worker, at the cost of an always-on device and service dependency.

Community reports around iOS 27 also combine the new notification automation trigger with Actions-scheduled notifications to approximate dynamically scheduled work. See [reported scheduling pattern](https://www.reddit.com/r/shortcuts/comments/1u49od2/theres_finally_a_reliable_way_to_schedule/). Treat this as a reported composition, not a project guarantee; Apple's released behavior and native scheduling options should be checked before adopting the workaround.

## Implication for future agents

Future agents should be able to answer two different questions:

1. **What semantic capability is needed?** e.g. atomic counter, secure secret, arbitrary JavaScript, Python/scientific transform, remote iOS execution.
2. **Which implementation is currently best under this user's installed apps and constraints?** native Shortcuts, Actions, Scriptable, a-Shell, Pyto, Toolbox Pro, Pushcut, or another provider.

That separation lets the harness remain stable while providers evolve. It also makes third-party dependencies explicit instead of burying them inside a generated workflow.