# API Standards

## Scope and architecture reference

These standards implement the versioned FastAPI boundary described in `ARCHITECTURE.md`. Routes are transport adapters; schemas validate contracts; application/domain services enforce use cases and authorization; repositories/providers handle infrastructure. Browser clients never receive privileged credentials.

## Versioning

- Prefix public application APIs with `/api/v1`.
- Use a new major path version only for intentionally incompatible contract changes.
- Prefer additive, optional changes within a major version; never silently change field meaning.
- Document deprecation, migration, and removal dates before retiring a contract.
- Version AI policy/provider internals separately from client-facing APIs when the external contract is unchanged.

## Naming

- Use lowercase plural resource nouns and hyphenated multiword path segments: `/student-profiles`, `/practice-sets`.
- Use path parameters for identity and nesting only when the parent relationship is meaningful.
- Use `snake_case` JSON fields consistent with Python schemas.
- Use ISO 8601 UTC timestamps and explicit units in names when ambiguity exists.
- Avoid verbs in resource endpoints; use action subresources only when no resource model is natural.

## Endpoint conventions

| Operation | Method | Pattern |
|---|---|---|
| List | GET | `/api/v1/resources` |
| Retrieve | GET | `/api/v1/resources/{resource_id}` |
| Create | POST | `/api/v1/resources` |
| Partial update | PATCH | `/api/v1/resources/{resource_id}` |
| Replace | PUT | Only when full replacement semantics are genuinely supported |
| Delete | DELETE | Only with approved lifecycle/authorization semantics |

GET/HEAD are safe; PUT/DELETE should be idempotent; POST submission/finalization endpoints should support an approved idempotency strategy where retries could duplicate effects. Never encode secrets or sensitive content in URLs.

## Request validation

- Validate path, query, header, body, and file inputs with explicit schemas and bounds.
- Reject unknown fields for security-sensitive requests unless forward compatibility requires and documents otherwise.
- Normalize only after validation; do not silently coerce ambiguous values.
- Enforce content type, body/file size, collection length, text length, enum, and cross-field/domain rules.
- Treat browser validation as usability only; the server remains authoritative.

## Response format

Successful single-resource responses return the documented resource representation. Collections use a consistent envelope:

```json
{
  "data": [],
  "pagination": {
    "next_cursor": null,
    "has_more": false,
    "limit": 25
  },
  "request_id": "opaque-correlation-id"
}
```

Errors use one safe envelope:

```json
{
  "error": {
    "code": "stable_machine_code",
    "message": "Safe user-facing summary",
    "details": [],
    "request_id": "opaque-correlation-id"
  }
}
```

Do not expose stack traces, provider payloads, SQL, secret values, or sensitive resource existence. Field omission and `null` must have distinct documented meanings.

## HTTP status codes

| Code | Use |
|---:|---|
| 200 | Successful read/update or completed action with body |
| 201 | Resource created; include `Location` when practical |
| 202 | Accepted asynchronous work with status resource |
| 204 | Successful operation with no response body |
| 400 | Malformed request not represented by field validation |
| 401 | Missing/invalid authentication |
| 403 | Authenticated but not authorized; do not reveal protected existence |
| 404 | Resource absent or intentionally concealed by authorization policy |
| 409 | State, uniqueness, version, or idempotency conflict |
| 413 | Request/upload too large |
| 415 | Unsupported media type |
| 422 | Syntactically valid request failing schema/domain validation |
| 429 | Rate limit exceeded, with safe retry guidance |
| 500 | Unexpected internal failure |
| 502/503/504 | Controlled upstream/unavailable/timeout conditions |

## Pagination, filtering, and sorting

- Default and maximum limits must be bounded and documented.
- Prefer cursor pagination for mutable/high-volume event data; offset pagination is acceptable for small stable admin lists.
- Cursors are opaque and tamper-resistant; clients must not construct them.
- Allowlist filters and sort fields; use deterministic tie-break sorting.
- Return pagination metadata without expensive total counts unless the product needs and can support them.

## Authentication

Use the server-managed authentication approach approved by the threat model. Authentication errors are generic, sessions/tokens are short-lived and revocable, transport is protected by TLS when hosted, and credentials are never logged or returned to unauthorized clients. Cookie-based flows require secure cookie and CSRF controls.

## Authorization

- Enforce role, relationship, organization scope, resource ownership, and action policy in application/domain services.
- Deny by default and filter collections at the data-access boundary; do not fetch all then hide in the UI.
- Parent-child, teacher-class, administrator-school, and government organizational scopes require explicit tests.
- Field-level disclosure rules apply independently of endpoint access.

## Error handling

Translate schema, domain, persistence, provider, and unexpected failures into stable error codes. Log full diagnostic context only where privacy-safe, return a request ID, preserve transactional integrity, and retry only transient idempotent operations with bounded backoff. AI/provider failure must not be misrepresented as student error.

## Logging and observability

- Generate or accept a validated correlation/request ID and propagate it through services/providers.
- Use structured logs with event name, severity, timestamp, route template, status, latency, actor/scope identifiers only when justified, and safe failure category.
- Never log secrets, authentication material, raw uploads, unnecessary personal data, or unrestricted AI prompts/responses.
- Record security-relevant audit events separately with integrity and retention controls.
- Expose health/readiness signals without configuration or dependency secrets.

## OpenAPI rules

- FastAPI routes must declare operation IDs, tags, summaries, request/response schemas, auth requirements, status responses, and useful examples using synthetic data.
- Generated OpenAPI must match runtime responses and be checked in tests.
- Mark deprecated operations explicitly; do not publish internal/provider schemas unintentionally.
- Schema descriptions must state units, nullability, enum meaning, and sensitive-field behavior.

## Rate limiting and usage controls

Apply limits by endpoint risk, authenticated actor, organization, and trusted network signal where appropriate. Authentication, AI, upload, export, and report operations need stricter limits and quotas. Return 429 with safe `Retry-After` guidance when known. Limits must not be the sole defense against authorization or abuse.

## Security headers and transport

Hosted APIs require TLS. Configure restrictive CORS allowlists, `X-Content-Type-Options: nosniff`, an appropriate Content Security Policy for web delivery, clickjacking defense (`frame-ancestors`), Referrer Policy, Permissions Policy, and HSTS after HTTPS-only readiness. Prevent sensitive response caching with explicit cache directives. Header choices must be tested and documented per deployment.

## API completion gate

An endpoint is complete only when its contract, authorization policy, validation, errors, logging, OpenAPI description, rate-limit classification, and positive/negative pytest coverage align with `ARCHITECTURE.md`, `DATABASE_STANDARDS.md`, `SECURITY_STANDARDS.md`, and `TESTING_STANDARDS.md`.
