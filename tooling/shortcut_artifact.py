"""Local unsigned-plist canonicalization and guarded literal edits. Never signs/runs."""
import argparse
import base64
import copy
import datetime
import hashlib
import json
import math
from pathlib import Path
import plistlib

MAX_BYTES = 10 * 1024 * 1024


def typed(value):
    """Canonical typed tree; preserves unknown fields and plist scalar distinctions."""
    if isinstance(value, dict):
        return ['dict', [[k, typed(value[k])] for k in sorted(value)]]
    if isinstance(value, list):
        return ['array', [typed(v) for v in value]]
    if isinstance(value, bool):
        return ['bool', value]
    if isinstance(value, plistlib.UID):
        return ['uid', str(value.data)]
    if isinstance(value, int):
        return ['int', str(value)]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError('Non-finite reals are unsupported')
        return ['real', value.hex()]
    if isinstance(value, bytes):
        return ['data', base64.b64encode(value).decode('ascii')]
    if isinstance(value, datetime.datetime):
        return ['date', value.isoformat()]
    if isinstance(value, str):
        return ['string', value]
    raise ValueError('Unsupported plist value type')


def untyped(node):
    kind, value = node
    if kind == 'dict':
        if len({k for k, _ in value}) != len(value):
            raise ValueError('Duplicate canonical dictionary key')
        return {k: untyped(v) for k, v in value}
    if kind == 'array':
        return [untyped(v) for v in value]
    decoders = {'bool': lambda v: v, 'uid': lambda v: plistlib.UID(int(v)),
                'int': int, 'real': float.fromhex,
                'data': lambda v: base64.b64decode(v, validate=True),
                'date': datetime.datetime.fromisoformat, 'string': lambda v: v}
    if kind not in decoders:
        raise ValueError('Unknown canonical type')
    return decoders[kind](value)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(workflow):
    return json.dumps(typed(workflow), ensure_ascii=False, separators=(',', ':')).encode()


def read(raw):
    if len(raw) > MAX_BYTES:
        raise ValueError('Input exceeds 10 MiB')
    if not (raw.startswith(b'bplist00') or raw.lstrip().startswith(b'<?xml')):
        raise ValueError('Decoded unsigned plist required; signed containers are unsupported')
    workflow = plistlib.loads(raw)
    if not isinstance(workflow, dict) or not isinstance(workflow.get('WFWorkflowActions'), list):
        raise ValueError('Expected a workflow action array')
    canonical(workflow)  # Reject unsupported values before editing.
    return workflow


def patch(raw, spec):
    """Replace one existing literal, selected by unique UUID and action identifier."""
    if sha(raw) != spec['expected_sha256']:
        raise ValueError('conflict: source hash changed')
    workflow = read(raw)
    edited = copy.deepcopy(workflow)
    matches = [a for a in edited['WFWorkflowActions'] if isinstance(a, dict)
               and isinstance(a.get('WFWorkflowActionParameters'), dict)
               and a['WFWorkflowActionParameters'].get('UUID') == spec['action_uuid']]
    if len(matches) != 1:
        raise ValueError('Expected exactly one matching action UUID')
    action = matches[0]
    if action.get('WFWorkflowActionIdentifier') != spec['action_identifier']:
        raise ValueError('Action identifier mismatch')
    key = spec['parameter']
    if key in ('UUID', 'GroupingIdentifier', 'WFControlFlowMode', 'AppIntentDescriptor'):
        raise ValueError('Structural wiring parameters are not literal-edit targets')
    params = action['WFWorkflowActionParameters']
    if key not in params or typed(params[key]) != typed(spec['expected_value']):
        raise ValueError('conflict: parameter value changed')
    if type(params[key]) not in (str, int, bool, float) or type(spec['value']) is not type(params[key]):
        raise ValueError('Only same-type scalar literal replacement is supported')
    params[key] = spec['value']
    output = plistlib.dumps(edited, fmt=plistlib.FMT_BINARY, sort_keys=True)
    if len(output) > MAX_BYTES:
        raise ValueError('Output exceeds 10 MiB')
    if canonical(read(output)) != canonical(edited):
        raise ValueError('Serialization lost information')
    # A patch never preserves an Apple signature; output is explicitly unsigned.
    return output, {'status': 'drafted', 'signed': False, 'device_verified': False,
                    'source_sha256': sha(raw), 'output_sha256': sha(output),
                    'canonical_sha256': sha(canonical(edited)),
                    'changed_action_uuid': spec['action_uuid'], 'changed_parameter': key}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('canonical', 'patch'):
        p = sub.add_parser(command)
        p.add_argument('input', type=Path)
        p.add_argument('output', type=Path)
        if command == 'patch':
            p.add_argument('--spec', required=True, type=Path)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error('Use a separate output; preserve the source artifact')
    raw = args.input.read_bytes()
    if args.command == 'canonical':
        output = canonical(read(raw)) + b'\n'
        report = {'status': 'artifact-inspected', 'source_sha256': sha(raw)}
    else:
        output, report = patch(raw, json.loads(args.spec.read_text()))
    with args.output.open('xb') as handle:
        handle.write(output)
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
