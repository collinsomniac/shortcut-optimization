# URL builder

Python 3, standard library only. Development utility; phone users do not need Python to use published links.

```sh
python3 tooling/shortcut_url.py "SO Echo" --text "Hello & goodbye"
python3 tooling/shortcut_url.py "SO Echo" --json-file agents/request.example.json
python3 -m unittest discover -s tooling -p 'test_*.py'
```

The utility preserves text and encodes parameter values once. JSON-file mode validates syntax only, not the proposed protocol. Output is a URL for an already installed shortcut. It does not establish a client-specific URL size limit or guarantee that a chat UI renders custom schemes as tappable links.

Tests cover encoding, Unicode, empty input, and invalid arguments. They do not run iOS.
