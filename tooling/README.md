# URL builder

Python 3, standard library only. Development utility; phone users do not need Python to use published links.

```sh
python3 tooling/shortcut_url.py "SO Echo" --text "Hello & goodbye"
python3 tooling/shortcut_url.py "SO Echo" --json-file agents/request.example.json
python3 -m unittest discover -s tooling -p 'test_*.py'
```

The utility preserves text and encodes parameter values once. JSON-file mode validates syntax only, not the proposed protocol. Output is a URL for an already installed shortcut. It does not establish a client-specific URL size limit or guarantee that a chat UI renders custom schemes as tappable links.

Tests cover encoding, Unicode, empty input, and invalid arguments. They do not run iOS.

## Decoded-workflow inspector

For an **already decoded, unsigned** binary or XML Shortcuts property list:

```sh
python3 tooling/inspect_shortcut.py path/to/decoded.plist
```

The command outputs an ordered-action count, action identifiers, bundle identifiers, import-question count, and SHA-256 of the exact input. It omits action parameter values by default, which avoids accidentally printing prompt text, contacts, URLs, or tokens in routine summaries. Review output before publishing; identifiers themselves can still reveal installed apps.

This is a local structural inspector, not a decompiler for signed `.shortcut` containers or an iCloud downloader. Cherri's documented [beta importer](https://cherrilang.org/decompilation.html) can retrieve an iCloud-linked shortcut for further authoring experiments. The inspector does not claim to validate execution or signatures.


## Deterministic inventory probe

Builds a one-action unsigned workflow containing only Apple's native Get My Shortcuts action:

```sh
python3 tooling/build_shortcut_inventory_probe.py \
  --output /tmp/SO-Inventory-Probe.shortcut
```

This is a compiler fixture, not an installable release by itself. It still requires a trusted signing/import path. It is useful for separating library-access tests from Apple Intelligence generation.

## Guarded artifact literal editing

`shortcut_artifact.py` accepts decoded **unsigned** binary/XML workflows. It preserves all decoded fields using a canonical typed tree; it does not decode signed containers or retain signatures. Canonical files contain full workflow values and must remain private for private inputs.

```sh
python3 tooling/shortcut_artifact.py canonical source.plist source.canonical.json
python3 tooling/shortcut_artifact.py patch source.plist patched.unsigned.plist --spec patch.json
```

Outputs must be new files. A patch supplies `expected_sha256`, `action_uuid`, `action_identifier`, `parameter`, `expected_value`, and `value`. Only an existing same-type scalar literal can change; UUID/control-flow/AppIntent descriptor edits are refused. The report omits parameter contents and explicitly says unsigned and not device-verified.

See the [reproducible registry experiment](../experiments/registry-roundtrip/README.md) for a generated patch specification and verified local postconditions. This does not establish general graph editing or live installation.
