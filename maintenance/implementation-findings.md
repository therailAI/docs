# Documentation rectification — September 26, 2026

The audit compared the public docs with pinned repository default branches and with the newer local preview. Immutable source revisions and a row for every customer operation are in `implementation-audit.json`. Primary integration guidance now follows the repository baseline; local-preview guides remain available with prominent qualification.

## Findings and corrections

| Finding | Documentation correction | Implementation follow-up |
| --- | --- | --- |
| Local CLI/profile/govern helpers were documented as generally available, but are absent from reviewed default branches | Marked preview workflows and imports; added a tooling baseline table | Publish/review the newer source and distributions before presenting it as repository functionality |
| Repository TypeScript package has an empty export map; normal package import fails | Reproduced `ERR_PACKAGE_PATH_NOT_EXPORTED`; replaced installation/import instructions with a tested direct source-build path | Correct package exports and validate a packaged consumer before a release |
| Repository SDKs lack per-call custom-header options shown for the preview | Version-qualified header behavior and documented the transport requirement | Port and qualify the preview header support if desired |
| Six product namespaces do not map to six network services or automatically select service hosts | Added owning service to every endpoint, a ten-service table, and distinct platform/execution addresses in samples | A unified customer gateway remains a deployment concern |
| Principal/project records were easy to confuse with active enrollment | Added operator enrollment, effective-scope intersection, and project configuration requirements | A self-service enrollment workflow is not established |
| Human enrollment enforcement was conflated with enforcement of OAuth grant type/step-up | Distinguished Rail's human/eligibility checks from identity-provider login and assurance controls | Qualify production IdP flows; the reviewed handler does not itself prove MFA or grant type |
| Contract enumerates four reconciliation reasons; handler supports two | Added exact supported reasons and unavailable-response behavior to the guide and endpoint | Target-status/idempotency-state adapters remain unavailable through this endpoint |
| Registry/routing and authority issuance do not automatically support execution's conditional approval workflow | Added unsupported-obligation notes | Implement additional handlers only if required by the deployment |
| Webhook HTTPS syntax alone is insufficient | Added operator hostname approval, public-address checks, and expired-challenge behavior | No Svix integration was claimed or added |
| Execution completion was insufficiently distinguished from result release and output retrieval | Documented owner/project checks, independent release gate, and admitted-assertion output | Application artifact retrieval still follows the object flow |

## What matched

- Customer contract 0.1.1 is unchanged across both source baselines.
- All 127 customer operations have service handler registrations, across ten services.
- Both SDK operation catalogs match all 127 methods, paths, request schemas, and success-response schemas in each baseline.
- Published schemas, security requirements, and operation contracts match the reviewed source after the existing public-document sanitization.
- Existing endpoint URLs, product/resource grouping, and legacy redirects are preserved.

## Verification

- Full repository SDK suites: TypeScript 17 tests; Python 14 tests.
- Targeted Go tests: public schema compilation/CORS, identity validation/fault cases, webhook domain behavior.
- All ten service module trees compile (`go test -run '^$'`); this is a compilation check, not execution of their integration tests.
- Revised TypeScript examples type-check and execute with a mocked transport using the real built repository client and direct entry-file import.
- Revised Python examples execute with the real repository client, correct service destinations, schema-valid mock responses, and owned transports closed.
- All shell examples pass syntax validation; source/contract comparison, docs structure, Mintlify build, and internal links pass.

No authenticated production endpoints, real payment providers, or database-backed service integration suites were exercised. Registered handlers and matching schemas do not establish complete semantic or production readiness. Implementation defects and unpublished source were documented, not silently patched or published as part of the docs change.
