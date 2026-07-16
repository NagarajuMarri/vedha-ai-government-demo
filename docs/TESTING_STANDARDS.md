# Testing Standards

## Scope and architecture reference

Testing follows the layers and trust boundaries in `ARCHITECTURE.md`: responsive clients, versioned FastAPI APIs, application/domain services, repositories, file storage, and the server-side OpenAI gateway. Tests provide release evidence; they do not replace review, observability, threat modeling, or stakeholder acceptance.

## Core principles

- Trace tests to task acceptance criteria, risks, contracts, and educational/language rules.
- Keep tests deterministic, isolated, readable, and fast at the lowest suitable layer.
- Use synthetic data only; never copy real student, government, credential, or production data.
- Test positive, boundary, negative, failure, retry, timeout, ownership, and recovery paths.
- A failing test is fixed or explicitly triaged; it is never silently disabled to pass a gate.
- External AI, time, randomness, filesystem, and network behavior must be controlled at unit/integration boundaries.

## Test pyramid and environments

Favor many unit tests, focused integration/API tests, and a smaller set of critical browser/end-to-end journeys. Each environment uses repeatable configuration, isolated databases/storage, and fake credentials/providers. Test runs must never contact production or mutate shared uncontrolled state.

## Unit tests

Cover domain rules, schemas, policies, calculations, authorization decisions, language validation, practice composition, error translation, and utility behavior without real network/database dependencies. Use clear arrange/act/assert structure and parameterize meaningful boundaries. Mock at architectural ports rather than internal implementation details.

## Integration tests

Verify repository behavior, SQLite constraints/transactions/migrations, application-service orchestration, file metadata/storage boundaries, and provider adapters with controlled fakes. Test rollback, idempotency, concurrency-sensitive behavior, foreign keys, and representative previous-schema migration paths.

## API tests

Validate every documented status, request/response schema, content type, pagination, error envelope, OpenAPI contract, authentication state, role/relationship/scope authorization, rate-limit classification, and correlation ID behavior. Include cross-user object access, field disclosure, oversized payloads, unsupported media, duplicate submission, and upstream failure.

## Frontend tests

Test navigation, forms, validation, API success/failure, focus, loading, empty, permission, retry, and responsive behavior for all four interfaces. Critical paths require browser-level coverage at selected mobile and desktop widths. Verify separate English/Telugu paths, safe DOM rendering, duplicate-action prevention, and absence of secrets in browser artifacts.

## AI tests

Use layered evaluation:

- Deterministic unit tests for prompt/policy assembly, trusted/untrusted separation, schema parsing, language checks, and safe fallbacks.
- Contract tests against a fake provider for timeout, throttling, malformed output, refusal, and retry behavior.
- Curated synthetic evaluation sets across classes, subjects, concepts, English/Telugu, misconceptions, unsafe requests, and prompt injection.
- Invariant tests requiring exactly 15 accepted practice questions: 5 Easy, 5 Medium, and 5 Hard.
- Rubric review for teach-before-test, age appropriateness, simple stepwise explanation, mistake identification, corrective guidance, and performance adaptation.

Live-provider evaluations require explicit configuration, cost controls, no personal data, recorded model/policy versions, tolerance for nondeterminism, and must not be the sole CI gate.

## Regression tests

Every defect gains a focused regression test at the lowest effective layer. Maintain a versioned critical-journey suite covering authentication, student tutor/practice/assessment/progress, parent linking, teacher scope, government aggregation, bilingual behavior, uploads, and AI policies. Review rather than blindly grow the suite; quarantine requires owner, reason, risk, and deadline.

## Performance tests

Define measurable budgets during Phase 1 for non-AI API latency, AI time-to-feedback/timeout, page responsiveness, upload size/time, database concurrency, and dashboard queries. Test representative synthetic volume, warm/cold behavior, rate limits, degradation, and recovery. Record environment and percentiles; averages alone are insufficient. Rehearse the expected demonstration concurrency on SQLite.

## Accessibility tests

Combine automated scanning with manual keyboard and screen-reader checks. Cover semantic structure, headings/landmarks, labels, error association, focus order/visibility, dialogs/navigation, status announcements, contrast, zoom/reflow, touch targets, reduced motion, chart alternatives, media captions/transcripts, and English/Telugu text/glyph behavior. Target WCAG 2.1 AA practices defined in `UI_GUIDELINES.md`.

## Security tests

Use threat-model-driven tests for authentication/session weaknesses, role/relationship/scope authorization, object and field access, injection, output encoding, CSRF/CORS as applicable, rate limits, security headers, error leakage, secrets, upload spoofing/path traversal/size/malware controls, AI prompt injection/data leakage, audit events, and dependency/configuration risk. Critical/high findings block release unless formally accepted by authorized humans.

## Test data and fixtures

Fixtures are minimal, deterministic, role-labeled, privacy-safe, and isolated per test. Factories express intent and avoid brittle global state. Uploaded fixtures contain known safe/unsafe synthetic samples without harmful executable payloads. Telugu fixtures include realistic script, mixed technical terms, long text, and Unicode edge cases.

## Test evidence and reporting

Record command/suite, environment, revision, result, duration, failures, skipped/quarantined tests, relevant coverage, and artifacts. Defects include severity, reproduction, expected/actual result, affected roles/languages, security/privacy impact, and traceable task. Never include secrets or unnecessary personal/AI content in artifacts.

## Definition of test completion

Testing is complete for a task only when:

- Acceptance criteria and architectural risks have traceable coverage.
- Required unit, integration, API, frontend, AI, regression, performance, accessibility, and security layers are executed or a justified non-applicability is reviewed.
- English and Telugu, mobile/desktop, success/failure, and role boundaries are covered where applicable.
- All required suites pass; no unresolved critical/high security or privacy defect remains.
- Flaky, skipped, quarantined, and manual cases are disclosed with owner and follow-up.
- Results and residual risk are reviewed by QA and the relevant technical/security owner.
- `PROJECT_MANAGER.md` and `TASKS.md` are updated when project state changes.

## Quality gate ownership

The feature engineer supplies tests; the QA Engineer verifies strategy and evidence; the Security Reviewer independently reviews security-critical results; the Project Manager AI reports status. Production deployment still requires explicit human approval under the project rules.
