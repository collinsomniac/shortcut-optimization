# Next-chat handoff

## Preferred continuation — direct compiled persistent controller

Do **not** resume the action-pasteboard or imported Generate Shortcut routes as
the primary plan. Both have device evidence against them.

Current install candidate:
- `harness.shortcuts.library` v0.2
- source: `examples/shortcut-worker/harness.shortcuts.library.cherri`
- build workflow: `.github/workflows/compile-shortcut-library-manager.yml`
- green run: `36096803489`
- signed SHA-256: `2d1968b1bcb432d1dfa8d31bdea19ca00c129b9ee7f0984a6b7645b90589e1ab`
- adds `export_to_worker` through the separately grounded a-Shell Put File intent

The build is deterministic in source/tool versions but uses runtime-random
control-flow UUIDs because Cherri's derive-UUID mode produced invalid duplicate
GroupingIdentifiers. Exact signed byte identity therefore need not reproduce
across builds; source + normalized semantic graph + validation are the important
reproducibility anchors.

After the user imports the signed controller, validate in this order:
1. invoke `capabilities` by run-shortcut URL with JSON text input;
2. invoke `list` and inspect output;
3. invoke `export_to_worker` on a harmless existing Shortcut and use `shell.exec.simple` to verify whether a native `.shortcut` file appears in the a-Shell App Group;
3. create a disposable uniquely named test Shortcut;
4. run/open it;
5. rename it;
6. create an iCloud link only if the user accepts the external share;
7. call delete with confirm != true and verify refusal;
8. delete the disposable fixture with explicit user confirmation;
9. only after the above route the semantic Supabase facade through the installed
   controller.

Then expand the native plane with Move and attributes using real exported action
donors or otherwise empirically grounded entity serialization.

## Action-pasteboard route — 2026-09-25 UTC (current preferred next experiment)

The native export/parser/editor milestone is complete enough that whole-file signing is no longer the only way forward. A generic five-action helper, `SO Copy Actions`, can convert a JSON payload of base64-encoded action plists into the native `com.apple.shortcuts.action` clipboard representation using Sindre Sorhus's Actions app.

Verified in code / infrastructure:
- exact Actions AppIntent descriptor recovered;
- helper graph recorded in repo;
- generic helper signed through HubSign, no private harness bytes included;
- stable whitelisted public fixture endpoint deployed;
- desktop fetch reproduced exact 22,337-byte AEA1 helper SHA;
- local packer preserves action order, UUIDs and cross-action references;
- two-action Text → Show Result device fixture committed.

Not yet verified:
- iOS accepts/imports the helper;
- helper creates a pasteable native action clipboard on this phone;
- pasted actions round-trip through export exactly;
- private patched `harness.info` duplicate executes with the added fixture.

Preferred sequence now:
1. install `SO Copy Actions`;
2. run the two-action fixture and paste it into a blank Shortcut;
3. execute/export/compare;
4. pack the private 11-action patched `harness.info` locally;
5. paste into a separately named duplicate;
6. export/decode/canonical-compare;
7. execute and verify `_roundtrip_fixture = harness.info.patch.v1`.

See [iOS action-pasteboard experiment](../experiments/ios-action-pasteboard/README.md) and [HubSign generic probe](../experiments/hubsign-import-probe/README.md).

## Native export milestone — 2026-09-25 UTC (supersedes earlier export blocker)

The supplied `harness.info` export was decoded locally on Linux with AEA signature/integrity verification, canonicalized, and structurally patched. All 11 actions and existing tokenized Dictionary fields were preserved; one inert `_roundtrip_fixture` text field was added. 19 tests pass. Playground diagnostics are identical before/after (four pre-existing checks, not a full validation pass). **Unsigned patch only; signing/import/device fixture execution remain blocked.**

Artifact evidence refines the old “hardcoded manifest” description: the export uses Get My Shortcuts in four fixed harness folders, then formats their members. The folder scope/schema are fixed, the members are dynamically discovered, and the whole library is not scanned. Dispatcher allowlist behavior and installed/exported byte identity remain unknown. Do not assume adding an output field registers a callable tool.

Whole-file trusted signing remains useful, but the current preferred route is action-level pasteboard reconstruction so the private patched harness need not leave the user's environment. [Exact experiment, hashes, boundaries and reproduction](../experiments/native-harness-roundtrip/README.md).

## Latest experiment — 2026-09-25 UTC

- Live `harness.info` completed; the artifact `get` facade reached the phone but returned inner `tool_not_found` for `shortcuts.control`, despite transport `ok=true`. Native controller installation remains unknown.
- No native exports/versions/receipts are recorded yet. The shared bus and existing dispatcher remain unchanged.
- Added guarded unsigned-plist literal editing with typed canonical preservation, exact-source hash/old-value checks, and unique action UUID selection.
- A synthetic registry fixture appended one disabled entry deterministically; full untouched-field comparison and 13 tests passed. Pinned Playground iOS 27 validation passed. **Not signed, imported, or device-executed.**
- Next: obtain a native File export of `harness.info` or a duplicate; inspect its actual representation before adapting the patch. Signed containers require a trusted decoding route. No private harness artifact should go to an external signer by default.
- Reproduction, request IDs, artifact hashes, the checked-in probe's malformed trailing-byte finding, and exact remaining boundary: [registry round trip](../experiments/registry-roundtrip/README.md).

Use this file when continuing development in a fresh conversation.

## Read first

