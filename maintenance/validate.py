#!/usr/bin/env python3
"""Validate the public docs structure without requiring a hosted environment."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
config=json.loads((ROOT/'docs.json').read_text())
spec=json.loads((ROOT/'api-reference/openapi.json').read_text())
manifest=json.loads((ROOT/'maintenance/contract-baseline.json').read_text())
errors=[]
def check(condition,message):
    if not condition: errors.append(message)
def pages(node):
    if isinstance(node,dict):
        for key,value in node.items():
            if key=='pages':
                for item in value:
                    if isinstance(item,str):yield item
                    else:yield from pages(item)
            elif isinstance(value,(list,dict)):yield from pages(value)
    elif isinstance(node,list):
        for item in node:yield from pages(item)
nav=list(pages(config['navigation']))
check(len(nav)==len(set(nav)),'Duplicate navigation route')
for route in nav:check((ROOT/(route+'.mdx')).is_file(),'Missing navigation route: '+route)
check(config['api']['playground']['display']=='simple','API playground must remain non-interactive')
for redirect in config.get('redirects',[]):
    check(redirect['source']!=redirect['destination'],'Redirect cycle')
    check((ROOT/(redirect['destination'].strip('/')+'.mdx')).is_file(),'Missing redirect destination')
    check(not (ROOT/(redirect['source'].strip('/')+'.mdx')).exists(),'Redirect shadows a page')
for old in json.loads((ROOT/'maintenance/previous-files.json').read_text()):
    if old.endswith('.mdx') and not (ROOT/old).exists():check('/'+old[:-4] in [r['source'] for r in config['redirects']],'Unmapped legacy route: '+old)
endpoints=set()
for file in ROOT.rglob('*.mdx'):
    content=file.read_text();relative=str(file.relative_to(ROOT))
    check(content.startswith('---\n'),'Missing frontmatter: '+relative)
    check(content.count('```')%2==0,'Unclosed code fence: '+relative)
    check(bool(re.search(r'^title: .+',content,re.M)),'Missing title: '+relative)
    check(bool(re.search(r'^description: .+',content,re.M)),'Missing description: '+relative)
    check(relative[:-4] in nav,'Unlisted content page: '+relative)
    for href in re.findall(r'\]\((/[^)]+)\)|href="(/[^"]+)"',content):
        path=urlsplit(next(x for x in href if x)).path.lstrip('/')
        check((ROOT/path).is_file() or (ROOT/(path+'.mdx')).is_file(),'Broken local link: '+relative+' -> '+path)
    match=re.search(r'^openapi: "(/api-reference/openapi.json) (GET|POST|PATCH|PUT|DELETE) (.+)"$',content,re.M)
    if match:
        _,method,path=match.groups();check(path in spec['paths'] and method.lower() in spec['paths'][path],'Unknown endpoint: '+relative)
        endpoints.add((method.lower(),path))
ops={(method,path) for path,item in spec['paths'].items() for method in item if method in ['get','post','patch','put','delete']}
check(endpoints==ops,'Endpoint pages do not cover the exact customer operation set')
check(len(ops)==127,'Customer operation count changed')
for method,path in ops:
    op=spec['paths'][path][method]
    check(path.startswith('/v1/') and op.get('x-audience')=='customer','Non-customer endpoint: '+path)
    check(op.get('security') and all('OAuth2' in req for req in op['security']),'Missing OAuth requirement: '+path)

def refs(value):
    if isinstance(value,dict):
        for key,item in value.items():
            if key=='$ref':
                check(item.startswith('#/'),'External schema reference: '+item)
                if item.startswith('#/'):
                    target=spec
                    try:
                        for part in item[2:].split('/'):target=target[part.replace('~1','/').replace('~0','~')]
                    except (KeyError,TypeError):errors.append('Broken schema reference: '+item)
            refs(item)
    elif isinstance(value,list):
        for item in value:refs(item)
refs(spec)
check(manifest['published_sha256']==hashlib.sha256((ROOT/'api-reference/openapi.json').read_bytes()).hexdigest(),'OpenAPI digest drift')
for file in [ROOT/'docs.json',ROOT/'api-reference/openapi.json',*ROOT.rglob('*.mdx')]:
    text=file.read_text()
    for pattern in [r'layer2financial',r'rail\.io',r'tryrail',r'Gate5A',r'x-source',r'Utility_Application',r'/Users/',r'BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY',r'/internal/v1/']:
        check(not re.search(pattern,text,re.I),'Non-public or unrelated content in '+str(file.relative_to(ROOT))+': '+pattern)
if errors:
    print('\n'.join(errors));raise SystemExit(1)
print(f'PASS: {len(nav)} navigable pages, {len(ops)} customer operations, {len(config["redirects"])} legacy redirects, all local links/schema refs, public-content boundaries, and contract digest.')
