# Shortcut Worker implementation status

Updated: 2026-09-25 UTC.

## Current architecture

The project now separates three operational planes:

1. **Persistent native execution/management**
   - target Shortcut: `harness.shortcuts.library`;
   - JSON-in, structured result-out;
   - first-party Shortcuts actions only in v0.3;
   - intended for inventory/create/run/open/folder/rename/link/delete.

2. **Desktop artifact/compiler plane**
   - Cherri compilation;
   - plist normalization/decompilation;
   - graph diff/patch;
   - third-party action schema ingestion;
   - pinned iOS 27 validation;
   - signing preparation/provenance;
   - Git/build tooling.

3. **Artifact staging/import**
   - target Shortcut: `harness.shortcuts.stage`;
   - download a signed artifact on iPhone;
   - save it into the Shortcuts/Files container;
   - open it for Apple's native import sheet;
   - Apple still owns the Add Shortcut confirmation.

See [execution boundaries](../architecture/execution-boundaries.md).

## Pure-native library manager v0.3

Source:
`examples/shortcut-worker/harness.shortcuts.library.cherri`

Build:
`.github/workflows/compile-shortcut-library-manager.yml`

Pinned dependencies:
- Cherri `d96eee9c7768649d441df0166b68a7e3c742690c`;
- Shortcuts Playground validator/catalog `2de03bffe4ce8802e06d184931d9e4ec366a2ef2`.

Latest successful compile run:
`36200258576`

Signed v0.3 artifact:
- 29,817 bytes;
- AEA1;
- SHA-256 `6c544ab7c186e9fead24bcdac30cf107f79c48ffba4550b6016c99c03cae57a6`;
- 176 actions;
- zero third-party actions;
- zero a-Shell actions;
- zero model/Apple-Intelligence actions.

Current v0.3 operations:
- `capabilities`
- `list`
- `create`
- `run`
- `open`
- `create_folder`
- exact-name `rename`
- exact-name `create_link`
- exact-name guarded `delete`

Content operations such as edit/duplicate/install/export intentionally return
`unsupported_content_operation` and belong to the desktop artifact plane.

**Device import/execution of v0.3 is not yet verified.**

## Parameterized runner

The repo contains:

`examples/shortcut-worker/parameterized-runner-builder-prompt.txt`

It asks Apple's in-app builder to create a small persistent
`harness.shortcuts.run` that:
- accepts JSON text with `name` and optional `input`;
- resolves an exact installed Shortcut using Get My Shortcuts;
- runs it;
- returns its output.

This independently tests the fast reusable execution path. Generation/signing
is not part of each run.

## Artifact stager

Source:
`examples/shortcut-worker/harness.shortcuts.stage.cherri`

Intent:
- input JSON: `url`, optional `filename`;
- Download URL;
- Save File into the Shortcuts file container;
- reopen that staged file using Open File;
- let iOS present the native Shortcut import sheet.

This is intentionally pure Shortcuts. No a-Shell or UI coordinates.

The first two CI attempts failed at **compile time**, before signing or iOS:
1. wrong Cherri helper name (`getContentsOfURL`);
2. by-reference helper syntax for Save File.

The source was revised to explicit native/raw action links. CI run
`36200750546` now passes pinned iOS 27 runtime/schema validation and HubSign.

Signed v0.1 stager:
- 26,934 bytes;
- AEA1;
- SHA-256 `e21b977817577bf03d9b3b3364f53568e8994dfeaa04d9018b0f6e325bc395b0`.

**Device staging/import behavior is not yet verified.**

## Create Shortcut boundary

Current Cherri/iOS action metadata shows
`com.apple.shortcuts.CreateWorkflowAction` accepts a name plus
`OpenWhenRun` and returns a Shortcut object.

It is useful for creating an empty persistent Shortcut shell. It is **not**
currently grounded as a general action-graph/content installer.

## a-Shell boundary

a-Shell is demoted from the core manager.

Acceptable optional roles:
- `Execute Command` for small sandbox-safe transforms;
- `Put File` / `Get File` as an explicitly tested adapter.

Do not use it for:
- private Shortcuts DB access;
- Cherri/build work;
- heavy parsing/diffing/Git;
- long-running server behavior.

The old v0.2 manager used `AsheKube.app.a-Shell.PutFileIntent` for
`export_to_worker`. That build remains useful research evidence but is
superseded by pure-native v0.3 as the install candidate.

## Desktop boundary

`desktop-main` is the preferred heavy executor. It is registered and
heartbeating, with PowerShell/process/Codex capabilities.

Recent `desktop.exec` probe requests have remained unleased despite heartbeat,
so direct command execution and automatic VS Code launch are currently
**degraded/unverified**.

Desired semantic app helper is documented in:
`harness/desktop/apps.json`

Target:
`desktop.app.ensure({"app":"vscode"})`

Do not claim this works until a request is actually leased and the Code process
postcondition is observed.

## Third-party action support

Do not depend on Apple's AI builder for third-party actions.

Preferred compiler path:
- ingest provider/maintainer action metadata;
- normalize identifiers/parameters/returns;
- pin provider/catalog version;
- verify provider is installed on the phone;
- generate deterministic graph;
- validate and sign.

Sindre Sorhus's Actions app is a high-value source because it publishes
AI-oriented action metadata.

## Failed/demoted routes

### Imported GenerateShortcutAction bootstrap
Failed on-device. iOS showed:
“Can't Import Shortcut — contains features not supported on this device.”

Do not use imported GenerateShortcutAction as primary bootstrap.

### SO-Copy-Actions / action pasteboard
Helper itself imported, and its Actions AppIntent resolved. But the expected
Paste/Paste Below path was not reproduced on the target iOS 27 editor. Even if
it worked, it remains editor/UI-bound. Keep as research only.

## Native artifact work already complete

The user's actual `harness.info` export was:
- decoded from AEA profile-0;
- cryptographically integrity-checked;
- canonicalized;
- structurally patched while preserving all 11 actions/wiring.

The private patched artifact/payload remains local and has not been sent to an
external signer.

## Supabase state / security

Shortcut-specific internal state lives under `shortcuts.*`.

`shortcuts.artifacts` has RLS enabled. Five internal tables still have RLS
disabled:
- `shortcuts.inventory`
- `shortcuts.versions`
- `shortcuts.capability_snapshots`
- `shortcuts.receipts`
- `shortcuts.callbacks`

This should be hardened in a dedicated access-policy pass. Do not blindly
enable RLS without first preserving the service-role/worker paths.

## Next empirical milestones

1. Install and run pure-native `harness.shortcuts.library` v0.3.
2. Test `capabilities` and `list` only.
3. Test the independent parameterized runner.
4. Finish stager CI.
5. Install stager once; use it to stage a harmless signed artifact and confirm
   the native Add Shortcut sheet opens.
6. Create/run/rename/delete a disposable Shortcut through the native manager.
7. Only then route the public `shortcuts.*` Supabase facade through the
   installed manager.
8. Separately repair `desktop.exec` leasing and verify
   `desktop.app.ensure(vscode)`.
