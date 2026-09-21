# The Rail developer docs

Public Mintlify documentation for **the authorization and clearing layer for autonomous agents**.

The site covers the 0.1.1 customer HTTP contract, integration patterns, development SDK usage, and recorded reference workflows. Contract coverage does not imply that every operation is deployed or publicly hosted.

## Preview and validate

Use Node.js 22 and Python 3.12+. Install the [Mintlify CLI](https://www.mintlify.com/docs/cli/install):

```bash
npm install -g mint
python3 maintenance/validate.py
mint validate
mint broken-links
mint dev
```

The current validation environment uses Mint CLI 4.2.502. `docs.json` defines navigation and branding. Guides are MDX files. `api-reference/openapi.json` is the self-contained public customer reference; the browser playground is intentionally non-interactive because no shared public sandbox is specified.

## Maintain the API reference

Use a reviewed customer contract and matching product catalog from the authorized maintainer checkout:

```bash
python3 maintenance/build_reference.py /path/to/rail.openapi.json /path/to/products/catalog.json
```

The generator preserves customer request and response constraints, parameters, security requirements, and status codes. It removes source-disclosure annotations and inherited fixture examples, rewrites the public introduction, and generates 127 endpoint pages. It never imports runtime or internal service specifications. `maintenance/contract-baseline.json` records the source and published hashes.

After changing operation grouping, copy the generated groups in `maintenance/api-navigation.json` into the API tab in `docs.json`, then run all validation commands. Follow [Mintlify's OpenAPI setup](https://www.mintlify.com/docs/api-playground/openapi-setup) for configuration changes.

## Publishing

The connected Mintlify GitHub app deploys its configured production branch. A successful GitHub commit is not by itself confirmation of a successful Mintlify build; inspect the deployment check in GitHub or the Mintlify dashboard.

Do not publish credentials, private source links, internal ingress specifications, or patent materials. Use `AGENTS.md` for contributor boundaries.
