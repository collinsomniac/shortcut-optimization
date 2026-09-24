# Supabase compartmentalization for the device harness

Live inspection snapshot: 2026-09-23/24 UTC. This document records architecture, not secrets.

## Current live state

The connected account currently exposes **one active Supabase project**, `iphone-harness` (`us-west-1`). The live database contains:
- `rpc_requests` — about 1.5k queued/historical jobs;
- `rpc_results` — about 1.5k results;
- `harness_events` — about 4.5k events;
- `workers` — 3 registered workers;
- `worker_credentials` — 2 credential records.

Workers observed:
- `desktop-main`: Windows desktop, currently idle/healthy, `desktop-worker-v1.4-canary`; exposes PowerShell/process plus Codex inspect/turn/status/steer/respond/await methods.
- `iphone-main`: iOS Shortcuts worker; still registered but has not heartbeated recently.
- `diagnostic-test`: legacy diagnostic worker.

There is one Edge Function, `harness-worker`, whose JWT verification is disabled because the function performs its own `x-harness-token` worker authentication against hashed credentials. The public tables have RLS enabled with no policies; Supabase's advisor reports that state informationally. Service-role RPC functions mediate the existing worker path.

There are no Supabase development branches.

## Why it feels like two projects

The schema evolved by **generalizing the original iPhone queue into a desktop control plane**. The project name still says iPhone, while the core tables are now device-agnostic.

The right conceptual split is therefore not necessarily another Supabase project. It is:

~~~text
shared control plane
 ├─ iphone executor
 ├─ desktop executor
 ├─ shortcut-management domain
 ├─ agent/session domain
 └─ artifacts/events
~~~

## Free-plan constraint

Supabase currently grants two active Free projects across organizations where the account is Owner/Admin. A second project is therefore possible without upgrading, but it creates another Postgres/Auth/Functions/Realtime instance and another project URL/credential set.

