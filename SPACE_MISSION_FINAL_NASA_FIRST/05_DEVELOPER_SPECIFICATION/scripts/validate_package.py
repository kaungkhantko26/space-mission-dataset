#!/usr/bin/env python3
from pathlib import Path
import json, csv, sys
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
errors=[]
for p in (ROOT/'schemas').glob('*.schema.json'):
    try:
        schema=json.loads(p.read_text(encoding='utf-8'))
        Draft202012Validator.check_schema(schema)
    except Exception as e:
        errors.append(f'{p.name}: invalid schema: {e}')

# Resolve local refs for handoff schema and validate all example payloads with a simple registry.
schemas={p.name:json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'schemas').glob('*.schema.json')}
class LocalResolver:
    pass
from referencing import Registry, Resource
registry=Registry()
for name,schema in schemas.items():
    registry=registry.with_resource(name, Resource.from_contents(schema))
for ex in (ROOT/'examples').glob('*.example.json'):
    payload=json.loads(ex.read_text(encoding='utf-8'))
    if ex.name.startswith('spacecraft_state'):
        s=schemas['spacecraft-state.schema.json']
    elif ex.name.startswith('telemetry_record'):
        s=schemas['telemetry-record.schema.json']
    elif ex.name.startswith('mission_event'):
        s=schemas['mission-event.schema.json']
    elif ex.name.startswith('launch_to_transfer'):
        s=schemas['module-handoff.schema.json']
    else:
        continue
    v=Draft202012Validator(s, registry=registry, format_checker=FormatChecker())
    for e in v.iter_errors(payload):
        errors.append(f'{ex.name}: {list(e.absolute_path)}: {e.message}')

for p in (ROOT/'data').glob('*.csv'):
    try:
        with p.open(newline='',encoding='utf-8') as f:
            reader=csv.DictReader(f)
            if not reader.fieldnames:
                errors.append(f'{p.name}: missing CSV header')
            list(reader)
    except Exception as e:
        errors.append(f'{p.name}: CSV parse error: {e}')

if errors:
    print('FAIL')
    print('\n'.join(errors))
    sys.exit(1)
print('PASS: JSON schemas valid; all example JSON payloads validate; all CSV files parse.')
