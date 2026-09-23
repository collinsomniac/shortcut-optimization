import plistlib
import unittest

from inspect_shortcut import summarize


class InspectionTests(unittest.TestCase):
    def test_counts_structure_without_leaking_parameter_values(self):
        secret = "PRIVATE-PARAMETER-DO-NOT-EMIT"
        raw = plistlib.dumps({
            "WFWorkflowActions": [
                {"WFWorkflowActionIdentifier": "is.workflow.actions.choosefrommenu",
                 "WFWorkflowActionParameters": {"WFControlFlowMode": 0, "WFMenuPrompt": secret}},
                {"WFWorkflowActionIdentifier": "is.workflow.actions.timer.start",
                 "WFWorkflowActionParameters": {"WFDuration": {"Magnitude": secret},
                    "AppIntentDescriptor": {"BundleIdentifier": "com.apple.mobiletimer"}}},
            ],
            "WFWorkflowImportQuestions": [],
            "WFWorkflowHasShortcutInputVariables": False,
        })
        result = summarize(raw)
        self.assertEqual(result["action_entries"], 2)
        self.assertEqual(result["menu_control_modes"], {"0": 1})
        self.assertEqual(result["app_bundle_identifiers"], ["com.apple.mobiletimer"])
        self.assertNotIn(secret, str(result))

    def test_rejects_unrelated_plist(self):
        with self.assertRaises(ValueError):
            summarize(plistlib.dumps({"name": "Unrelated"}))


if __name__ == "__main__":
    unittest.main()
