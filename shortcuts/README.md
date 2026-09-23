# Shortcut packages

No installable releases yet. Do not mistake specifications for working downloads.

First candidate: **SO Echo**. Inputs: text. Output: exactly the same text. Dependencies: built-in Shortcuts only. Side effects: display result; optional explicit copy. Purpose: isolate installation and transport from AI behavior.

Proposed action sequence:
1. Read Shortcut Input as text.
2. Display it without transformation.
3. End with the original text as output.

Keep the empty-input case distinct from a failed launch. Add an optional manual-input variant separately so prompts do not obscure transport measurements.

Release requires an actual exported artifact, iCloud link, clean import, and recorded fixtures. Use [the package convention](../docs/distribution.md).

Next candidates after Echo: structured request validation, bounded local memory, and a share-sheet context packer. AI enrichment should be optional so the deterministic path remains testable.
