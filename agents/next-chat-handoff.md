# Next-chat handoff

Updated: 2026-09-26 UTC.

## Read first

1. [Shortcuts control plane](../docs/architecture/shortcut-control-plane.md)
2. [Current harness architecture](../docs/architecture/current-harness.md)
3. [Execution boundaries](../docs/architecture/execution-boundaries.md)
4. [Shortcut Worker status](../docs/implementation/shortcut-worker-status.md)
5. [Protocol](../examples/shortcut-worker/protocol.json)
6. [GitHub issue #4](https://github.com/collinsomniac/shortcut-optimization/issues/4)

## Current preferred path

Do **not** restart from clipboard injection or imported
`GenerateShortcutAction`.

### 1. Resident native controller

`shortcuts.control` v0.8

This supersedes `harness.shortcuts.library` as the agent-facing local authority. The older manager remains a compatibility/test fixture only.

Current source: `examples/shortcut-worker/harness.shortcuts.control.cherri`

Stable signed bootstrap endpoint:
`https://zpdtlzpvshlpyqbfbzye.supabase.co/functions/v1/shortcut-bootstrap`

Verified response: `application/x-apple-shortcut`, 37,468 bytes,
SHA-256 `5128c52f0633df61102d5aa6f805a97629bf02c9c5954b1f16340730556b411e`,
signed workflow name `shortcuts.control`, version header `0.8`.

v0.8 removes callback networking and self-registration. The resident worker now explicitly routes `shortcuts.control` and `shortcuts.open_url`.

Legacy manager reference:

`harness.shortcuts.library` v0.3

- source: `examples/shortcut-worker/harness.shortcuts.library.cherri`
- green CI: `36200258576`
- signed SHA-256:
  `6c544ab7c186e9fead24bcdac30cf107f79c48ffba4550b6016c99c03cae57a6`
- 29,817 bytes / AEA1
- 176 actions
- no a-Shell, network, model, or third-party actions

Use it for native library CRUD/run only.

### 2. Parameterized runner

Builder prompt:
`examples/shortcut-worker/parameterized-runner-builder-prompt.txt`

Target:
`harness.shortcuts.run`

Use this to test repeatedly running arbitrary already-installed Shortcuts with
JSON `name` + optional `input`.

### 3. Pure-native artifact stager

Source:
`examples/shortcut-worker/harness.shortcuts.stage.cherri`

Target flow:
signed artifact URL → Download URL → Save File → Open File → Apple Add Shortcut
sheet.

Apple's final import confirmation remains the trust boundary.

Green CI: `36200750546`.
Signed stager:
- 26,934 bytes / AEA1;
- SHA-256 `e21b977817577bf03d9b3b3364f53568e8994dfeaa04d9018b0f6e325bc395b0`.

Compilation/schema/signing are verified. Device staging/import behavior is not.

## Executor policy

- **iPhone/Shortcuts:** native library authority and execution.
- **desktop-main:** Cherri, parsing, diffing, validation, signing preparation,
  Git, heavy terminal work.
- **a-Shell:** optional narrow adapter only.
- **VS Code:** optional UI, never a prerequisite for the worker.

Desktop heartbeat is live, but recent `desktop.exec` requests remained
unleased. Verify leasing before claiming automatic VS Code launch.

## Known failed/deprioritized routes

- Imported `GenerateShortcutAction`: target iPhone rejected the signed artifact
  as containing unsupported features.
- `SO-Copy-Actions`: imported, but no usable Paste/Paste Below insertion was
  reproduced; still UI-bound even in the best case.

## Important platform boundary

`Create Shortcut` is grounded as creating an empty Shortcut by name and
optionally opening it. Do not treat it as arbitrary action-graph installation.

Full new workflow path:

~~~text
agent
→ desktop/CI compile
→ normalize/validate
→ sign
→ iPhone stager
→ Apple import confirmation
→ persistent installed Shortcut
→ parameterized/native runner for future executions
~~~

## User intent

The user is comfortable treating Shortcuts primarily as an agent-managed
workspace. Desired experience is natural semantic tools:
create/generate, inspect, organize, run, edit/version, duplicate, share, and
delete with confirmation.

Heavy terminal work should live on desktop rather than being forced into
a-Shell. The desktop worker should eventually be able to ensure VS Code is
running without physical desktop presence.

## Immediate next actions

1. Complete Apple's Add/Replace confirmation for `shortcuts.control` v0.8 if the sheet is still pending.
2. Probe `private.shortcut_call('ping', ...)` until the device reports v0.8.
3. Re-run disposable acceptance in order: create → get → rename → create folder/move → get.
4. Do not test delete until its native entity serialization is separately grounded and compiled.
5. Keep `harness.shortcuts.library`, `harness.shortcuts.stage`, and `harness.shortcuts.run` as compatibility/research fixtures, not prerequisites.
6. Prefer `private.shortcut_call(op, params, ttl)`; controller update handoff is `private.shortcut_install_controller(ttl)`.
7. Heavy compile/diff/sign work remains on CI/desktop; a-Shell is not on the Shortcuts critical path.

## Latest device-facing test state — 2026-09-25 UTC

- ChatGPT-hosted v0.3/v0.1 attachment downloads failed before Shortcuts import.
  Do not treat this as a Cherri/device rejection.
- A stable Supabase compatibility endpoint is deployed and CI-verified for all
  11 signed fixtures in `public/shortcut-import-compat/manifest.json`.
- Test fixtures in order and stop at the first meaningful import failure.
- Cherri compact builds are dramatically smaller than old `--comments` builds:
  basic 1/37 actions, manager 134/176, stager 24/115.
- User has an Apple-generated `harness.shortcuts.run`; verify it against
  installed `probe.echo` with input `RUNNER_PROBE_001`.
- A native `harness.shortcuts.fetch` builder prompt exists as fallback if
  direct HTTPS attachment delivery behaves inconsistently.


### Live bootstrap verification — 2026-09-25 late evening

- zero-touch request `53bbcd96-cad1-4cf4-b94f-c533f0236e5f` proved
  `shortcuts.run` is still absent from the installed resident worker:
  wake/lease/completion succeeded and the inner result was `tool_not_found`;
- Pushcut Automation Server probe returned HTTP 502 because no linked iOS device
  is currently running Automation Server;
- therefore the remaining one-time native boundary is either:
  1. apply `rpc-worker-zero-touch-bootstrap-prompt.txt` surgically to the
     existing `RPC Worker Harness`, or
  2. install/run `shortcuts.control` v0.8 once so it moves itself into the
     existing tools folder.
- after either path, immediately submit `shortcuts.run` / `shortcuts.control`
  probes and continue create → run → rename → move → delete acceptance tests.


### Zero-touch control milestone — 2026-09-26

Verified on the target phone:

- `shortcuts.control` worker branch: working;
- `ping`: working;
- `list`: working against the real library;
- `run probe.echo` with caller-provided input: exact output returned;
- `shortcuts.open_url`: working and returns `{"opened":true}`;
- `private.shortcut_call`: working;
- `private.shortcut_install_controller`: working;
- stale lease reaper: working.

Installed v0.5 bugs:
- empty callback causes `Get Contents of URL` / no-URL error;
- raw create produced `New Shortcut` instead of requested name;
- raw rename produced an interactive text prompt.

v0.8 fixes callback removal and typed create/rename/folder/move serialization. The v0.8 artifact has been opened on-device but a version probe still reports v0.5, so Apple replacement confirmation remains pending at this handoff.
