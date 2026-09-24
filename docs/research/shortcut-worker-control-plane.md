# Shortcut Worker control plane

Reviewed 2026-09-23. This is the target architecture for a phone-resident Shortcuts worker controlled through a durable external control plane. It distinguishes public Apple capabilities, community-reported/prototype features, and project hypotheses.

## Goal

From a new agent/chat, the desired user experience is:

> "Create a shortcut that does X, install it on my phone, test it, and tell me what happened."

The agent should not need to know iOS UI coordinates, private Shortcuts serialization, Supabase table names, or the worker's implementation. It should see a small semantic tool surface backed by a phone worker, desktop/compiler services, and explicit receipts.

## What iOS already exposes

Apple's documented URL scheme can open Shortcuts, create a blank shortcut, open a named shortcut in the editor, and run a named shortcut with text/clipboard input:
- [Open/create Shortcuts URL scheme](https://support.apple.com/guide/shortcuts/open-create-and-run-a-shortcut-apda283236d7/ios)
- [Run a shortcut from a URL](https://support.apple.com/guide/shortcuts/run-a-shortcut-from-a-url-apd624386f42/ios)

Apple's action set has accumulated a surprisingly complete management surface:
- Get My Shortcuts — returns Shortcut objects; established action used for listing/backup.
- Run Shortcut and Open Shortcut.
- Create Shortcut, Delete Shortcuts, Open Folder — documented in Apple's iOS 16 release notes.
- Create Folder, Create iCloud Link for Shortcut, Add Shortcut to Home Screen — documented in iOS 18 release notes.
- Move Shortcut and Rename Shortcut — documented in iOS 18.1 release notes.
See [Apple Shortcuts release notes](https://support.apple.com/121131) and the older [Shortcuts release notes](https://support.apple.com/101583).

Apple documents exporting shortcuts as signed files or iCloud links from the editor, and Get My Shortcuts output can be saved/archived in workflows:
- [Share shortcuts](https://support.apple.com/guide/shortcuts/share-shortcuts-apdf01f8c054/ios)
- [Get My Shortcuts reference/example](https://matthewcassinelli.com/actions/get-my-shortcuts/)

iOS 27 adds **Describe a Shortcut**: Apple Intelligence can create a workflow from natural language and modify the current shortcut when the user describes a change:
- [Create a custom shortcut](https://support.apple.com/guide/shortcuts/create-a-custom-shortcut-apd84c576f8c/ios)
- [Apple Intelligence 2026 announcement](https://www.apple.com/newsroom/2026/06/apple-intelligence-brings-powerful-ai-capabilities-into-everyday-experiences/)

A community report describes a feature-flagged/prototype **Generate Shortcut** action whose output is a Shortcut object. Treat it as reported, not public API:
- [reported Generate Shortcut action](https://www.reddit.com/r/shortcuts/comments/1vgk21f/new_shortcut_action_generate_shortcut_from/)

## The important boundary

Native actions can **manage Shortcut objects and metadata**, but the public action surface does not expose a general "edit this shortcut's arbitrary internal action graph" primitive.

There are therefore three edit/generation strategies:

### Strategy A — native builder

Open/create the target shortcut and use Describe a Shortcut to create or revise it. Highest compatibility with current iOS actions and App Intents because Apple's own builder owns the graph.

Advantages:
- understands installed app actions on the actual phone;
- no private file-format dependency;
- generated result is immediately native and synced.

Cost:
- currently UI-bound unless the reported Generate Shortcut action becomes public/available;
- requires visual/UI automation or a user interaction boundary;
- difficult to guarantee deterministic diffs.

### Strategy B — native object management + Generate Shortcut if feature-detected

Bootstrap one worker manually. If the device exposes a callable Generate Shortcut action, the worker can:
1. receive a natural-language workflow specification;
2. Generate Shortcut;
3. Rename / Move it;
4. Create iCloud Link;
5. Run it with a fixture;
6. return metadata/receipt.

This is the ideal iOS-native path if the action is actually available on the target release. Feature-detect it; never make the harness depend on a hidden feature flag.

### Strategy C — artifact compiler

Export Shortcut objects to signed .shortcut files, decompile/inspect on a desktop/server, transform or build a new plist graph, then sign/import.

Apple provides the signing CLI only on macOS. A Windows desktop can inspect/build the plist but cannot use Apple's documented `shortcuts sign` CLI itself. Community projects such as [apple-shortcuts](https://github.com/julian-englert/apple-shortcuts) and [shortcuts-generator](https://github.com/cranecj/shortcuts-generator/blob/main/SKILL.md) are valuable format/compiler references, but private serialization remains version-sensitive.

The iPhone itself can export/share signed files or iCloud links, so a hybrid compiler can use the phone as the Apple-authorized artifact boundary.

## Worker bootstrap

The first manually-created worker should be intentionally boring. It receives a JSON request dictionary and dispatches only stable native operations.

Suggested native operations:

| Operation | Native basis | Result |
|---|---|---|
| `inventory.list` | Get My Shortcuts | normalized list |
| `inventory.export` | Get My Shortcuts → Save File | .shortcut files in worker export folder |
| `shortcut.run` | Run Shortcut | output/receipt |
| `shortcut.open` | Open Shortcut | launched editor |
| `shortcut.create_empty` | Create Shortcut | Shortcut object |
| `shortcut.rename` | Rename Shortcut | updated object |
| `shortcut.move` | Move Shortcut | updated folder |
| `shortcut.delete` | Delete Shortcuts | destructive; approval policy |
| `shortcut.create_link` | Create iCloud Link for Shortcut | share URL |
| `folder.create` | Create Folder | folder |
| `shortcut.generate_native` | Generate Shortcut if available; otherwise builder/UI fallback | Shortcut object |
| `builder.open_create` | `shortcuts://create-shortcut` | UI handoff |
| `builder.open` | Open Shortcut / URL scheme | UI handoff |

Do not overload this Shortcut with desktop compilation, model calls, repository logic, or every file operation. It is an iOS executor.

## Tool surface I would want in a fresh chat

The agent should receive semantic tools like:

### Read-only

`shortcuts.capabilities()`
- target OS/build;
- worker version;
- available management actions;
- whether Generate Shortcut was feature-detected;
- installed extension providers;
- inventory freshness.

`shortcuts.list(folder?, query?, include_hashes=false)`

`shortcuts.get(ref, view="summary|actions|artifact")`

`shortcuts.diff(ref_a, ref_b)`

`shortcuts.validate(ref, fixture?)`

### Mutating

`shortcuts.run(ref, input, wait=true)`

`shortcuts.generate(spec, strategy="auto", dry_run=true)`

`shortcuts.edit(ref, patch_or_spec, strategy="auto", dry_run=true)`

`shortcuts.rename(ref, name)`

`shortcuts.move(ref, folder)`

`shortcuts.delete(ref, expected_version)`

`shortcuts.install(artifact_ref, expected_hash)`

`shortcuts.create_link(ref)`

The agent should not receive a raw "tap coordinate" tool as its normal interface. UI automation belongs behind a narrow fallback such as:

`shortcuts.builder.apply_description(ref, description)`

with screenshot/state verification and explicit failure modes.

## Object identity

Names are not stable enough. Keep a project-side `shortcut_ref` mapped to:
- current native name;
- folder;
- exported content hash;
- last-seen device worker;
- last-seen timestamp;
- latest artifact/version;
- optional iCloud link;
- known dependencies.

Every mutating request should include an expected version/hash where possible. If the library changed since the agent read it, return a conflict rather than editing the wrong workflow.

## Editing contract

Prefer declarative intent over graph surgery:

~~~json
{
  "target": "shortcut://worker-ref/abc",
  "base_version": "sha256:...",
  "goal": "After receiving a URL, fetch the page title and append it to my Research Inbox note.",
  "constraints": {
    "native_actions_first": true,
    "no_external_api": true,
    "preserve_existing_trigger": true
  },
  "test_cases": [
    {"input": "https://example.com", "expect": {"status": "completed"}}
  ]
}
~~~

The worker/compiler chooses the implementation:
- native Describe-a-Shortcut edit;
- Generate Shortcut + replacement;
- compiler patch;
- ask user if none is reliable.

## Inventory and file exploration

Use two related namespaces rather than pretending the private Shortcuts database is an ordinary filesystem:

### Shortcut collection

`shortcuts.list/get/export/run/open/... `

Backed by Get My Shortcuts and native management actions.

### Worker files

`workspace.list/read/write/move/delete`

Scoped to a dedicated Files/iCloud Drive directory such as:
`Shortcuts/ShortcutWorker/`

Suggested subdirectories:

~~~text
ShortcutWorker/
  inbox/
  exports/
  generated/
  snapshots/
  fixtures/
  receipts/
  logs/
~~~

This gives agents familiar file-explorer semantics without granting arbitrary Files access by default.

## Generation pipeline

A good `shortcuts.generate` request should produce a staged job:

1. normalize natural-language goal into a workflow specification;
2. query target-device capabilities/action providers;
3. pick native-builder / feature-detected generator / compiler route;
4. generate a draft;
5. inventory/export the resulting Shortcut object;
6. inspect/diff;
7. run benign fixture;
8. record receipt;
9. create iCloud link only when requested;
10. mark version current.

The frontier model can design/repair workflows, while fast classifiers can route which builder/compiler/action family is appropriate. The phone remains authority for installed app actions and final execution.

## Can a chat create a runnable Shortcut with no worker?

Not fully.

A chat can:
- design the workflow;
- generate a textual specification or private-format plist source;
- generate documented URL schemes such as `shortcuts://create-shortcut` or `shortcuts://run-shortcut?name=...`;
- generate a GitHub-hosted artifact if a valid signed .shortcut already exists.

A chat cannot, by itself:
- place a workflow into the user's personal Shortcuts library;
- create an iCloud Shortcut share link;
- use Apple's Describe-a-Shortcut UI;
- sign an arbitrary generated .shortcut on Windows using Apple's documented signer;
- know which third-party App Intents exist on the target phone.

A URL like `shortcuts://create-shortcut` opens the builder; it does not inject an arbitrary workflow description. A run URL only works for a shortcut that already exists in the collection.

That gap is exactly what Shortcut Worker should close.
