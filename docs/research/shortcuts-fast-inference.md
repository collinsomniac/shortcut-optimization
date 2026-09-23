# Sub-second decision inference from Shortcuts

Reviewed 2026-09-23. Goal: determine how directly a Shortcut can invoke a Jev/Laya/GLiClass/SetFit-style local classifier and receive typed output. This is a deployment map, not a measured latency claim.

## Short answer

**Sub-second warm classifier calls are technically plausible from a Shortcuts-based harness, but the cleanest route is a native App Intent backed by a bundled local model.**

Shortcuts itself does not expose a general-purpose action for loading arbitrary ONNX/Core ML checkpoints.

| Route | Generic Shortcut? | Background? | Hot-loop suitability | Assessment |
|---|---:|---:|---:|---|
| Native app + App Intent + local model | yes | yes, if supported | best | preferred |
| Safari page/PWA + Run JavaScript on Webpage | active Safari webpage required | page context | good inside page, poor if crossing Shortcuts every step | excellent prototype |
| Safari Web Extension + JS/native extension | Safari-specific | extension lifecycle | good browser-local | strong browser route |
| Scriptable/a-Shell/Pyto action | provider-specific | provider-specific | uncertain | useful experiments |
| URL/x-callback helper | yes | app handoff | poor repeated latency | fallback |
| remote HTTP | yes | yes | network-limited | useful cloud/Jev route |

## Route A — background App Intent

Apple's current App Intents API exposes `supportedModes`, including a `background` mode that runs an action entirely in the background. The system resolves parameters and then calls the intent's `perform()` method, which returns the result.

Sources:
- [AppIntent supportedModes](https://developer.apple.com/documentation/appintents/appintent/supportedmodes)
- [Creating your first App Intent](https://developer.apple.com/documentation/appintents/creating-your-first-app-intent)
- [AppIntent perform](https://developer.apple.com/documentation/AppIntents/AppIntent/perform%28%29)

A future helper app can conceptually expose:

~~~swift
struct EvaluateDecisionIntent: AppIntent {
    static var title: LocalizedStringResource = "Evaluate Decision"
    static var supportedModes: IntentModes = .background

    @Parameter var stateJSON: String
    @Parameter var schemaJSON: String

    func perform() async throws -> some IntentResult {
        // invoke bundled decision runtime and return typed output
    }
}
~~~

The exact result/model code is intentionally omitted until implementation validation.

### Why this is the strongest design

- To Shortcuts it behaves like a normal semantic action.
- It can run without foregrounding the app when the work fits background mode.
- The app can own model weights and preprocessing.
- The same runtime can later back App Intents, a Share Extension, Safari extension, and the app itself.
- The Shortcut can immediately branch on returned typed output.

Potential runtimes include Core AI/Core ML conversion or another native App-Store-compatible runtime. Conversion and latency for Laya/GLiClass remain experiments.

## Route B — Safari + Run JavaScript on Webpage

Apple documents several useful properties of this Shortcuts action:
- input must be an **active Safari webpage**;
- the shortcut is launched from the Safari share sheet / supported Safari controller;
- JavaScript can finish asynchronously;
- `completion(result)` returns any JSON-compatible value directly into Shortcuts;
- the action has a time limit and should complete quickly.

Primary source:
[Run JavaScript on Webpage](https://support.apple.com/guide/shortcuts/intro-to-the-run-javascript-on-webpage-action-apd218e2187d/ios).

Safari 26 ships WebGPU on iOS, and WebKit explicitly lists ONNX Runtime and Transformers.js among frameworks working with Safari WebGPU:
[WebKit Safari 26](https://webkit.org/blog/17333/webkit-features-in-safari-26-0/).

This makes the following research route plausible:

~~~text
classifier/game PWA already loaded and warm
        ↓
Run JavaScript on Webpage
        ↓
observation / page-local classifier
        ↓
completion({decision, probabilities, timing})
        ↓
Shortcut Dictionary
~~~

The crucial limitation is that this is **not a generic background JavaScript action**. It requires a Safari webpage. Even if inference is 20–50 ms, Share Sheet / Shortcuts transitions may dominate end-to-end latency.

## Route C — Safari Web Extension

Safari Web Extensions can modify/read page content and communicate with a native app extension.

Sources:
- [Safari extensions](https://developer.apple.com/safari/extensions/)
- [Native messaging](https://developer.apple.com/documentation/safariservices/messaging-between-the-app-and-javascript-in-a-safari-web-extension)

Possible classifier placement:

~~~text
page → extension JS → browser ONNX/WebGPU
~~~

or:

~~~text
page → extension background JS
     → nativeMessaging
     → native app extension/model runtime
~~~

The second design could share a model/runtime with App Intents.

## Route D — helper scripting apps

Scriptable, a-Shell and Pyto already expose programmable work to Shortcuts and may be useful for tiny embedding/classification prototypes.

For repeated neural inference, however, interpreter/process startup and model loading may dominate. They remain worth measuring, especially for very small SetFit-style models, but should not be the default architecture before measurement.

## Hot loop versus orchestration loop

### Hot loop
~10–100+ decisions/sec:
- game policy;
- continuous interaction;
- controller response.

Keep this **inside one resident page/process**:
- Web Worker/browser page;
- native app;
- another persistent local runtime.

### Orchestration loop
~0.1–5 decisions/sec:
- Share Sheet routing;
- notification handling;
- workflow action choice;
- error/recovery decisions;
- selecting another Shortcut/App Intent.

This is where Shortcuts + background App Intent can plausibly excel.

Do not build a game loop that repeatedly bounces:

`Safari → Share Sheet → Shortcut → helper → Shortcut → Safari`.

That mainly measures process/UI switching.

## Whole-call benchmark

Eventually measure:

~~~text
Shortcut input dictionary
   ↓
Evaluate Decision App Intent
   ↓
preprocess
   ↓
model inference
   ↓
calibration/schema decode
   ↓
Intent result
   ↓
Shortcut branches
~~~

Record cold and warm latency, p50/p95 over many calls, model-only versus end-to-end time, load residency, background behavior, memory, thermal state, schema size, and number of batched questions.

Useful experimental bands, not promises:
- <100 ms warm: excellent;
- 100–300 ms: highly useful;
- 300–800 ms: useful but less reflexive;
- >1 s: no longer especially System-One-like at the workflow level.

## CourierGrid integration

The browser example exposes:

~~~js
window.courierGrid.getObservation()
window.courierGrid.getFullState() // oracle/debug only
window.courierGrid.getAvailableActions()
window.courierGrid.step("forward")
window.courierGrid.reset()
~~~

A future Safari Shortcut can do one complete transport step:

~~~js
const obs = window.courierGrid.getObservation();
// Later: const decision = await localClassifier(obs)
const result = window.courierGrid.step("forward");
completion({obs, result});
~~~

Autonomous high-frequency play should stay page-local. The Shortcut route tests typed transport and integration.

## Conclusion

For "**invoke a zero/few-shot classifier from any Shortcut and get a typed result well under a second**," prioritize:

1. native helper app;
2. bundled/converted decision model;
3. background App Intent;
4. stable schema input/output;
5. warm model caching where OS lifecycle permits;
6. Shortcuts as orchestrator, not model host.

Use Safari WebGPU as the strongest no-native-app prototype and browser-specific deployment surface.
