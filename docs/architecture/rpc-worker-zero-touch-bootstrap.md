# RPC Worker Harness v2 — zero-touch Shortcuts bootstrap

Updated: 2026-09-25.

## Purpose

This is the one-time bootstrap patch that turns the already-working
`RPC Worker Harness` wake path into a permanent zero-touch Shortcuts control
plane.

Do not replace Pushcut, the iOS Notification automation, worker authentication,
or the existing queue transport.

Known-good wake remains:

```
Supabase rpc_requests
→ Pushcut Harness Wake notification
→ iOS 27 Notification automation (Pushcut, no filters, Run Immediately)
→ RPC Worker Harness
→ harness-worker Edge Function
```

## Why this patch is necessary

The current worker router is explicit/hardcoded. Live tests prove that advertised
but unrouted names such as `tool.exec`, `safari.open.url`,
`supabase.worker.http.test`, and an older `Harness Echo` all return
`tool_not_found`.

a-Shell's `openurl` is not a substitute. Controlled tests seeded a second
queue request without a Pushcut wake and then used a-Shell to open both a
`shortcuts://run-shortcut` URL and an HTTPS→Shortcuts trampoline. Neither
caused `RPC Worker Harness` to run.

Therefore the missing authority is exactly one native bridge inside Shortcuts.

## Add exactly two worker methods

### 1. `shortcuts.open_url`

Request:

```json
{
  "method": "shortcuts.open_url",
  "params": {
    "url": "shortcuts://import-shortcut?url=...&silent=true"
  }
}
```

Implementation inside `RPC Worker Harness`:

1. Read `request.params.url`.
2. Validate it is non-empty.
3. Use the first-party **Open URLs** action on that URL.
4. Return a structured success result if execution continues:
   ```json
   {"opened": true}
   ```
5. If Open URLs transfers execution and the parent does not resume, the server
   must not treat worker completion as registration proof. Registration is
   verified with the next `shortcuts.run`/inventory request.

This method is intended primarily for the signed import route:

```
shortcuts://import-shortcut?url=<percent-encoded-signed-shortcut-url>&silent=true
```

Do not route this through a-Shell or Safari.

### 2. `shortcuts.run`

Request:

```json
{
  "method": "shortcuts.run",
  "params": {
    "name": "harness.import.probe.v4",
    "input": "optional text input"
  }
}
```

Implementation:

1. Read `request.params.name` and `request.params.input`.
2. Get My Shortcuts.
3. Resolve exactly one Shortcut whose Name equals `name`.
4. If none exists, return:
   ```json
   {"ok": false, "error": {"code": "shortcut_not_found", "name": "..."}}
   ```
5. Run the resolved Shortcut with `input`.
6. Return its actual output as the request result.

Prefer a native Run Shortcut action. Do not construct a
`shortcuts://run-shortcut` URL.

## Lock-screen policy

Agent-built workflows must be signed with:

```xml
<key>WFWorkflowIsDisabledOnLockScreen</key>
<false/>
```

This is the serialized equivalent of **Allow Running When Locked**.

The project build pipelines set this before signing for resident agent
artifacts.

## First acceptance test after bootstrap

The currently published generic probe is:

- name: `harness.import.probe.v4`
- behavior: HTTPS callback only; no a-Shell, no app-opening action, no UI
- direct serving endpoint:
  `https://zpdtlzpvshlpyqbfbzye.supabase.co/functions/v1/shortcut-device-probe`

Sequence:

1. Agent submits `shortcuts.open_url` with a native import URL targeting the
   signed v4 endpoint and `silent=true`.
2. Pushcut wakes the existing worker zero-touch.
3. Worker executes Open URLs from inside Shortcuts.
4. Agent submits `shortcuts.run` for `harness.import.probe.v4`.
5. The v4 Shortcut POSTs its own HTTPS callback.
6. Pass only if the callback result is exactly
   `harness-import-probe-v4-executed`.

This proves:

```
remote wake
→ native silent signed registration
→ installed-library resolution
→ locked execution
→ independent HTTPS receipt
```

## After that passes

Install `harness.shortcuts.control` and/or smaller single-purpose tools via
the same path. Higher-level management can remain modular because arbitrary
installed Shortcuts are now callable through `shortcuts.run`.

Longer term, replace the explicit method router with a namespaced dynamic tool
registry, but do not make that a bootstrap prerequisite.
