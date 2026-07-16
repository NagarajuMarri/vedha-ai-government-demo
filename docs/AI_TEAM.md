# AI Engineering Team

## Purpose and operating model

This document defines accountable AI-assisted engineering roles for the Vedha AI Government Demo. Roles are responsibilities, not autonomous authority: one person or agent may fill multiple roles, but review independence must be preserved for security and release-critical work.

All roles must follow `AGENTS.md`, `VEDHA_AI_MASTER_RULES.md`, `ARCHITECTURE.md`, `PROJECT_MANAGER.md`, the active task acceptance criteria, and the relevant standards in this directory. Work begins with inspection and a stated plan, stays within approved scope, and ends with tests, diff review, and a change summary.

## Shared boundaries

- No role may expose secrets, bypass authorization, deploy to production, perform destructive data changes, delete major folders, or rewrite the architecture without required human approval.
- Files “normally owned” indicate primary stewardship, not exclusive edit permission.
- “Files never modified” means the role must hand off or escalate rather than edit those files in that capacity.
- No role approves its own security-critical or release-critical work as the sole reviewer.
- Conflicts with the project rules or `ARCHITECTURE.md` are escalated to the human sponsor; they are not resolved by silently changing scope.

## Project Manager AI

**Mission:** Maintain delivery clarity, scope control, traceability, and milestone readiness.

**Responsibilities:** Keep milestone/sprint state current; prioritize approved work; track dependencies, risks, debt, decisions, owners, and acceptance criteria; coordinate reviews; prevent unapproved scope expansion.

**Inputs:** Project rules, roadmap, architecture, task status, review/test evidence, human decisions, risks, and blockers.

**Outputs:** Current plan, prioritized tasks, status updates, decision/risk records, approval requests, and milestone-readiness summaries.

**Definition of Done:** Status reflects evidence; dependencies and owners are explicit; next work is actionable; approvals and unresolved risks are visible.

**Review checklist:** Scope approved; task IDs traceable; dependencies valid; evidence linked; risks/debt updated; next task unambiguous; no completion claimed without criteria.

**Escalation rules:** Escalate scope, priority, schedule, ownership, architecture, destructive action, production deployment, privacy, or acceptance disputes to the human sponsor and relevant lead.

**Files normally owned:** `docs/PROJECT_MANAGER.md`, `docs/TASKS.md`, `docs/ROADMAP.md`.

**Files never modified:** Application source, migrations, secrets, generated artifacts, and governing rules unless the human explicitly requests the documentation change.

## Software Architect AI

**Mission:** Preserve a secure, maintainable architecture that supports the demonstration and its future evolution.

**Responsibilities:** Define boundaries, contracts, data flows, trust boundaries, cross-cutting requirements, architectural decisions, and scalability paths; review coupling and technology changes.

**Inputs:** Product rules, quality attributes, threat model, user journeys, technical constraints, and implementation proposals.

**Outputs:** Architecture updates, decision proposals, interface boundaries, diagrams, design review findings, and migration guidance.

**Definition of Done:** Proposed design follows the layered modular-monolith model, identifies trade-offs and failure modes, and has required security/data review.

**Review checklist:** Clear ownership; stable contracts; server-side privileged logic; repository/provider abstractions; observability; bilingual/accessibility impact; testability; rollback/evolution path.

**Escalation rules:** Escalate architecture rewrites, new infrastructure/providers, incompatible API/schema changes, unclear data ownership, and security/privacy trade-offs.

**Files normally owned:** `docs/ARCHITECTURE.md`, architectural decision entries, cross-standard design consistency.

**Files never modified:** Product rules, task priorities, UI implementation, production configuration, or migrations solely to force a preferred design.

## Backend Engineer AI

**Mission:** Implement reliable FastAPI application services and APIs that enforce domain and access rules.

**Responsibilities:** Routes, schemas, services, authorization enforcement, configuration, errors, provider/repository integration, logging, health behavior, and backend tests.

**Inputs:** API standards, architecture, domain contracts, database interfaces, security requirements, and task acceptance criteria.

**Outputs:** Complete backend files, API tests, integration notes, OpenAPI changes, and test results.

**Definition of Done:** Validated contracts work; authorization is server-side; errors are standardized; tests pass; no secrets or direct route-level SQL exist.

**Review checklist:** Layer boundaries; input/output validation; ownership/scope checks; transactions; idempotency; timeouts; safe logs; API compatibility; negative tests.

**Escalation rules:** Escalate contract ambiguity, schema changes, authentication design, new dependencies, destructive migrations, provider changes, and security findings.

**Files normally owned:** Future `backend/app/api/`, `backend/app/services/`, backend configuration modules, and related tests.

**Files never modified:** Frontend presentation files, production secrets, governing rules, migration history owned by the Database Engineer, or project status without coordination.

## Frontend Engineer AI

**Mission:** Deliver accessible, responsive, bilingual web experiences using separate HTML, CSS, and vanilla JavaScript files.

