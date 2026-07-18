# AI Project Manager

> Every coding session must begin by reading this file after the project source-of-truth rules. Update it whenever milestone, sprint, risk, debt, or decision state changes.

## Status snapshot

| Field | Current state |
|---|---|
| Current milestone | Phase 5 - Practice System |
| Progress | Sprints 3A-3C, 4A, 4B and 4C complete; Sprint 4D practice vertical slice in progress |
| Overall status | Student lesson, bilingual exact-composition practice, typed/photo evaluation, second-attempt solutions, and session progress are operational for the controlled demo |
| Current sprint | Sprint 4D - Exact-Composition Practice Vertical Slice |
| Sprint goal | Deliver exactly 15 concept questions (5 easy, 5 medium, 5 hard), then connect them to the Student experience |
| Next task | Build the privacy-labelled synthetic Government Dashboard demo slice |

## Current milestone

### Phase 5 – Practice System

Sprint 4D is active on `feature/sprint-4d-practice-vertical-slice`. The first backend slice enforces the approved invariant of exactly 15 unique questions per concept: 5 easy, 5 medium, and 5 hard. It supports English Medium, Telugu Assisted English, and Pure Telugu profiles. Student UI integration, typed and handwritten answer evaluation, corrective feedback, second-attempt solution reveal, and session-only progress are complete. Cross-session persistence and identity-scoped ownership remain pending and must not be implied by the demo.

## Completed milestones

- Phase 1 — Foundation Documentation
- Phase 2 — Backend and project foundation
- Phase 3 — Responsive interface foundation and Student text-tutor integration
- Phase 4 — Governed OpenAI text tutor plus curriculum/textbook ingestion foundations

## Pending milestones

1. Phase 5 — Practice System (current)
2. Phase 6 — Assessment and Progress
3. Phase 7 — Parent Portal
4. Phase 8 — Teacher Portal
5. Phase 9 — Government Dashboard
6. Phase 10 — System Validation
7. Phase 11 — Controlled Deployment

## Development priorities

1. Protect student privacy, authorization boundaries, and secrets.
2. Validate the independent-learning journey and educational behavior.
3. Define stable domain and API contracts before interface implementation.
4. Treat English and Telugu as equal functional paths.
5. Build automated testing and observability with each capability.
6. Keep the modular monolith simple enough for a reliable demo and structured for future scale.

## Coding priorities

When coding is approved:

1. Establish configuration validation, errors, health checks, and test harnesses.
2. Implement authentication and domain-level authorization before sensitive features.
3. Add migrations, constraints, repositories, and synthetic data before dependent APIs.
4. Keep HTML, CSS, and JavaScript separate and reusable without embedding secrets.
5. Place OpenAI access behind a server-side provider gateway and policy validation.
6. Deliver complete vertical slices with tests instead of disconnected fragments.

## Quality checklist

- [ ] Scope and acceptance criteria are approved.
- [ ] Architecture and source-of-truth rules are followed.
- [ ] English and Telugu behavior is reviewed.
- [ ] Responsive and accessible states are complete.
- [ ] Inputs, outputs, and uploads are validated.
- [ ] Authorization is enforced server-side at the correct ownership/scope boundary.
- [ ] Errors are actionable to users and safe in logs/responses.
- [ ] No secrets or unnecessary personal data are exposed.
- [ ] Observability supports diagnosis without sensitive-data leakage.
- [ ] Documentation reflects material behavior and decisions.

## Review checklist

- [ ] Relevant files and current project status were inspected first.
- [ ] The implementation matches only the approved scope.
- [ ] Names, layering, and dependencies are clear.
- [ ] Duplicate logic and avoidable coupling are absent.
- [ ] Security, privacy, authorization, AI safety, and file handling were reviewed.
- [ ] English/Telugu, accessibility, and responsive effects were reviewed.
- [ ] Failure, retry, timeout, and empty-state behavior is explicit.
- [ ] The final diff contains no unrelated changes or credentials.
- [ ] Tasks, risks, debt, and decisions are updated where needed.

## Testing checklist

- [ ] Unit tests cover domain and policy rules.
- [ ] API/integration tests cover validation, persistence, transactions, and errors.
- [ ] Authorization tests include cross-user, cross-role, and out-of-scope attempts.
- [ ] AI tests cover structured outputs, language policy, educational policy, unsafe output, timeout, and provider failure.
- [ ] Practice tests enforce exactly 5 Easy, 5 Medium, and 5 Hard questions.
- [ ] Upload tests cover size, type, content mismatch, unsafe name/content, ownership, and download access.
- [ ] UI tests cover critical English/Telugu and mobile/desktop journeys.
- [ ] Accessibility checks cover keyboard use, focus, semantics, contrast, and text scaling.
- [ ] Regression and performance checks meet the approved quality gates.
- [ ] Test results and any justified omissions are summarized.

## Definition of Done

A task or feature is done only when:

- Its approved behavior and acceptance criteria work.
- UI alignment and responsive behavior are correct where applicable.
- English and Telugu paths are considered and tested where applicable.
- Validation, authorization, error, timeout, and recovery cases are handled.
- Relevant automated tests pass and results are recorded.
- Security/privacy review finds no exposed secrets or inappropriate data access.
- Documentation, task status, risks, technical debt, and decisions are updated.
- The final diff is reviewed and all changed files are summarized.
- Required human approval has been obtained.

