# Agent harness: bounded capabilities on a phone

The useful abstraction is a **capability contract**, not arbitrary control over iOS. A catalog item names an installed shortcut, version, input schema, output schema, side effects, required apps, permissions, offline/network behavior, and evidence. The agent chooses from that set; the phone remains the execution authority.

| Boundary | Supported design today | What still needs a device result |
|---|---|---|
| Read repo | Agent/browser can read Markdown, static JSON and manifest URLs | Whether a given agent/client actually has repo or browser access. |
| Call installed shortcut | Apple documents `shortcuts://run-shortcut?name=…&input=text&text=…` and x-callback-url forms; construct a URL after name/input validation | Per-client opening, clipboard/URL fidelity and explicit return to the same chat. See [handoffs](links-and-handoffs.md). |
| JSON / web requests | Shortcuts provides Dictionary/JSON and Get Contents of URL, including API methods and request bodies | Permissions, authentication location, retries, HTTP/error response and phone background limits. [Apple API](https://support.apple.com/en-ca/guide/shortcuts/apd58d46713f/ios), [JSON](https://support.apple.com/en-ca/guide/shortcuts/apd0f2e057df/ios). |
| Change a shortcut | Native AI builder can create/edit workflows from description; signed export/import paths are documented separately | Third-party action preservation, edits within app actions, arbitrary file mutation, signed build and reimport on target OS. See [AI builder](ai-builder.md). |
| Install/organize | iCloud link / signed file enters Apple import flow; possible folder management after explicit device test | Silent import, arbitrary folder placement, install confirmation or same-chat callback. See [distribution](distribution.md). |

## Minimum action loop

1. Agent reads `agents/catalog.json`; selects a released capability with a compatible artifact and adequate evidence.
2. It builds a bounded request with version, `request_id`, expected app action, input, timeout and no credential in URL. The user opens a known installed shortcut.
3. Shortcut validates schema, asks before side effects, acts, and returns a typed result or canceled/error status. The user relays the result or a tested callback supplies it.
4. Agent checks the matching request ID and output, then may propose a dependent step. The intent to act and the attempted launch are not completion receipts.

Start with text echo, then read-only storage inspection or structured classification; add idempotent put/get and narrowly scoped API calls only after receipts. Separate *planner* (ChatGPT/other agent), *decision* (If/rules/Laya), *executor* (Shortcuts/App Intents), and *transport* (URL/share sheet/callback). This enables provider swaps without pretending the agent has unrestricted phone automation.

## Shortcut as source artifact

The existing [sharing modes](sharing-modes.md) distinguish iCloud Link versus signed file and Anyone versus People Who Know Me. For a repo release, include actual Apple-exported signed `.shortcut` when distributable, a stable iCloud import link if desired, a manifest with SHA-256 and source revision, a readable action inventory, setup questions and a fixture. Never synthesize a purported signed file from a prompt or plist. A checked-in plist/graph can be a *reviewable source* but still needs a validated signing/import path and run test. Keep configuration and personal data out of exports; record unknown third-party action identifiers rather than guessing.

**Agentic authoring experiment:** duplicate a harmless baseline, capture its exported graph, ask the builder to change one native node near a third-party node, re-export, compare action types, parameters, variable references and counts, then execute both fixtures. Repeat with one app-action parameter change and one connected output. An agent can suggest the edit and inspect before/after artifacts; there is no documented general Shortcuts editor API or unattended phone import established in this repo. [Builder study](ai-builder.md)

## Privacy and failure behavior

Reject arbitrary action names, uncontrolled URL schemes, file paths and web destinations suggested by untrusted content. Pin allowed capabilities and destinations; avoid secrets in shortcut parameters, link query strings, repository data and Pages JavaScript. Distinguish `proposed`, `launched`, `permission_denied`, `canceled`, `timed_out`, `executed`, and `verified_output`. Preserve a human permission step for contacts, messages, purchases and destructive data writes. Site hosted code and model output are inputs to review, not authority on device.
