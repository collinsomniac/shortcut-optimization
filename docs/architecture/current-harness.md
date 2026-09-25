# Current harness architecture

Snapshot: 2026-09-24. This is the canonical system overview for agents continuing the project.

## Mission

Turn Apple Shortcuts into a first-class, inspectable, versioned execution surface for agents while preserving a clean separation between:

- **planner** — ChatGPT or another frontier/local agent;
- **semantic tool layer** — stable names such as `shortcuts.list`, `shortcuts.generate`, `shortcuts.run`;
- **control plane** — Supabase job transport, worker state, receipts, artifact/version metadata;
- **executors** — iPhone Shortcuts/App Intents, desktop worker, browser/shell/native helpers;
- **compiler/editor** — deterministic Shortcut artifact inspection/generation/patching where possible;
- **verification** — correlated receipts, fixture runs, hashes, diffs and explicit status.

The desired experience in a fresh chat is:

> “Create the shortcuts you need, organize them, execute them, inspect the results, and revise them if necessary.”

The agent should normally use the contained `shortcuts.*` subsystem and should only fall back to generic desktop/shell/UI tools when the Shortcut subsystem cannot provide the required primitive.

## Repository

Primary home base:

`collinsomniac/shortcut-optimization`

The repository contains:
- source-backed research and platform constraints;
- the agent-facing protocol;
- Supabase migrations/Edge Function source;
- artifact/compiler tooling;
- browser/local-model experiments;
- current implementation status and handoff documents.

Start future work from:
1. [this architecture](current-harness.md);
2. [Shortcut Worker implementation status](../implementation/shortcut-worker-status.md);
3. [next-agent handoff](../../agents/next-chat-handoff.md);
4. [Shortcut Worker protocol](../../examples/shortcut-worker/protocol.json).

## Supabase control plane

Connected project:

- name: `iphone-harness`
- project ref: `zpdtlzpvshlpyqbfbzye`
- region: `us-west-1`
- state at last inspection: ACTIVE_HEALTHY
- Postgres: 17.x

The project began as an iPhone-specific queue and was generalized to support desktop execution. Do not split iPhone and desktop into separate projects merely because they are different devices; the shared bus is useful. If a second free project is used later, prefer a staging/failure-domain split such as `shortcut-lab`.

### Legacy/shared transport

Existing public control-plane tables remain authoritative for compatibility:

- `public.rpc_requests`
- `public.rpc_results`
- `public.workers`
- `public.harness_events`
- `public.worker_credentials`

Existing agents already understand the older RPC system. Preserve compatibility unless there is a strong migration reason.

### Shortcut domain

Shortcut-specific internal state now lives under `shortcuts`:

- `inventory`
- `versions`
- `capability_snapshots`
- `receipts`
- `callbacks`
- `artifacts`

The agent-facing service facade is currently:

`public.submit_shortcut_job(operation, params, ttl)`

which routes supported operations to:

`iphone-main / shortcuts.control`

Current v0.2 operations:

`register, capabilities, list, get, run, open, generate, edit, rename, move, delete, create_link`.

The intended long-term direction is an `api` schema or equivalent narrow facade while keeping storage/credentials/helpers internal.

## Workers

### iphone-main

Phone-side execution authority.

Verified capabilities from the existing harness include:
- Pushcut/Supabase wake and leasing;
- `harness.info`;
- `phone.info`;
- `shell.exec.simple`;
- shell/Linux helper actions;
- an existing hardcoded tool registry used by the worker dispatcher.

Important: **`harness.info` is a folder-scoped manifest, not a live inventory of every installed Shortcut.** The supplied 2026-09-25 export uses four Get My Shortcuts actions scoped to fixed harness folders. Folder membership is dynamically read; dispatcher policy is a separate uninspected mechanism. Absence from `harness.info` does not prove a Shortcut is absent from the phone.

Manifest output observed:

~~~text
core:
  tool.exec
  supabase.worker
  supabase.worker.backup

tests:
  supabase.worker.http.test
  supabase.worker.token.test
  rpc.binary.photo.test

tools:
  probe.echo
  shell.exec.simple
  shell.inspect
  shell.exec
  phone.info
  harness.info
  linux.inspect
  linux.exec

drivers:
  safari.exec.javascript
  safari.open.url
~~~

