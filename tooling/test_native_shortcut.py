import copy
import datetime
import io
import plistlib
import struct
import unittest
from decode_shortcut import decode, extract_workflow, BoundedOutput
from patch_shortcut_dictionary import append_text_field
from shortcut_artifact import canonical, sha


def aa_file(data, path='Shortcut.wflow'):
    path = path.encode()
    fields = b'TYP1F' + b'PATP' + struct.pack('<H', len(path)) + path + b'DATB' + struct.pack('<I', len(data))
    return b'AA01' + struct.pack('<H', 6+len(fields)) + fields + data


class NativeTests(unittest.TestCase):
    def setUp(self):
        self.items = {'WFSerializationType': 'WFDictionaryFieldValue', 'Value': {'WFDictionaryFieldValueItems': [
            {'WFKey': {'WFSerializationType': 'WFTextTokenString', 'Value': {'string': 'tools'}},
             'WFValue': {'WFSerializationType': 'WFTextTokenString', 'Value': {'string': '\ufffc',
                          'attachmentsByRange': {'{0, 1}': {'OutputUUID': 'upstream', 'Type': 'ActionOutput'}}}},
             'WFItemType': 0}]}}
        self.workflow = {'Unknown': b'opaque', 'WFWorkflowActions': [
            {'WFWorkflowActionIdentifier': 'is.workflow.actions.dictionary',
             'WFWorkflowActionParameters': {'UUID': 'dict', 'WFItems': self.items}}]}
        self.raw = plistlib.dumps(self.workflow, fmt=plistlib.FMT_BINARY)
        self.spec = {'expected_sha256': sha(self.raw), 'action_uuid': 'dict',
                     'expected_items_sha256': sha(canonical(self.items)),
                     'key': '_roundtrip_fixture', 'value': 'harness.info.patch.v1'}

    def test_append_preserves_tokens_and_unknown_fields(self):
        output, report = append_text_field(self.raw, self.spec)
        result = plistlib.loads(output)
        fields = result['WFWorkflowActions'][0]['WFWorkflowActionParameters']['WFItems']['Value']['WFDictionaryFieldValueItems']
        new = fields.pop()
        self.assertEqual(new['WFValue']['Value']['string'], self.spec['value'])
        self.assertEqual(canonical(result), canonical(self.workflow))
        self.assertEqual(output, append_text_field(self.raw, self.spec)[0])
        self.assertFalse(report['signed'])

    def test_conflicts(self):
        for field, value in [('expected_sha256','wrong'), ('expected_items_sha256','wrong'),
                             ('action_uuid','wrong'), ('key','tools')]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                append_text_field(self.raw, {**self.spec, field:value})

    def test_rejects_dynamic_keys(self):
        self.items['Value']['WFDictionaryFieldValueItems'][0]['WFKey']['Value']['attachmentsByRange'] = {}
        raw = plistlib.dumps(self.workflow, fmt=plistlib.FMT_BINARY)
        with self.assertRaises(ValueError):
            append_text_field(raw, {**self.spec, 'expected_sha256':sha(raw), 'expected_items_sha256':sha(canonical(self.items))})

    def test_exact_aa_blob_boundaries(self):
        self.assertEqual(extract_workflow(aa_file(self.raw)), self.raw)
        for data in [aa_file(self.raw)[:-1], aa_file(self.raw)+b'trailer',
                     aa_file(self.raw)*2, aa_file(self.raw,'../Shortcut.wflow')]:
            with self.subTest(size=len(data)), self.assertRaises(ValueError):
                extract_workflow(data)

    def test_bound_output(self):
        from unittest.mock import patch
        with patch('decode_shortcut.MAX_BYTES', 4):
            output = BoundedOutput()
            with self.assertRaises(ValueError):
                output.write(b'12345')

    def test_signature_and_tamper_rejection(self):
        try:
            import aea
        except ImportError:
            self.skipTest('Install requirements-shortcut-decode.txt for cryptographic integration test')
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.x509.oid import NameOID
        key = ec.generate_private_key(ec.SECP256R1())
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'synthetic-test')])
        now = datetime.datetime.now(datetime.timezone.utc)
        cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
                .serial_number(1).not_valid_before(now).not_valid_after(now+datetime.timedelta(days=1))
                .sign(key, hashes.SHA256()))
        auth = plistlib.dumps({'SigningCertificateChain':[cert.public_bytes(serialization.Encoding.DER)]}, fmt=plistlib.FMT_BINARY)
        private = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
        signed = aea.encode(aa_file(self.raw), signature_priv=private, auth_data=auth)
        decoded, report = decode(signed)
        self.assertEqual(decoded, self.raw)
        self.assertTrue(report['aea_integrity_verified'])
        self.assertFalse(report['apple_ca_trust_verified'])
        altered = bytearray(signed); altered[12+len(auth)+5] ^= 1
        with self.assertRaises(Exception):
            decode(bytes(altered))
