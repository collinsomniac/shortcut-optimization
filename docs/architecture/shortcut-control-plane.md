# Shortcuts control plane

Updated: 2026-09-26.

This is the canonical agent-facing model for Shortcuts. Agents should reason in
terms of primitives below, not helper Shortcut filenames, URL schemes, a-Shell
commands, HubSign requests, or Pushcut implementation details.

## Layers

| Layer | Primitive | Current implementation | Status |
| --- | --- | --- | --- |
| Author | `shortcuts.generate` | Cherri / deterministic plist construction | working |
| Compile | `shortcuts.compile` | pinned Cherri → XML plist / unsigned shortcut | working |
| Sign | `shortcuts.sign` | `shortcuts.artifacts` + HubSign + SHA-256 cache | working |
| Transfer | `shortcuts.install` | stable signed artifact URL → native `shortcuts.open_url` | device verified handoff |
| Register | `shortcuts.install` | Apple native signed import/replace | user confirmation boundary |
| Inspect | `shortcuts.list/get` | resident `shortcuts.control` | list verified; get route verified |
| Execute | `shortcuts.run` | resident controller → Run Shortcut | device verified input/output |
| Manage | `shortcuts.create/rename/link` | first-party Shortcuts App Intents | create/rename typed fixes in v0.8; device acceptance pending |
| Organize | `shortcuts.create_folder/move_new_folder` | typed Create Folder + Move Shortcut | v0.8 compiled/signed; device acceptance pending |
| Edit content | `shortcuts.edit` | generate a replacement signed artifact, then import/replace | compiler path working; registration boundary remains |
| Verify | receipt/callback | controller/stager HTTP POST → `shortcuts.callbacks` | broker implemented; device proof pending |

## Resident device components

### `shortcuts.control`

The controller is the local library authority only. It does not compile or sign
workflow content and it does not stage files.

Current v0.8 operations:

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

The controller accepts JSON text from the resident RPC worker and returns its result directly to the worker. v0.8 removes the old callback dependency entirely; the worker result is the canonical completion path. The installed v0.5 build still needs a callback as a compatibility workaround until v0.8 replaces it.

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

The live worker router now has two verified explicit native branches:

- `shortcuts.control` → Run the installed `shortcuts.control` with JSON request input and return its child output through normal RPC completion;
- `shortcuts.open_url(url)` → first-party Open URLs, used for signed artifact handoff.

Both have completed zero-touch on the target phone. Normal agents should use the server-side facade `private.shortcut_call(op, params, ttl)`; controller updates use `private.shortcut_install_controller(ttl)`. The worker does not need a-Shell for Shortcuts control.

### a-Shell boundary

a-Shell remains useful for terminating shell computation only. Controlled
no-wake tests show that a-Shell `openurl` does not reliably re-enter the
Shortcuts worker, even when opening:

- `shortcuts://run-shortcut?name=RPC Worker Harness`;
- an HTTPS page that immediately redirects to that Shortcuts URL.

Do not use a-Shell, Safari, or x-callback as the Shortcuts registration or
execution bridge.

### Registration path

The verified registration handoff is:

```
signed artifact
→ stable HTTPS endpoint
→ native worker `shortcuts.open_url`
→ Apple's Add/Replace Shortcut surface
→ user confirmation
→ native inventory/version verification
```

Do not treat `opened=true` as installation proof. Legacy `silent=true` import attempts did not produce a reliable registered result on the target iOS 27 phone, so silent import is not a core dependency.

Agent-built workflows are signed with `WFWorkflowIsDisabledOnLockScreen = false`, so imported tools are eligible for locked execution after registration.

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

The only core resident artifact is now `shortcuts.control` v0.8.

Stable endpoint:

`https://zpdtlzpvshlpyqbfbzye.supabase.co/functions/v1/shortcut-bootstrap`

Expected v0.8 SHA-256:

`5128c52f0633df61102d5aa6f805a97629bf02c9c5954b1f16340730556b411e`

`harness.shortcuts.stage` remains compatibility/research tooling rather than a prerequisite.

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


## Live consolidation — 2026-09-26

Empirically verified on the target phone:

- Pushcut zero-touch wake;
- request lease/completion in `RPC Worker Harness`;
- explicit `shortcuts.control` routing;
- controller `ping`;
- live library `list`;
- `run` with arbitrary input and exact returned output using `probe.echo`;
- explicit `shortcuts.open_url` native artifact handoff;
- stable v0.8 controller artifact endpoint;
- server-side `private.shortcut_call(op, params, ttl)` facade;
- server-side `private.shortcut_install_controller(ttl)` update facade;
- stale RPC lease reaping.

Observed implementation bugs in installed v0.5:

- empty optional callback degraded to `Get Contents of URL` with no URL;
- raw Create Shortcut serialization created `New Shortcut` instead of the requested name;
- raw Rename Shortcut serialization degraded the name field into an interactive text prompt.

v0.8 removes callback networking and uses typed Cherri/AppIntent serialization for create, rename, folder creation, and move. These mutation fixes are compiled/signed but still require device acceptance after v0.8 replacement.

Delete remains outside the stable surface until its entity serialization and postcondition are verified. Do not use it merely because the older controller advertises it.
