# Development Task Tracker

## Usage

- Move tasks between status sections rather than duplicating them.
- Keep status, dependencies, acceptance criteria, and owner current.
- Owners are roles until named people are assigned.
- Effort is an initial working estimate and should be refined during sprint planning.
- New scope requires a new task ID and alignment with the roadmap.

## Locked government-demo requirements

These requirements were approved by the project sponsor on 2026-07-19 and are non-negotiable for the controlled government demonstration:

1. **Role-wide bilingual voice input:** Student, Teacher, Parent, and Government interfaces accept English and Telugu speech, show an editable transcript before submission, and retain typed-input fallback.
2. **Spoken output:** Lessons and role-appropriate insights support English/Telugu read-aloud with play, pause, replay, mute, and failure fallback.
3. **Narrated educational animations:** Concept visuals are instructional rather than decorative. Narration, captions, and highlighted visual steps remain synchronized.
4. **Accessible learner controls:** Animations provide step-by-step mode, individual-step replay, a readable transcript, and a short understanding check.
5. **Functional Parent Portal:** Demonstrates linked-child progress, strengths, attention areas, recent activity, and support recommendations using clearly labeled synthetic data.
6. **Functional Teacher Portal:** Demonstrates class/student performance, concept insights, intervention signals, and assignable remedial actions using clearly labeled synthetic data.
7. **Integrated government-demo journey:** Student, Parent, Teacher, and Government experiences must work together in the final bilingual rehearsal and runbook.

Decorative background motion, disabled microphone controls, silent animations, and static portal shells do not satisfy these requirements.

## TODO

### VGD-002 — Approve architecture and threat model

| Field | Value |
|---|---|
| Priority | P0 |
| Description | Review system boundaries, data flows, trust boundaries, role scopes, AI risks, and upload risks before implementation. |
| Dependencies | VGD-001 |
| Estimated effort | 2–3 days |
| Owner | Tech Lead + Security Reviewer |
| Status | TODO |

**Acceptance criteria:**

- Architecture assumptions and trust boundaries are reviewed.
- Authentication, authorization, AI, data, and upload threats have mitigations and owners.
- Material decisions are recorded in the project decision log.

### VGD-003 — Define user journeys and UX acceptance baseline

| Field | Value |
|---|---|
| Priority | P0 |
| Description | Define the primary responsive journeys for student, parent, teacher, and government users, including English/Telugu and failure states. |
| Dependencies | VGD-001 |
| Estimated effort | 3–5 days |
| Owner | Product + UX |
| Status | TODO |

**Acceptance criteria:**

- Each interface has an approved navigation and critical-task flow.
- Mobile, accessibility, bilingual, loading, empty, and error states are included.
- Student flows preserve teach-before-test behavior.

### VGD-004 — Define domain model and API contracts

| Field | Value |
|---|---|
| Priority | P0 |
| Description | Specify core entities, ownership rules, API resources, schemas, errors, pagination, and versioning. |
| Dependencies | VGD-002, VGD-003 |
| Estimated effort | 3–5 days |
| Owner | Backend Lead |
| Status | TODO |

**Acceptance criteria:**

- Identity, curriculum, tutoring, practice, assessment, progress, files, and reporting boundaries are defined.
- Every sensitive resource has an explicit authorization rule.
- Contracts cover validation and standardized error responses.

### VGD-005 — Define test and quality strategy

| Field | Value |
|---|---|
| Priority | P0 |
| Description | Establish automated test layers, target browsers, bilingual cases, accessibility checks, security tests, AI evaluation, and release gates. |
| Dependencies | VGD-002, VGD-003 |
| Estimated effort | 2–3 days |
| Owner | QA Lead |
| Status | TODO |

**Acceptance criteria:**

- Unit, integration, API, UI, AI policy, security, and regression responsibilities are assigned.
- Required English/Telugu, responsive, and role-access scenarios are listed.
- Measurable release gates are proposed for approval.

