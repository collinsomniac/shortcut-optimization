# Registry structural-edit experiment — 2026-09-25 UTC

## Live boundary (reproduced)

Same shared project: `iphone-harness` / `zpdtlzpvshlpyqbfbzye`.

- `harness.info` request `d1c601b3-1162-4421-a81f-90aaf1c02df6` completed; its four hardcoded groups match the repository snapshot.
- `submit_shortcut_job('get', '{"name":"harness.info","view":"artifact"}', 120)` produced request `714a5cf6-4609-4565-96cb-5c88eb67039b`. It completed after an explicit wake, but its **inner result was `tool_not_found`, method `shortcuts.control`**.
- The transport row said `ok=true`; the result was a malformed/double-braced JSON-like string containing the error. Do not classify transport completion as operation success, or repair arbitrary malformed output into a success receipt.
- `shortcuts.inventory` and `shortcuts.versions` each had zero rows; `shortcuts.receipts` had none. Both phone and desktop worker records remain in the shared project.
- This falsifies the current facade as an export route. It does **not** prove the controller is absent from the native library.

## Alternative compiler path (reproduced locally)

`reproduce.py` reuses the committed non-sensitive generator probe envelope, replaces its actions with two documentation Comments and one Text action holding the repository registry snapshot, and patches that JSON literal to append one **disabled** planned fixture entry. It does not edit the live registry or dispatcher.

The source fixture unexpectedly ends with UTF-8 `ÿÿÿ` (`c3bfc3bfc3bf`) after `</plist>`. Strict plist parsing fails. The reproduction asserts and removes only that exact suffix from this exact fixture before using the envelope. The original committed file remains intact; the general parser does not silently strip trailers. No donor fetch/discovery was repeated.

Verified:
- canonical typed representation round-trips decoded plist values, including opaque bytes, dates, UIDs, scalar types, arrays, and unknown dictionaries;
- exact source SHA-256 and old-value preconditions prevent stale edits;
- UUID must resolve uniquely and match the expected action identifier;
- only one same-type scalar parameter is replaced; wiring parameters are refused;
- reversing that literal produces canonical equality with the original complete workflow;
- output bytes are deterministic;
- appended registry entry is present, disabled, and existing groups are unchanged;
- **13 tooling tests pass**.

Canonical means lossless **decoded plist semantics**, not identical XML formatting, dictionary ordering, signed container bytes, or signature preservation. The representation retains all fields rather than reconstructing only known actions. This is a literal editor, not an arbitrary graph rewrite engine.

### Catalog validation

Upstream: <https://github.com/viticci/shortcuts-playground-plugin>

Pinned inspected revision: `2de03bffe4ce8802e06d184931d9e4ec366a2ef2`.

The upstream validator passed with `--target-platform ios --target-macos 27`. Its authoring policy requires two leading Comments and a literal Playground attribution marker. The fixture explicitly labels that marker as a validator requirement and separately identifies this repository as its actual generator. Passing those authoring checks is not evidence of iOS execution.

### Reproduce

From the repository root:

```sh
python3 experiments/registry-roundtrip/reproduce.py /tmp/registry-roundtrip
python3 -m unittest discover -s tooling -p 'test_*.py'
python3 /path/to/shortcuts-playground-plugin/claude/skills/shortcuts-playground/scripts/validate_shortcut.py /tmp/registry-roundtrip/after.unsigned.plist --target-platform ios --target-macos 27
```

Hashes and local postcondition results: [result.json](result.json). Source, canonical representations, patch specification, and unsigned output are regenerated locally rather than committed as release artifacts.

## Remaining boundary / exact next action

**No native harness export, signing, import, or device execution was achieved.** No private content or credentials were sent to an external signer. Existing RPC methods, schema, registry and live workflows were not modified.

Obtain a File export of `harness.info` (or a duplicate) from the iPhone's Shortcuts Share menu, preferably directly attached to the development session rather than publicly shared. A signed/encrypted container may need an Apple-authorized decoding/export path; do not feed it to the unsigned-plist parser or assume changing bytes preserves its signature.

Then inspect its actual action structure, adapt the literal patch only if the registry is indeed a plain text literal (dictionary/tokenized forms need a separate guarded adapter), patch a duplicate, use a user-controlled authenticated macOS signer or a demonstrated native import route, and verify the fixture on-device. Do not repeat the already-failed unauthenticated GitHub macOS signing experiment. Do not use a third-party signer for the native harness without content review and explicit justification.
