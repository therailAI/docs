# The Rail developer docs

Public Mintlify documentation for **the authorization and clearing layer for autonomous agents**.

The site covers the 0.1.1 customer HTTP contract, integration patterns, the development CLI and SDKs, and recorded reference workflows. The CLI & SDKs tab includes local setup, profiles, governed effect callbacks, approvals, recovery, and evidence export. Contract coverage does not imply that every operation is deployed or publicly hosted.

## Preview and validate

Use Node.js 22 and Python 3.12+. Install the [Mintlify CLI](https://www.mintlify.com/docs/cli/install):

```bash
npm install -g mint
python3 maintenance/validate.py
mint validate
mint broken-links
mint dev
```

To try the API playground in a local preview, start the sandbox with the preview's origin allowed:

```bash
rail sandbox up -origins http://localhost:3000
```

The current validation environment uses Mint CLI 4.2.502. `docs.json` defines navigation and branding. Guides are MDX files. `api-reference/openapi.json` is the self-contained public customer reference; its first server is the local sandbox (`https://localhost:8443`), which the interactive playground calls directly from the reader's browser (`proxy: false`); there is no shared hosted sandbox.

## Maintain the API reference

Use a reviewed customer contract and matching product catalog from the authorized maintainer checkout:

```bash
python3 maintenance/build_reference.py /path/to/rail.openapi.json /path/to/products/catalog.json
```

The generator preserves customer request and response constraints, parameters, security requirements, and status codes. It removes source-disclosure annotations and inherited fixture examples, rewrites the public introduction, and generates 127 endpoint pages. It never imports runtime or internal service specifications. `maintenance/contract-baseline.json` records the source and published hashes.

Resource labels live in `maintenance/reference_navigation.py`. The generator produces collapsed product groups with collapsed resource groups. After regeneration, copy `maintenance/api-navigation.json` into the `pages` array of **Browse by product** in the API tab of `docs.json`, then run all validation commands. Preserve the HTTP conventions group. Only nested groups collapse in Mintlify; do not move product groups to the top level. Validation checks coverage, grouping drift, collapsed defaults, and resource group size. See [Mintlify navigation](https://www.mintlify.com/docs/organize/navigation) and [OpenAPI setup](https://www.mintlify.com/docs/api-playground/openapi-setup).

## Reconcile docs with source

The October 3 audit (release 0.2.0) compares one baseline: the repositories' default branches, pinned by the release manifest. `maintenance/implementation-audit.json` records immutable revisions and operation coverage. `maintenance/implementation-notes.json` supplies reviewed restrictions to the endpoint generator; update it rather than editing generated endpoint pages.

To repeat the comparison, obtain an authorized workspace snapshot (pass it as both `--main` and `--preview` when there is one baseline), run `go run maintenance/list_handlers.go --root WORKSPACE` for each, and pass those JSON outputs to `maintenance/audit_implementation.py --main MAIN_WORKSPACE --preview PREVIEW_WORKSPACE --main-handlers MAIN_HANDLERS.json --preview-handlers PREVIEW_HANDLERS.json --date YYYY-MM-DD`. Inspect semantic restrictions separately: route coverage alone does not prove implementation completeness. Run the relevant SDK/service checks and record their scope in the validation report.

## Publishing

The connected Mintlify GitHub app deploys its configured production branch. A successful GitHub commit is not by itself confirmation of a successful Mintlify build; inspect the deployment check in GitHub or the Mintlify dashboard.

Do not publish credentials, private source links, internal ingress specifications, or patent materials. Use `AGENTS.md` for contributor boundaries.
