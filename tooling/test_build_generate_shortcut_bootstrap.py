import plistlib
import unittest

from tooling.build_generate_shortcut_bootstrap import GENERATE_ACTION_ID, rewrite_prompt


class BootstrapTests(unittest.TestCase):
    def test_rewrites_only_generate_prompt(self):
        workflow = {
            "WFWorkflowClientVersion": "1",
            "WFWorkflowActions": [{
                "WFWorkflowActionIdentifier": GENERATE_ACTION_ID,
                "WFWorkflowActionParameters": {
                    "UUID": "test",
                    "prompt": "old",
                    "AppIntentDescriptor": {
                        "AppIntentIdentifier": "GenerateShortcutAction",
                        "BundleIdentifier": "com.apple.shortcuts",
                    },
                },
            }],
        }
        raw = plistlib.dumps(workflow, fmt=plistlib.FMT_BINARY)
        out = rewrite_prompt(raw, "new prompt")
        parsed = plistlib.loads(out)
        self.assertEqual(
            parsed["WFWorkflowActions"][0]["WFWorkflowActionParameters"]["prompt"],
            "new prompt",
        )
        self.assertEqual(
            parsed["WFWorkflowActions"][0]["WFWorkflowActionIdentifier"],
            GENERATE_ACTION_ID,
        )


if __name__ == "__main__":
    unittest.main()
