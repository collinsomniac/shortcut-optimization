# Native harness.info export — 2026-09-25 UTC

## Reproduced result

The user supplied a 23,634-byte `harness.info.shortcut`. It is AEA profile 0, with a certificate chain in its authentication metadata. Using **python-aea 1.1.0 locally on Linux**, we verified the AEA signature against its embedded leaf public key and checked the archive integrity, then extracted the exact 4,379-byte `Shortcut.wflow` blob from AA01 headers. No Mac or remote decoding service was needed. This does **not** validate the certificate chain against Apple's trust store or establish iOS import acceptance.

Container SHA-256: `2f13b0803ceddda54ae23fa2d797b1241842bdfe70504a769475837716554df5`.

Decoded SHA-256: `da54821f29938c7879b786826b136d0f3851e0892703b30f9b0df0a94c4219f8`.

The full export, canonical representation, patch specification and unsigned result remain private; no folder identifiers, certificate contents, or full native workflow are committed here.

## Important refinement of the earlier manifest description

This exported artifact contains **11 actions**:

1. Four native Get My Shortcuts actions, each scoped to a fixed harness folder: tools, core, tests, drivers.
2. Four Actions app `FormatTextListIntent` actions, wired to those native outputs.
3. One native Dictionary action with tokenized values for `tools`, `core`, `drivers`, `tests`.
4. Actions app `PrettyPrintDictionariesIntent`.
5. Native output action.

Thus **the folder scope and output schema are fixed; the exported workflow discovers the folder members dynamically**. It is neither a full-library inventory nor a literal hardcoded name list. This refines the previous docs/user description based on the supplied artifact. It does not establish the internal policy of `tool.exec`, which has not been exported, nor prove that the uploaded version is byte-identical to the installed version.

Fresh baseline RPC `b93de41b-8906-48e1-a19e-b11160aef4da` completed with the familiar four groups. That corroborates the output shape, not artifact identity or untested folder-mutation behavior. The previous `shortcuts.control` routing failure remains valid.

## Deterministic patch

The native Dictionary serializes its fields under `WFItems.Value.WFDictionaryFieldValueItems`. The previous plain scalar editor was therefore insufficient.

Added `patch_shortcut_dictionary.py`: select a unique Dictionary UUID; require exact source and dictionary hashes; reject dynamic/duplicate keys; append one plain text field; preserve every original field/token/wire and verify canonical equality after removing only the appended field.

Actual patch: `_roundtrip_fixture` → `harness.info.patch.v1`.

This is inert output metadata, **not a new routed tool or allowlist grant**. No existing group is changed and no action is added. Patched SHA-256: `6778a75e81845548c14e287bf9093a8fc7afe2573ebe228c06d1a1a4fd137964`.

Locally verified: canonical typed round trip; original 11 actions and all existing fields preserved; deterministic patch output; expected new dictionary field; 19 tests pass, including synthetic AEA signature verification/tamper rejection and strict AA blob/path bounds.

## Catalog validation

Shortcuts Playground revision `2de03bffe4ce8802e06d184931d9e4ec366a2ef2`, iOS / ToolKit 27 selection, produced **identical diagnostics before and after**:

- declared input classes although Shortcut Input is unused;
- first action is not a Comment;
- second action is not the Playground prompt Comment;
- insufficient Comment blocks.

Full validator result is **failed baseline, unchanged after patch**, not a clean pass. The native artifact was not rewritten merely to satisfy Playground's generated-workflow conventions. No new diagnostics appeared. This does not prove installed Actions app compatibility; the original's descriptors and tokens were preserved exactly.

## Reproduce privately

```sh
# If the environment defaults to unavailable clang, use CC=gcc when installing.
python3 -m pip install -r tooling/requirements-shortcut-decode.txt
python3 tooling/decode_shortcut.py /private/harness.info.shortcut /private/harness.info.decoded.plist
python3 tooling/shortcut_artifact.py canonical /private/harness.info.decoded.plist /private/harness.info.canonical.json
python3 tooling/patch_shortcut_dictionary.py /private/harness.info.decoded.plist /private/harness.info.patched.unsigned.plist --spec /private/patch.json
python3 -m unittest discover -s tooling -p 'test_*.py'
```

The private patch spec needs `expected_sha256`, `action_uuid`, `expected_items_sha256` (SHA-256 of `canonical(WFItems)`), `key`, and `value`. The decoder is intentionally bounded to profile 0 and one `Shortcut.wflow` entry with known AA field types; unsupported envelopes fail explicitly. It never extracts arbitrary archive paths to disk. Optional decoding dependencies are pinned separately; without them the cryptographic integration test is explicitly skipped.

## Remaining boundary

**Decode → canonicalize → patch → local verification is now reproduced on the actual user export. Signing → duplicate import → device execution is not.** The original file and live harness remain unchanged.

A valid signature on the original cannot be reused after modifying its workflow. The supplied public certificate supplies verification, not a signing private key. This experiment does not attempt to forge/reuse it or claim a self-signed AEA is Apple-trusted.

Preferred next step: sign the patched plist with a user-controlled authenticated Apple/macOS signing route, import under a distinct fixture name, run it, and verify the added output field plus unchanged four groups. No such signer is currently established. Do not repeat the known unauthenticated GitHub-macOS signing failure. Native iPhone signing/import of arbitrary compiler bytes remains unproven. An external signer would receive the complete native artifact, including folder identifiers, so it was not used.

## Sources

- [python-aea API](https://aea.readthedocs.io/en/latest/reference/aea/) and [implementation](https://github.com/kinnay/AEA): local AEA signature/integrity decoding; installed version 1.1.0.
- [iOSShortcutDecoder](https://github.com/tctvn/iOSShortcutDecoder), inspected revision `195a0977e3c27ca3ec45da2cd2b2c7e9420b06b2`: lead for embedded public-key extraction; its lossy JSON encoder and magic-byte scanning were not adopted.
- [libNeoAppleArchive field representation](https://github.com/0xilis/libNeoAppleArchive/blob/main/docs/NeoAAFieldType.md): field encoding reference; our actual AA header/data boundaries were directly inspected and tested.
