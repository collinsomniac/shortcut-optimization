#!/usr/bin/env python3
"""Pack a decoded Shortcut workflow into the SO Copy Actions clipboard payload.

Input must be an unsigned decoded plist (XML or binary). This tool does not
sign, install, run, or upload anything.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import plistlib
from pathlib import Path
from typing import Any


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode_action(action: dict[str, Any]) -> str:
    raw = plistlib.dumps(action, fmt=plistlib.FMT_XML, sort_keys=False)
    # Verify our own serialization before transport.
    if plistlib.loads(raw) != action:
        raise ValueError("action plist did not round-trip")
    return base64.b64encode(raw).decode("ascii")


def pack_workflow(raw: bytes, label: str | None = None) -> dict[str, Any]:
    workflow = plistlib.loads(raw)
    actions = workflow.get("WFWorkflowActions")
    if not isinstance(actions, list):
        raise ValueError("workflow has no WFWorkflowActions array")
    if not all(isinstance(action, dict) for action in actions):
        raise ValueError("WFWorkflowActions contains a non-dictionary item")

    identifiers = [str(a.get("WFWorkflowActionIdentifier", "<missing>")) for a in actions]
    return {
        "protocol": "shortcut-actions-pasteboard/0.1",
        "source_sha256": sha256(raw),
        "action_count": len(actions),
        "actions": [encode_action(a) for a in actions],
        "report": label or ("SO Copy Actions payload: " + str(len(actions)) + " actions"),
        "action_identifiers": identifiers,
    }


def verify_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    blobs = payload.get("actions")
    if not isinstance(blobs, list):
        raise ValueError("payload actions must be an array")
    out = []
    for index, blob in enumerate(blobs):
        if not isinstance(blob, str):
            raise ValueError(f"payload action {index} is not base64 text")
        out.append(plistlib.loads(base64.b64decode(blob, validate=True)))
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--label")
    parser.add_argument("--expected-sha256")
    args = parser.parse_args()

    raw = args.workflow.read_bytes()
    digest = sha256(raw)
    if args.expected_sha256 and digest != args.expected_sha256.lower():
        raise SystemExit(f"source hash mismatch: {digest}")

    payload = pack_workflow(raw, args.label)
    decoded = verify_payload(payload)
    workflow = plistlib.loads(raw)
    if decoded != workflow["WFWorkflowActions"]:
        raise SystemExit("packed actions do not reproduce the source action array")

    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(json.dumps({
        "status": "packed",
        "source_sha256": digest,
        "action_count": payload["action_count"],
        "output": str(args.output),
        "signed": False,
        "device_verified": False,
    }))


if __name__ == "__main__":
    main()
