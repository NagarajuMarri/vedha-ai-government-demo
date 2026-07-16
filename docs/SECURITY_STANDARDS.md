# Security Standards

## Scope and architecture reference

These standards apply to every layer and trust boundary in `ARCHITECTURE.md`. Security is a shared engineering requirement with independent review; browser interfaces are untrusted clients, the FastAPI backend is the policy-enforcement point, repositories/providers are constrained adapters, and external AI/file services are separate trust boundaries.

## Security principles

- Deny by default, grant least privilege, and verify every request independently.
- Minimize collection, disclosure, retention, privileges, dependencies, and exposed surface.
- Keep secrets and privileged decisions server-side.
- Use defense in depth; UI hiding, identifiers, rate limits, and AI instructions are not authorization controls.
- Fail safely without leaking protected existence or internal details.
- Use synthetic demo data until real-data governance is explicitly approved.

## Authentication

- Use an approved server-managed session/token design with modern credential hashing, short lifetimes, rotation/revocation, and secure recovery.
- Protect login/recovery with generic responses, throttling, audit events, and abuse detection.
- Hosted cookie sessions require `Secure`, `HttpOnly`, appropriate `SameSite`, CSRF protection, and bounded scope/lifetime.
- Prevent session fixation and invalidate sessions after sensitive identity changes.
- Require stronger authentication for administrative/government access before production readiness.
- Never store plaintext passwords, reusable tokens, or authentication secrets in logs or browser storage without an approved threat-model decision.

## Authorization

- Enforce role, action, resource ownership, relationship, field disclosure, and organization scope in backend application/domain services.
- Parent access requires an active parent-child link; teacher access requires current assignments; administrators/government users require explicit organizational scope.
- Filter lists and aggregates by authorized scope before data leaves the repository/service boundary.
- Use opaque identifiers but never treat unpredictability as authorization.
- Test cross-user, cross-role, changed-assignment, direct-object, nested-resource, export, upload, and aggregate disclosure attempts.

## Secrets and environment variables

- Commit no secret values. Use environment variables for the controlled demo and a managed secret store for hosted production evolution.
- Commit only safe variable-name templates with non-secret examples.
- Validate required configuration at startup; never fall back to insecure defaults.
- Separate secrets by environment/service, grant least privilege, rotate periodically and after suspected exposure, and document revocation.
- Redact secrets from errors, logs, traces, test artifacts, screenshots, process output, and client bundles.
- Suspected exposure is an incident: stop use, revoke/rotate, assess logs/history, notify the authorized human, and record remediation without reproducing the value.

## OpenAI API protection

- Call OpenAI only from the backend gateway; never expose the API key or direct privileged provider access to frontend JavaScript.
- Send the minimum validated learner/context data and avoid personal identifiers or raw files unless explicitly required and approved.
- Separate trusted policy instructions from untrusted student/file content and defend against prompt injection and data exfiltration.
- Enforce model allowlists, request/output limits, structured schemas, safety/language/educational validation, timeouts, bounded retries, quotas, and cost monitoring.
- Do not log unrestricted prompts/responses; retain only governed, minimized telemetry with policy and retention.
- Provider output is untrusted until validated and safely encoded for its destination.

## Upload security

- Require authentication and ownership/scope authorization before upload, processing, metadata access, or download.
- Allowlist business-required extensions and independently detected content types; reject mismatches, double extensions, archives, executables, and unsafe active content.
- Enforce file count, per-file/request size, image dimensions/pages, processing time, and storage quota.
- Generate opaque server filenames, prevent traversal, isolate private storage outside web roots, and set restrictive permissions.
- Scan for malicious content where supported; decode/re-encode media when appropriate; process with least-privilege isolated workers for future production.
- Store integrity hash and safe metadata, define retention/deletion, and serve only through authorized endpoints or short-lived signed URLs.
- Never pass unvalidated uploaded content directly into AI or render it as trusted browser content.

## Student privacy

