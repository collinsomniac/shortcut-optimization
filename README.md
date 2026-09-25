# Shortcut Optimization

Phone-first research and reusable building blocks for AI, Apple Shortcuts, local iOS workflows, and a future capability-oriented agent harness.

**Status:** active research + harness implementation. The repository now documents and partially implements a live Supabase control plane, iPhone/desktop workers, Shortcut-management protocol, callback/artifact services, and compiler probes while continuing source-backed ecosystem research. Documentation reviewed 2026-09-24.

## Start with a goal

| I want to… | Start here |
|---|---|
| Continue active harness engineering in a new chat | [Next-chat handoff](agents/next-chat-handoff.md) · [copy-paste prompt](agents/next-chat-prompt.md) |
| Understand the live system architecture | [Current harness architecture](docs/architecture/current-harness.md) |
| Understand the project and current research state | [Research home base](docs/research/index.md) |
| Continue research consistently across agents | [Research methodology](docs/research/methodology.md) and [capability template](docs/research/capability-record-template.md) |
| Understand how the technologies could compose into a harness | [Capability stack](docs/research/capability-stack.md) |
| Explore compound workflow/agent-skill ideas | [Use-case atlas](docs/research/use-cases.md) |
| Compare third-party action/code/remote-execution providers | [Extension ecosystem](docs/research/extension-ecosystem.md) |
| Understand workflow representation and optimization | [Shortcut as program](docs/research/shortcut-as-program.md) |
| Compare Jev/Laya-style decision models, training, teacher pairing and iOS/ChatGPT surfaces | [System-One decision models](docs/research/system-one-decision-models.md) |
| Inspect a browser-local model flow instrument | [Latent Scope](examples/latent-scope/) · [visual/adapter design](examples/latent-scope/docs/visual-and-adapter-design.md) |\n| Study learned optional escalation with a browser game | [CourierGrid benchmark](docs/research/game-policy-benchmark.md) and [browser example](examples/courier-grid/) |
| Invoke fast local classifiers from Shortcuts | [Sub-second Shortcuts inference](docs/research/shortcuts-fast-inference.md) |
| Build a chat-controllable Shortcut library worker | [Shortcut Worker control plane](docs/research/shortcut-worker-control-plane.md), [live implementation status](docs/implementation/shortcut-worker-status.md), and [protocol example](examples/shortcut-worker/) |
| Understand/reorganize the existing Supabase harness | [Supabase compartmentalization](docs/research/supabase-compartmentalization.md) |
| Compare rules, Laya, local LLMs and cloud models | [Model routing](docs/research/model-routing.md) and [inference routes](docs/inference-routes.md) |
| Trace research claims back to sources | [Research source ledger](docs/research/source-ledger.md) |
| Trigger a shortcut from chat or the browser | [Links and handoffs](docs/links-and-handoffs.md) |
| Build with AI, then replace pieces with app actions | [Builder and third-party actions](docs/ai-builder.md) |
| Install, share, or modify a shortcut | [Distribution](docs/distribution.md) |
| Understand File / iCloud / audience options | [Sharing modes](docs/sharing-modes.md) |
| Compare existing compilers, collections, and agents | [Ecosystem](docs/ecosystem.md) |
| Inspect a supplied workflow without rebuilding it | [Intake design](docs/intake-and-roundtrip.md) |
| Keep reusable state on my phone | [Local storage](docs/local-storage.md) |
| Use subscriptions and free tiers deliberately | [Compute inventory](docs/compute-inventory.md) |
| Give an agent useful, bounded phone capabilities | [Agent harness](docs/agent-harness.md) |
| Turn community ideas into research leads | [Research landscape](docs/research-landscape.md) |
| Connect a future agent to this collection | [Agent research brief](agents/research-brief.md) and [agent entry point](agents/README.md) |
| Contribute a finding | [Evidence rules](docs/evidence.md) |

## Project thesis

Make useful phone capabilities discoverable, composable, inspectable and eventually verifiable. Treat Shortcuts as more than a gallery of recipes: it can become a typed execution layer whose deterministic actions, App Intents, state, web/shell extensions and model calls are selected behind explicit capability contracts.

The central research hypothesis is that a future optimizer/harness can **use the smallest adequate primitive**: deterministic action → bounded learned decision → local generative model → remote/cloud model → user escalation. A second hypothesis is that agent-generated Shortcuts can be inspected and transformed like programs to reduce unnecessary model/network/interaction cost without changing intended behavior.

A proposed later handoff remains **agent selects capability → user/device authorizes a known workflow → installed shortcut validates input and runs → explicit result is verified**. Fully automatic installation and same-chat result delivery remain research questions.

## What is here

- `docs/research/`: synthesis layer, capability map, use cases, model-routing work, source ledger and optimizer hypotheses.
- `docs/`: narrower capability guides and source-backed platform boundaries.
- `shortcuts/`: package convention and future release specifications.
- `agents/`: durable handoff for future agents plus discovery/catalog conventions.
- `skills/`: reusable task recipes for agents and humans.
- `tooling/`: structural inspection and URL utilities.
- `experiments/`: future reproducible tests plus preserved inspection records.
- `examples/`: executable research architectures that illustrate the design without claiming production validation.

Evidence labels: **documented**, **artifact-inspected**, **reproduced**, **reported**, **hypothesis**, **unknown**. “Documented” is not “tested on this phone.” See [evidence rules](docs/evidence.md).

## Current phase: research + implementation

Continue expanding the source-backed capability map while converting the most valuable paths into reproducible harness experiments. The current engineering focus is native Shortcut inventory, a source-controlled/dynamic registry, artifact round-trip editing, verified execution receipts, and a contained `shortcuts.*` semantic tool surface. Prefer primary documentation, retain useful community reports as reported evidence, and turn promising combinations into falsifiable architecture hypotheses.

The later first execution milestone remains **SO Echo**, a diagnostic shortcut that accepts text and returns it unchanged. That milestone is intentionally deferred while the project builds its research base. See [roadmap](docs/roadmap.md).

Core scope remains phone-first. Desktop/cloud components are welcome where they provide a clear compiler, build, training, control-plane or escalation role; they should not silently become prerequisites for ordinary phone use.

Research also includes a [static inspection of a supplied example](experiments/restaurant-assistant-inspection.md). The example is a research specimen, not an installable project release.

[Core sources](docs/sources.md) · [Research source ledger](docs/research/source-ledger.md) · [Community questions](docs/community.md) · [Contributing](CONTRIBUTING.md) · [MIT license](LICENSE)