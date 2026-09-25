# Execution boundaries

Updated 2026-09-25.

## Principle

Put work on the cheapest executor that has the required authority.

The iPhone should own **native iOS authority**. The desktop should own
**heavy/general computation**. Supabase should coordinate them. Do not use a
phone shell merely because a shell is available.

## iPhone / Shortcuts

Preferred responsibilities:

- inventory installed Shortcuts with Get My Shortcuts;
- run already-installed Shortcuts;
- create empty Shortcut objects/folders;
- open/rename/delete/share installed Shortcuts through first-party actions;
- invoke installed third-party App Intents such as Actions when a workflow
  genuinely needs them;
- stage a signed artifact into Files and open it for Apple's native import
  confirmation.

The phone is authoritative for the actual installed app/action surface.

## a-Shell

a-Shell is an **optional adapter**, not the core Shortcut runtime.

Permitted uses should be narrow and empirically verified, such as:
- Execute Command for small local transforms;
- Put File / Get File across a-Shell's own App Group;
- hashing/format conversion that is cheap and sandbox-safe.

Do not use a-Shell for:
- accessing the private Shortcuts database;
- Cherri compilation;
- large artifact analysis/diffing;
- Git/build orchestration;
- long-running services that iOS lifecycle rules make unreliable.

If an operation can be done by a first-party Shortcuts action or on
`desktop-main`, prefer that over adding a shell dependency to the core manager.

## desktop-main

Preferred responsibilities:

- Cherri compilation;
- plist canonicalization/decompilation;
- Shortcut graph diffing and structural patching;
- catalog/schema normalization;
- Git operations;
- CI/build reproduction;
- signing preparation and trusted-signer integration;
- substantial Python/PowerShell/Node tooling;
- model/runtime experiments that do not require iPhone authority.

VS Code is a convenience UI, not the transport. The worker should remain usable
without VS Code open.

### Desired application-control helper

Add a narrow semantic method such as:

~~~text
desktop.app.ensure({
  "app": "vscode",
  "workspace": "<optional path>"
})
~~~

Expected behavior:
1. detect an existing Code process;
2. if absent, resolve the `code` command or known Code.exe locations;
3. launch VS Code without requiring the user at the desktop;
4. verify a Code process exists;
5. return `already_running`, `launched`, or a structured failure.

As of 2026-09-25, `desktop-main` heartbeat is live but recent
`desktop.exec` requests have remained unleased. Therefore VS Code launch is a
**desired capability, not yet verified**.

## Supabase

Supabase remains the shared control plane:
- request transport;
- worker state;
- receipts;
- Shortcut inventory/version metadata;
- short-lived artifact delivery where appropriate.

Do not split iPhone/desktop merely because they use different executors.

## Shortcut content lifecycle

There are two distinct operational loops.

### A. Persistent runner

~~~text
agent
  → harness.shortcuts.library / harness.shortcuts.run
  → resolve already-installed Shortcut
  → pass input
  → execute
  → return output/receipt
~~~

No compilation/signing occurs per run.

### B. New or changed Shortcut

~~~text
agent specification
  → desktop/CI compiler
  → normalized plist
  → pinned iOS 27 validation
  → signing
  → harness.shortcuts.stage
  → Files/open artifact
  → Apple Add Shortcut confirmation
  → persistent installed Shortcut
  → future runs use loop A
~~~

Apple's Create Shortcut action is useful for creating an empty native object,
but its currently observed schema exposes a name and OpenWhenRun rather than an
arbitrary action graph. Do not treat it as a general workflow-content installer.

## Third-party action schemas

Third-party App Intents are compiler inputs, not reasons to fall back to the
in-app AI generator.

For providers such as Actions:
1. ingest maintainer-published machine-readable action metadata;
2. normalize identifiers, parameters, returns and availability;
3. validate generated graphs against the pinned provider snapshot;
4. verify the action is actually installed on the target phone before relying
   on it.

This preserves support for richer third-party workflows while keeping
generation deterministic.
