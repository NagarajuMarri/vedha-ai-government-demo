# Database Standards

## Scope and architecture reference

These standards govern persistence behind the repository layer defined in `ARCHITECTURE.md`. SQLite is the controlled-demo database; domain and application services must not depend on SQLite-specific behavior so a future managed PostgreSQL migration remains practical. This document defines policy and intentionally contains no SQL.

## Naming standards

- Use lowercase `snake_case` for tables, columns, constraints, indexes, and migration identifiers.
- Use plural table names and singular descriptive column names.
- Primary keys use `id`; foreign keys use `<referenced_entity>_id`.
- Boolean fields use positive, unambiguous forms such as `is_active` or timestamped lifecycle fields.
- Timestamps end in `_at`; dates end in `_date`; measured values include units when not self-evident.
- Constraint/index names follow a documented predictable pattern and remain within PostgreSQL identifier limits.
- Avoid reserved words, unexplained abbreviations, and names tied to UI labels.

## Table conventions

- One table represents one durable concept, relationship, event, or aggregate with clear ownership.
- Normalize transactional data by default; denormalization requires measured reporting/performance need and a refresh/consistency owner.
- Define nullability deliberately. Absence, unknown, not applicable, and empty are not interchangeable.
- Enforce stable domain invariants with database constraints where portable and with domain validation as appropriate.
- Store structured data in typed columns when it is queried or constrained; opaque JSON is exceptional and documented.
- Persist enum-like values through stable machine codes rather than display text; application localization remains outside the database.
- Synthetic demo records must be deterministic and visibly distinguishable without weakening production-oriented constraints.

## Primary keys

- Every durable entity has an immutable, opaque primary key that carries no personal or organizational meaning.
- Choose a key strategy during schema design that behaves consistently in SQLite and PostgreSQL and does not rely on client trust.
- Public resource identifiers must not enable authorization bypass or enumeration assumptions; authorization is always explicit.
- Never reuse deleted identifiers or change a primary key to reflect business data.

## Foreign keys and ownership

- Enable and enforce foreign keys in every environment, including tests.
- Declare deletion/update behavior explicitly; default to restriction when data loss or orphaning would be unsafe.
- Model parent-child, teacher-class, organization, and government scope relationships explicitly enough for server-side authorization.
- Validate required ownership/scope both through service policy and suitable constraints/transactions.
- Avoid polymorphic foreign keys that cannot be enforced without a reviewed design decision.

## Indexes

- Index primary/unique constraints and foreign keys used in joins or authorization filters.
- Design composite indexes around verified query predicates and sort order, with the most selective/useful prefix justified.
- Use unique indexes/constraints for true business uniqueness, including scoped uniqueness where relevant.
- Avoid speculative or duplicate indexes; every nontrivial index requires an access-pattern rationale.
- Review write/storage cost and query plans using representative synthetic data.
- Reassess indexes after PostgreSQL migration because planners and index capabilities differ.

## Audit columns and audit events

Mutable business tables normally include `created_at` and `updated_at` in UTC. Add `created_by`/`updated_by` only when meaningful, authorized, and privacy-appropriate. Lifecycle fields such as `deleted_at` are used only under the soft-delete policy.

Audit columns do not replace the separate audit-event capability described in `ARCHITECTURE.md`. Security-relevant and privileged actions require append-oriented events with actor, action, target category, permitted scope, result, timestamp, and correlation ID—without secrets or unnecessary student content.

## Soft delete policy

- Soft delete is not the universal default.
- Use it only when restoration, retention, audit, or relationship continuity requires logical deletion.
- Define who can delete/restore, default query filtering, uniqueness behavior, cascading effects, retention duration, and final purge authority before adoption.
- Sensitive-data deletion obligations may require irreversible purge/anonymization through an explicitly approved process.
- Never use soft delete to conceal destructive schema changes or retain data indefinitely.

## Transactions and concurrency

Application services own transaction boundaries. Multi-record state changes—submission/evaluation/progress, upload finalization, and relationship changes—must be atomic. Keep transactions short, define retry/idempotency behavior, and do not make slow external AI/network calls while holding database locks. Use explicit conflict handling rather than last-write-wins assumptions for sensitive updates.

## Migration policy

- Every schema change uses a versioned, reviewed migration; no manual schema drift.
- Migrations must be deterministic, ordered, repeatable on a clean database, and tested against representative prior state.
- Separate schema change from risky backfill when practical and document forward, rollback/roll-forward, backup, downtime, and compatibility behavior.
- Never edit migration history after it has been shared/applied; add a correcting migration.
- Destructive changes, irreversible data transformation, or production execution require explicit human approval.
- Application/database compatibility must support the chosen deployment sequence.

## SQLite limitations and controls

- SQLite permits limited concurrent writes; keep transactions short and size/rehearse the demo workload.
- Type affinity is less strict than PostgreSQL; application schemas and constraints must prevent invalid values.
- Foreign-key enforcement must be explicitly enabled per connection.
- Some ALTER operations, concurrency controls, date/time behavior, case sensitivity, JSON behavior, and advanced index features differ.
- SQLite is a local file, so filesystem permissions, backup consistency, path safety, and single-instance assumptions matter.
- Do not treat SQLite as the production scaling target or use SQLite-only shortcuts in domain contracts.

## Future PostgreSQL migration

- Keep repositories and migration tooling database-aware while domain services remain database-neutral.
- Prefer portable types and semantics; document unavoidable SQLite/PostgreSQL differences.
- Store timestamps in UTC and define timezone conversion at application boundaries.
- Avoid dependence on implicit ordering, truthiness, case-insensitive comparison, auto-increment quirks, or permissive coercion.
- Before migration, run compatibility tests, data validation, mapping rehearsal, performance/index review, backup/restore rehearsal, and reconciliation counts.
- Plan connection pooling, least-privilege database roles, encryption, managed backups, observability, and zero/minimal-downtime deployment according to approved cloud requirements.

## Data privacy, retention, and backup

Collect the minimum data needed. Real student data is prohibited until a privacy/data-governance approval exists; use clearly labeled synthetic data for the demo. Classify sensitive fields, restrict repository queries by scope, avoid personal data in seeds/logs, define retention and purge, encrypt hosted backups, and test restoration. A backup is not valid evidence until restore and reconciliation succeed.

## Database completion gate

A database change is complete only when naming, constraints, ownership, migration behavior, transaction boundaries, indexes, privacy/retention, SQLite behavior, PostgreSQL portability, repository integration, and migration/authorization tests have been reviewed against `ARCHITECTURE.md`, `API_STANDARDS.md`, `SECURITY_STANDARDS.md`, and `TESTING_STANDARDS.md`.
