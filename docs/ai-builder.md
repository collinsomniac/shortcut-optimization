# AI building and third-party actions

## Three distinct interfaces

| Interface | Evidence | What it establishes |
|---|---|---|
| Describe a Shortcut | Apple announcement [S4] | Natural-language creation and follow-up changes |
| Use Model | Apple developer session [S5] | Model invocation during a workflow |
| App Intent entities passed to Use Model | Developer example [S5] | Exposed app properties can be model inputs |

Do not transfer an integration guarantee from runtime Use Model to the shortcut builder.

**Reported by the project owner:** creating from scratch with third-party actions has failed, while edits to some existing shortcuts containing them have succeeded. Exact prompts/builds/actions were not recorded; conditions remain unknown.

**Hypotheses to separate:** the builder edits only native nodes; it preserves third-party nodes opaquely; it can use some exposed metadata; support differs by app/action; apparent success changes the graph incorrectly.

## Architecture: what is actually known

Apple attributes description-based creation to Apple Intelligence [S4]. The reviewed source does not specify the builder's model identifier, parameter count, context limit, action schema, training data, validation/repair loop, or per-request routing. Do not infer those from general Apple Intelligence architecture.

The runtime transcript inspection shown in [S5] helps inspect data sent to Use Model. It is not proof of builder introspection, nor a view of hidden reasoning.

## Native skeleton → replaceable adapter

Design the contract before prompting: named inputs, output types, failure behavior, side effects, and one clearly marked replacement point. Use a native Text/Dictionary fixture to simulate the third-party output. Replace that block manually, then rerun identical cases. A wrapper invoked with Run Shortcut may isolate app-specific details; builder preservation remains to be tested.

Prompt template:

> Build a shortcut named SO Adapter Probe using only built-in actions. Accept text input. If no input is supplied, ask for text. Add a Comment named ADAPTER PLACEHOLDER, followed by a Text action containing the input. Display that output. Do not use third-party actions or network requests. Keep the placeholder as a single replaceable block.

Follow-up test:

> Change only the display step to prefix the output with “Result: ”. Preserve the adapter block and all of its parameters and variable connections.

These are untested prompts, not exports.

## Controlled experiment

Duplicate the same baseline for every trial. Compare native-only creation, third-party creation, native edits around an existing app action, edits to that action's parameters, and edits to its connected output. Test text and typed entity outputs separately. Repeat each case three times; save before/after exports, exact prompt, errors, and runtime results. “Generated” and “correct” are different outcomes.

Use [the experiment record](../experiments/record.template.json). Sources: [S4, S5](sources.md).
