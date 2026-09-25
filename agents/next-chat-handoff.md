# Next-chat handoff

Updated: 2026-09-25 UTC.

## Read first

1. [Current harness architecture](../docs/architecture/current-harness.md)
2. [Execution boundaries](../docs/architecture/execution-boundaries.md)
3. [Shortcut Worker status](../docs/implementation/shortcut-worker-status.md)
4. [Protocol](../examples/shortcut-worker/protocol.json)
5. [GitHub issue #4](https://github.com/collinsomniac/shortcut-optimization/issues/4)

## Current preferred path

Do **not** restart from clipboard injection or imported
`GenerateShortcutAction`.

### 1. Pure-native persistent manager

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

Inspect the latest stager workflow run before claiming a signed/device-compatible
stager exists.

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

1. Check latest stager CI.
2. Make exact v0.3 manager signed artifact available for phone import.
3. User imports v0.3; test only `capabilities` and `list`.
4. Test the parameterized runner independently.
5. Once stager passes, install it and stage a harmless signed Shortcut.
6. Repair `desktop.exec` leasing; verify VS Code detection/launch.
7. Update canonical docs/issue after each empirical result.
