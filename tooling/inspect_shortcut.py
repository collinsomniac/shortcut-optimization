"""Summarize a decoded Shortcuts property list without printing action values.

Only reads an unsigned binary/XML property list. Does not decrypt signed exports,
resolve iCloud URLs, verify a signature, import a shortcut, or run any actions.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import plistlib


MAX_BYTES = 10 * 1024 * 1024


def summarize(data: bytes) -> dict:
    if len(data) > MAX_BYTES:
        raise ValueError("Input exceeds the 10 MiB inspection limit")
    workflow = plistlib.loads(data)
    if not isinstance(workflow, dict) or not isinstance(workflow.get("WFWorkflowActions"), list):
        raise ValueError("Expected a decoded Shortcuts property list")

    actions = workflow["WFWorkflowActions"]
    identifiers = []
    bundles = set()
    control_modes = Counter()
    for action in actions:
        if not isinstance(action, dict):
            raise ValueError("Invalid action entry")
        identifier = action.get("WFWorkflowActionIdentifier")
        if not isinstance(identifier, str):
            raise ValueError("Missing action identifier")
        identifiers.append(identifier)
        params = action.get("WFWorkflowActionParameters", {})
        if not isinstance(params, dict):
            raise ValueError("Invalid action parameters")
        descriptor = params.get("AppIntentDescriptor", {})
        if isinstance(descriptor, dict):
            bundle = descriptor.get("BundleIdentifier")
            if isinstance(bundle, str):
                bundles.add(bundle)
        if identifier == "is.workflow.actions.choosefrommenu":
            mode = params.get("WFControlFlowMode")
            if isinstance(mode, int):
                control_modes[str(mode)] += 1

    questions = workflow.get("WFWorkflowImportQuestions", [])
    return {
        "inspection_status": "artifact-inspected; execution and import not tested",
        "sha256_decoded_input": hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data),
        "action_entries": len(actions),
        "action_identifiers": dict(sorted(Counter(identifiers).items())),
        "app_bundle_identifiers": sorted(bundles),
        "menu_control_modes": dict(sorted(control_modes.items())),
        "import_question_count": len(questions) if isinstance(questions, list) else None,
        "shortcut_input_variable_flag": workflow.get("WFWorkflowHasShortcutInputVariables")
            if isinstance(workflow.get("WFWorkflowHasShortcutInputVariables"), bool) else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plist", type=Path, help="A decoded binary or XML Shortcuts plist")
    args = parser.parse_args()
    print(json.dumps(summarize(args.plist.read_bytes()), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
