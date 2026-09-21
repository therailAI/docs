# The Rail developer documentation

This is the public Mintlify documentation for The Rail: the authorization and clearing layer for autonomous agents. Configuration is in `docs.json`; pages are MDX with YAML frontmatter.

## Writing and terminology

- Use concise active voice, second person, and sentence case headings.
- Say “The Rail” for the product; preserve API identifiers exactly.
- Distinguish OAuth authentication, bounded authority, execution, verification, clearing, and confirmed settlement.
- A receipt is evidence, not a grant. Completion, result release, and settlement have separate gates.
- Label contract behavior, deployment requirements, recorded evidence, and illustrative examples.
- Do not imply public package releases, hosted endpoints, production SLAs, live customer results, or compliance guarantees without supporting release evidence.

## Sources and boundaries

- The bundled reference is customer contract 0.1.1. Generate endpoint pages with `maintenance/build_reference.py`; do not hand-edit generated files.
- Never publish internal/runtime ingress specifications, secrets, patent source maps, private source URLs, or customer information.
- Keep the six recorded workflow links and limitations aligned with the public website.
- Use official Mintlify documentation for configuration and MDX behavior. Prefer Mintlify MCP when available; otherwise edit locally and validate with the installed CLI.

## Validation

Run `python3 maintenance/validate.py`, `mint validate`, and `mint broken-links`. Verify SDK examples against the matching supplied SDK when changing them. Confirm navigation and redirects. Keep the API playground non-interactive until a documented public environment exists.
