# iOS Shortcut import compatibility matrix

Updated 2026-09-25.

## Why

The target iPhone successfully imported `SO-Copy-Actions`, but later
ChatGPT-hosted download links for `harness.shortcuts.library` v0.3 and
`harness.shortcuts.stage` v0.1 failed at the **file download** layer before
Shortcuts saw the artifacts.

The successful SO helper and the newer controller also differ in construction:
SO-Copy-Actions was assembled with repository plist tooling; the new artifacts
are Cherri-compiled.

This matrix holds delivery constant and varies construction/action families.

## Order

1. `known-good-copy-actions` — exact already-imported positive control.
2. `manual-hubsign-probe` — repo-built native Comment + Show Result, HubSign.
3. `cherri-basic` — minimal Cherri Show Result.
4. `cherri-inventory` — Cherri + first-party Get My Shortcuts.
5. `cherri-create` — Cherri + current Create Shortcut AppIntent.
6. `cherri-controlflow` — Cherri + conditional grouping.
7. `manager-v03` — full pure-native manager.
8. `stager-v01` — download/save/open stager.

Do not infer anything from later fixtures until the earlier control passes.

## Interpretation

- #1 fails: transport/serving problem.
- #1 succeeds, #2 fails: artifact/signing or current OS acceptance changed.
- #2 succeeds, #3 fails: Cherri serialization/top-level envelope is implicated.
- #3 succeeds, #4 fails: legacy Shortcut object action is implicated.
- #4 succeeds, #5 fails: Create Shortcut AppIntent descriptor/action is implicated.
- #5 succeeds, #6 fails: Cherri control-flow grouping is implicated.
- #1–#6 succeed but manager fails: complexity or another management action family.
- manager succeeds but stager fails: document/network action family or stager graph.

Import success and execution success are recorded separately.
