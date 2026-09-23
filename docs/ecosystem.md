# Existing work and where this project adds value

Research pass: 2026-09-23. This compares documented designs and first-person reports; none of these toolchains was installed or device-tested here.

For additional phone agent examples, dynamic automation claims, and model/runtime leads see [research landscape](research-landscape.md). The existence of TinyAgent and ShortcutStudio narrows the project's distinct value to trustworthy distribution, explicit contracts and reproducible correctness, rather than novelty of an agent or AI builder.

| Project | Useful precedent | Boundary for our project |
|---|---|---|
| [Shortcuts Playground](https://github.com/viticci/shortcuts-playground-plugin) | Claude/Codex generation, validation, remixing, action catalogs | Its documented signing path requires macOS; learn from validators without making desktop access a user requirement |
| [Cherri](https://github.com/electrikmilk/cherri) | Text source, raw actions, compiler, browser playground | Compilation and signing are separate; importer is beta |
| [Jelly agent library](https://github.com/Danjohnsonnj/jelly-shortcuts-builder) | Catalog plus shared agent workflows and editor-specific shims | Existing agent-repo precedent; documented build/sign path uses a Mac |
| [Open Jellycuts](https://github.com/OpenJelly/Open-Jellycuts) | Phone-oriented text authoring | README lists import and third-party object gaps relative to the closed version |
| [RoutineHub updater](https://routinehub.co/docs/updater/) | Installed-version manifest and update matching | Renames and canceled installs can undermine registry accuracy |
| [iffy-pi collection](https://github.com/iffy-pi/apple-shortcuts) | GitHub-hosted version/history metadata and helper dependencies | Its numeric version scheme is not our proposed version format |
| [David Blue's collection](https://extratone.github.io/routinehub/) | Broad catalog of practical app integrations | Useful discovery precedent; catalog presence does not prove current compatibility |
| [ScPL](https://github.com/pfgithub/scpl) | Earlier text language and inverse conversion | Maintainer notes action coverage stops before newer iOS actions; historical reference |

## Authoring and inspection

Shortcuts Playground packages action knowledge and validators, and explicitly calls out remaining variable/loop wiring errors. Prefer evaluating existing validation coverage over maintaining a second complete action database. Its reported success rate is not our benchmark.

Cherri documents importing iCloud links or unsigned files, but warns that signed-file decompilation is unsupported and that variable references/includes can need repair. Its toolkit support and raw-action fallback are relevant to third-party preservation. A successful decompile is not proof of equivalent behavior after rebuilding. [Importer](https://cherrilang.org/decompilation.html)

Cherri's browser playground makes browser authoring plausible, but its documented signing alternatives include a service. Label that route **phone-accessible authoring with remote signing**, not a fully offline phone compiler. [Signing](https://cherrilang.org/compiler/signing.html)

Open Jellycuts is separately assessable from the App Store product; do not transfer features between them based on the shared name.

## Distribution and updates

RoutineHub documents a real version registry, but also says its updater records the new version before the user completes Add. Canceling can leave metadata ahead of reality. This is a concrete opportunity for a **verified install receipt** after a benign self-check, with request/version correlation. It remains a proposed protocol, not an implemented guarantee.

The iffy-pi repository demonstrates that static JSON can coordinate multi-shortcut releases. We can adopt the pattern while using version strings, explicit dependency compatibility, and immutable release references. Avoid floating-point version comparison.

## Proposed differentiation

- Inspect a supplied artifact while preserving unfamiliar actions.
- Show what is documented, inspected, imported, and actually executed as separate facts.
- Support a useful phone-only consumption path even when authors use optional desktop tools.
- Separate user configuration/state from replaceable workflow code.
- Report installation and execution results truthfully, including cancellation.
- Publish action-level compatibility evidence for AI edits.
- Keep helpers optional until they measurably reduce setup or runtime effort.

The project should connect these existing capabilities into a dependable user experience. Building another compiler or an undifferentiated gallery has lower initial value.
