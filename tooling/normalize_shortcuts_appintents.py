#!/usr/bin/env python3
"""Normalize Cherri-emitted Shortcuts AppIntent actions for iOS 27.

This intentionally performs only narrow, reviewed rewrites. It does not invent
action parameters or alter control-flow structure.
"""
from __future__ import annotations

import argparse
import plistlib
from pathlib import Path

SHORTCUTS_APPINTENTS = {
    "com.apple.shortcuts.CreateWorkflowAction": "CreateWorkflowAction",
    "com.apple.shortcuts.OpenWorkflowAction": "OpenWorkflowAction",
    "com.apple.shortcuts.CreateFolderAction": "CreateFolderAction",
    "com.apple.shortcuts.RenameShortcutAction": "RenameShortcutAction",
    "com.apple.shortcuts.DeleteWorkflowAction": "DeleteWorkflowAction",
}

def descriptor(intent: str) -> dict[str, str]:
    return {
        "TeamIdentifier": "0000000000",
        "BundleIdentifier": "com.apple.shortcuts",
        "Name": "Shortcuts",
        "AppIntentIdentifier": intent,
    }

def normalize(obj: dict) -> tuple[dict, int]:
    changed = 0
    for action in obj.get("WFWorkflowActions", []):
        ident = action.get("WFWorkflowActionIdentifier")
        intent = SHORTCUTS_APPINTENTS.get(ident)
        if not intent:
            continue
        params = action.setdefault("WFWorkflowActionParameters", {})
        existing = params.get("AppIntentDescriptor")
        wanted = descriptor(intent)
        if existing is None:
            params["AppIntentDescriptor"] = wanted
            changed += 1
        elif existing != wanted:
            raise ValueError(f"unexpected AppIntentDescriptor for {ident}: {existing!r}")
    return obj, changed

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()
    raw = args.input.read_bytes()
    obj = plistlib.loads(raw)
    obj, changed = normalize(obj)
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(plistlib.dumps(obj, fmt=plistlib.FMT_XML, sort_keys=False))
    print(f"normalized_appintents={changed} actions={len(obj.get('WFWorkflowActions', []))}")

if __name__ == "__main__":
    main()
