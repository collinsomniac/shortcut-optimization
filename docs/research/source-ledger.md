# Research source ledger

Reviewed 2026-09-22/23. This ledger complements the smaller [core source list](../sources.md). Links are grouped by role so future agents can recover the evidence chain without searching old conversations. A source can document one primitive without proving the project's proposed composition.

## Apple: Shortcuts and app capabilities

| Source | Type | Why it matters |
|---|---|---|
| [Shortcuts User Guide](https://support.apple.com/guide/shortcuts/welcome/ios) | primary | Baseline action/control-flow/input/API/URL documentation |
| [What's new in Shortcuts — WWDC26](https://developer.apple.com/videos/play/wwdc2026/310/) | primary | iOS 27-era automations, Storage/global values, Use Model/transcript features |
| [Apple Intelligence 2026 announcement](https://www.apple.com/newsroom/2026/06/apple-intelligence-brings-powerful-ai-capabilities-into-everyday-experiences/) | primary | Describe a Shortcut creation/refinement |
| [Get Contents of URL](https://support.apple.com/guide/shortcuts/request-your-first-api-apd58d46713f/ios) | primary | HTTP methods and structured request bodies |
| [Using JSON](https://support.apple.com/guide/shortcuts/use-json-apd0f2e057df/ios) | primary | Dictionary/list mapping to JSON |
| [Run JavaScript on a webpage](https://support.apple.com/guide/shortcuts/run-javascript-on-a-webpage-apdb71a01d93/ios) | primary | Safari DOM/script extension surface |
| [Receive What's On Screen](https://support.apple.com/guide/shortcuts/receive-whats-onscreen-apd350ce757a/ios) | primary | Context intake from supported apps |
| [URL schemes](https://support.apple.com/guide/shortcuts/intro-to-url-schemes-apd621a1ad7a/ios) and [x-callback-url](https://support.apple.com/guide/shortcuts/use-x-callback-url-apdcd7f20a6f/ios) | primary | App/Shortcut handoff and return conventions |
| [Share shortcuts](https://support.apple.com/guide/shortcuts/share-shortcuts-apdf01f8c054/ios) | primary | iCloud/file export, audience modes, import questions |
| [App Intents](https://developer.apple.com/documentation/AppIntents) | primary | Semantic actions/entities apps expose to system experiences |
| [App Intents Testing](https://developer.apple.com/documentation/AppIntentsTesting) | primary | Out-of-process intent/entity/query testing surface |
| [AppIntent supportedModes](https://developer.apple.com/documentation/appintents/appintent/supportedmodes) | primary | explicit background/immediate/dynamic/deferred execution modes for App Intents |
| [Run JavaScript on Webpage](https://support.apple.com/guide/shortcuts/intro-to-the-run-javascript-on-webpage-action-apd218e2187d/ios) | primary | active-Safari requirement, async completion, JSON return types and time-limit boundary |
| [Shortcuts URL scheme: open/create/run](https://support.apple.com/guide/shortcuts/open-create-and-run-a-shortcut-apda283236d7/ios) | primary | open app/editor, create blank Shortcut, open/run saved Shortcut by name |
| [Run Shortcut from URL](https://support.apple.com/guide/shortcuts/run-a-shortcut-from-a-url-apd624386f42/ios) | primary | invoke an already-installed Shortcut with text/clipboard input |
| [Apple Shortcuts release notes](https://support.apple.com/121131) | primary | recent native management actions including Create Folder/iCloud Link/Home Screen and Move/Rename |
| [Older Shortcuts release notes](https://support.apple.com/101583) | primary | Create Shortcut, Delete Shortcuts, Open Folder and related management actions |
| [Create a custom shortcut / Describe a Shortcut](https://support.apple.com/guide/shortcuts/create-a-custom-shortcut-apd84c576f8c/ios) | primary | natural-language creation and modification through Apple's builder UI |
| [Shortcuts command-line tool](https://support.apple.com/guide/shortcuts-mac/run-shortcuts-from-the-command-line-apd455c82f02/mac) | primary | macOS list/view/run/sign artifact backend |
| [Safari 26 WebGPU](https://webkit.org/blog/17333/webkit-features-in-safari-26-0/) | primary/WebKit | WebGPU on iOS Safari; explicitly names ONNX Runtime and Transformers.js support |
| [Safari Web Extensions](https://developer.apple.com/documentation/safariservices/safari-web-extensions) | primary | iOS Safari extension packaging, page integration and browser-extension surface |
| [Safari extension native messaging](https://developer.apple.com/documentation/safariservices/messaging-between-the-app-and-javascript-in-a-safari-web-extension) | primary | browser-extension ↔ native app-extension messaging and app-group boundaries |

## Apple: model and agent frameworks

| Source | Type | Why it matters |
|---|---|---|
| [Bring an LLM provider to Foundation Models](https://developer.apple.com/videos/play/wwdc2026/339/) | primary | `LanguageModel` and `LanguageModelExecutor` custom-provider abstraction |
| [Build agentic app experiences with Foundation Models](https://developer.apple.com/videos/play/wwdc2026/242/) | primary | Dynamic Profiles, tools and orchestration patterns |
| [What's new in Foundation Models](https://developer.apple.com/videos/play/wwdc2026/241/) | primary | model/session changes and built-in tool directions |
| [Foundation Models updates](https://developer.apple.com/documentation/updates/foundationmodels) | primary | release-indexed API additions such as DynamicProfile |
| [Meet Core AI](https://developer.apple.com/videos/play/wwdc2026/324/) | primary | on-device model conversion/runtime and Foundation Models bridge |
| [Integrate on-device AI models into your app](https://developer.apple.com/videos/play/wwdc2026/326/) | primary | model discovery, optimization/compilation and deployment workflow |
| [Evaluations framework](https://developer.apple.com/videos/play/wwdc2026/298/) | primary | dataset/metric/judge methodology for probabilistic features |
| [Robust evaluation workflows](https://developer.apple.com/videos/play/wwdc2026/299/) | primary | synthetic data and trajectory/tool evaluation ideas |

## Decision and generative models

| Source | Type | Why it matters |
|---|---|---|
| [TypeSafe: Introducing System One Models & Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev) | primary/provider | Jev framing, typed probabilistic decisions, parallel sampling, launch performance/cost claims and explicit caveats |
| [TypeSafe workflow evals](https://evals.typesafe.ai/) | primary/provider | decomposed workflow examples using noul/choice/score plus deterministic code |
| [TypeSafe OpenAPI](https://api.typesafe.ai/docs) | primary/provider | public typed System One API and schemas |
| [GLiClass](https://github.com/Knowledgator/GLiClass) | upstream/model | dynamic zero-shot labels, hierarchical labels and single-pass classifier alternative |
| [SetFit zero-shot](https://huggingface.co/docs/setfit/how_to/zero_shot) | upstream/framework | synthetic class-name training and published fast classifier comparison |
| [SetFit distillation](https://huggingface.co/docs/setfit/how_to/knowledge_distillation) | upstream/framework | larger-teacher to small-student distillation pattern |
| [Learning to Defer](https://papers.neurips.cc/paper_files/paper/2018/hash/09d37c08f7b129e96277388757530c72-Abstract.html) | research | learned PASS/defer action to an external decision-maker; conceptual basis for optional frontier assistance |
| [FrugalGPT](https://arxiv.org/abs/2305.05176) | research | learned model cascades under cost/quality constraints |
| [Adaptive inference / early exits](https://arxiv.org/abs/2106.05022) | research survey | broader adaptive-compute context for input-dependent inference cost |
| [Laya model card](https://huggingface.co/convaiinnovations/laya) | upstream/model | architecture, typed decisions, latency and benchmark caveats |
| [Laya typed-decisions checkpoint](https://huggingface.co/convaiinnovations/laya-typed-decisions) | upstream/model | fine-tuned benchmark and calibration data |
| [Official Laya TypeScript/browser runtime](https://github.com/NandhaKishorM/laya/blob/main/laya-ts/README.md) | upstream/model runtime | split ONNX encoder/head, browser WebGPU to WASM fallback, export parity checks and event hooks; phone fit remains untested |\n| [Laya training README](https://github.com/NandhaKishorM/laya/blob/main/README.md) | project/community | training recipe and specialization guidance |
| [laya-onnx](https://huggingface.co/Mattepiu/laya-onnx) | independent | ONNX conversion lead |
| [receptron/laya](https://github.com/receptron/laya) | independent | TypeScript/ONNX Runtime implementation lead |
| [mizchi/laya-multilingual-onnx](https://huggingface.co/mizchi/laya-multilingual-onnx) | independent | browser WebGPU parity report/demo lead |
| [ONNX Runtime Web](https://github.com/microsoft/onnxruntime/tree/main/js/web) | upstream/runtime | browser WASM/GPU inference substrate |
| [Gemma 4 overview](https://huggingface.co/blog/gemma4) | publisher/model | E4B architecture/parameter/context overview |
| [Gemma 4 E4B](https://huggingface.co/google/gemma-4-E4B) / [E4B-it](https://huggingface.co/google/gemma-4-E4B-it) | publisher/model | exact model distributions |
| [Unsloth E4B QAT GGUF](https://huggingface.co/unsloth/gemma-4-E4B-it-qat-GGUF) | independent distribution | current quantized artifacts for llama.cpp-style runtimes |
| [wllama](https://github.com/ngxson/wllama) | upstream/runtime | browser llama.cpp WASM/WebGPU, splitting, multimodal/tool calls |
| [Llamas on the Web](https://reeselevine.github.io/llamas-on-the-web/) | research/independent | browser GPU implementation and mobile-memory warnings |
| [iPhone local LLM runtime comparison](https://rockyshikoku.medium.com/local-llm-on-iphone-which-runtime-is-actually-fastest-58096685481e) | first-person benchmark | runtime-dependent E2B speed/memory lead; not E4B/browser proof |
| [WebKit RAM internals](https://www.catchmetrics.io/blog/deep-dive-ram-internals-webkit) | independent analysis | directional browser memory/process-pressure research |


## Sequential-control and game benchmarks

| Source | Type | Why it matters |
|---|---|---|
| [MiniGrid](https://minigrid.farama.org/) | benchmark/framework | lightweight configurable discrete grid worlds with language missions and partial observations |
| [MiniGrid GoToObject](https://minigrid.farama.org/environments/minigrid/GoToObjectEnv/) | benchmark docs | representative 7-action, local-view + mission task structure |
| [LunarLander](https://gymnasium.farama.org/environments/box2d/lunar_lander/) | benchmark docs | established 4-action / 8-state-vector real-time control comparison |
| [BrowserGym](https://github.com/ServiceNow/BrowserGym) | research framework | later bridge from toy browser game to realistic web-agent tasks |

## Extension and artifact tooling

| Source | Type | Why it matters |
|---|---|---|
| [Actions](https://sindresorhus.com/actions) and [AI-readable action data](https://gist.githubusercontent.com/sindresorhus/fbba65a774fb9da915e624807a02a6d2/raw/7be21a65977b6dd82d1a6cc34be4476df057ea06/actions.md) | maintainer | 180+ typed Shortcuts actions and a machine-readable capability-catalog precedent |
| [Data Jar](https://datajar.app/) | developer | JSON-compatible offline/iCloud Shortcuts state backend |
| [Scriptable docs](https://docs.scriptable.app/) / [URL scheme](https://docs.scriptable.app/urlscheme/) | developer | JavaScript runner, typed Shortcut I/O and URL/universal-link invocation |
| [Pyto](https://pyto.app/) | developer | iOS Python/scientific runtime with Shortcuts integration |
| [Toolbox Pro](https://toolboxpro.app/) | developer | large action library, persistent state/UI/file/device precedents |
| [Pushcut Automation Server](https://www.pushcut.io/support/automation-server) | developer | dedicated-device remote Shortcut execution through schedules/API/webhooks |
| [AI Actions](https://sindresorhus.com/ai-actions) | developer | model-provider Shortcuts actions and Keychain-backed user API credentials |
| [a-Shell](https://github.com/holzschu/a-shell#shortcuts) | maintainer | Shortcuts Execute Command/Put File/Get File and mobile shell |
| [a-Shell commands](https://github.com/holzschu/a-Shell-commands) | maintainer | reusable WASM command ecosystem |
| [Shortcuts Playground](https://github.com/viticci/shortcuts-playground-plugin) | maintainer/community | current iOS/macOS 27 ToolKit v78 action catalogs, parameter/enum metadata, validator, golden examples and compiler patterns |
| [shortcuts-generator skill](https://github.com/cranecj/shortcuts-generator/blob/main/SKILL.md) | community | programmatic plist generation + Apple signing precedent |
| [shortcut-lib format notes](https://github.com/findlaywebb/shortcut-lib/blob/main/docs/format.md) | community | reverse-engineered serialized structure |
| [apple-shortcuts](https://github.com/julian-englert/apple-shortcuts) | community/macOS | reverse-engineered macOS Shortcuts SQLite/action extraction and plist build/sign/import research; requires private DB access/Apple CLI and is not an iPhone API |
| [Hidden Generate Shortcut report](https://www.reddit.com/r/shortcuts/comments/1vgk21f/new_shortcut_action_generate_shortcut_from/) | reported/community | prototype self-generation/management lead; not a released API guarantee |

See [extension ecosystem](extension-ecosystem.md) for a comparative synthesis of action providers/code runners and [ecosystem](../ecosystem.md) for Cherri, Shortcuts Playground, Jelly/Open Jellycuts, RoutineHub updater, ScPL and catalog precedents.

## Compute/control-plane resources

| Source | Type | Why it matters |
|---|---|---|
| [Google: Colab joins Google AI plans](https://developers.googleblog.com/colab-is-now-part-of-your-google-ai-plan/) | primary | AI-plan Colab rollout and accelerator access |
| [Google AI plan benefits](https://support.google.com/googleone/answer/14534406?hl=en) | primary | current AI Pro entitlements such as 200 CCUs and developer benefits |
| [GitHub included usage](https://docs.github.com/en/billing/reference/product-usage-included) | primary | Free Actions/Codespaces quotas |
| [GitHub-hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners) | primary | public/private standard runner resources |
| [Supabase billing](https://supabase.com/docs/guides/platform/billing-on-supabase) | primary | Free quotas and current two-active-project Free-plan limit |
| [Supabase custom schemas](https://supabase.com/docs/guides/api/using-custom-schemas) | primary | internal schema compartmentalization and deliberate exposed-schema configuration |
| [Supabase API security](https://supabase.com/docs/guides/api/securing-your-api) | primary | dedicated API schema, explicit grants, RLS, default privilege guidance |
| [Supabase Edge Function limits](https://supabase.com/docs/guides/functions/limits) | primary | CPU/memory/wall-clock boundaries |
| [OpenRouter pricing](https://openrouter.ai/pricing) | primary/provider | current free-model/request surface |
| [OpenAI: ChatGPT vs API billing](https://help.openai.com/en/articles/9039756-billing-settings-in-chatgpt-vs-platform) | primary/provider | ChatGPT subscription and API are separate billing systems |


## ChatGPT/plugin integration

| Source | Type | Why it matters |
|---|---|---|
| [Build for ChatGPT](https://developers.openai.com/chatgpt) | primary/provider | current ChatGPT developer surfaces and MCP/plugin entry point |
| [Plugins](https://developers.openai.com/plugins) | primary/provider | skills + MCP servers + optional UI packaging |
| [Plugin quickstart](https://developers.openai.com/plugins/quickstart) | primary/provider | connecting a remote MCP server and invoking it from ChatGPT Work |
| [Developer mode and MCP apps](https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt) | primary/provider | current account/workspace caveats for custom/full MCP behavior |
| [Chrome Web Store mobile limitation](https://support.google.com/chrome_webstore/answer/1698338?hl=en) | primary/provider | Chrome extensions are not installable on mobile devices, including iOS |

## Community/discourse index

The qualitative community sample lives in [community](../community.md) and [research landscape](../research-landscape.md). Keep rolling subreddit rankings as discovery mechanisms rather than stable citations. When a post reveals a new capability, search for an official API/release source before upgrading it from reported to documented.

## Maintenance rule

For volatile plan limits, beta/prototype actions, model artifacts and OS-specific behavior, re-check the original source before an engineering decision. If a link changes meaning, preserve the old dated claim in history and add the new state rather than rewriting the past as though it was always true.