1. [Current harness architecture](../docs/architecture/current-harness.md)
2. [Shortcut Worker implementation status](../docs/implementation/shortcut-worker-status.md)
3. [Shortcut Worker protocol](../examples/shortcut-worker/protocol.json)
4. [Shortcut Worker control-plane research](../docs/research/shortcut-worker-control-plane.md)
5. [Supabase compartmentalization](../docs/research/supabase-compartmentalization.md)
6. [Research brief](research-brief.md)

Do not reconstruct state from old chat messages unless a repo/live-system discrepancy requires it.

Track the concrete implementation checklist in [GitHub issue #4](https://github.com/collinsomniac/shortcut-optimization/issues/4). The current hardcoded registry snapshot is [`harness/registry.json`](../harness/registry.json).

## Live resources

GitHub repository:
`collinsomniac/shortcut-optimization`

Supabase project:
- `iphone-harness`
- ref `zpdtlzpvshlpyqbfbzye`

Workers:
- `iphone-main`
- `desktop-main`

The desktop worker may be used where compiler/build/inspection work benefits from persistence, but the Shortcut subsystem should remain a contained semantic tool family.

## User intent

The user is comfortable treating the Shortcuts app primarily as an **agentic workspace**. They do not need to preserve an important personal collection of unrelated workflows.

Priorities:
- complete library visibility and management;
- programmatic generation;
- programmatic editing, ideally lower-level than Describe a Shortcut;
- ability to organize agent-generated workflows into folders;
- execution with verified receipts;
- ability to modify/optimize the harness itself;
- third-party/AppIntent compatibility;
- clear contained tools so agents do not reflexively fall back to generic shell/desktop controls.

## Critical correction

`harness.info` is a scoped harness manifest, not a full-library inventory. The supplied export dynamically scans four fixed folders; dispatcher policy remains separately unverified.

Do not use its absence of a name as proof a Shortcut is absent from the library.

This makes the registry itself a prime target for programmatic editing:
- extract its source/artifact;
- model its registry structurally;
- make the registry source-controlled/dynamic;
- regenerate or patch `harness.info`;
- keep allowlisting as a policy layer rather than a manual maintenance burden.

## The most valuable next experiment

Aim to prove a complete lower-level round trip on one harmless harness Shortcut:

~~~text
native Shortcut object
  → export
  → inspect/decompile
  → canonical graph/IR
  → small deterministic patch
  → validate
  → sign/import through trusted path
  → execute fixture
  → verify output
  → compare before/after
~~~

Ideal first target: `harness.info` or a duplicate of it.

A successful experiment should add one new registry item without rebuilding the entire workflow manually and without using UI coordinates as the primary mechanism.

## Recommended implementation order

### A. Dynamic registry
Create a canonical machine-readable registry in the repo, for example:

`harness/registry.json`

with entries containing:
- semantic method name;
- native Shortcut name;
- category/domain;
- input/output shape;
- effect class;
- enabled flag;
- minimum worker/controller version;
- source/version hash.

Then decide whether:
- `harness.info` is generated from it;
- the dispatcher reads/syncs it;
- or both.

### B. Inventory
Use native Get My Shortcuts, not filesystem crawling.

Normalize:
- native name;
- folder;
- native/stable identifier if available;
- source/export hash;
- dependency/AppIntent metadata where obtainable.

Sync to `shortcuts.inventory`.

### C. Artifact round trip
Export one harmless existing harness Shortcut.

Use:
- repo compiler tooling;
- Shortcuts Playground action catalogs/validator;
- other open-source parsers only as references unless validated against the target artifact.

Record unknown fields rather than dropping them.

### D. Structural patching
Add a minimal patch operation:
- append one registry entry;
- change one literal;
- or replace one known action parameter.

Do not start with arbitrary whole-program rewriting.

### E. Trusted signing/import
Compare:
- user-controlled macOS signer if/when available;
- iPhone-native generation/import;
- Apple-signed/exported artifacts;
- third-party HubSign only for non-sensitive experiments.

Make signer/provenance explicit in `shortcuts.versions`.

### F. Agent-facing tools
Once the round trip works, expose it behind:
- `shortcuts.get`
- `shortcuts.diff`
- `shortcuts.edit`
- `shortcuts.install`
- `shortcuts.validate`

The agent should not need to know plist details in ordinary use.

## Things already learned; do not repeat

- a-Shell cannot inspect the native private Shortcuts DB.
- Shortcuts library folders are not Files folders.
- Get My Shortcuts is the correct native inventory primitive.
- The iOS 27 Generate Shortcut donor artifact was inspected and contains a single `GenerateShortcutAction`.
- GitHub-hosted macOS signing without an authenticated Apple/iCloud environment is not sufficient.
- Direct phone → Supabase callback POST works.
- A URL launch is not a verified Shortcut run.
- `harness.info` is hardcoded, not discovery.
- Supabase is one shared project and should remain the bus unless a staging/failure-domain reason justifies a second project.

## Security rules for development

- Keep worker/service-role credentials out of GitHub.
- Do not expose generic `desktop.exec` merely because a Shortcut method is missing.
- Require explicit confirmation for destructive Shortcut deletion.
- Use exact identity/version/hash for mutations where possible.
- Treat external artifact signing as a trust boundary.
- Keep private Shortcut contents out of third-party signers unless explicitly acceptable.
- RLS-disabled internal tables currently have no anon/auth table privileges; preserve or improve that boundary.

## Definition of a good stopping point for the next agent

Do not stop after another design note.

Prefer one of:
- live inventory successfully synced;
- one harness Shortcut exported and parsed;
- one deterministic patch round-tripped and verified;
- registry made source-controlled/dynamic;
- or a precise falsified route with a reproducible artifact/log showing why it cannot work.

Update this handoff and the implementation status when the system materially changes.
