"""Build a Shortcuts run URL. Does not install or execute anything."""
import argparse
import json
from urllib.parse import quote, urlencode

def build_url(name, text):
    if not isinstance(name, str) or not name.strip():
        raise ValueError("An installed shortcut name is required")
    if not isinstance(text, str):
        raise TypeError("Input must be text")
    return "shortcuts://run-shortcut?" + urlencode(
        {"name": name, "input": "text", "text": text}, quote_via=quote
    )

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text")
    group.add_argument("--json-file", help="Validate JSON and send the original UTF-8 text")
    args = parser.parse_args()
    payload = args.text
    if args.json_file:
        with open(args.json_file, encoding="utf-8") as handle:
            payload = handle.read()
        json.loads(payload)
    print(build_url(args.name, payload))

if __name__ == "__main__":
    main()
