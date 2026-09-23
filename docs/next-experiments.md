# Research priorities after ecosystem comparison

| Priority | Question | Approach | Decision unlocked |
|---|---|---|---|
| 1 | Can we reliably inspect shared workflows? | Repeat supplied-link intake with synthetic native/third-party examples; compare opaque fields | Artifact-backed agent intake |
| 2 | Can edits preserve unfamiliar app actions? | Native neighbor edit, third-party parameter edit, graph diff, runtime check | Native skeleton plus adapter workflow |
| 3 | Which authoring path preserves the most information? | Evaluate Cherri import/raw actions and existing Playground validation against the same specimens | Reuse tooling versus custom transformation |
| 4 | Can installation be confirmed after cancellation/rename? | Benign version-report/self-check and local-name mapping | Dependable catalog/updater |
| 5 | Which state backend is simplest? | Native Storage, Data Jar, JSON files with identical fixtures | Local-memory backend |
| 6 | Can a phone/browser flow return useful results to ChatGPT? | Explicit copy/share baseline, then callback experiments | Agent consumption UX |

Research can narrow these questions, but exact client/build behavior needs execution evidence. No need to extract a personal collection.

## Add Data Jar to the storage comparison

The developer describes a JSON-compatible Shortcuts data store with offline storage and iCloud synchronization. This is a closer baseline for small persistent state than recreating a relational server. It does not establish SQL support, atomic transactions, or no-sync operation. [Developer site](https://datajar.app/)

## Add Scriptable to the transport comparison

Scriptable documents app URL schemes and HTTPS universal links for running an existing script, with query parameters available to the script. This offers an alternate handoff to evaluate if a chat client handles HTTPS better. It requires Scriptable and an installed script; it does not itself establish same-chat result ingestion. [Developer documentation](https://docs.scriptable.app/urlscheme/)

## Avoid premature scope

Do not build a database engine, new programming language, general installer, or complete action catalog yet. Prioritize preserving real workflows, explaining requirements, and confirming successful use. Those improvements serve both small useful shortcuts and more ambitious agents.
