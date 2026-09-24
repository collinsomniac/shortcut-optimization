#!/usr/bin/env python3
"""Build an unsigned, read-only Get My Shortcuts probe from the known donor envelope.

The generated workflow contains exactly one action:
is.workflow.actions.getmyworkflows

It still requires a trusted signing/import path before iOS can install it.
"""

from __future__ import annotations

import argparse
import plistlib
import uuid
from pathlib import Path

from tooling.build_generate_shortcut_bootstrap import fetch_donor

INVENTORY_ACTION_ID = "is.workflow.actions.getmyworkflows"


def rewrite_as_inventory_probe(raw: bytes) -> bytes:
    workflow = plistlib.loads(raw)
    workflow["WFWorkflowActions"] = [{
        "WFWorkflowActionIdentifier": INVENTORY_ACTION_ID,
        "WFWorkflowActionParameters": {"UUID": str(uuid.uuid4()).upper()},
    }]
    workflow["WFWorkflowHasShortcutInputVariables"] = False
    return plistlib.dumps(workflow, fmt=plistlib.FMT_XML, sort_keys=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--donor-id", default="cbde31e881ee4784b421c1eea4727d30")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    output = rewrite_as_inventory_probe(fetch_donor(args.donor_id))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output)
    print(args.output)


if __name__ == "__main__":
    main()
