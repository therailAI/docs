#!/usr/bin/env python3
"""Derive public endpoint pages from a reviewed customer contract and product catalog."""
import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from reference_navigation import product_group

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('contract', type=Path)
parser.add_argument('catalog', type=Path)
args = parser.parse_args()
source_bytes = args.contract.read_bytes()
source = json.loads(source_bytes)
catalog = json.loads(args.catalog.read_text())
assert hashlib.sha256(source_bytes).hexdigest() == catalog['contract_sha256']

def public(value):
    if isinstance(value, dict):
        return {k: public(v) for k, v in value.items()
                if not k.startswith('x-source') and k not in ('x-design-decisions', 'examples', 'example')}
    if isinstance(value, list):
        return [public(v) for v in value]
    if isinstance(value, str):
        return value.replace('See docs/CRYPTOGRAPHY.md.', 'See the evidence verification guide.').replace('See docs/WEBHOOKS.md.', 'See the events and webhooks guide.')
    return value

spec = public(source)
spec['info'] = {
    'title': 'The Rail customer API', 'version': source['info']['version'],
    'summary': 'Authorization and clearing for autonomous agents.',
    'description': 'Customer contract reference 0.1.1. Deployment support must be confirmed for your environment; this reference is not a public sandbox or a production availability guarantee. Use the endpoint and identity configuration supplied by your operator. All .invalid URLs are non-routable placeholders. Customer calls require OAuth and tenant/object authorization. Capabilities have additional sender-binding requirements. Every protected effect needs current authority. HTTP success does not establish execution, verification, or release of value. Runtime and internal-service APIs are excluded.'}
# Keep schema constraints, security and statuses; omit inherited fixture examples,
# which include historical signatures and generic responses reused across operations.
for path, item in spec['paths'].items():
    assert path.startswith('/v1/')
    for method, operation in item.items():
        if method not in ('get','post','put','patch','delete'): continue
        assert operation.get('x-audience') == 'customer'
        operation['description'] = 'Contract 0.1.1; confirm support in your deployment. ' + operation.get('description', '')

(ROOT/'api-reference').mkdir(exist_ok=True)
(ROOT/'api-reference/openapi.json').write_text(json.dumps(spec, indent=2, ensure_ascii=False)+'\n')
groups = [(p['title'], p['id'], p['operations']) for p in catalog['products']]
groups += [('Shared platform', 'platform', catalog['shared_operations']), ('Advanced routing and edge', 'advanced', catalog['advanced_operations'])]
navigation = []
seen = set()
implementation_notes = json.loads((ROOT/'maintenance/implementation-notes.json').read_text())
for title, slug, operations in groups:
    pages = []
    for operation in operations:
        method, path, oid = operation['method'], operation['path'], operation['operation_id']
        assert oid not in seen
        seen.add(oid)
        assert source['paths'][path][method.lower()]['operationId'] == oid
        route = 'api-reference/endpoints/'+re.sub(r'(?<!^)(?=[A-Z])','-',oid).lower()
        page = ROOT/(route+'.mdx'); page.parent.mkdir(parents=True,exist_ok=True)
        scopes = ', '.join('`'+s+'`' for s in operation['scopes'])
        content = '\n'.join(['---','title: '+json.dumps(operation['summary']), 'description: '+json.dumps(f'{method} {path} — The Rail customer contract 0.1.1.'), 'openapi: '+json.dumps(f'/api-reference/openapi.json {method} {path}'), '---', '', '<Note>Contract 0.1.1. Confirm that this operation is enabled in your deployment. Example hosts are placeholders; this page does not send API requests.</Note>', '', f'**Required OAuth scope:** {scopes}. Tenant, object, and domain authorization also apply.', ''])
        if method != 'GET': content += '\nSupply an explicit `Idempotency-Key`. See [idempotency and retries](/api-reference/idempotency).\n'
        if operation['consequential']: content += '\nThis is a consequential operation. Credentials and OAuth scope alone do not authorize the effect; applicable authority and policy must also permit it.\n'
        content += '\n**Service:** `'+operation['service']+'`. Use its operator-provided base URL, or a gateway explicitly configured to route this operation. See [implementation and release status](/get-started/implementation-status).\n'
        if oid in implementation_notes:
            content += '\n## Implementation notes\n\n'+implementation_notes[oid]+'\n'
        page.write_text(content)
        pages.append((route, path))
    navigation.append(product_group(title, pages))
assert len(seen) == 127
(ROOT/'maintenance/api-navigation.json').write_text(json.dumps(navigation,indent=2)+'\n')
manifest = {'contract_version':spec['info']['version'],'source_sha256':hashlib.sha256(source_bytes).hexdigest(),'published_sha256':hashlib.sha256((ROOT/'api-reference/openapi.json').read_bytes()).hexdigest(),'customer_operations':len(seen),'runtime_operations':0,'internal_operations':0,'transformations':['Remove source-disclosure annotations and private source links','Omit fixture examples; retain request/response schemas, parameters, OAuth requirements and statuses','Replace top-level introduction and annotate deployment qualification']}
(ROOT/'maintenance/contract-baseline.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(f'Generated {len(seen)} customer endpoint pages and a bundled public OpenAPI reference.')
