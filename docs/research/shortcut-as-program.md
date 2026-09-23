# Shortcut as program: representation, transformation and generation

Status: research architecture. No canonical IR or optimizer has been implemented.

## Why treat a Shortcut as a program?

A visual workflow is still a directed computation with actions, typed values, variable references, control flow, external effects, permissions and failure behavior. Treating it as a program creates useful questions that screenshots and prompt recipes cannot answer: Which steps are redundant? Which model calls can become deterministic? Which network calls can be cached? Which branches have side effects? Which edits preserve semantics?

## Candidate intermediate representation

A future canonical representation could attach these fields to every node/edge: action kind, stable/local identifier, typed inputs and outputs, variable dependencies, control-flow region, side-effect class, required app/permission, network destination, persistence behavior, model/provider, latency estimate, energy/memory estimate, quota/cost estimate, privacy class, determinism, known failure modes and evidence level.

This is deliberately more semantic than Apple's private serialization. The project can preserve unknown fields and third-party actions without pretending it knows their meaning.

## Optimization families worth documenting

| Family | Example research question |
|---|---|
| Constant/rule folding | Can a model call that answers a date/time predicate become a direct comparison? |
| Dead/redundant action removal | Are values computed but never consumed, or repeatedly converted between the same types? |
| Request coalescing/caching | Are identical API/model calls repeated within one run or across a stable state window? |
| Filter pushdown | Can Find/Filter narrow data before expensive loops/model calls? |
| Bounded-model substitution | Can a free-form classifier become rules or a calibrated Laya node? |
| Local/cloud placement | Can an operation move on-device without losing capability, or does a cloud model actually add needed quality? |
| Permission minimization | Can a narrower app action or input type avoid broad data access? |
| Modularization | Should repeated graph fragments become versioned sub-shortcuts/skills? |
| Verification insertion | Where should a destructive/external effect gain user confirmation or a postcondition check? |

These are compiler hypotheses, not claims about transforms that are currently safe.

## Artifact surfaces that are documented

Apple documents sharing a Shortcut through an iCloud link or exporting it as a file in [Share shortcuts](https://support.apple.com/guide/shortcuts/share-shortcuts-apdf01f8c054/ios). File sharing includes audience modes such as Anyone and People Who Know Me; Apple states an Anyone copy is sent to Apple for validation.

On macOS, Apple documents the `shortcuts` command-line tool for listing/viewing/running workflows and `shortcuts sign` for signing files in [Run shortcuts from the command line](https://support.apple.com/guide/shortcuts-mac/run-shortcuts-from-the-command-line-apd455c82f02/mac). This makes macOS a useful optional build/sign backend without making it a requirement for the phone-first consumption path.

Community projects expose additional reverse-engineered structure. For example [shortcuts-generator](https://github.com/cranecj/shortcuts-generator/blob/main/SKILL.md) creates property-list workflow graphs and then invokes Apple's signing command, while [shortcut-lib format notes](https://github.com/findlaywebb/shortcut-lib/blob/main/docs/format.md) document observed serialized structure. These are useful precedents but the private plist schema is not a stable public Apple AST contract.

## Natural-language generation is another frontend

Apple documents Describe a Shortcut as natural-language creation/refinement powered by Apple Intelligence in its [June 2026 announcement](https://www.apple.com/newsroom/2026/06/apple-intelligence-brings-powerful-ai-capabilities-into-everyday-experiences/). That suggests a compiler pipeline where natural language is one frontend, not the optimizer itself:

intent → generated Shortcut → structural inspection/IR → optimization proposals → verification → distributable artifact.

A community report also describes a hidden/prototype iOS 27 `Generate Shortcut` action that accepts text and returns a Shortcut object, alongside shortcut-management actions. See the [reported discovery](https://www.reddit.com/r/shortcuts/comments/1vgk21f/new_shortcut_action_generate_shortcut_from/). Because the report says it is behind a feature flag, this repo must classify it as **reported/prototype** until it appears in released public documentation or is reproduced on-device.

## Research consequence

The project should avoid building an entire compiler before it understands the artifact and action surfaces well enough. But it should collect optimizer-friendly metadata now. Every workflow specimen, generated example and community failure can be indexed by graph pattern, effect type and failure mode so later implementation starts with a real corpus rather than a blank abstraction.