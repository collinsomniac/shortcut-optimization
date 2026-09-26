# Shortcuts control plane

Updated: 2026-09-25.

This is the canonical agent-facing model for Shortcuts. Agents should reason in
terms of primitives below, not helper Shortcut filenames, URL schemes, a-Shell
commands, HubSign requests, or Pushcut implementation details.

## Layers

| Layer | Primitive | Current implementation | Status |
| --- | --- | --- | --- |
| Author | `shortcuts.generate` | Cherri / deterministic plist construction | working |
| Compile | `shortcuts.compile` | pinned Cherri → XML plist / unsigned shortcut | working |
| Sign | `shortcuts.sign` | `shortcuts.artifacts` + HubSign + SHA-256 cache | working |
| Transfer | `shortcuts.stage` | HTTPS signed artifact → `harness.shortcuts.stage` | working build; device v0.2 update pending |
| Register | `shortcuts.install` | Apple native signed import | manual confirmation proven; legacy silent import under test |
| Inspect | `shortcuts.list/get` | resident `harness.shortcuts.control` | working build; device install pending |
| Execute | `shortcuts.run` | resident controller → Run Shortcut | working build; callback verification pending |
| Manage | `shortcuts.create/rename/delete/link` | first-party Shortcuts App Intents | working build; device execution pending |
| Organize | `shortcuts.create_folder/move_new_folder` | Create Folder + Move Shortcut | working build; device execution pending |
| Edit content | `shortcuts.edit` | generate a replacement signed artifact, then import/replace | compiler path working; registration boundary remains |
| Verify | receipt/callback | controller/stager HTTP POST → `shortcuts.callbacks` | broker implemented; device proof pending |

## Resident device components

### `harness.shortcuts.control`

The controller is the local library authority only. It does not compile or sign
workflow content and it does not stage files.

Current v0.3 operations:

- `ping`
- `capabilities`
- `list`
- `get`
- `run`
- `create`
- `open`
- `create_folder`
- `move_new_folder`
- `rename`
- `delete` (requires `confirm=true`)
- `create_link`

The controller accepts JSON text and optionally a `callback` URL. Remote calls
must include that callback. The Shortcut itself POSTs the device result; do not
use shell-process completion or x-callback as execution proof.

### `harness.shortcuts.stage`

The stager is the content-plane handoff only. It downloads an already-signed
`.shortcut`, saves it, POSTs a "staged" receipt, then opens Apple's native
import surface. Receipt is deliberately sent before the foreground transition.

## Transport modes

### Interactive main-phone transport

A Pushcut notification may carry a default action that directly runs
`harness.shortcuts.control` with the JSON request. This requires one user tap
but avoids a-Shell entirely.

### a-Shell launch adapter

The existing `iphone-main` worker can launch a `shortcuts://` URL, but iOS
may suspend a-Shell immediately after the foreground switch. Therefore:

- never wait for `openurl` as the operation result;
- never treat `shell.exec.simple` completion as Shortcut execution proof;
- the controller/stager callback owns completion;
- callback consumption may close the suspended launch request and return the
  worker to idle.

### Zero-touch wake

Not yet solved on the user's main iPhone. The configured Pushcut webhook is a
notification webhook, not an Automation Server endpoint. Pushcut Automation
Server provides unattended execution but is designed around a dedicated iOS
device running the server.

The legacy `shortcuts://import-shortcut?...&silent=true` route remains an
experimental compatibility path. Current tests were confounded by the wake/app
suspension boundary and do not yet prove either success or rejection on iOS 27.

## Native content boundary

First-party Shortcuts actions can create an empty Shortcut object, enumerate
Shortcuts, run them, rename them, delete them, create links, create folders and
move Shortcut entities. They do not expose an action that inserts an arbitrary
action graph into an existing Shortcut.

Therefore arbitrary workflow creation/editing is intentionally:

```
source → compile → sign → signed .shortcut → native import/replace
```

This is not a reason to put compilation into the resident controller.

## Organization boundary

`move_new_folder` is grounded as a fully native operation:

1. resolve the Shortcut entity by exact name;
2. Create Folder from text;
3. feed the returned folder entity to Move Shortcut.

Moving into an already-existing *empty* folder is not yet exposed because the
Move action requires a folder entity and there is no grounded name-to-empty-
folder resolver in the current controller. Do not silently approximate it.

## Verification states

Use these states consistently:

`generated → compiled → signed → transferred → registered → launched → executed → verified`

A browser/file open, an import sheet, a shell launch, and a successful execution
are different states. Record the strongest state actually observed.

## Current bootstrap target

Install/update these two signed artifacts once:

- `harness.shortcuts.control` v0.3
- `harness.shortcuts.stage` v0.2

After that, test in this order:

1. controller `ping` and HTTP receipt;
2. `list`;
3. create a disposable Shortcut;
4. run it / verify output;
5. rename it;
6. create a new folder and move it;
7. delete it with explicit confirmation;
8. stage a newly generated signed probe;
9. import/replace the probe and execute it;
10. record device inventory/version/receipt state.

Only after the above passes should these primitives be treated as stable
building blocks for higher-level agent workflows.