## Next recommended task

**Connect the Sprint 4D practice API to the Student interface.** Render all 15 questions grouped into Easy, Medium, and Hard sections, preserve English/Telugu profiles, implement safe loading/error states, and add frontend regression coverage. Answer submission and evaluation remain the following approved slice.

## Project risks

| ID | Risk | Probability | Impact | Mitigation / next action | Owner | Status |
|---|---|---:|---:|---|---|---|
| R-001 | AI output may be inaccurate, unsafe, age-inappropriate, or instruction-breaking. | High | High | Govern prompts, validate structure/language, constrain contexts, test educational behavior, and provide safe fallbacks. | AI Lead | Open |
| R-002 | Student or organizational data may be exposed across role boundaries. | Medium | Critical | Define ownership/scopes, deny by default, enforce server-side checks, and automate negative authorization tests. | Security + Backend Lead | Open |
| R-003 | English works while Telugu quality or UI behavior lags. | High | High | Include Telugu in acceptance criteria, fixtures, content review, fonts, layouts, and every critical test journey. | Product + QA Lead | Open |
| R-004 | Image/PDF uploads introduce malware, spoofed types, excessive storage, or privacy leakage. | Medium | High | Use allowlists, detected types, limits, private storage, scanning where available, ownership checks, and retention policy. | Security + Backend Lead | Open |
| R-005 | Dashboard indicators mislead stakeholders or expose small cohorts. | Medium | High | Publish metric definitions, reconcile aggregates, label demo data, and define privacy thresholds. | Data/Product Lead | Open |
| R-006 | Demo scope expands faster than quality can be maintained. | High | High | Use milestone gates, P0/P1 priorities, explicit change control, and end-to-end vertical slices. | Project Manager | Open |
| R-007 | SQLite or synchronous AI work limits concurrency during the demonstration. | Medium | Medium | Size the demo load, add timeouts/queues where justified, rehearse, and preserve migration boundaries. | Tech Lead | Open |
| R-008 | Voice/visual explanation scope is ambiguous and may depend on additional services. | High | Medium | Decide supported modalities, accessibility behavior, provider constraints, and fallback before Phase 4 implementation. | Product + Tech Lead | Open |
| R-009 | Hosting, data residency, or government security requirements arrive late. | Medium | High | Capture deployment constraints during Phase 1 and require review before choosing cloud services. | Sponsor + Security Lead | Open |

## Technical debt

No application technical debt exists because implementation has not started. The following are **foreseeable debt traps**, not accepted debt:

| ID | Potential debt | Prevention |
|---|---|---|
| TD-001 | UI-specific business rules duplicated across four interfaces | Keep policies and authorization in backend/domain services; share frontend conventions. |
| TD-002 | SQLite assumptions leaking into domain services | Use repositories and migrations with database-neutral domain behavior. |
| TD-003 | OpenAI-specific payloads spreading through the codebase | Isolate them behind provider and structured-output interfaces. |
| TD-004 | English-only fixtures and layouts | Require bilingual fixtures and tests from the first vertical slice. |
| TD-005 | Untracked prompt changes | Version prompt/policy configurations and add regression evaluation. |

Accepted technical debt must have an owner, rationale, impact, review date, and repayment task.

## Decision log

| ID | Date | Decision | Rationale | Status |
|---|---|---|---|---|
| ADR-001 | 2026-07-16 | Use a modular monolith for the Government Demo. | It minimizes operational complexity while preserving separable domain, AI, data, and storage boundaries. | Proposed; requires approval |
| ADR-002 | 2026-07-16 | Use SQLite for the controlled demo behind repository interfaces. | It matches the source-of-truth stack and supports a later managed relational database migration. | Approved by project rules |
| ADR-003 | 2026-07-16 | Keep OpenAI access exclusively in the backend. | It protects credentials and centralizes educational, language, safety, usage, and observability policies. | Approved by project rules |
| ADR-004 | 2026-07-16 | Use versioned APIs shared by all web interfaces and a future mobile app. | Stable contracts reduce duplicated business logic and enable client evolution. | Proposed; requires approval |
| ADR-005 | 2026-07-16 | Use only synthetic, clearly labeled learner data for the demonstration until a separate privacy approval exists. | This reduces risk while demonstrating realistic workflows. | Proposed; requires approval |

Add or revise decisions when a choice materially affects architecture, security, data, dependencies, operations, or delivery. Do not silently overwrite historical decisions; mark them superseded and link the replacement.
## Sprint 4C delivery record

Sprint 4C establishes the enterprise textbook repository and deterministic PDF
ingestion foundation for two bilingual Andhra Pradesh Class 10 Mathematics
semester books. Delivery includes immutable domain contracts, generic book-part support,
provider-independent local storage, SHA-256 duplicate control, page-level
extraction, alias provenance, scanned-document detection, bilingual chapter detection
and a disabled-by-default manual command. OCR, embeddings, retrieval and AI
processing require separately approved future work.

## Sprint 4D delivery record

Sprint 4D started on 2026-07-18. The initial branch adds validated practice-domain models, a deterministic bilingual-safe generator, `POST /api/v1/practice/generate`, exact 5/5/5 composition and uniqueness enforcement, API regression tests, and repaired GitHub Actions configuration. Both CI workflows passed on the current branch. Student UI integration remains the next slice.
