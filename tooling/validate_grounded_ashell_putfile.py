#!/usr/bin/env python3
"""Validate the narrowly approved a-Shell Put File action embedded in a Shortcut plist."""
from __future__ import annotations
import argparse, plistlib
from pathlib import Path

IDENT = "AsheKube.app.a-Shell.PutFileIntent"
ALLOWED = {"UUID", "file", "overwrite", "ShowWhenRun"}

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("shortcut", type=Path)
    args=ap.parse_args()
    obj=plistlib.loads(args.shortcut.read_bytes())
    found=0
    for idx, action in enumerate(obj.get("WFWorkflowActions", [])):
        if action.get("WFWorkflowActionIdentifier") != IDENT:
            continue
        found += 1
        params=action.get("WFWorkflowActionParameters")
        if not isinstance(params, dict):
            raise SystemExit(f"{IDENT} index {idx}: parameters must be dictionary")
        extra=set(params)-ALLOWED
        if extra:
            raise SystemExit(f"{IDENT} index {idx}: unreviewed parameters {sorted(extra)}")
        if "file" not in params:
            raise SystemExit(f"{IDENT} index {idx}: missing file")
        if "overwrite" in params and not isinstance(params["overwrite"], bool):
            raise SystemExit(f"{IDENT} index {idx}: overwrite must be Boolean")
        if "ShowWhenRun" in params and not isinstance(params["ShowWhenRun"], bool):
            raise SystemExit(f"{IDENT} index {idx}: ShowWhenRun must be Boolean")
        if params.get("ShowWhenRun") is not False:
            raise SystemExit(f"{IDENT} index {idx}: ShowWhenRun must be false")
        if params.get("overwrite") is not True:
            raise SystemExit(f"{IDENT} index {idx}: overwrite must be true for managed export")
    if found != 1:
        raise SystemExit(f"expected exactly one {IDENT}; found {found}")
    print(f"grounded_third_party_validation=pass identifier={IDENT} count={found}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
