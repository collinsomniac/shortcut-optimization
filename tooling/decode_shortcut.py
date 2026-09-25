"""Offline AEA profile-0 Shortcut decoder. No signing, trust-store check or execution.

Requires requirements-shortcut-decode.txt. Supports only the observed AA01
single-file envelope; rejects ambiguous paths/types instead of scanning for magic.
"""
import argparse
import io
import json
from pathlib import Path
import plistlib
import struct
from shortcut_artifact import MAX_BYTES, read, sha


def extract_workflow(payload):
    if len(payload) > MAX_BYTES:
        raise ValueError('Decoded archive exceeds size limit')
    position, files = 0, []
    while position < len(payload):
        if payload[position:position+4] != b'AA01' or position+6 > len(payload):
            raise ValueError('Expected AA01 entry')
        size = int.from_bytes(payload[position+4:position+6], 'little')
        end = position + size
        if size < 6 or end > len(payload):
            raise ValueError('Invalid AA header size')
        cursor, fields, blobs = position+6, {}, []
        while cursor < end:
            if cursor+4 > end:
                raise ValueError('Truncated AA field')
            key = payload[cursor:cursor+3].decode('ascii')
            kind = chr(payload[cursor+3]); cursor += 4
            if key in fields:
                raise ValueError('Duplicate AA field')
            if kind in '1248':
                width = int(kind)
            elif kind in 'ABC':
                width = {'A': 2, 'B': 4, 'C': 8}[kind]
            elif kind in 'ST':
                width = {'S': 8, 'T': 12}[kind]
            elif kind == 'P':
                if cursor+2 > end:
                    raise ValueError('Truncated string length')
                width = int.from_bytes(payload[cursor:cursor+2], 'little'); cursor += 2
            else:
                raise ValueError('Unsupported AA field type')
            if cursor+width > end:
                raise ValueError('Truncated AA value')
            value = payload[cursor:cursor+width]; cursor += width
            if kind in '1248ABC':
                value = int.from_bytes(value, 'little')
            elif kind == 'P':
                value = value.decode('utf-8')
            fields[key] = value
            if kind in 'ABC':
                blobs.append((key, value))
        data_end = end + sum(length for _, length in blobs)
        if data_end > len(payload):
            raise ValueError('Truncated AA blob')
        if fields.get('TYP') == ord('D'):
            if fields.get('PAT') not in ('', '.') or blobs:
                raise ValueError('Only an empty root directory is supported')
        elif fields.get('TYP') == ord('F'):
            if fields.get('PAT') != 'Shortcut.wflow' or len(blobs) != 1 or blobs[0][0] != 'DAT':
                raise ValueError('Expected one Shortcut.wflow data blob')
            files.append(payload[end:data_end])
        else:
            raise ValueError('Unsupported AA entry type')
        position = data_end
    if len(files) != 1:
        raise ValueError('Expected exactly one workflow file')
    read(files[0])
    return files[0]


class BoundedOutput(io.BytesIO):
    def write(self, data):
        if self.tell() + len(data) > MAX_BYTES:
            raise ValueError('Decoded archive exceeds size limit')
        return super().write(data)


def decode(raw):
    import aea
    from cryptography import x509
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    if len(raw) < 12 or len(raw) > MAX_BYTES or raw[:4] != b'AEA1':
        raise ValueError('Expected bounded AEA1 input')
    profile, auth_size = struct.unpack_from('<II', raw, 4)
    if profile != 0:
        raise ValueError('Only profile 0 signed archives are supported')
    if not 0 < auth_size <= len(raw)-12:
        raise ValueError('Invalid authentication metadata size')
    metadata = plistlib.loads(raw[12:12+auth_size])
    chain = metadata.get('SigningCertificateChain')
    if not isinstance(chain, list) or not chain or not isinstance(chain[0], bytes):
        raise ValueError('Missing embedded signing certificate')
    cert = x509.load_der_x509_certificate(chain[0])
    public_key = cert.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
    output = BoundedOutput()
    # Verifies the signature using the supplied leaf key and checks MAC/checksum.
    # An embedded leaf key is NOT an Apple CA trust decision.
    aea.decode_stream(io.BytesIO(raw), output, signature_pub=public_key)
    payload = output.getvalue()
    workflow = extract_workflow(payload)
    return workflow, {'status': 'artifact-inspected', 'profile': profile,
                      'container_sha256': sha(raw), 'decoded_sha256': sha(workflow),
                      'container_bytes': len(raw), 'decoded_bytes': len(workflow),
                      'aea_integrity_verified': True, 'apple_ca_trust_verified': False,
                      'device_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    workflow, report = decode(args.input.read_bytes())
    with args.output.open('xb') as handle:
        handle.write(workflow)
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