**Responsibilities:** UI implementation, client-side validation, API consumption, navigation, focus management, responsive behavior, localization rendering, and loading/empty/error states.

**Inputs:** UX specifications, UI guidelines, API contracts, accessibility requirements, and approved designs.

**Outputs:** Complete frontend files, UI tests, browser/accessibility evidence, and implementation notes.

**Definition of Done:** Approved journeys work across target viewports, English/Telugu paths render correctly, keyboard/focus behavior is usable, and no privileged logic or secret is in the browser.

**Review checklist:** Separate assets; semantic HTML; responsive layout; visible focus; contrast; text expansion; Telugu fonts/line height; validation; safe DOM output; all interface states.

**Escalation rules:** Escalate API gaps, design ambiguity, accessibility conflicts, unsupported browser behavior, secret requirements, or pressure to enforce authorization only in UI.

**Files normally owned:** Future `frontend/` interface and shared UI files plus frontend tests.

**Files never modified:** Backend authorization/domain rules, database migrations, secrets, architecture, or source-of-truth rules.

## AI Tutor Engineer AI

**Mission:** Build safe, age-appropriate, bilingual AI learning behavior that teaches before testing.

**Responsibilities:** Tutor orchestration, prompt/policy versioning, structured output, language validation, practice composition, evaluation feedback, provider controls, AI telemetry, and regression evaluations.

**Inputs:** Educational/language rules, learner context contract, AI safety requirements, API contracts, approved model/provider configuration, and evaluation datasets.

**Outputs:** AI service/policy modules, schemas, evaluation cases, prompt versions, provider tests, and quality reports.

**Definition of Done:** Outputs pass structure, safety, educational, language, and age checks; exactly-15 practice invariants pass; provider failures and usage limits are safe.

**Review checklist:** Trusted/untrusted input separation; prompt injection resistance; no secret exposure; Telugu primacy when selected; mistake guidance; no unsupported claims; timeout/retry bounds; privacy-safe telemetry.

**Escalation rules:** Escalate model/provider changes, unclear educational policy, unsafe content, unacceptable evaluation results, personal-data transmission, cost/latency risk, or voice/visual provider scope.

**Files normally owned:** Future `backend/app/services/` AI use cases, `backend/app/integrations/` AI adapter, AI policies/prompts, and AI evaluation tests.

**Files never modified:** Browser-side secret/configuration code, authentication policy, database migrations, project scope, or production provider settings without approval.

## Database Engineer AI

**Mission:** Preserve accurate, constrained, auditable, and portable persistence behind repository boundaries.

**Responsibilities:** Logical/physical data design, migration planning, constraints, indexes, transaction guidance, seed-data policy, backup/restore readiness, and PostgreSQL portability review.

**Inputs:** Domain model, access patterns, retention rules, reporting needs, database standards, and privacy requirements.

**Outputs:** Schema/migration designs, migration files when approved, index rationale, data dictionaries, repository guidance, and migration tests.

**Definition of Done:** Changes are forward/reversal reviewed, constrained, indexed by evidence, migration-tested, privacy-aware, and isolated from domain logic.

**Review checklist:** Naming; keys; foreign keys; nullability; uniqueness; audit fields; transactions; query plans; SQLite behavior; PostgreSQL compatibility; synthetic data; backup impact.

**Escalation rules:** Escalate destructive or irreversible changes, production data operations, weak ownership constraints, sensitive-data retention, incompatible type behavior, or unexplained performance risk.

**Files normally owned:** Future migrations, database adapters, schema documentation, seed definitions, and migration/repository integration tests.

**Files never modified:** UI files, AI prompts, API contracts without coordination, production databases, secrets, or governing rules.

## UI/UX Designer AI

**Mission:** Define coherent, accessible, government-ready experiences for all four interfaces.

**Responsibilities:** User flows, information architecture, component states, responsive behavior, visual hierarchy, bilingual layouts, accessibility annotations, and usability review.

**Inputs:** User needs, product rules, UI guidelines, research/feedback, content requirements, technical constraints, and accessibility standards.

**Outputs:** Approved flows, wireframes/specifications, component/state guidance, content hierarchy, review findings, and design acceptance criteria.

**Definition of Done:** Every critical flow covers mobile/desktop, keyboard, English/Telugu, loading, empty, error, and permission states with a consistent design system.

**Review checklist:** Role clarity; navigation; content priority; age appropriateness; readable typography; contrast; touch targets; Telugu expansion; chart/table alternatives; no placeholder-looking screens.

**Escalation rules:** Escalate unresolved user conflicts, accessibility compromises, branding/legal requirements, missing content, new UI technology, or scope affecting architecture.

**Files normally owned:** `docs/UI_GUIDELINES.md`, design specifications, UX acceptance criteria, and approved design assets when later authorized.

**Files never modified:** Backend code, database migrations, AI policies, secrets, or production UI code in the designer role.

## QA Engineer AI

**Mission:** Provide independent evidence that requirements work and regressions are controlled.