- Treat identity, learning activity, answers, evaluations, progress, voice/image/PDF content, and parent links as sensitive student data.
- Collect only what the approved learning journey needs; define purpose, access, retention, correction, and deletion before collection.
- Use synthetic data for the Government Demo unless explicit privacy/legal/governance approval authorizes otherwise.
- Do not expose student data to unrelated parents, teachers, schools, government scopes, analytics, logs, or AI providers.
- Avoid harmful labeling; feedback and metrics must be contextual, age-appropriate, and limited to authorized users.
- Complete privacy and child-safety review before any real learner deployment.

## Government and aggregate data

- Government access is organization-scoped and purpose-limited; it does not imply unrestricted student-level access.
- Prefer aggregates and apply approved minimum-cohort/privacy suppression rules.
- Define metrics, periods, sources, freshness, missing-data behavior, and demo/synthetic labels.
- Prevent filter/drill-down combinations that reconstruct small groups or individuals.
- Audit privileged views/exports and apply stronger authentication, export limits, watermarking/labeling, and retention when approved.

## Logging, auditing, and monitoring

- Use structured, access-controlled logs with correlation IDs and safe operational fields.
- Never log credentials, tokens, secret configuration, raw uploads, unnecessary personal data, or unrestricted AI content.
- Security audit events capture actor, action, target category, permitted scope, result, time, and correlation ID; protect integrity and retention.
- Monitor authentication abuse, authorization denials, unusual exports/uploads, AI usage anomalies, error spikes, and administrative actions.
- Keep user-facing errors generic and diagnostics server-side; redact before third-party monitoring.

## OWASP considerations

Threat modeling and review must cover current OWASP web/API classes, including broken access control/object authorization, cryptographic failures, injection, insecure design, security misconfiguration, vulnerable components, authentication failures, integrity failures, logging/monitoring failures, server-side request forgery, unrestricted resource consumption, unsafe API inventory/consumption, mass assignment/property authorization, and unsafe file handling.

Controls include schema allowlists, parameterized persistence, context-aware output encoding, restrictive outbound access, dependency review, locked/verified builds when introduced, CORS/CSRF/header controls, body/time/rate quotas, OpenAPI inventory, server-side property allowlists, and negative authorization tests. Compliance checklists supplement rather than replace system-specific threat modeling.

## Dependency and supply-chain security

When packages are later approved, minimize them, use trusted sources, pin/lock reproducibly, review licenses/maintenance, scan known vulnerabilities, protect CI credentials, and verify generated artifacts. New runtime dependencies require rationale and architecture/security review. Never run untrusted install scripts or commit package credentials.

## Incident and vulnerability handling

Classify findings by exploitability and impact, assign an owner and deadline, preserve appropriate evidence, and avoid spreading sensitive details. Suspected breach, cross-user disclosure, secret exposure, or critical vulnerability is immediately escalated and affected release/deployment work stops. Risk acceptance requires an authorized human, rationale, expiry/review date, and compensating controls.

## Future production readiness

Before production or real student data:

- Obtain explicit human deployment and data-governance approval.
- Complete threat model, privacy/child-safety review, penetration testing, and critical/high remediation.
- Use TLS-only hosting, WAF/edge protections as appropriate, managed secrets, least-privilege service/database identities, network boundaries, encryption, and hardened configuration.
- Establish data classification, residency, retention/deletion, consent/legal requirements, vendor agreements, and incident notification responsibilities.
- Verify backups/restores, disaster recovery, monitoring/alerting, audit retention, capacity/rate limits, patching, vulnerability management, rollback, and operational runbooks.
- Separate environments and data; prohibit production data in development/test.
- Require CI quality/security gates and post-deployment smoke/security checks.

## Security completion gate

A change is security-complete only when its trust boundaries, data classification, authentication/authorization, validation/output handling, secret/provider/upload exposure, privacy, abuse limits, logs/audit, dependencies, failure behavior, and required negative tests are reviewed against `ARCHITECTURE.md`, `API_STANDARDS.md`, `DATABASE_STANDARDS.md`, and `TESTING_STANDARDS.md`. Critical/high findings block completion unless explicitly accepted by an authorized human.
