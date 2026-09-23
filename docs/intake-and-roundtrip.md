# Intake and round-trip design

**Proposal, informed by one successful artifact inspection.** The universal layer should be an evidence-bearing package, not a new shortcut language.

## Intake stages

1. Accept an explicitly supplied share link or file.
2. Retain the original bytes privately for inspection; identify signed container versus decodable plist.
3. Extract ordered actions, control-flow groups, variable links, app descriptors, import questions, input/output declarations, and trigger metadata if present.
4. Create a human-readable report. Preserve unfamiliar fields and opaque app payloads in source copies.
5. Produce a candidate manifest with unknowns explicitly null.
6. Only promote to a release after redaction, artifact verification, import, and execution tests.

Do not infer user-facing iOS versions from internal Workflow client-version numbers without a mapping. An accepted-input list is not proof that the workflow consumes those inputs. An Apple-style action identifier does not eliminate the need to inspect its app descriptor.

## Representations and ownership

| Representation | Role | Rule |
|---|---|---|
| Original export | Authoritative received artifact | Preserve; do not overwrite |
| Decoded plist/XML | Exact action structure when available | Preserve unknown keys and object types |
| Normalized report | Review/search aid | Not executable or lossless source |
| Cherri/Jelly source | Optional authoring representation | Prove supported round trips before adopting |
| Prompt | Creation/edit aid | Never substitute for the artifact |
| Manifest | Requirements and evidence | No fabricated install/runtime status |

Use a raw-byte hash for artifact identity. A separate future normalized structural digest could reduce UUID/signing noise, but its exclusions must be explicit. Equal normalized digests would not prove semantic equivalence.

## Required round-trip checks

For decode → transform → compile → sign → import, compare ordered actions, grouping references, variable connections, parameters, app descriptors, input settings, import questions, triggers, and stored state. Do not silently drop unrecognized action types.

Add a fixture where a third-party action is preserved unchanged while a neighboring native action is edited. This directly tests the proposed adapter strategy. A file-diff check is useful but still needs execution with the actual dependency installed.

## Proposed install state machine

Track **offered → import opened → self-check confirmed**. Cancellation stays unconfirmed. Store package ID, declared version, device-local shortcut name, and last self-check separately. Renaming should update a mapping, not create a new package identity. Never mark an update installed merely because the user tapped its link.

A self-check receipt is evidence of that declared implementation running, not cryptographic proof that every action matches a release. Stronger artifact matching remains a separate research task.

## Next practical experiment

Compare untouched and minimally edited exports of a synthetic native shortcut, then a synthetic one-action third-party specimen. Use existing compiler/importer tooling where it preserves the action graph. This does not require organizing or exposing a personal shortcut collection.
