# Import, export, and versioned packages

Apple documents iCloud sharing links and exported files on iPhone, plus import questions for recipient configuration [S7]. Users can therefore install a real workflow without reconstructing it from a prompt.

## Release procedure

1. Duplicate the shortcut and remove personal input, tokens, file paths, account selections, and stored values. Inspect nested dependencies.
2. Add configuration/import questions where supported; document remaining manual setup.
3. Export for **Anyone** for a general audience. Apple describes validation for this sharing option. The contacts-only option includes contact information [S7].
4. Generate the iCloud share link and retain the exported `.shortcut` file.
5. Import into a clean test setup; check dependencies, permissions, variable bindings, and fixtures.
6. Publish the versioned artifact, checksum, installation link, manifest, and concise guide together. Record which artifact the link was tested against.
7. After editing, re-export and re-test. Do not assume existing installs or old links automatically update.

An iCloud link can be revoked. A repository release artifact gives a separately versioned record. A hash identifies bytes; it does not prove safety or Apple acceptance.

## Proposed package contents

| File | Purpose |
|---|---|
| README.md | Outcome, install/configure/run, limits |
| manifest.json | Version, required apps/builds, contract, permissions, test status |
| artifact.shortcut | Actual exported installable workflow, when available |
| build-prompt.md | Optional reconstruction aid, explicitly noncanonical |
| fixtures/ | Example input and expected output |
| evidence/ | Redacted import and execution records |

For third-party actions, record app version, action name, required subscription if applicable, and setup. Exporting a shortcut does not install its dependencies or guarantee another device can resolve its entities.

Do not label hand-authored plist/JSON or generated prompts as universally importable. Compilation/signing tools are a later research track with Apple-device import as the acceptance gate. Source: [S7](sources.md).
