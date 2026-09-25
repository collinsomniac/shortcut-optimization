import base64
import json
import plistlib
import unittest

from pack_shortcut_actions import encode_action, pack_workflow, verify_payload


class PackShortcutActionsTests(unittest.TestCase):
    def test_action_round_trip(self):
        action = {
            "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
            "WFWorkflowActionParameters": {
                "UUID": "11111111-1111-4111-8111-111111111111",
                "WFTextActionText": "hello",
            },
        }
        blob = encode_action(action)
        self.assertEqual(plistlib.loads(base64.b64decode(blob)), action)

    def test_workflow_payload_preserves_order_and_wiring(self):
        actions = [
            {
                "WFWorkflowActionIdentifier": "is.workflow.actions.gettext",
                "WFWorkflowActionParameters": {
                    "UUID": "A0000000-0000-4000-8000-000000000001",
                    "WFTextActionText": "hello",
                },
            },
            {
                "WFWorkflowActionIdentifier": "is.workflow.actions.showresult",
                "WFWorkflowActionParameters": {
                    "UUID": "A0000000-0000-4000-8000-000000000002",
                    "Text": {
                        "Value": {
                            "OutputName": "Text",
                            "OutputUUID": "A0000000-0000-4000-8000-000000000001",
                            "Type": "ActionOutput",
                        },
                        "WFSerializationType": "WFTextTokenAttachment",
                    },
                },
            },
        ]
        raw = plistlib.dumps({"WFWorkflowActions": actions})
        payload = pack_workflow(raw, "fixture")
        self.assertEqual(payload["action_count"], 2)
        self.assertEqual(verify_payload(payload), actions)
        self.assertEqual(
            verify_payload(payload)[1]["WFWorkflowActionParameters"]["Text"]["Value"]["OutputUUID"],
            "A0000000-0000-4000-8000-000000000001",
        )

    def test_rejects_non_action_array(self):
        raw = plistlib.dumps({"WFWorkflowActions": ["not-an-action"]})
        with self.assertRaises(ValueError):
            pack_workflow(raw)


if __name__ == "__main__":
    unittest.main()
