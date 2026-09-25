"""Append one inert text field to a native Dictionary action; preserve all wiring."""
import argparse
import copy
import json
from pathlib import Path
import plistlib
from shortcut_artifact import MAX_BYTES, canonical, read, sha


def append_text_field(raw, spec):
    if sha(raw) != spec['expected_sha256']:
        raise ValueError('conflict: source hash changed')
    original = read(raw)
    workflow = copy.deepcopy(original)
    matches = [a for a in workflow['WFWorkflowActions'] if isinstance(a, dict)
               and isinstance(a.get('WFWorkflowActionParameters'), dict)
               and a['WFWorkflowActionParameters'].get('UUID') == spec['action_uuid']]
    if len(matches) != 1 or matches[0].get('WFWorkflowActionIdentifier') != 'is.workflow.actions.dictionary':
        raise ValueError('Expected unique native Dictionary action')
    params = matches[0]['WFWorkflowActionParameters']
    container = params['WFItems']
    if container.get('WFSerializationType') != 'WFDictionaryFieldValue':
        raise ValueError('Unsupported dictionary serialization')
    if sha(canonical(container)) != spec['expected_items_sha256']:
        raise ValueError('conflict: dictionary changed')
    fields = container['Value']['WFDictionaryFieldValueItems']
    if not isinstance(fields, list):
        raise ValueError('Expected dictionary field list')
    keys = []
    for field in fields:
        key = field['WFKey']
        if key.get('WFSerializationType') != 'WFTextTokenString' or set(key['Value']) != {'string'}:
            raise ValueError('Dynamic dictionary keys are unsupported')
        keys.append(key['Value']['string'])
    key, value = spec['key'], spec['value']
    if not isinstance(key, str) or not key or not isinstance(value, str):
        raise ValueError('Expected nonempty text key and text value')
    if len(set(keys)) != len(keys) or key in keys:
        raise ValueError('conflict: duplicate dictionary key')
    fields.append({'WFKey': {'Value': {'string': key}, 'WFSerializationType': 'WFTextTokenString'},
                   'WFItemType': 0,
                   'WFValue': {'Value': {'string': value}, 'WFSerializationType': 'WFTextTokenString'}})
    output = plistlib.dumps(workflow, fmt=plistlib.FMT_BINARY, sort_keys=True)
    if len(output) > MAX_BYTES or canonical(read(output)) != canonical(workflow):
        raise ValueError('Output limit or preservation failure')
    fields.pop()
    if canonical(workflow) != canonical(original):
        raise ValueError('Unexpected change outside appended field')
    return output, {'status': 'drafted', 'signed': False, 'device_verified': False,
                    'source_sha256': sha(raw), 'output_sha256': sha(output),
                    'action_count': len(original['WFWorkflowActions']),
                    'appended_fields': 1, 'original_fields_preserved': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--spec', required=True, type=Path)
    args = parser.parse_args()
    output, report = append_text_field(args.input.read_bytes(), json.loads(args.spec.read_text()))
    with args.output.open('xb') as handle:
        handle.write(output)
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
