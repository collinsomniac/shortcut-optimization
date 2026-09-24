#!/usr/bin/env python3
"""Build an unsigned Generate Shortcut bootstrap from an Apple-approved donor.

The donor is fetched from an iCloud shared Shortcut. We preserve its workflow
metadata and change only the GenerateShortcutAction prompt. The result still
requires Apple signing before import.
"""

from __future__ import annotations

import argparse
import json
import plistlib
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_DONOR_ID = "cbde31e881ee4784b421c1eea4727d30"
GENERATE_ACTION_ID = "com.apple.shortcuts.GenerateShortcutAction"


def fetch_donor(shortcut_id: str = DEFAULT_DONOR_ID) -> bytes:
    api = f"https://www.icloud.com/shortcuts/api/records/{shortcut_id}"
    with urllib.request.urlopen(api, timeout=30) as response:
        record = json.load(response)
    url = record["fields"]["shortcut"]["value"]["downloadURL"]
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()


def rewrite_prompt(raw: bytes, prompt: str) -> bytes:
    workflow: dict[str, Any] = plistlib.loads(raw)
    actions = workflow.get("WFWorkflowActions")
    if not isinstance(actions, list) or len(actions) != 1:
        raise ValueError("Expected exactly one donor action")
    action = actions[0]
    if action.get("WFWorkflowActionIdentifier") != GENERATE_ACTION_ID:
        raise ValueError("Donor is not GenerateShortcutAction")
    params = action.setdefault("WFWorkflowActionParameters", {})
    descriptor = params.get("AppIntentDescriptor", {})
    if descriptor.get("AppIntentIdentifier") != "GenerateShortcutAction":
        raise ValueError("Unexpected Generate Shortcut AppIntent descriptor")
    params["prompt"] = prompt
    return plistlib.dumps(workflow, fmt=plistlib.FMT_BINARY, sort_keys=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", help="Literal Generate Shortcut prompt")
    parser.add_argument("--prompt-file", type=Path, help="UTF-8 prompt file")
    parser.add_argument("--donor-id", default=DEFAULT_DONOR_ID)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if bool(args.prompt) == bool(args.prompt_file):
        parser.error("Provide exactly one of --prompt or --prompt-file")
    prompt = args.prompt if args.prompt is not None else args.prompt_file.read_text(encoding="utf-8")
    raw = fetch_donor(args.donor_id)
    output = rewrite_prompt(raw, prompt.strip())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output)

    parsed = plistlib.loads(output)
    print(json.dumps({
        "output": str(args.output),
        "bytes": len(output),
        "action": parsed["WFWorkflowActions"][0]["WFWorkflowActionIdentifier"],
        "prompt_chars": len(parsed["WFWorkflowActions"][0]["WFWorkflowActionParameters"]["prompt"]),
        "signed": False,
    }))


if __name__ == "__main__":
    main()
