# Research methodology

Purpose: make research accumulated by different conversations/agents comparable, traceable and reusable. This project is currently literature/ecosystem-first; an unknown that can only be resolved empirically should be recorded for the later experiment phase rather than answered by confidence or repetition.

## Research unit: the claim, not the webpage

A source page may contain several claims with different scopes. Record each important claim with:

- capability or behavior;
- platform/app/model and version/date;
- input/output or preconditions;
- source type and URL;
- evidence label from [evidence policy](../evidence.md);
- what the source actually establishes;
- what it does **not** establish;
- related providers/alternatives;
- useful compound workflows;
- unresolved questions.

This prevents a source such as an Apple WWDC session, model card or Reddit post from becoming a blanket endorsement of an inferred architecture.

## Source hierarchy

Use the strongest available source for each kind of question:

1. **Primary platform/model/provider documentation** for public API, action, model, artifact and plan claims.
2. **Maintainer documentation/source** for open-source implementation details.
3. **Independent technical analysis/benchmarks** for measured behavior that primary sources do not provide.
4. **First-person/community reports** for demand, workflows, bugs, hidden/prototype behavior and research leads.
5. **Project hypothesis** for compositions or conclusions not directly stated by a source.

Popularity and search rank are discovery signals, not evidence quality. A community report can be extremely valuable while remaining `reported`.

## Research loop

### 1. Discover

Canvass official release documentation, developer sessions, model/runtime repos, action-provider catalogs, forum discussions and adjacent automation/agent projects. For communities, combine broad samples (top/month/year where accessible) with targeted searches for specific failure modes and capabilities.

### 2. Canonicalize

Translate a product-specific feature into a semantic capability: e.g. Actions `Counter` → `state.atomic_increment`; Shortcuts Get Contents of URL → `web.request`; Scriptable Run Script → `script.javascript`; Laya typed choice → `decision.classify`.

Do not erase provenance. The canonical capability is a project abstraction; the concrete provider/action remains attached.

### 3. Triangulate

Ask whether an official source documents the primitive, whether independent/community evidence exposes practical constraints, and whether a newer OS release supersedes older workarounds. Preserve disagreements and version drift.

### 4. Connect

Map capabilities into compound patterns in [use-case atlas](use-cases.md). Prefer interfaces where one layer's typed output naturally becomes another layer's typed input.

### 5. Hypothesize

Write the design claim in falsifiable form. Example: “A task-specific Laya classifier can replace cloud classification for notification routing with acceptable calibration and lower end-to-end latency.” This is better than “Laya will make Shortcuts faster.”

### 6. Queue

If more reading can answer the question, add a research lead. If only execution can answer it, add a later experiment question with the exact variables that need measurement.

## Capability record

Use [capability record template](capability-record-template.md) for substantial new surfaces. Small facts can remain in topical Markdown, but a capability that may enter the future harness deserves explicit inputs, outputs, effects, dependencies and evidence.

Recommended stable semantic groups:

- `context.*` — gather user/device/app/web context;
- `state.*` — persistent or transient state operations;
- `decision.*` — bounded rules/classifiers/routing;
- `model.*` — open-ended generation/interpretation;
- `app.*` — App Intent/native app operations;
- `web.*` — HTTP, DOM and URL transport;
- `file.*` — file metadata/transformation/storage;
- `script.*` / `shell.*` — programmable execution;
- `shortcut.*` — compose/manage/run Shortcut workflows;
- `user.*` — ask/confirm/select;
- `result.*` — verify/report/receipt.

These namespaces are research vocabulary, not a frozen API.

## Comparison methodology

When comparing providers, avoid a single “best” score. Compare on dimensions that determine placement:

| Dimension | Questions |
|---|---|
| Semantics | Is output deterministic, bounded probabilistic, or generative? |
| Type fidelity | Are inputs/outputs explicit, inspectable and composable? |
| Side effects | What external state can it change? Is the operation reversible/idempotent? |
| Execution authority | Shortcut extension, foreground app, browser, dedicated device, remote service? |
| Lifecycle | Can it survive background execution, app switching and repeated runs? |
| Privacy | What data leaves the device? Where are secrets stored? |
| Availability | Native, free extension, paid app, account/server requirement? |
| Resource cost | Latency, energy, memory, quota, money, network dependency |
| Portability | What happens on another user's phone without the provider installed? |
| Evidence | Documented, reported, reproduced, unknown? |

Do not collapse these dimensions into an evaluative ranking during research; the future harness may choose different providers under different constraints.

## Community research method

Community examples are most useful when categorized by **trigger → context → decision → side effect → persistence → failure mode** rather than by app or popularity. Examples such as calendar-driven alarms, notification expense logging, Focus-based routines, Home Assistant control and modular AI agents reveal reusable workflow structures even when the exact Shortcut is unsuitable for this repo.

Capture recurring pain points separately: setup burden, lost variable bindings, background reliability, third-party action availability, import/update drift, missing scheduling, permissions, app-opening requirements and opaque AI-generated graphs.

## Version/change discipline

Maintain a watchlist for rapidly changing areas:

- iOS/Shortcuts releases and beta-to-release behavior;
- App Intents and Foundation Models/Core AI APIs;
- model cards/checkpoints/quantized artifacts;
- wllama/ONNX Runtime browser support;
- third-party action catalogs;
- subscription/free-tier limits;
- hidden/prototype actions reported by communities.

Re-check these sources before decisions. Git history should preserve prior states rather than silently rewriting them.

## Handoff discipline

A future conversation should be able to orient from the repository without retrieving old chat history. When a research pass materially changes the architecture:

1. update the relevant topical synthesis;
2. add/refresh the source ledger;
3. update [research home base](index.md) if the map changed;
4. update [agents/research-brief.md](../../agents/research-brief.md) only for high-level state/north-star changes;
5. leave concrete implementation/test claims untouched unless evidence justifies them.

Research is “done enough” for a topic when additional reading mostly repeats existing knowledge and the remaining discriminating questions require measurement.