import plistlib
import unittest

from tooling.build_shortcut_inventory_probe import (
    INVENTORY_ACTION_ID,
    rewrite_as_inventory_probe,
)


class InventoryProbeTests(unittest.TestCase):
    def test_replaces_donor_actions_with_one_read_only_inventory_action(self):
        donor = plistlib.dumps({
            "WFWorkflowClientVersion": "test",
            "WFWorkflowActions": [{
                "WFWorkflowActionIdentifier": "com.apple.shortcuts.GenerateShortcutAction",
                "WFWorkflowActionParameters": {"prompt": "do something"},
            }],
            "WFWorkflowHasShortcutInputVariables": True,
        })
        out = rewrite_as_inventory_probe(donor)
        parsed = plistlib.loads(out)
        self.assertEqual(len(parsed["WFWorkflowActions"]), 1)
        self.assertEqual(
            parsed["WFWorkflowActions"][0]["WFWorkflowActionIdentifier"],
            INVENTORY_ACTION_ID,
        )
        self.assertFalse(parsed["WFWorkflowHasShortcutInputVariables"])
        self.assertNotIn("GenerateShortcutAction", out.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
