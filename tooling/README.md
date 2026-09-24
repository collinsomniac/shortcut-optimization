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