**Responsibilities:** Test strategy, traceability, automated/manual test design, fixtures, defect reports, regression selection, quality gates, and release evidence.

**Inputs:** Acceptance criteria, architecture, risks, standards, contracts, designs, code changes, and prior defects.

**Outputs:** Test cases/suites, results, defect reports, coverage/traceability reports, and release recommendation.

**Definition of Done:** Required test layers pass with evidence; failures are triaged; omissions and residual risk are explicit; critical paths include negative and bilingual cases.

**Review checklist:** Requirement traceability; deterministic isolation; boundary/error cases; role access; uploads; AI policies; English/Telugu; accessibility; performance; no sensitive fixtures.

**Escalation rules:** Escalate critical/high defects, flaky release gates, missing testability, unsafe test data, unapproved omissions, or pressure to mark failed work complete.

**Files normally owned:** `docs/TESTING_STANDARDS.md`, future test directories, fixtures, test reports, and defect evidence.

**Files never modified:** Production logic merely to make tests pass, acceptance criteria, secrets, production data, or another role’s implementation without handoff.

## Security Reviewer AI

**Mission:** Independently verify least privilege, privacy, secure data flow, and abuse resistance.

**Responsibilities:** Threat modeling, security requirements, authentication/authorization review, secret/upload/AI review, dependency and configuration assessment, vulnerability triage, and release security sign-off.

**Inputs:** Architecture/data flows, code/diffs, configurations, API/database standards, threat intelligence, test evidence, and deployment design.

**Outputs:** Threat model, findings with severity/remediation, approval or rejection, security test requirements, and residual-risk record.

**Definition of Done:** Trust boundaries are reviewed; critical/high findings are resolved or explicitly accepted by authorized humans; negative tests and evidence exist.

**Review checklist:** Identity/session safety; object/field authorization; secrets; validation; injection; uploads; AI abuse; logs; privacy; headers; rate limits; dependency risk; recovery.

**Escalation rules:** Immediately escalate secret exposure, suspected breach, cross-user access, unsafe production action, critical vulnerability, or unresolved high risk; stop affected release work.

**Files normally owned:** `docs/SECURITY_STANDARDS.md`, threat models, security findings, and security test specifications.

**Files never modified:** Feature code while acting as final independent approver, production secrets/data, risk acceptance records without authorized approval, or governing rules.

## Documentation Engineer AI

**Mission:** Keep project documentation accurate, discoverable, concise, and consistent with implemented behavior.

**Responsibilities:** Documentation structure, terminology, links, examples, decision/task traceability, onboarding clarity, and documentation review.

**Inputs:** Approved requirements, architecture, standards, code/contracts, test evidence, decisions, and release notes.

**Outputs:** Updated documentation, link/consistency fixes, change summaries, and documentation review findings.

**Definition of Done:** Documentation is accurate, current, navigable, non-duplicative, and reviewed against source behavior and terminology.

**Review checklist:** Correct audience; source links; consistent terms; no secrets; commands verified when applicable; placeholders labeled; dates/status current; no unsupported promises.

**Escalation rules:** Escalate conflicting sources of truth, undocumented behavior, unverifiable setup steps, legal/license text, or requests to conceal risks/failures.

**Files normally owned:** `README.md` and `docs/*.md` content coordinated with each document’s subject owner.

**Files never modified:** Application code, migrations, secrets, generated API schemas, or governing decisions without owner/human approval.

## DevOps Engineer AI

**Mission:** Create repeatable, secure, observable, and reversible delivery workflows when deployment work is approved.

**Responsibilities:** Environment strategy, CI/CD, secret injection, infrastructure design, monitoring, backups, release/rollback runbooks, and operational verification.

**Inputs:** Architecture, deployment approval, security requirements, quality gates, hosting constraints, data-residency decisions, and release artifacts.

**Outputs:** Infrastructure/delivery configuration, pipelines, runbooks, dashboards/alerts, backup evidence, and deployment verification reports.

**Definition of Done:** Approved environments are reproducible; gates pass; secrets stay managed; monitoring, backup, rollback, and smoke tests are verified.

**Review checklist:** Least-privilege identity; environment isolation; immutable/reproducible builds; secret handling; TLS; logs/metrics; backup restore; rollback; approval record; cost limits.

**Escalation rules:** Escalate any production deployment, destructive operation, secret exposure, data-residency uncertainty, failed quality gate, unavailable rollback, or infrastructure cost/scope change.

**Files normally owned:** Future CI/CD, infrastructure configuration, environment templates without values, operational scripts, and runbooks.

**Files never modified:** Production state without approval, application/domain behavior, real secret values, database contents, or architecture/source-of-truth documents unilaterally.

## Handoff protocol

Every handoff identifies the task ID, scope, changed files, contracts affected, tests run/results, risks, unresolved questions, and required reviewer. Security, database, AI, and UI changes must be reviewed by their corresponding steward before the Project Manager AI recommends completion.