### VGD-006 — Build backend foundation

| Field | Value |
|---|---|
| Priority | P0 |
| Description | Establish FastAPI structure, validated configuration, versioned APIs, errors, health checks, and test harness. |
| Dependencies | VGD-004, VGD-005 |
| Estimated effort | 5–8 days |
| Owner | Backend Team |
| Status | TODO |

**Acceptance criteria:**

- Configuration fails safely when required values are absent.
- API and test conventions follow the approved architecture.
- Health and standardized error behavior have passing pytest coverage.

### VGD-007 — Implement identity and scoped authorization

| Field | Value |
|---|---|
| Priority | P0 |
| Description | Implement authentication, roles, parent links, teacher assignments, government scopes, and audit events. |
| Dependencies | VGD-006 |
| Estimated effort | 8–13 days |
| Owner | Backend Team |
| Status | TODO |

**Acceptance criteria:**

- All defined roles can authenticate through approved flows.
- Cross-user and out-of-scope resource access is denied and tested.
- Privileged and failed access events are auditable without leaking secrets.

### VGD-008 — Implement database and core repositories

| Field | Value |
|---|---|
| Priority | P0 |
| Description | Create the approved SQLite schema, migrations, repositories, constraints, indexes, and synthetic demo data. |
| Dependencies | VGD-004, VGD-006 |
| Estimated effort | 8–13 days |
| Owner | Backend Team |
| Status | TODO |

**Acceptance criteria:**

- Migrations apply repeatably to a clean database.
- Foreign keys, ownership, domain constraints, and transactions are tested.
- Seed data is synthetic, deterministic, and labeled for demonstration use.

### VGD-009 — Build responsive bilingual frontend foundation

| Field | Value |
|---|---|
| Priority | P0 |
| Description | Establish separate HTML/CSS/JavaScript assets, design conventions, navigation, API client, language handling, and common states. |
| Dependencies | VGD-003, VGD-004, VGD-006 |
| Estimated effort | 8–13 days |
| Owner | Frontend Team |
| Status | TODO |

**Acceptance criteria:**

- Approved breakpoints and target browsers render cleanly.
- English/Telugu switching, keyboard navigation, focus, loading, empty, and error states work.
- No API keys or privileged configuration are present in browser assets.

### VGD-010 — Implement AI Tutor service and experience

| Field | Value |
|---|---|
| Priority | P0 |
| Description | Build server-side OpenAI orchestration, governed tutoring, follow-ups, and text/voice/visual explanation pathways. |
| Dependencies | VGD-007, VGD-008, VGD-009 |
| Estimated effort | 13–21 days |
| Owner | AI + Full-stack Team |
| Status | IN PROGRESS |

**Acceptance criteria:**

- Tutor responses meet educational and age-appropriateness rules.
- Telugu-selected requests produce primarily Telugu responses.
- Provider errors, timeouts, unsafe output, and usage limits are handled and tested.

**Sprint 3A status:**

- Provider-neutral lesson request/response types exist.
- OpenAI provider integration is isolated in the provider layer.
- Language profile policy engine is provider-independent.
- Deterministic fallback generation and internal AI exceptions are implemented.
- Sprint 3A tests pass without making live API calls.

**Sprint 3C status:**

- The Student setup preserves exact backend class, subject, and learning-profile values.
- A centralized browser API client handles JSON, timeout, safe error classification, and complete response validation.
- The Tutor renders all structured lesson sections and profile-appropriate fallback messaging.
- Loading, duplicate prevention, question retention, accessible errors, Unicode, and the 1500-character boundary are covered by regression tests.
- Voice, attachments, persistence, authentication, streaming, and conversation history remain explicitly out of scope.

**Sprint 4A status:**

