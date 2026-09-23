# Use-case atlas: compound workflows and agent skills

Purpose: widen the design space without confusing an idea with a supported product. Each pattern below combines documented primitives; the end-to-end composition is a hypothesis until reproduced.

| Pattern | Composition | Why it is interesting |
|---|---|---|
| Notification triage | notification automation → parse fields → rules/Laya → Storage → alert/defer/app action | Fast bounded decision loop; good candidate for specialized routing |
| Screenshot inbox | screenshot trigger → OCR/image model → classify → file/album/note action | Converts an incidental capture gesture into structured intake |
| Onscreen semantic action | Receive What's On Screen → normalize entity/text → choose skill → App Intent/API | Context-aware actions without screen-coordinate automation |
| Web research extractor | Share Sheet/current webpage → Run JavaScript → Dictionary/JSON → local transform/model → notes/files | Mixes DOM access with typed downstream processing |
| API skill | typed request dictionary → Get Contents of URL → validate response → deterministic/model transform → app action | Turns a web service into a reusable agent capability |
| Personal state memory | action result/entity → Storage/global value → later trigger/model prompt | Persistent lightweight context without remote infrastructure |
| Local file ETL | Files → a-Shell command/WASM/Python-compatible script → Shortcuts result | Extends Shortcuts with CLI-shaped deterministic transforms |
| Fast/slow reasoning | rules → Laya confidence → local generative model → cloud only if needed | Tests whether expensive reasoning can become exceptional |
| Model-aware workflow optimizer | inspect graph → identify expensive semantic operation → propose rule/local replacement → preserve fixture semantics | Gives the repository a measurable technical thesis |
| Generated-shortcut auditor | Describe a Shortcut output → structural/action inventory → policy/effect review → revision proposal | Natural-language builders create drafts; this layer focuses on correctness/trust |
| Agent skill launcher | planner selects capability contract → user/device authorizes Shortcut → typed receipt → planner continues | Bridges chat planning and iOS execution without pretending the chat owns the phone |
| Contextual routine | time/location/focus/calendar/app entities → rules/model → multi-app actions | Rich automation while keeping deterministic context explicit |
| Error recovery router | action/API error → normalized error state → bounded retry/alternate/escalate decision | Makes failure behavior a first-class skill rather than prompt improvisation |
| Local knowledge lookup | app/native search or future Spotlight search tool → structured evidence → model summary/action | Potential native RAG path in a later app/provider bridge |
| Workflow generator-of-generators | capability catalog + constraints → produce native-first skeleton → preserve adapters → inspect/share | Could turn the repo's knowledge base into authoring guidance for future agents |

## Platform anchors

Apple's [WWDC26 Shortcuts session](https://developer.apple.com/videos/play/wwdc2026/310/) documents notification/screenshot-style automation additions, persistent/global Storage, richer Use Model behavior and transcript inspection. [Receive What's On Screen](https://support.apple.com/guide/shortcuts/receive-whats-onscreen-apd350ce757a/ios), [Run JavaScript on a webpage](https://support.apple.com/guide/shortcuts/run-javascript-on-a-webpage-apdb71a01d93/ios), and [Get Contents of URL](https://support.apple.com/guide/shortcuts/request-your-first-api-apd58d46713f/ios) provide three distinct context/transport routes.

Apple's Foundation Models work adds a second, app-development-oriented research axis. [What's new in Foundation Models](https://developer.apple.com/videos/play/wwdc2026/241/) describes built-in tools including OCR/barcode capabilities and Spotlight search, while [agentic app experiences](https://developer.apple.com/videos/play/wwdc2026/242/) presents Dynamic Profiles and orchestration patterns. These should inspire later native bridges without being mislabeled as stock Shortcuts actions.

Community examples are useful for discovering demand, not proving compatibility. The project's [research landscape](../research-landscape.md) already tracks multi-shortcut agents, notification-driven automations, generated Shortcut builders and everyday contextual workflows.

## Skill-design method

A promising workflow should be documented as a capability before it becomes a Shortcut:

1. user outcome and trigger/context;
2. typed inputs and expected outputs;
3. deterministic portion;
4. semantic decision/generation portion, if any;
5. side effects and permissions;
6. state lifetime and privacy boundary;
7. failure/cancel/retry behavior;
8. candidate implementations for each step;
9. evidence currently supporting each candidate;
10. eventual fixture that would falsify the design.

This structure lets the same skill migrate between implementations. For example, a `decision.evaluate` step can begin as an If block, later compare Laya, and still escalate to a generative provider without changing the rest of the skill contract.

## High-value research themes

**Ambient intake.** Notifications, screenshots, Share Sheet and onscreen content are all ways to convert human context into structured workflow input. Research should compare what each trigger/input surface exposes, under what permissions and lock/foreground conditions.

**Stateful automations.** Persistent Storage changes the kinds of workflows worth considering: cooldowns, histories, preference memory, deduplication, counters and context carry-over can remain local instead of requiring a service.

**Semantic app control.** App Intents are more interesting than generalized UI automation when available because they expose named actions/entities with machine-readable parameters. A capability catalog should therefore index installed app intents/actions and their schemas, not only Shortcut names.

**Learned branching.** Laya-style specialists could turn fuzzy categories into cheap typed decisions, especially when several questions can be batched over one state. The training/calibration burden is part of the design, not an afterthought.

**Optimization as a product.** AI-generated workflows make it easy to produce something plausible; they also create an opportunity for a second system that audits effect boundaries, removes unnecessary model/network work, and explains each rewrite.

**Harness convergence.** Over time, a small stable semantic vocabulary—context, state, decision, model, app, web, shell, user approval and verification—could let Shortcuts become one executor within a larger cross-device harness rather than a special case.