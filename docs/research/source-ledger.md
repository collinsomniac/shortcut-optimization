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
| [Shortcuts command-line tool](https://support.apple.com/guide/shortcuts-mac/run-shortcuts-from-the-command-line-apd455c82f02/mac) | primary | macOS list/view/run/sign artifact backend |

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
| [Laya model card](https://huggingface.co/convaiinnovations/laya) | upstream/model | architecture, typed decisions, latency and benchmark caveats |
| [Laya typed-decisions checkpoint](https://huggingface.co/convaiinnovations/laya-typed-decisions) | upstream/model | fine-tuned benchmark and calibration data |
| [Laya training README](https://github.com/NandhaKishorM/laya/blob/main/README.md) | project/community | training recipe and specialization guidance |
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

## Extension and artifact tooling

| Source | Type | Why it matters |
|---|---|---|
| [a-Shell](https://github.com/holzschu/a-shell#shortcuts) | maintainer | Shortcuts Execute Command/Put File/Get File and mobile shell |
| [a-Shell commands](https://github.com/holzschu/a-Shell-commands) | maintainer | reusable WASM command ecosystem |
| [shortcuts-generator skill](https://github.com/cranecj/shortcuts-generator/blob/main/SKILL.md) | community | programmatic plist generation + Apple signing precedent |
| [shortcut-lib format notes](https://github.com/findlaywebb/shortcut-lib/blob/main/docs/format.md) | community | reverse-engineered serialized structure |
| [Hidden Generate Shortcut report](https://www.reddit.com/r/shortcuts/comments/1vgk21f/new_shortcut_action_generate_shortcut_from/) | reported/community | prototype self-generation/management lead; not a released API guarantee |

See [ecosystem](../ecosystem.md) for Cherri, Shortcuts Playground, Jelly/Open Jellycuts, RoutineHub updater, ScPL and catalog precedents.

## Compute/control-plane resources

| Source | Type | Why it matters |
|---|---|---|
| [Google: Colab joins Google AI plans](https://developers.googleblog.com/colab-is-now-part-of-your-google-ai-plan/) | primary | AI-plan Colab rollout and accelerator access |
| [Google AI plan benefits](https://support.google.com/googleone/answer/14534406?hl=en) | primary | current AI Pro entitlements such as 200 CCUs and developer benefits |
| [GitHub included usage](https://docs.github.com/en/billing/reference/product-usage-included) | primary | Free Actions/Codespaces quotas |
| [GitHub-hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners) | primary | public/private standard runner resources |
| [Supabase billing](https://supabase.com/docs/guides/platform/billing-on-supabase) | primary | Free database/storage/egress/realtime/function quotas |
| [Supabase Edge Function limits](https://supabase.com/docs/guides/functions/limits) | primary | CPU/memory/wall-clock boundaries |
| [OpenRouter pricing](https://openrouter.ai/pricing) | primary/provider | current free-model/request surface |
| [OpenAI: ChatGPT vs API billing](https://help.openai.com/en/articles/9039756-billing-settings-in-chatgpt-vs-platform) | primary/provider | ChatGPT subscription and API are separate billing systems |

## Community/discourse index

The qualitative community sample lives in [community](../community.md) and [research landscape](../research-landscape.md). Keep rolling subreddit rankings as discovery mechanisms rather than stable citations. When a post reveals a new capability, search for an official API/release source before upgrading it from reported to documented.

## Maintenance rule

For volatile plan limits, beta/prototype actions, model artifacts and OS-specific behavior, re-check the original source before an engineering decision. If a link changes meaning, preserve the old dated claim in history and add the new state rather than rewriting the past as though it was always true.