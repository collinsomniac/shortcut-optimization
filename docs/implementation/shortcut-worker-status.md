# Shortcut Worker implementation status

Snapshot: 2026-09-24.

This page records what is **live and verified**, what is staged but not yet verified on the phone, and the current bootstrap boundary.

## Live and verified

### Existing harness
- `iphone-main` is live on iOS 27.0 and can be woken through the existing Pushcut/Supabase path.
- Fresh `harness.info`, `phone.info`, and `shell.exec.simple` requests complete through the existing queue.
- `desktop-main` remains a separate executor on the same control plane; the Shortcut subsystem does not require agents to fall back to desktop execution.

### Shortcut domain in Supabase
Internal `shortcuts` schema:
- `inventory`
- `versions`
- `capability_snapshots`
- `receipts`
- `callbacks`
- `artifacts`

Existing public queue/result/worker tables remain unchanged.

Service-role facades include:
- `submit_shortcut_job(operation, params, ttl)` → `iphone-main / shortcuts.control`
- `sync_shortcut_inventory(worker, items, complete)`
- `issue_shortcut_callback(...)`
- callback consumers
- short-lived artifact issue/resolve/complete functions

The v0.2 job facade allows:
`register, capabilities, list, get, run, open, generate, edit, rename, move, delete, create_link`.

### Edge Functions
Active:
- `harness-worker`
- `shortcut-callback`
- `shortcut-artifact`
- `shortcut-bootstrap`

The callback endpoint has successfully accepted one-time-token and structured POST probes from the phone. Keep this distinct from Apple's x-callback flow: direct callback transport is verified; a Shortcuts x-callback run has not yet produced a verified receipt in this setup.

### Generation / signing research
The public iCloud donor "Generate Shortcut Action (OS 27)" was artifact-inspected:
- CloudKit record reports Apple-approved signing status.
- Raw workflow is 978 bytes.
- It contains exactly one action: `com.apple.shortcuts.GenerateShortcutAction`.
- The AppIntent descriptor is `GenerateShortcutAction`.

The current v0.2 bootstrap source contains:
- `register`
- `callback_url`
- `controller_version "0.2"`
- list/run/open/generate/rename/move/delete/create_link/get
- an explicit native `edit = unsupported` result until builder/compiler editing exists.

A non-sensitive v0.2 bootstrap was signed through RoutineHub HubSign and is served by `shortcut-bootstrap`. This external signer must **not** be treated as the default for workflows containing secrets or private embedded data.

### Deterministic inventory path
A one-action deterministic probe was constructed from the known-good workflow envelope by replacing Generate Shortcut with:
`is.workflow.actions.getmyworkflows` (Get My Shortcuts).

This proves the compiler path no longer has to depend on Apple Intelligence for basic inventory. The signed-probe import action was blocked by the execution guard in this agent environment before reaching the phone, so phone import/execution is **not** claimed.

## Current iOS bootstrap boundary

The signed v0.2 bootstrap import handoff and bootstrap run URLs were launched on the phone, followed by a direct `register` invocation. However, a subsequent `harness.info` still showed only the original Tools set and direct RPC to `shortcuts.control` still returned `tool_not_found`.

Therefore one of these remains true:
1. the import/generation UI requires a visible Apple confirmation;
2. Generate Shortcut did not materialize the requested controller;
3. the generated controller did not complete registration into Tools.

Do not claim the controller is installed until `harness.info` advertises it or a `submit_shortcut_job('capabilities')` call succeeds.

## Filesystem boundary verified

a-Shell runs inside its own App Group. A recursive scan of its accessible current workspace found no Shortcut library folders or `.shortcut` files, and direct access to the private Shortcuts SQLite path is sandbox-blocked.

Thus:
- Shortcuts **library folders** such as Tools are not filesystem folders.
- Native library inventory should use Get My Shortcuts.
- File-style exploration applies after explicit export into a worker-owned Files/iCloud workspace.

## Security note — action required before wider exposure

Supabase currently reports RLS disabled on:
- `shortcuts.inventory`
- `shortcuts.versions`
- `shortcuts.capability_snapshots`
- `shortcuts.receipts`
- `shortcuts.callbacks`

Explicit grants to `anon`/`authenticated` were revoked and the schema is intended to remain non-exposed, but Supabase still flags this as a critical defense-in-depth issue. Do **not** silently enable RLS without deciding the access model, because RLS with no policies can block intended access.

The generated migration SQL suggested by Supabase is:

~~~sql
ALTER TABLE shortcuts.inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE shortcuts.versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE shortcuts.capability_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE shortcuts.receipts ENABLE ROW LEVEL SECURITY;
ALTER TABLE shortcuts.callbacks ENABLE ROW LEVEL SECURITY;
~~~

Review this together with exposed-schema configuration and service-role-only RPC requirements before applying it.

## Next validation sequence

Once the visible bootstrap/controller is confirmed on-device:
1. run `submit_shortcut_job('register')`;
2. verify `harness.info` discovers `shortcuts.control`;
3. run `capabilities`;
4. run `list` and sync it into `shortcuts.inventory`;
5. generate a benign echo shortcut into `Agent Generated`;
6. create its iCloud link;
7. execute and capture a verified callback/receipt;
8. rename and move it;
9. call delete with `confirm=false` and verify refusal;
10. confirmed cleanup of test artifacts.

## Remaining engineering work
- Complete the on-device bootstrap/registration boundary.
- Normalize native inventory fields actually returned by iOS.
- Export artifacts and compute content/version hashes.
- Enumerate available App Intents/actions on the device.
- Add compiler/builder structural `get/diff/edit`.
- Make the phone dispatcher understand a dedicated Shortcuts module/folder instead of requiring the first controller to live in generic Tools.
- Replace or tightly scope third-party signing for production/private artifacts.
