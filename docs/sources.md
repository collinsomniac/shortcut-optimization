# Primary sources

Reviewed 2026-09-23. Links are living documents; preserve dated evidence for release decisions. This page keeps the small core citation set used by early guides. The broader ongoing inventory is [docs/research/source-ledger.md](research/source-ledger.md).

| ID | Source | Supports |
|---|---|---|
| S1 | [Apple: Run a shortcut from a URL](https://support.apple.com/guide/shortcuts/run-a-shortcut-from-a-url-apd624386f42/ios) | Name/text/clipboard invocation |
| S2 | [Apple: Open and create](https://support.apple.com/guide/shortcuts/open-create-and-run-a-shortcut-apda283236d7/ios) | Editor entry points |
| S3 | [Apple: x-callback-url](https://support.apple.com/guide/shortcuts/use-x-callback-url-apdcd7f20a6f/ios) | Success/error/cancel and result |
| S4 | [Apple: June 2026 intelligence announcement](https://www.apple.com/newsroom/2026/06/apple-intelligence-brings-powerful-ai-capabilities-into-everyday-experiences/) | Describe a Shortcut creation/editing |
| S5 | [Apple: WWDC26, What's new in Shortcuts](https://developer.apple.com/videos/play/wwdc2026/310/) | Automations, runtime model inputs/transcript, persistent/global Storage |
| S6 | [Apple: First API request](https://support.apple.com/en-sg/guide/shortcuts/apd58d46713f/ios) | Get Contents of URL |
| S7 | [Apple: Share shortcuts](https://support.apple.com/guide/shortcuts/share-shortcuts-apdf01f8c054/ios) | iCloud, file export, audience, import questions |
| S8 | [a-Shell maintainer README](https://github.com/holzschu/a-shell#shortcuts) | Commands/file transfer, extension versus app execution |
| S9 | [a-Shell commands](https://github.com/holzschu/a-Shell-commands) | WASM command ecosystem |
| S10 | [SQLite: Persistent storage options](https://sqlite.org/wasm/doc/trunk/persistence.md) | Browser persistence and VFS constraints |

S5's chapter/session text has contained release-number wording that does not line up cleanly with its WWDC26/iOS 27 context. Preserve that inconsistency and verify exact build support later rather than deriving a minimum OS version solely from the session date.

The expanded [research source ledger](research/source-ledger.md) adds App Intents, Foundation Models/Core AI, evaluation frameworks, Laya/ONNX, Gemma/wllama, artifact tooling and current compute/control-plane references. Community questions are separately linked in [community.md](community.md) and [research landscape](research-landscape.md).

No community workaround is promoted to verified capability merely because it is plausible or popular. Account limits and rolling forum views are volatile and require rechecking before an engineering/release decision.