# API documentation versus implementation audit

Reconcile the public documentation with the current source on the service, shared runtime, contract, and SDK repositories. First pin repository revisions and retrieve changes since the previous documentation baseline without changing active implementation checkouts. Build an operation-by-operation comparison of the public contract, customer handler registration, shared request/response validation, and gateway exposure. Inspect semantic restrictions in handlers and authentication, webhook, SDK, and CLI behavior.

Correct public documentation and generated endpoint annotations where implementation is narrower than the contract, source behavior has changed, or examples imply unsupported flows. Preserve contract constraints unless a reviewed source contract changed. Do not publish private implementation paths, internal ingress routes, credentials, or private repository URLs. Document source coverage separately from deployment qualification and executed integration tests.

Keep a reproducible audit manifest and a readable findings report. Validate exact operation coverage, schemas, navigation, local links, changed SDK examples, and Mintlify build. Publish checked corrections to the docs repository and verify its deployment check. Implementation changes outside the docs repository are not part of this rectification.
