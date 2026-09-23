# Supplied specimen: Restaurant Assistant

Status: **artifact-inspected**, not imported or executed here. User supplied this hand-built example specifically for research; it is not a polished package release.

Source: [provided iCloud link](https://www.icloud.com/shortcuts/b0668d200bd34f15b0dd47180aa60b34).
Inspection date: 2026-09-23.

The iCloud record endpoint returned metadata and separate unsigned/signed assets. The unsigned asset decoded with Python's standard plistlib. This demonstrates inspection of this specimen without prompt reconstruction. Endpoint stability and support for other sharing formats are unverified.

| Observation | Value |
|---|---|
| Decoded asset size | 4,252 bytes |
| SHA-256 of decoded-source asset bytes | cf27b80c39aaf1eb1012a8bfb9bf6ca32ece80c14a9fba081766615d7e1c3e8a |
| Serialized entries | 32 |
| Menu/control-flow entries | 15 |
| Timer-start entries | 16 |
| Image-text extraction entries | 1 |
| Explicit timer duration absent | 3 entries |
| Import questions | None |
| Explicit Shortcut Input variable flag | false |
| App descriptor observed | Apple's Clock, com.apple.mobiletimer |
| Record signing status | APPROVED; metadata only, signature not independently verified |

Menu start/branch/end markers account for 15 entries; “32 entries” should not be interpreted as 32 independent tasks.

## What can be inferred, cautiously

Timer branches contain pairs such as 11 and 22 minutes, with no Wait action between them. The structure is consistent with cumulative deadlines started close together, rather than waiting 11 minutes before starting another 11-minute timer. Confirm timing and multiple-timer behavior on-device.

Three timer entries lack an explicit duration. That establishes absent serialized values, not whether this iOS build prompts, defaults, or fails.

The recipe branch contains image-text extraction but no explicit photo selection/camera action or explicit input binding. Input acquisition and output presentation need testing; the broad accepted-input metadata is not a functional input contract.

Only native actions were identified in this specimen. It provides no direct evidence about the AI builder's third-party editing behavior.

## General lessons

- Introspection can identify incomplete configuration before device testing.
- Signing approval and workflow completeness are separate.
- Reusable workflows need explicit input and output paths, not just accepted-type metadata.
- Configuration should move into a clearly defined block or store when a prototype becomes a reusable package.
- Keep this specimen in experiments; do not advertise it in the installable package catalog.

Original action data, temporary asset URLs, and iCloud account/device metadata are not republished here.