Source: [Supabase billing](https://supabase.com/docs/guides/platform/billing-on-supabase).

For this harness, **one project with internal schemas is the better first reorganization** because existing agents keep the same project reference and RPC semantics.

## Target logical schemas

Supabase/Postgres schemas are ideal here because non-exposed schemas can organize and protect internal state while a narrow API schema defines the public Data API surface. Supabase explicitly recommends dedicated API schemas as an extra boundary:
- [Using Custom Schemas](https://supabase.com/docs/guides/api/using-custom-schemas)
- [Securing your API](https://supabase.com/docs/guides/api/securing-your-api)

Proposed target:

~~~text
api
  submit_job()
  observe_job()
  wait_job()
  list_capabilities()
  shortcut_inventory()
  ...

control
  jobs
  job_results
  workers
  worker_leases
  events

shortcuts
  inventory
  versions
  dependencies
  fixtures
  receipts
  builder_jobs

desktop
  sessions
  process_handles
  codex_threads
  interaction_events

iphone
  device_state
  shortcut_sync_state
  wake_state
  app_capability_snapshots

artifacts
  manifests
  hashes
  locations
  lineage

private
  worker_credentials
  service secrets
  internal helper functions
~~~

Only `api` needs to be exposed through PostgREST if direct Data API clients are desired. Internal schemas should remain unexposed.

## Preserve existing agents

Do **not** rename or remove `rpc_requests`, `rpc_results`, `workers`, or existing RPC functions in the first migration.

Use a compatibility phase:

### Phase 1 — additive

- keep current public objects unchanged;
- add domain columns/metadata to new internal objects;
- add new namespaced worker methods;
- introduce `shortcuts.*` jobs using the same existing queue;
- add new read-only capability-discovery RPC.

Existing agents continue using:
`desktop.exec`, `desktop.codex.*`, old submit/observe/wait APIs.

New agents can start using:
`shortcuts.inventory.list`, `shortcuts.run`, etc.

### Phase 2 — mirror

Add internal domain tables and mirror/dual-write only where genuinely useful. A compatibility view or RPC can still present the old queue model.

### Phase 3 — facade

Make `api.submit_job` the canonical ingress and keep old RPC names as thin wrappers. Existing agents do not need to learn the new storage layout.

### Phase 4 — retire legacy storage only after observed zero legacy use

Never force every prior agent/session to revise its mental model at once.

## Namespace the RPC protocol, not the project

The current method naming already moved in the right direction:

~~~text
desktop.exec
desktop.process
desktop.codex.inspect
...
~~~

Add:

~~~text
shortcuts.capabilities
shortcuts.inventory.list
shortcuts.inventory.export
shortcuts.get
shortcuts.run
shortcuts.open
shortcuts.generate
shortcuts.edit
shortcuts.rename
shortcuts.move
shortcuts.delete
shortcuts.create_link
shortcuts.validate
shortcuts.sync

workspace.list
workspace.read
workspace.write

iphone.info
iphone.app_capabilities
iphone.builder.status
~~~

A job can carry `domain`, `worker`, `method`, and `request_id`, but agents only need the method contract.

## Worker roles

Keep one registry but make role/capability discovery explicit:

~~~json
{
  "worker": "iphone-main",
  "domains": ["shortcuts", "iphone"],
  "capabilities": {
    "shortcuts.inventory": 1,
    "shortcuts.run": 1,
    "shortcuts.generate_native": 0,
    "shortcuts.builder_ui": 1
  }
}
~~~

The desktop can advertise:

~~~json
{
  "worker": "desktop-main",
  "domains": ["desktop", "compiler"],
  "capabilities": {
    "shortcut.plist.inspect": 1,
    "shortcut.plist.generate": 1,
    "shortcut.sign.apple": 0
  }
}
~~~

That final zero is important on Windows: do not let an agent infer that plist generation means an importable signed Shortcut exists.

## Artifact lane

Do not stuff large Shortcut files or screenshots into `rpc_results`.

Use results as manifests:

~~~json
{
  "ok": true,
  "artifact": {
    "kind": "shortcut",
    "version": "sha256:...",
    "location": "storage://shortcut-worker/exports/...",
    "mime": "application/octet-stream"
  }
}
~~~

Supabase Storage or a GitHub artifact can hold the bytes. The database records identity, hashes, provenance, and authorization.

## Shortcut version model

Suggested fields:

~~~text
shortcuts.inventory
  shortcut_ref uuid
  device_worker text
  native_name text
  folder text
  native_identifier text nullable
  latest_version text
  last_seen_at timestamptz
  deleted_at timestamptz nullable

shortcuts.versions
  version_id uuid
  shortcut_ref uuid
  content_sha256 text
  artifact_ref text
  source enum(native_export, native_generate, compiler, builder_ui)
  parent_version uuid nullable
  created_at timestamptz
  metadata jsonb
~~~

This supports diffs, optimistic concurrency, rollback, and agent-safe edits without requiring private Shortcuts database access.

## Security changes worth making before expanding

The current design already restricts important RPC routines to `service_role`/postgres and keeps RLS on public tables. Before adding more device-control operations:

1. Move worker credentials and internal helpers fully into a non-exposed `private` schema.
2. Create a dedicated `api` schema for any client-facing functions instead of growing `public`.
3. Revoke automatic default privileges for future public objects so exposure becomes opt-in.
4. Keep arbitrary desktop execution separate from shortcut-scoped methods; a new agent that only needs Shortcuts should not automatically receive `desktop.exec`.
5. Add per-method capability/authorization checks and optional approval class: read, reversible_write, external_write, destructive.
6. Add immutable artifact hashes and expected-version checks for Shortcut edits/deletes.
7. Keep the current custom Edge Function token flow only if it remains necessary; document that `verify_jwt=false` is intentional because worker authentication happens inside the function.

Supabase's current API security guidance recommends explicit grants and dedicated API schemas; functions are controlled by EXECUTE grants rather than RLS:
[Securing your API](https://supabase.com/docs/guides/api/securing-your-api).

## When to use the second free project

A second project becomes worthwhile if one of these becomes true:
- experimental migrations threaten the working control plane;
- untrusted/public web clients need isolation from device-control infrastructure;
- storage/log growth from experiments materially interferes with the worker;
- you want disposable test credentials and schema;
- you want a clean staging environment for destructive migrations.

Then use:
- `iphone-harness`: production/shared control plane;
- `shortcut-lab`: experimental compiler/builder/corpus/staging.

Do not split desktop and iPhone into separate projects merely because they are different devices. They need to exchange jobs/artifacts, and one shared control plane is simpler.

## Migration principle

**Compartmentalize by schema, method namespace, worker capability and artifact lineage first; split into another project only for trust/failure-domain isolation.**

That preserves every existing agent's current project reference while giving future agents a much cleaner mental model.
