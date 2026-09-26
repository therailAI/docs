#!/usr/bin/env python3
"""Reconcile public contract, handler registrations, and both SDK catalogs.

Run list_handlers.go for each workspace first. Inputs are maintainer-owned;
the output contains no credentials, internal routes, or source file contents.
"""
import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--main', type=Path, required=True)
p.add_argument('--preview', type=Path, required=True)
p.add_argument('--main-handlers', type=Path, required=True)
p.add_argument('--preview-handlers', type=Path, required=True)
p.add_argument('--date', required=True)
args = p.parse_args()

def public(value):
    if isinstance(value, dict):
        return {k: public(v) for k, v in value.items()
                if not k.startswith('x-source') and k not in ('x-design-decisions', 'examples', 'example')}
    if isinstance(value, list): return [public(v) for v in value]
    if isinstance(value, str):
        return value.replace('See docs/CRYPTOGRAPHY.md.', 'See the evidence verification guide.').replace('See docs/WEBHOOKS.md.', 'See the events and webhooks guide.')
    return value

published = json.loads((ROOT/'api-reference/openapi.json').read_text())
methods = {'get', 'post', 'put', 'patch', 'delete'}
report = {'review_date': args.date, 'contract_version': published['info']['version'],
          'method': 'Static source and catalog comparison; registration is not end-to-end qualification.',
          'baselines': {}, 'operations': []}
operations = {}
for baseline, workspace, handler_file in [('repository', args.main, args.main_handlers), ('local_preview', args.preview, args.preview_handlers)]:
    source_bytes = (workspace/'rail-api-contract/rail.openapi.json').read_bytes()
    source = json.loads(source_bytes)
    handlers = json.loads(handler_file.read_text())
    py = json.loads((workspace/'rail-sdk-python/src/rail_sdk/operations.json').read_text())
    ts_text = (workspace/'rail-sdk-typescript/src/operations.ts').read_text()
    ts = json.loads(ts_text.split('=', 1)[1].rsplit('as const;', 1)[0].strip())
    assert published['components'] == public(source['components']), 'Published schema/security drift'
    versions = {'typescript': json.loads((workspace/'rail-sdk-typescript/package.json').read_text())['version'],
                'python': re.search(r'^version = "(.+)"$', (workspace/'rail-sdk-python/pyproject.toml').read_text(), re.M)[1]}
    revision = {}
    for component in ['contract', 'core', *sorted(handlers), 'typescript', 'python']:
        repo = {'contract':'rail-api-contract','core':'rail-go','typescript':'rail-sdk-typescript','python':'rail-sdk-python'}.get(component, component)
        revision[component] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=workspace/repo, text=True).strip()
    seen = set()
    for path, item in source['paths'].items():
        for method, op in item.items():
            if method not in methods: continue
            oid, service = op['operationId'], op['x-service']
            seen.add(oid)
            expected = public(op)
            expected['description'] = 'Contract 0.1.1; confirm support in your deployment. ' + expected.get('description', '')
            assert published['paths'][path][method] == expected, 'Published operation drift: '+oid
            assert oid in handlers['rail-'+service+'-api'], 'Missing registered handler: '+oid
            request = op.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema')
            responses = {}
            for status, response in op['responses'].items():
                if not status.startswith('2'): continue
                if '$ref' in response: response = source['components']['responses'][response['$ref'].split('/')[-1]]
                responses[status] = response.get('content', {}).get('application/json', {}).get('schema', True)
            for sdk in [py, ts]:
                actual = sdk[oid]
                assert actual['method'] == method.upper() and actual['path'] == path, 'SDK route drift: '+oid
                assert actual['requestSchema'] == request, 'SDK request drift: '+oid
                assert actual['responseSchemas'] == responses, 'SDK response drift: '+oid
            operations.setdefault(oid, {'operation_id':oid, 'method':method.upper(), 'path':path, 'service':service})[baseline] = 'handler registered; both SDK catalogs match'
    assert set(py) == set(ts) == seen, 'SDK operation coverage drift'
    report['baselines'][baseline] = {'source_contract_sha256':hashlib.sha256(source_bytes).hexdigest(),
        'customer_operations':len(seen), 'sdk_versions':versions, 'revisions':revision}
report['operations'] = sorted(operations.values(), key=lambda x:x['operation_id'])
report['services'] = dict(sorted(Counter(x['service'] for x in operations.values()).items()))
report['limitations'] = ['No authenticated production endpoint exercised',
    'Handler registration and schema agreement do not establish every semantic branch or provider integration',
    'Customer source contract remains authoritative; implementation restrictions are separate endpoint notes',
    'Local preview capabilities are not assumed to exist in the reviewed repository baseline']
(ROOT/'maintenance/implementation-audit.json').write_text(json.dumps(report, indent=2)+'\n')
print(f"PASS: {len(operations)} customer operations, {len(report['services'])} services, both SDK catalogs and published schemas agree across both source baselines.")
