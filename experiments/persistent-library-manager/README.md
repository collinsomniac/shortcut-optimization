# Persistent library manager

Status: **bootstrap signed and publicly staged; generated manager not yet device-verified**  
Updated: 2026-09-25 UTC.

## Goal

Create one durable Shortcut named:

`harness.shortcuts.library`

that handles the stable/native library-management plane and can be invoked
repeatedly without regenerating workflow logic.

The resulting manager is intended to persist in the Shortcuts library.

## Supported semantic operations

Requested from Apple's iOS 27 generator:

- `capabilities`
- `list`
- `create`
- `run`
- `open`
- `rename`
- `move`
- `create_folder`
- `open_folder`
- `create_link`
- `get_attributes`
- guarded `delete`

It must return structured dictionaries and use exact-name resolution for
mutating operations.

It intentionally returns `unsupported_content_operation` for:
- `duplicate`
- `edit`

Those belong to the artifact/content plane, not the stable native management
plane.

## Why persistent

The harness should not generate the same Shortcut every time an agent wants to
run it.

High-level `shortcuts.ensure(spec)` should:
1. inventory installed objects;
2. resolve the project-side `shortcut_ref`;
3. compare desired version/hash;
4. reuse when current;
5. update or clone only when changed.

Generation is a compile/install event. Execution should normally call an
already-installed persistent object.

## Bootstrap

The one-time bootstrap is a generic one-action Shortcut containing
`com.apple.shortcuts.GenerateShortcutAction`. Its prompt lives at:

`examples/shortcut-worker/library-manager-bootstrap-prompt.txt`

It contains no private harness contents.

Signed artifact:
- name: `SO Library Manager Bootstrap`
- bytes: 23,247
- container: `AEA1`
- SHA-256: `ba26c9241d4a7e88c6bdadf310ed5a99dbecebf269b764a48c76c0ca5aaddb57`
- external signer: RoutineHub HubSign
- intended generated object: `harness.shortcuts.library`

The signed bytes are embedded in the deliberately whitelisted
`shortcut-public-artifact` Edge Function under
`name=library-manager-bootstrap`.

External signing is acceptable here because the bootstrap is generic and does
not contain user/private Shortcut data.

## Device validation sequence

1. Install `SO Library Manager Bootstrap`.
2. Run it once and allow Apple's native Generate Shortcut action to create
   `harness.shortcuts.library`.
3. Open the generated manager and inspect the actual action graph.
4. Exercise `capabilities`.
5. Exercise read-only `list`.
6. Create a disposable test Shortcut.
7. Rename/move/open/run it.
8. Create an iCloud link only for that disposable fixture.
9. Verify delete with `confirm=false` refuses.
10. Delete the disposable fixture with explicit confirmation.
11. Only after these tests route the Supabase `shortcuts.*` facade to this
    installed manager.

Do not claim the generated manager is correct merely because the bootstrap
runs. The Apple-generated action graph must be inspected and empirically tested.
