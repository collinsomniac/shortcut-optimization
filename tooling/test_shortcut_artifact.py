import copy
import datetime
import json
import plistlib
import unittest
from shortcut_artifact import canonical, patch, read, sha, typed, untyped


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.workflow = {'WFWorkflowActions': [{
            'WFWorkflowActionIdentifier': 'is.workflow.actions.gettext',
            'WFWorkflowActionParameters': {'UUID': 'fixture-id', 'WFTextActionText': 'before',
                                           'UnknownParameter': {'bytes': b'\x00\xff'}}}],
            'UnknownTopLevel': [True, 1, 1.0, -0.0, plistlib.UID(5),
                               datetime.datetime(2026, 9, 25), b'opaque']}
        self.raw = plistlib.dumps(self.workflow, fmt=plistlib.FMT_BINARY)
        self.spec = {'expected_sha256': sha(self.raw), 'action_uuid': 'fixture-id',
                     'action_identifier': 'is.workflow.actions.gettext',
                     'parameter': 'WFTextActionText', 'expected_value': 'before', 'value': 'after'}

    def test_lossless_canonical_types_and_unknown_fields(self):
        decoded = untyped(json.loads(canonical(read(self.raw))))
        self.assertEqual(typed(decoded), typed(self.workflow))
        self.assertNotEqual(typed(True), typed(1))
        self.assertNotEqual(typed(0.0), typed(-0.0))

    def test_one_change_and_deterministic_bytes(self):
        output, report = patch(self.raw, self.spec)
        expected = copy.deepcopy(self.workflow)
        expected['WFWorkflowActions'][0]['WFWorkflowActionParameters']['WFTextActionText'] = 'after'
        self.assertEqual(canonical(read(output)), canonical(expected))
        self.assertEqual(patch(self.raw, self.spec)[0], output)
        self.assertFalse(report['signed'])

    def test_stale_hash_and_wrong_value_fail(self):
        for field, value in [('expected_sha256', '0'*64), ('expected_value', 'stale'),
                             ('action_identifier', 'other'), ('value', 7),
                             ('parameter', 'UUID')]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                patch(self.raw, {**self.spec, field: value})

    def test_duplicate_uuid_fails(self):
        self.workflow['WFWorkflowActions'] *= 2
        raw = plistlib.dumps(self.workflow, fmt=plistlib.FMT_BINARY)
        with self.assertRaises(ValueError):
            patch(raw, {**self.spec, 'expected_sha256': sha(raw)})

    def test_rejects_signed_or_unrelated_input(self):
        for raw in [b'AEA1opaque signed artifact', plistlib.dumps({'unrelated': []})]:
            with self.assertRaises(ValueError):
                read(raw)
