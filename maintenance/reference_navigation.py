"""Stable, compact resource navigation shared by the docs and contract generator."""
RESOURCE_GROUPS = {
    'operations': 'Asynchronous operations',
    'actions': 'Actions and evaluations', 'evaluations': 'Actions and evaluations',
    'executions': 'Executions', 'approvals': 'Approvals',
    'principals': 'Principals', 'authority-grants': 'Authority grants',
    'delegations': 'Delegations', 'capability-tokens': 'Capabilities and reservations',
    'authority-reservations': 'Capabilities and reservations',
    'receipts': 'Receipts and proofs', 'verification-keys': 'Receipts and proofs',
    'receipt-verifications': 'Verification and dispositions', 'dispositions': 'Verification and dispositions',
    'projections': 'Projections and effect decisions', 'effect-decisions': 'Projections and effect decisions',
    'dependency-invalidations': 'Invalidation and retention', 'checkpoints': 'Invalidation and retention',
    'twin-retention-requests': 'Invalidation and retention',
    'events': 'Events and webhooks', 'webhook-subscriptions': 'Events and webhooks',
    'assets': 'Assets and versions', 'promotions': 'Promotions and process cases',
    'process-cases': 'Promotions and process cases',
    'contributions': 'Contributions and provenance', 'outcomes': 'Contributions and provenance',
    'provenance-graphs': 'Contributions and provenance',
    'rights-records': 'Rights and allocations', 'allocations': 'Rights and allocations',
    'beneficiary-updates': 'Rights and allocations', 'disclosure-requests': 'Selective disclosure',
    'lots': 'Lots and transformations', 'lot-transformations': 'Lots and transformations',
    'realizations': 'Realizations and remedies', 'escrow-accounts': 'Escrow accounts',
    'settlements': 'Settlements and release', 'disputes': 'Disputes',
    'context': 'Context and projects', 'projects': 'Context and projects',
    'object-uploads': 'Object storage', 'objects': 'Object storage',
    'targets': 'Targets and adapters', 'adapters': 'Targets and adapters',
    'challenges': 'Attestation', 'attestations': 'Attestation',
    'resource-measurements': 'Resource and energy evidence', 'resource-estimates': 'Resource and energy evidence',
    'energy-comparisons': 'Resource and energy evidence',
    'edge-nodes': 'Edge nodes and allocations', 'edge-allocations': 'Edge nodes and allocations',
    'coverage-evaluations': 'Coverage and campaigns', 'campaign-evaluations': 'Coverage and campaigns',
    'journeys': 'Journeys and safety',
    'suspensions': 'Suspensions', 'agent-profile-versions': 'Principals',
    'execution-shares': 'Execution shares', 'shares': 'Execution shares',
    'baseline-policy-proposals': 'Baseline policies', 'baseline-policies': 'Baseline policies',
    'contacts': 'Edge nodes and allocations', 'report': 'Receipts and proofs',
}
# A sub-resource under another resource's path (/v1/<resource>/{id}/<sub>)
# groups by <sub> when it has its own group, so 0.2.0 operations such as
# /v1/principals/{id}/suspensions and /v1/projects/{id}/baseline-policies sit
# with their resource rather than their parent.
SUB_RESOURCES = {('principals', 'suspensions'), ('principals', 'agent-profile-versions'), ('executions', 'shares'), ('projects', 'baseline-policy-proposals'), ('projects', 'baseline-policies'), ('edge-nodes', 'contacts'), ('receipts', 'report')}


def product_group(title, entries):
    """entries is an ordered iterable of (public route, HTTP path)."""
    resources = {}
    for route, path in entries:
        parts = path.split('/')
        key = parts[4] if len(parts) > 4 and (parts[2], parts[4]) in SUB_RESOURCES else parts[2]
        label = RESOURCE_GROUPS[key]
        resources.setdefault(label, []).append(route)
    return {'group': title, 'expanded': False, 'pages': [
        {'group': label, 'expanded': False, 'pages': pages}
        for label, pages in resources.items()
    ]}