A source-controlled snapshot now exists at [`harness/registry.json`](../../harness/registry.json), with [`harness/registry.schema.json`](../../harness/registry.schema.json). It does **not** drive the live dispatcher yet. A major next step is to make this or a successor manifest authoritative so agents can extend the harness without manually rewriting `harness.info`.

### desktop-main

Persistent Windows executor on the same bus.

Observed capability family:
- PowerShell / process execution;
- Codex inspect/turn/status/steer/respond/await flows;
- compiler/inspection work can live here when phone execution is unnecessary.

The desktop should be available to the Shortcut subsystem, but it should not become the default tool an agent reaches for when a scoped `shortcuts.*` method exists.

## Edge Functions

Active at last inspection:

- `harness-worker` — existing worker transport/auth path;
- `shortcut-callback` — one-time callback receipt ingestion;
- `shortcut-artifact` — short-lived signed artifact serving/cache;
- `shortcut-bootstrap` — serves the current non-sensitive Shortcut Worker bootstrap artifact.

Some functions intentionally run with `verify_jwt=false` because they implement custom token/nonce authentication. Do not generalize that pattern to new public functions without explicit authentication design.

## Shortcut library versus filesystem

Do not conflate the Shortcuts collection with an iOS filesystem directory.

Verified:
- a-Shell runs in its own sandbox/App Group;
- direct access to the private Shortcuts SQLite store is unavailable;
- a scan of the a-Shell workspace found no native Shortcut-library folders or `.shortcut` files.

Therefore:
- use **Get My Shortcuts** for native library inventory;
- use Shortcuts-native management actions for collection operations;
- use file-explorer semantics only after explicit export into a worker-owned Files/iCloud workspace.

## Current desired semantic tool surface

Agents should eventually see a contained subsystem approximately like:

~~~text
shortcuts.capabilities()
shortcuts.list(...)
shortcuts.get(...)
shortcuts.diff(...)
shortcuts.generate(...)
shortcuts.edit(...)
shortcuts.validate(...)
shortcuts.run(...)
shortcuts.open(...)
shortcuts.rename(...)
shortcuts.move(...)
shortcuts.delete(...)
shortcuts.create_link(...)
shortcuts.export(...)
shortcuts.install(...)

workspace.list(...)
workspace.read(...)
workspace.write(...)
~~~

Names and exact schemas may evolve, but the important property is containment: a Shortcut task should naturally remain inside the Shortcut tool family.

## Generation and editing routes

Treat generation/editing as a backend-selection problem rather than committing to one technique.

### 1. Native Apple generation

iOS 27 exposes Apple Intelligence “Describe a Shortcut”. A public/shared donor artifact was also inspected and found to contain:

`com.apple.shortcuts.GenerateShortcutAction`

with AppIntent identifier:

`GenerateShortcutAction`.

Use this route when it works because it understands the target phone’s native/app actions.

### 2. Deterministic artifact compiler

The repository can already manipulate the Shortcut plist envelope. A deterministic read-only probe was built by replacing the donor Generate action with:

`is.workflow.actions.getmyworkflows`

(Get My Shortcuts).

The next compiler milestone is not just generating whole workflows; it is **round-trip structural editing**:
- export;
- parse;
- normalize to an internal graph/IR;
- make a narrow patch;
- validate against known action schemas/catalogs;
- re-sign/import;
- run a fixture;
- compare output;
- preserve version lineage.

This is the route that can eventually edit harness workflows such as `harness.info` without relying on natural-language builder behavior.

### 3. Builder/UI fallback

Useful when an action cannot be represented reliably through known artifact formats/catalogs. Keep behind a narrow tool and verify screenshots/state rather than exposing arbitrary coordinates as the normal API.

### 4. Third-party/open-source compatibility layer

High-priority resources include:
- Shortcuts Playground static iOS 27 action/AppIntent catalogs and validator;
- community Shortcut plist compilers/decompilers;
- Actions, a-Shell, Scriptable, Pyto, Toolbox Pro and Pushcut action surfaces;
- macOS `shortcuts` CLI when an authenticated Apple/macOS signer is available.

The live phone remains authoritative for actually installed third-party App Intents.

## Signing boundary

Apple’s documented signer is macOS-only and requires a usable Apple environment.

Current research also demonstrated RoutineHub HubSign can sign a **non-sensitive** workflow artifact. Treat it as an external trust boundary:
- acceptable for generic/bootstrap experiments;
- not a default for workflows containing embedded secrets, private text, contact data or personal artifacts;
- provenance must be recorded.

