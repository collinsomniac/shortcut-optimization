# iOS action-pasteboard round trip

Status: **helper signed; device paste not yet reproduced**  
Updated: 2026-09-25 UTC.

## Objective

Avoid re-signing every edited Shortcut by using the Shortcuts editor's native
action clipboard representation.

Target path:

~~~text
decoded/patched workflow
  → split WFWorkflowActions
  → plist-serialize each action dictionary
  → base64 transport payload
  → SO Copy Actions
  → Actions: Set Uniform Type Identifier
       com.apple.shortcuts.action
  → native iOS clipboard
  → paste into a new/duplicate Shortcut
  → export
  → canonical compare
  → fixture execution
~~~

The whole patched workflow remains local/private. Only the generic helper was
sent to the external signing service.

## Evidence

### Upstream action clipboard format

The inspected `mehrlander/shortcut-tools` project contains a five-action
`Copy-ActionFromClaude` receiver:

1. coerce Shortcut Input to Dictionary;
2. read `actions` and Base64 Decode the list;
3. Actions app `SetUniformTypeIdentifier`;
4. set type to `com.apple.shortcuts.action`;
5. Copy to Clipboard.

Its packer serializes **each action dictionary as its own plist document**, then
base64-encodes each one and sends:

~~~json
{
  "actions": ["<base64 action plist>", "..."],
  "report": "human-readable label"
}
~~~

This means the transport preserves action ordering and UUID references across
the chain.

Pinned inspected source:
- `mehrlander/shortcut-tools` revision visible through GitHub during this pass;
- `workflows/copy-action-from-claude.json`;
- `tools/pack.py`;
- `docs/shortcuts-format-notes.md`.

The upstream notes explicitly describe the on-device ceiling as **create empty,
then paste**; they use `CreateWorkflowAction` plus this pasteboard route.

### Exact Actions AppIntent descriptor

Recovered descriptor:

~~~json
{
  "id": "com.sindresorhus.Actions.SetUniformTypeIdentifier",
  "AppIntentDescriptor": {
    "AppIntentIdentifier": "SetUniformTypeIdentifier",
    "BundleIdentifier": "com.sindresorhus.Actions",
    "Name": "Actions",
    "TeamIdentifier": "YG56YK5RN5"
  },
  "parameters": {
    "file": "<action plist file/list>",
    "typeIdentifier": "com.apple.shortcuts.action"
  }
}
~~~

The current Shortcuts Playground iOS 27 catalog also contains the identifier.

### Generic helper

This repo now records the exact helper graph at:
`examples/shortcut-worker/copy-actions-helper.json`.

A generic `SO Copy Actions` artifact was signed through the existing
RoutineHub HubSign bridge. It contains no harness data.

Signed SHA-256:

`384763f4cd4e2a5012950820a5c803dfac352f9f40f585a5a8f6ce202c8f5088`

Size: 22,337 bytes. Cached container magic: `AEA1`.

A public Edge Function serves only this helper and a separate harmless
HubSign probe. It does not expose arbitrary rows from `shortcuts.artifacts`.

### Local packer

`tooling/pack_shortcut_actions.py` converts an already-decoded workflow into
the helper payload. It verifies every action plist round-trips and verifies the
decoded payload reproduces the original `WFWorkflowActions` array exactly.

This packer neither signs nor installs anything.

## First device fixture

Use a fresh blank Shortcut.

1. Install `SO Copy Actions`.
2. Feed it a payload containing two actions:
   - Text: `SO Pasteboard Probe`
   - Show Result bound to the Text output UUID.
3. Run the helper.
4. Open the blank Shortcut and Paste.
5. Verify two cards appear and their variable binding works.
6. Export the result and compare its action array with the payload.

Only after this passes should the real 11-action patched `harness.info` graph
be pasted into a duplicate.

## Why this is preferable to signing the private harness

The real harness export contains device-specific folder references and native
workflow structure. Sending the entire patched artifact to an external signer is
unnecessary if the editor can accept the action array locally.

HubSign remains useful for bootstrapping generic helpers and public fixtures.


## Continuation result — 2026-09-25 UTC

The full Shortcut tooling CI was broadened and passed on run `36091095278`:
- 22 tests run;
- 1 optional cryptographic integration skipped;
- bootstrap donor build verified.

The already-patched private `harness.info` was also packed locally into the helper format:
- source workflow SHA-256: `6778a75e81845548c14e287bf9093a8fc7afe2573ebe228c06d1a1a4fd137964`;
- 11 actions;
- private payload size: 19,551 bytes;
- payload SHA-256: `181750662f8aef82ed901f4b65601b4880804e94d0623bfebe97c0691f16a8f2`;
- decoding every base64 action reproduces the private patched `WFWorkflowActions` array exactly.

The private payload was **not committed and not sent to HubSign**.

Current device boundary: install the generic helper, reproduce the committed two-action fixture, then proceed to the private 11-action duplicate only if the native paste succeeds.