- The configured OpenAI provider uses the official Responses API with strict Pydantic parsing and zero live calls in automated tests.
- Application-owned source/fallback metadata is never accepted from model output.
- Six active prompt definitions cover general teaching and all five approved subjects at version `1.0.0`.
- Language-profile policy includes context-aware Pure Telugu subject and Mathematics terminology.
- Provider, parsing, refusal, and reviewer failures use complete deterministic fallback when enabled and a safe `503` when disabled.
- An explicit one-request manual integration command is available with an API-credit warning.
- Sprint 4B RAG Foundation is next; RAG, ingestion, embeddings, and vector storage were not introduced in Sprint 4A.

### VGD-011 — Implement exact-composition practice system

| Field | Value |
|---|---|
| Priority | P0 |
| Description | Generate and deliver concept practice sets with persisted learner sessions and validated question structure. |
| Dependencies | VGD-010 |
| Estimated effort | 8–13 days |
| Owner | AI + Full-stack Team |
| Status | TODO |

**Acceptance criteria:**

- Each accepted set contains exactly 15 questions: 5 Easy, 5 Medium, and 5 Hard.
- Invalid or duplicate-heavy output is rejected or safely regenerated.
- Only the owning student can access and submit a practice session.

**Sprint 4D controlled-demo status:**

- Student UI generates and renders exactly 5 Easy, 5 Medium, and 5 Hard questions.
- English, Telugu Assisted English, and Pure Telugu paths are covered.
- Typed answers and approved JPG/PNG phone photos receive corrective guidance.
- A second wrong attempt reveals a worked solution; question-scoped retry tracking is explicit.
- Session-only progress shows attempted, mastered, accuracy, and completion.
- Persistent ownership and cross-session progress remain outside this demo slice.

### VGD-012 — Implement assessment, uploads, and progress

| Field | Value |
|---|---|
| Priority | P0 |
| Description | Support typed/image/PDF answers, secure file validation, AI evaluation, corrective feedback, and progress updates. |
| Dependencies | VGD-008, VGD-011 |
| Estimated effort | 13–21 days |
| Owner | AI + Full-stack Team |
| Status | TODO |

**Acceptance criteria:**

- Unsafe, oversized, unsupported, and unauthorized files are rejected.
- Feedback identifies mistakes and offers corrective steps rather than only final answers.
- Repeated submissions cannot corrupt or duplicate progress updates.

### VGD-013 — Build Parent Portal

| Field | Value |
|---|---|
| Priority | P1 |
| Description | Present linked-child progress, strengths, attention areas, activity, and support recommendations. |
| Dependencies | VGD-009, VGD-012 |
| Estimated effort | 5–8 days |
| Owner | Full-stack Team |
| Status | TODO |

**Acceptance criteria:**

- Parents see only explicitly linked children.
- Metrics reconcile with assessment and progress records.
- Mobile and English/Telugu journeys pass review.

**Sprint 4G controlled-demo status:**

- Two explicitly synthetic linked-child profiles demonstrate the authorized parent experience.
- Weekly and monthly reports, subject-wise completion, upcoming-exam readiness, completed/remaining preparation topics, strengths, attention areas, activity and support recommendations are functional.
- English/Telugu switching, editable voice queries and spoken insights are supported.
- Production authentication, parent-child linking and persisted progress remain pending and are not implied.

### VGD-014 — Build Teacher Portal

| Field | Value |
|---|---|
| Priority | P1 |
| Description | Present authorized class/student performance, concept insights, and intervention signals. |
| Dependencies | VGD-009, VGD-012 |
| Estimated effort | 8–13 days |
| Owner | Full-stack Team |
| Status | TODO |

**Acceptance criteria:**

- Teachers see only assigned classes and students.
- Aggregates reconcile with underlying assessment records.
- Filters, tables/charts, accessibility, and bilingual states pass review.

### VGD-015 — Build Government Dashboard

| Field | Value |
|---|---|
| Priority | P1 |
| Description | Deliver privacy-preserving aggregate education indicators with approved organizational filters and drill-down limits. |
| Dependencies | VGD-012, VGD-013, VGD-014 |
| Estimated effort | 8–13 days |
| Owner | Full-stack + Data Team |
| Status | TODO |

