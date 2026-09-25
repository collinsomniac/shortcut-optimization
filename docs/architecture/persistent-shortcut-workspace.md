# Persistent Shortcut workspace

Updated 2026-09-25.

## Core rule

Generated Shortcuts are **persistent library objects**, not disposable prompts.

An agent should normally:

1. ask `shortcuts.inventory.list`;
2. resolve a project-side `shortcut_ref`;
3. compare the installed version/hash with the requested spec;
4. reuse the installed Shortcut when current;
5. update/clone only when the desired behavior differs;
6. execute the persistent object by reference/name;
7. snapshot meaningful versions for rollback.

This avoids repeated model calls and token-heavy regeneration.

## Canonical folders

Target organization:

~~~text
harness.core/
harness.tools/
harness.drivers/
harness.tests/
harness.shortcuts/   # Shortcut-management/editor/compiler helpers

Agent Generated/     # durable task/workflow Shortcuts created by agents
Archive/             # optional retired snapshots/imports
~~~

The existing folder-scoped `harness.info` should eventually include
`harness.shortcuts`, or be replaced by a registry-driven manifest.

## Native management surface

The iOS 27 action catalog and the live device expose a much broader native
management surface than the original design assumed. Relevant first-party
actions include:

- Create Shortcut
- Delete Shortcuts
- Get/Set Shortcut Attributes
- Move Shortcut
- Open Shortcut
- Rename Shortcut
- Run Shortcut / Run Shortcut from Folder
- Create/Open Folder
- Create iCloud Link for Shortcut
- Change Shortcut Icon
- Search in Shortcuts / Search Shortcuts Actions
- Add Shortcut to Home Screen
- Get My Shortcuts (legacy action identifier)

See `harness/shortcuts/native-capabilities.json` for identifiers and evidence
status.

Apple documents Create/Delete/Open Folder as first-party Shortcuts actions since
iOS 16 and Move/Rename plus Create Folder/Create iCloud Link in iOS 18 release
notes. The live iOS 27 Shortcuts Playground catalog exposes the richer current
AppIntent set.

## Duplication

There is a UI-level Duplicate command, but no dedicated first-party Duplicate
Shortcut AppIntent was found in the inspected iOS 27 catalog.

Therefore semantic `shortcuts.duplicate` should hide the implementation:

1. preferred: snapshot/export → clone artifact → change identity/name → trusted
   import;
2. if action-pasteboard is verified: Create Shortcut → inject copied action
   chain → rename/move;
3. final fallback: native UI Duplicate.

The user should never need to care which route was used.

## Declarative ensure

The most important high-level operation is:

~~~text
shortcuts.ensure(spec)
~~~

Example conceptual input:

~~~json
{
  "ref": "shortcut://project/research-capture",
  "name": "Research Capture",
  "folder": "Agent Generated",
  "desired_spec_hash": "sha256:...",
  "update_policy": "patch_if_changed"
}
~~~

Possible results:

- `reused` — already installed/current;
- `updated` — existing object patched;
- `installed` — new persistent object created;
- `conflict` — native object changed since the agent read it.

This is the answer to repeated generation cost: generation is a compile/install
step, not the execution loop.

## Editing versus management

Keep these separate:

**Management plane** — native, stable, cheap:
inventory/create/run/open/rename/move/folders/attributes/share/delete.

**Content plane** — harder:
get graph/diff/edit/duplicate/export/install.

The native management plane should become reliable first. Content editing may
select among deterministic artifact patching, action-pasteboard injection,
Apple Intelligence generation, or UI fallback.

## Current action-pasteboard experiment

The earlier Paste test was inconclusive because the helper was invoked with
`input=clipboard` after an a-Shell clipboard write that could not be read back.
On 2026-09-25 the same committed two-action fixture was re-invoked by passing
the JSON directly as `input=text`, bypassing system clipboard staging.

Device confirmation is still needed: reopen an action context menu after that
invocation. If Paste appears and the two-card fixture survives, the helper stays
as a local content-edit backend. If not, demote it and rely on artifact
import/export plus native management.

## Third-party surfaces visible on the device

The screenshots also confirm:
- Actions app: Set Uniform Type Identifier, Manage Shortcut Lock, Hide Shortcuts App;
- Pushcut: Schedule Shortcut and Run Shortcut (via Pushcut);
- two additional visible actions named Export Shortcuts / Import Shortcuts whose
  provider still needs to be identified before we depend on them.

Pushcut's documented Automation Server can enumerate/run shortcuts as server
actions and accepts input/returns responses, but it requires its server app to
remain foreground. It is useful as an execution transport, not as the canonical
library database.
