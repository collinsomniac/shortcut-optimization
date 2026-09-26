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

Current v0.5 operations:

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

### Zero-touch main-phone transport

Zero-touch wake is empirically proven on the user's main iPhone:

```
Supabase pending RPC
→ Pushcut Harness Wake notification
→ iOS 27 Notification automation
→ RPC Worker Harness
→ lease request
→ execute
→ complete to Supabase
```

The iOS automation is Pushcut, no notification filters, Run Immediately, with
Allow Running When Locked enabled. This is not Pushcut Automation Server.

Fresh `probe.echo` tests complete without a tap while the user remains in
another app.

### Native Shortcuts bridge

The current worker router is explicit/hardcoded. The minimal bootstrap patch is:

- `shortcuts.open_url(url)` → first-party Open URLs;
- `shortcuts.run(name,input)` → Get My Shortcuts + exact-name native Run Shortcut.

After those two methods exist, signed registration and execution stay entirely
inside Shortcuts. The worker does not need a-Shell for Shortcuts control.

### a-Shell boundary

a-Shell remains useful for terminating shell computation only. Controlled
no-wake tests show that a-Shell `openurl` does not reliably re-enter the
Shortcuts worker, even when opening:

- `shortcuts://run-shortcut?name=RPC Worker Harness`;
- an HTTPS page that immediately redirects to that Shortcuts URL.

Do not use a-Shell, Safari, or x-callback as the Shortcuts registration or
execution bridge.

### Registration path

The preferred registration primitive is the native Shortcuts URL importer,
opened from inside the already-running Shortcuts worker:

```
shortcuts://import-shortcut?url=<signed-artifact-url>&silent=true
```

Current Apple documentation still describes x-callback completion after a
Shortcut is imported, and iOS 27 binaries retain the signed Shortcut import
engine. The final empirical gate is invoking this route from the native worker,
rather than through a-Shell.

Agent-built workflows are signed with
`WFWorkflowIsDisabledOnLockScreen = false`, so imported tools are immediately
eligible for locked execution.

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

- `shortcuts.control` v0.5
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

## iOS notification timeout finding — 2026-09-25

The iOS notification banner

`pushcut.wake — Could not run Execute Command — The operation took too long to complete`

does **not** mean the Pushcut wake or native RPC dispatcher failed.

Measured on the target phone:

- a Pushcut wake for `harness.info` leased after roughly 3.5 seconds and the
  native tool completed in under one second with no user interaction;
- `probe.echo` likewise completes natively and returns arbitrary JSON/text;
- requests that enter `shell.exec.simple` can lease successfully and then
  surface the Execute Command timeout notification.

The failing boundary is a-Shell's `Execute Command` App Intent / app-switch
lifetime, not the Pushcut notification trigger and not nested Shortcuts in
general.

a-Shell source confirms two execution paths. Its intent extension treats a
small allowlist as lightweight commands expected to finish quickly; commands
outside that set continue in the full app. `openurl` is allowlisted, but its
implementation schedules URL opening through an app/window delegate, so URL
handoff is not a reliable completion primitive from the extension. Wrapping
`openurl` in `python3` forces the full-app path and is especially unsuitable
for a locked/background wake.

Policy:

- the zero-touch critical path MUST remain pure Shortcuts after Pushcut wake;
- do not route `shortcuts.*` through a-Shell;
- a-Shell remains an explicitly requested bounded compute adapter;
- shell RPC completion is never proof that a URL-handoff Shortcut executed;
- distinguish `wake_requested`, `leased`, `native_completed`,
  `handoff_launched`, and application-level `verified`.


## Bootstrap status — 2026-09-25 late evening

Live zero-touch probe request `53bbcd96-cad1-4cf4-b94f-c533f0236e5f`
proved the current installed worker still returns `tool_not_found` for
`shortcuts.run`. Wake, lease, and completion all succeeded, so this is a
router-capability failure rather than a transport failure.

Pushcut Automation Server was also probed using the existing Vault-held account
secret without exposing it. Pushcut returned HTTP 502 with
`Automation Server is currently not running on any iOS device linked to this account.`
Do not make Automation Server a bootstrap dependency for the main phone.

`shortcuts.control` v0.5 is now designed for a one-time native bootstrap:

- its signed workflow name is exactly `shortcuts.control`;
- it contains no a-Shell dependency;
- an ordinary first run with no Shortcut Input defaults to `bootstrap`;
- `bootstrap` finds the installed `probe.echo` entity, gets its Folder entity,
  and moves `shortcuts.control` into the same live tools folder;
- after that, the existing folder-scoped dispatcher can discover the controller
  without another library move.

The preferred long-term bootstrap remains the surgical in-place worker edit in
`examples/shortcut-worker/rpc-worker-zero-touch-bootstrap-prompt.txt`, adding
only `shortcuts.open_url` and `shortcuts.run`. Replacing the entire resident
worker is avoided because the Pushcut automation already references the proven
worker identity.
