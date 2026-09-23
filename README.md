# Shortcut Optimization

Phone-first research and reusable building blocks for AI, Apple Shortcuts, and local iOS workflows.

**Status:** research foundation. No installable shortcut releases or device-verified results yet. Documentation reviewed 2026-09-23.

## Start with a goal

| I want to… | Start here |
|---|---|
| Trigger a shortcut from chat or the browser | [Links and handoffs](docs/links-and-handoffs.md) |
| Build with AI, then replace pieces with app actions | [Builder and third-party actions](docs/ai-builder.md) |
| Install, share, or modify a shortcut | [Distribution](docs/distribution.md) |
| Understand File / iCloud / audience options | [Sharing modes](docs/sharing-modes.md) |
| Compare existing compilers, collections, and agents | [Ecosystem](docs/ecosystem.md) |
| Inspect a supplied workflow without rebuilding it | [Intake design](docs/intake-and-roundtrip.md) |
| Keep reusable state on my phone | [Local storage](docs/local-storage.md) |
| Compare local models, Laya, and browser inference | [Inference routes](docs/inference-routes.md) |
| Use subscriptions and free tiers deliberately | [Compute inventory](docs/compute-inventory.md) |
| Give an agent useful, bounded phone capabilities | [Agent harness](docs/agent-harness.md) |
| Turn community ideas into testable packages | [Research landscape](docs/research-landscape.md) |
| Connect an agent to this collection | [Agent entry point](agents/README.md) |
| Contribute a finding | [Evidence rules](docs/evidence.md) and [test plan](experiments/README.md) |

## Project thesis

Make useful phone capabilities discoverable, installable, callable, and verifiable. A shortcut should come with an installation artifact, a small input/output contract, requirements, and evidence—not just a screenshot or a prompt.

A proposed path is **agent selects capability → user opens a link → installed shortcut validates input and runs → user shares a result**. Fully automatic installation and delivery back into an existing chat remain research questions.

## What is here

- `docs/`: concise capability guides and source-backed boundaries.
- `shortcuts/`: package convention and first release specifications.
- `agents/`: discovery catalog and operating instructions.
- `skills/`: reusable task recipes for agents and humans.
- `tooling/`: dependency-free URL builder.
- `experiments/`: reproducible tests, including negative results.

Evidence labels: **documented**, **artifact-inspected**, **reproduced**, **reported**, **hypothesis**, **unknown**. “Documented” is not “tested on this phone.” See [evidence rules](docs/evidence.md).

## First milestone

Ship one genuinely reusable diagnostic shortcut: **SO Echo**, which accepts text and returns it unchanged. Use it to measure import, launch, encoding, cancellation, and return behavior before building local memory or multi-step agents. [Roadmap](docs/roadmap.md)

Core scope: iPhone, Shortcuts, browser, and ChatGPT handoffs. Remote workers and hosted databases are outside the initial roadmap. Local execution, offline operation, and absence of cloud sync are separate properties.

Research now includes a [static inspection of a supplied example](experiments/restaurant-assistant-inspection.md) and [prioritized follow-up experiments](docs/next-experiments.md). The example is a research specimen, not an installable project release. Personal shortcut collections are outside this intake.

[Research sources](docs/sources.md) · [Community questions](docs/community.md) · [Contributing](CONTRIBUTING.md) · [MIT license](LICENSE)