Long term, prefer a signer controlled by the user (authenticated macOS node, native phone route, or other trusted Apple-authorized path).

## Result semantics

Never collapse all stages into “success”.

Use explicit states such as:

~~~text
proposed
drafted
installed
registered
launched
executed
verified
updated
shared
deleted
confirmation_required
conflict
unsupported
failed
cancelled
~~~

A successful URL launch is not proof the Shortcut ran. A run is not verified until the intended postcondition/output is observed.

## Security posture

The `shortcuts` tables currently grant no read/write privileges to `anon` or `authenticated`; `service_role` has the intended access. Shortcut-related public RPC functions inspected on 2026-09-24 are likewise not executable by `anon` or `authenticated`.

Five internal tables still have RLS disabled:
- `shortcuts.inventory`
- `shortcuts.versions`
- `shortcuts.capability_snapshots`
- `shortcuts.receipts`
- `shortcuts.callbacks`

This is a defense-in-depth concern, not evidence that those tables are presently readable by public client roles. Review RLS and exposed-schema configuration before broadening access. Do not automatically enable RLS without verifying the worker/service-role path and policy intent.

## Zones of proximal development

Highest-value next work, roughly in dependency order:

1. **Registry source of truth**
   - stop treating `harness.info` as a hardcoded one-off;
   - define a versioned manifest/catalog consumed by the dispatcher;
   - optionally generate `harness.info` from that manifest.

2. **Native inventory**
   - execute Get My Shortcuts on-device;
   - normalize names/folders/stable identifiers;
   - sync into `shortcuts.inventory`.

3. **Artifact export + round trip**
   - export selected Shortcut objects;
   - hash and version them;
   - inspect action graph;
   - establish reproducible import/sign route.

4. **Programmatic edit of harness workflows**
   - first target: update `harness.info` or an equivalent registry Shortcut deterministically;
   - prove a small patch can be applied without rebuilding the whole workflow;
   - preserve variables/control flow.

5. **Third-party action/AppIntent inventory**
   - discover actual installed action providers on the phone;
   - compare against static catalogs;
   - store capability snapshots.

6. **Verified run receipts**
   - make `shortcuts.run` return correlated executed/verified status;
   - keep direct callback receipts separate from URL-launch status.

7. **Generation**
   - generate a benign workflow;
   - place it in an agent-managed folder;
   - execute, inspect, rename/move/share, and clean up.

8. **Structural `get/diff/edit`**
   - define canonical IR;
   - optimistic concurrency by artifact hash/version;
   - dry-run diffs and reversible updates.

9. **Harness optimization**
   - once editing works, use the same compiler/optimizer to simplify old harness Shortcuts and reduce duplicated logic.

10. **Security hardening**
   - dedicated API schema / explicit grants;
   - RLS defense-in-depth;
   - method-level authorization classes;
   - signer trust policy;
   - artifact retention/cleanup.

## Near-term definition of success

A fresh agent should be able to:

1. discover the phone’s Shortcut collection;
2. read a normalized representation of a selected Shortcut;
3. create or patch a harmless Shortcut programmatically;
4. install/organize it in an agent-managed folder;
5. execute it through the shared harness;
6. receive a correlated verified result;
7. make a second edit based on the result;
8. clean up its own test artifacts;
9. accomplish this through `shortcuts.*` tools without needing to understand raw Supabase RPC internals.


## Tracking

The primary implementation backlog is [GitHub issue #4: Programmatic Shortcut registry and self-editing round trip](https://github.com/collinsomniac/shortcut-optimization/issues/4).

## Structural editor update — 2026-09-25 UTC

A local guarded literal editor and typed canonical plist representation now exist; see the [empirical registry experiment](../../experiments/registry-roundtrip/README.md). The synthetic fixture passes local postconditions and pinned iOS 27 catalog validation. Native export/sign/import/run remains unverified; the live artifact-get request returned dispatcher `tool_not_found`. No live registry or RPC compatibility changes were made.

## Native export update — 2026-09-25 UTC

The actual supplied harness export now has a reproduced local AEA decode/canonicalize/Dictionary-field patch path. All original wiring is preserved. Signing/import/device fixture execution is still unverified. See [native round trip](../../experiments/native-harness-roundtrip/README.md). The parser supports profile-0 archives, not arbitrary signed/encrypted containers.
