# Shortcut Worker implementation status

Snapshot: 2026-09-23/24.

This page records what is **live** versus what is still a bootstrap dependency.

## Live now

### Existing harness
- `iphone-main` can be woken remotely through the existing Pushcut/Supabase path.
- Fresh `harness.info` succeeds and advertises the existing core/tests/tools/drivers registry.
- Existing tool methods such as `shell.exec.simple` execute and return through `rpc_results`.
- `desktop-main` remains online under the existing desktop-worker v1.4 control plane.

### Shortcut domain in Supabase
The shared project now has an internal `shortcuts` schema containing:
- `inventory`
- `versions`
- `capability_snapshots`
- `receipts`
- `callbacks`

Legacy queue/result/worker tables remain unchanged.

Service-role-only functions:
- `submit_shortcut_job(operation, params, ttl)` → routes to `iphone-main / shortcuts.control`
- `issue_shortcut_callback(request_id, ttl)`
- `consume_shortcut_callback(...)` for the Edge Function only

### Result callback
`shortcut-callback` Edge Function is deployed with custom one-time-token authentication. An end-to-end phone probe successfully changed a callback row from pending → success and stored the result. This is the basis for verified run/x-callback receipts.

### Generation research
- The shared iCloud “Generate Shortcut Action (OS 27)” record was fetched from the phone.
- Its CloudKit record reports `signingStatus=APPROVED`.
- Its raw 978-byte plist was parsed and verified to contain exactly one action:
  `com.apple.shortcuts.GenerateShortcutAction`.
- The action has AppIntent identifier `GenerateShortcutAction` and a literal natural-language `prompt`.
- `tooling/build_generate_shortcut_bootstrap.py` can harvest that approved donor and replace only the prompt to produce an unsigned bootstrap.
- GitHub-hosted macOS was tested as a signing service. The `shortcuts` CLI is installed, but `shortcuts sign` fails because the ephemeral runner is not signed into iCloud. Do not treat GitHub Actions as an Apple signer.

## Current bootstrap blocker

The iPhone dispatcher does not yet have a `shortcuts.control` tool in its searchable Tools collection. A service-facade probe successfully reached the phone but correctly returned `tool_not_found`.

The phone has been staged for the one-time native bootstrap:
1. the exact controller prompt is in `examples/shortcut-worker/bootstrap-prompt.txt`;
2. the live iPhone clipboard was populated from that file;
3. `shortcuts://create-shortcut` was opened.

The user needs to paste/send the prompt in iOS 27 Describe a Shortcut, allow generation to complete, and place the resulting `shortcuts.control` workflow into the existing harness Tools folder.

After that, the next validation sequence is:
1. `submit_shortcut_job('capabilities')`
2. `submit_shortcut_job('list')`
3. sync inventory into `shortcuts.inventory`
4. generate a benign echo/test shortcut into an Agent Generated folder
5. create an iCloud link
6. execute with x-callback receipt
7. rename/move it
8. test delete with `confirm=false`, then clean it up with confirmed delete.

## Security note

The Shortcut tables live in a non-exposed custom schema and grants to `anon`/`authenticated` were revoked. RLS itself is currently disabled on these internal tables; Supabase's generic table inspection therefore emits an RLS warning. Enabling RLS with no client policies is a reasonable defense-in-depth follow-up, but was intentionally not auto-applied during this pass because it changes the database access model.

## Remaining work

- Native inventory normalization: exact name/folder/native identifier representation returned by iOS.
- Device action/AppIntent inventory.
- Version hashes based on native export artifacts.
- Structural `get/diff/edit` beyond Apple Intelligence builder semantics.
- Dedicated `shortcuts` folder support in the phone dispatcher rather than colocating the first controller with generic Tools.
- Optional desktop compiler adapter using Shortcuts Playground's iOS 27 static ToolKit catalogs for design/validation.
