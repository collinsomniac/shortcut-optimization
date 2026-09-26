# Next-chat handoff

Updated: 2026-09-25 UTC.

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

`harness.shortcuts.control` v0.3

This supersedes `harness.shortcuts.library` as the agent-facing local authority. The older manager remains a compatibility/test fixture only.

Current source: `examples/shortcut-worker/harness.shortcuts.control.cherri`

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

1. Install/update `harness.shortcuts.control` v0.3 from the immutable compatibility endpoint.
2. Test controller `ping` with its direct HTTP callback, then `list`.
3. Use Pushcut notification default-action transport as the reliable one-tap main-phone route; do not route normal controller calls through a-Shell.
4. Verify `run` against a deterministic echo target.
5. Exercise disposable create → rename → move_new_folder → delete.
6. Update/install `harness.shortcuts.stage` v0.2 and verify its callback-before-import handoff.
7. Test signed replacement/import and execution proof.
8. Keep zero-touch wake and legacy silent import as separate platform-boundary research.
9. Separately repair `desktop.exec` leasing for private arbitrary compilation.


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