**Acceptance criteria:**

- Government users see only their approved organizational scope.
- Aggregates are accurate, performant, and protected by privacy thresholds.
- All synthetic/demo data is clearly identified.

**Controlled-demo status:**

- A responsive executive dashboard presents fictional statewide and district indicators.
- District and class-band filters update synthetic aggregate metrics and charts.
- Synthetic-data labelling is persistent and explicit.
- The demo provides no student-level drill-down and explains the intended privacy boundary.
- Production authentication, approved organizational scope, privacy thresholds, and live data integration remain pending.

### VGD-016 — Complete system validation and demo rehearsal

| Field | Value |
|---|---|
| Priority | P0 |
| Description | Execute full functional, bilingual, responsive, accessibility, security, AI-policy, performance, and recovery validation. |
| Dependencies | VGD-010 through VGD-015 |
| Estimated effort | 8–13 days |
| Owner | QA + Entire Team |
| Status | TODO |

**Acceptance criteria:**

- All critical user journeys and approved release gates pass.
- No open critical/high security defects remain.
- Demo script, synthetic dataset, fallback behavior, and operator responsibilities are rehearsed.

### VGD-017 — Prepare controlled deployment

| Field | Value |
|---|---|
| Priority | P1 |
| Description | Prepare hosting, CI/CD, secrets, backups, monitoring, runbooks, rollback, and post-release checks. |
| Dependencies | VGD-016, explicit human approval |
| Estimated effort | 5–8 days |
| Owner | DevOps + Tech Lead |
| Status | TODO |

**Acceptance criteria:**

- Deployment approval is recorded before production-impacting action.
- Secrets, TLS, monitoring, backups, rollback, and smoke tests are verified.
- Deployment and incident-response runbooks have named owners.

## IN PROGRESS

### VGD-001 — Establish project foundation documentation

| Field | Value |
|---|---|
| Priority | P0 |
| Description | Establish architecture, roadmap, task tracking, project-manager controls, and repository overview. |
| Dependencies | Project rules approved |
| Estimated effort | 1–2 days |
| Owner | AI Project Manager + Human Sponsor |
| Status | IN PROGRESS |

**Acceptance criteria:**

- All five foundation documents exist and are internally consistent.
- Architecture, roadmap phases, and tracker dependencies align.
- Human sponsor reviews and approves the foundation before coding begins.

## REVIEW

No tasks are currently in review.

## COMPLETED

### VGD-4C — Enterprise textbook repository and PDF ingestion foundation

| Field | Value |
|---|---|
| Priority | P0 |
| Description | Register and deterministically inspect two bilingual AP Class 10 Mathematics semester textbooks represented by checksum-identical filename aliases. |
| Dependencies | Sprint 4B curriculum metadata foundation |
| Owner | Backend + Curriculum Engineering |
| Status | COMPLETED |

**Acceptance criteria:**

- Generic `book_part` supports semester, volume, part, full-year and custom structures.
- PDF validation, SHA-256 duplicate detection, page extraction, provenance, scanned detection and chapter detection are deterministic.
- Storage is provider-independent and local paths are not exposed.
- OCR, embeddings, vector search, OpenAI extraction and lesson grounding are absent.

### VGD-000 — Establish project source-of-truth rules

| Field | Value |
|---|---|
| Priority | P0 |
| Description | Record project purpose, product rules, technology constraints, security rules, workflow, approvals, and Definition of Done. |
| Dependencies | None |
| Estimated effort | Completed |
| Owner | Human Sponsor + Codex |
| Status | COMPLETED |

**Acceptance criteria:**

- `AGENTS.md` exists at the repository root.
- `docs/VEDHA_AI_MASTER_RULES.md` exists and matches the governing intent.
- Both files are treated as source-of-truth documents.

## BLOCKED

No tasks are currently blocked.
