# Vedha AI Government Demo

> The versioned React/TypeScript commercial frontend migration is available in `frontend-react/`. The legacy `frontend/` demo is preserved until every portal passes migration acceptance.

A professional Government Demonstration edition of the Vedha AI Learning Platform for education leaders, school communities, investors, parents, teachers, and students.

> **Project status:** Sprint 4A Real OpenAI Integration and Prompt Versioning is implemented. Real provider use is opt-in through server-side environment configuration; deterministic fallback remains the default safe path when provider configuration or service is unavailable.

## Project overview

Vedha AI Government Demo will showcase a polished, responsive learning platform spanning four coordinated experiences: a Student App, Teacher Portal, Parent Portal, and Government Dashboard. The demonstration is being designed with professional engineering, security, bilingual delivery, accessibility, and scalability in mind from the beginning.

The governing requirements are maintained in [AGENTS.md](AGENTS.md) and [the master rules](docs/VEDHA_AI_MASTER_RULES.md).

## Vision

Enable students from Classes 1–12 to learn and prepare independently at home while providing authorized adults and education leaders with useful, privacy-conscious insight into learning progress.

## Planned features

- Guided student profiles and class, subject, and concept selection
- English and Telugu learning paths
- AI Tutor chat with text, voice, visual, and follow-up explanations
- Concept practice and answer submission
- Image and PDF answer uploads with validation
- AI-supported answer evaluation and corrective guidance
- Student progress views
- Linked-child insights for parents
- Class and concept insights for teachers
- Aggregated, privacy-preserving indicators for government users

Feature behavior and constraints are governed by the master rules and will be implemented by the milestones in the roadmap.

## Architecture

The planned system begins as a modular monolith: four responsive HTML/CSS/vanilla JavaScript interfaces communicate with versioned FastAPI APIs. The backend owns authentication, scoped authorization, educational workflows, AI orchestration, persistence, secure file handling, and audit events. SQLite supports the controlled demo behind repository abstractions designed for later cloud evolution.

See [Software Architecture](docs/ARCHITECTURE.md) for diagrams, boundaries, security, scalability, and future cloud/mobile direction.

## Technology stack

| Area | Technology |
|---|---|
| Frontend | HTML5, CSS3, vanilla JavaScript |
| Backend | Python, FastAPI |
| Demo database | SQLite |
| AI integration | OpenAI API through the backend |
| Testing | pytest and planned UI/system validation |
| Design | Responsive web design with English/Telugu support |
| Version control | Git and GitHub |

## Project Setup

Create a virtual environment from the repository root:

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Install the project and test dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run the complete test suite:

```powershell
python -m pytest
```

Run FastAPI locally:

```powershell
uvicorn backend.app.main:app --reload
```

## Running locally

Start both services from the repository root in this order:

```powershell
# Terminal 1: backend
python -m uvicorn backend.app.main:app --reload
```

```powershell
# Terminal 2: frontend
python -m http.server 8080 --bind 127.0.0.1 --directory frontend
```

Open `http://127.0.0.1:8080/`, choose Student App, complete setup, and ask a question. The frontend defaults to `http://127.0.0.1:8000`; development hosts may define `window.VEDHA_API_BASE_URL` before `api-client.js` loads. This value is configuration only and must never contain secrets.

Manual acceptance profiles are Asha/Class 5/Mathematics/English Medium, Ravi/Class 6/Science/Telugu Assisted English, and సాయి/Class 5/Mathematics/Pure Telugu. Without a configured provider, the backend returns a safe structured fallback and the student sees a calm informational notice. Voice, attachments, persistence, authentication, streaming, and conversation history remain known limitations for later sprints.

## OpenAI provider configuration

Copy `backend/.env.example` to the ignored local file `backend/.env` and set these server-side values:

```dotenv
AI_PROVIDER=openai
OPENAI_API_KEY=your-local-secret
OPENAI_MODEL=your-account-supported-model
OPENAI_TIMEOUT_SECONDS=30
AI_FALLBACK_ENABLED=true
```

Never place the key in frontend assets, committed files, commands saved in documentation, or test fixtures. The provider uses the official SDK Responses API with strict typed parsing. Prompts are selected from an internal active registry by subject; the initial prompt IDs use version `1.0.0`. Prompt text and prompt metadata are not returned by the public lesson API.

When fallback is enabled, missing configuration, authentication, rate limits, timeouts, provider failures, refusals, malformed output, and deterministic review rejection return a complete fallback lesson. With fallback disabled, the API returns a safe `503` envelope without raw provider details.

An optional real-provider check makes exactly one request and may consume API credits:

```powershell
python -m scripts.manual_openai_lesson --i-understand-this-uses-api-credits
```

It runs only when explicitly invoked and requires `OPENAI_API_KEY`. Automated tests never invoke it and mock all provider calls. RAG, textbook ingestion, embeddings, persistence, streaming, conversation memory, voice, images, practice, evaluation, authentication, and analytics remain deferred. The next planned sprint is Sprint 4B RAG Foundation.

## Testing

Run the complete test suite from the repository root:

```powershell
python -m pytest
```

### Windows PermissionError troubleshooting

If pytest fails with `PermissionError: [WinError 5]` because the default Windows
temporary directory or `.pytest_cache` is unavailable, use a repository-local
temporary directory and disable pytest's cache provider:

```powershell
python -m pytest --basetemp=.pytest-temp -p no:cacheprovider
```

Both generated directories are ignored by Git. This workaround changes only
pytest's temporary and cache locations; tests should continue to use pytest's
`tmp_path` fixtures so the suite remains platform-independent.

## Project structure

Current documentation structure:

```text
Vedha-AI-Government-Demo/
├── AGENTS.md
├── README.md
└── docs/
    ├── ARCHITECTURE.md
    ├── PROJECT_MANAGER.md
    ├── ROADMAP.md
    ├── TASKS.md
    └── VEDHA_AI_MASTER_RULES.md
```

The planned implementation structure is documented in `docs/ARCHITECTURE.md`; its folders do not exist yet.

## Project documentation

| Document | Purpose |
|---|---|
| [Project rules](AGENTS.md) | Repository-wide instructions and approval boundaries |
| [Master rules](docs/VEDHA_AI_MASTER_RULES.md) | Product, educational, UI, code, security, and completion rules |
| [Architecture](docs/ARCHITECTURE.md) | System design and evolution path |
| [Roadmap](docs/ROADMAP.md) | Eleven delivery phases and milestone gates |
| [Task tracker](docs/TASKS.md) | Prioritized work, dependencies, ownership, and acceptance criteria |
| [Government demo runbook](docs/DEMO_RUNBOOK.md) | Presenter sequence, bilingual rehearsal, recovery paths, and readiness gate |
| [AI Project Manager](docs/PROJECT_MANAGER.md) | Current milestone, sprint controls, risks, debt, decisions, and next task |

## Contribution rules

### Typical Git workflow

Before starting work, update the current branch:

```powershell
git pull
```

After making and reviewing changes, commit and push them:

```powershell
git add .
git commit -m "message"
git push
```

Use a feature branch for focused development and review. Keep `main` stable and
merge a feature branch into `main` only after the feature is complete, tests
pass, and the change has been approved. A new local branch needs a configured
remote and an initial upstream push before plain `git pull` and `git push` work.

Before contributing:

1. Read `AGENTS.md`, `docs/VEDHA_AI_MASTER_RULES.md`, and `docs/PROJECT_MANAGER.md` completely.
2. Inspect relevant files and confirm the task scope and acceptance criteria.
3. Implement only approved work without modifying unrelated files.
4. Keep frontend HTML, CSS, and JavaScript separate when frontend work begins.
5. Validate inputs, enforce server-side authorization, handle errors, and keep secrets in environment variables.
6. Consider English and Telugu, responsive layout, accessibility, and privacy in every applicable feature.
7. Run relevant tests, fix failures, review the final diff, and summarize changes and test results.

Destructive database changes, major folder deletion, production deployment, secret exposure, or an architecture rewrite require explicit human approval.

## Roadmap summary

Delivery progresses through foundation, backend, frontend, AI Tutor, practice, assessment, the Parent Portal, Teacher Portal, Government Dashboard, system testing, and controlled deployment. Testing, security, bilingual validation, accessibility, and documentation remain continuous across phases.

See the [complete roadmap](docs/ROADMAP.md) and [current project status](docs/PROJECT_MANAGER.md).

## License

License terms have not yet been selected. Add an approved `LICENSE` file before external distribution or reuse.
## Sprint 4C textbook ingestion foundation

Vedha AI includes a provider-independent textbook repository foundation for
curriculum PDFs. The pilot treats Andhra Pradesh Class 10 Mathematics Semester
1 and Semester 2 as two bilingual English–Telugu textbook records. The four
supplied filenames are two checksum-identical alias pairs, not four books.

The ingestion pipeline validates PDF type, size, encryption, readability and
checksum; stores files behind an opaque local storage key; extracts text one
page at a time; preserves provenance; detects likely scanned documents without
running OCR; and detects explicit English/Telugu chapter headings. Approved
checksum-identical filename aliases resolve to one record and storage object;
different semester checksums remain independent.

Run the disabled-by-default manual command after configuring a private storage
directory and setting `TEXTBOOK_INGESTION_ENABLED=true`:

```powershell
python scripts/ingest_textbook.py textbook.pdf --board andhra_pradesh_state_board --academic-year 2025-2026 --curriculum-version your-verified-version --class-level 10 --subject mathematics --medium telugu --language te --book-part semester_1
```

Textbook PDFs and private storage content must never be committed. OCR,
embeddings, vector search, OpenAI extraction and lesson grounding remain out of
scope.

### Sprint 4C.3 pilot validation

Keep the four pilot source aliases outside the repository in a directory chosen and
explicitly supplied by the operator, using their approved filenames. No source
directory is assumed or searched automatically. Set `TEXTBOOK_STORAGE_PATH` to
a private ignored runtime directory and enable ingestion only for the manual
run. Board and academic year use configured defaults unless supplied. A
curriculum version must be supplied or configured as
`DEFAULT_CURRICULUM_VERSION`.

The manual ingestion command validates the PDF signature, readability,
encryption, checksum, all-page content language, Unicode
replacement characters, scanned/OCR indicators, images, tables, and chapter
headings before persisting the record. Filename and displayed file size do not
establish identity. Exact SHA-256 matches within an approved semester alias pair
resolve to one bilingual record; Semester 1 and Semester 2 must remain distinct.

Run both bilingual books and their four source aliases through one preflighted command:

```powershell
$env:TEXTBOOK_INGESTION_ENABLED="true"
$env:TEXTBOOK_STORAGE_PATH="backend/data/textbooks"
python scripts/ingest_pilot_textbooks.py --source-directory "C:\operator-supplied\textbooks" --curriculum-version "verified-version"
```

Replace the examples with the operator-supplied directory and configured or
verified curriculum identifiers. The command stops before registration if the directory is
invalid or unreadable, any expected filename is missing or unreadable, alias
checksums differ, or the two semesters have the same checksum. Existing matching
records are migrated in place. Review its JSON output for extraction counts,
Unicode status, warnings, and detected chapter headings. Repository metadata,
stored PDFs, full extracted text, and `pilot-validation.json` remain under the
private `TEXTBOOK_STORAGE_PATH`; never commit that directory or a report that
contains textbook page text.

Official title, publisher, edition, and publication year are extracted locally
and deterministically from embedded PDF metadata and the cover, copyright, and
early front-matter pages. These fields are never required CLI inputs. When a
value cannot be determined confidently, it remains null and the validation
report includes a warning; missing bibliographic metadata alone never blocks
ingestion.

Language validation scans every extracted page and reports English, Telugu,
mixed, and unreadable page counts, Unicode character counts, bilingual coverage,
and adjacent English/Telugu page pairs. Verified bilingual metadata remains
distinct from extraction quality: PDFs whose embedded fonts prevent Telugu
Unicode extraction retain an explicit warning for manual review.

### PDF text-layer diagnostics

Sprint 4C.4 provides a diagnostic-only command that inspects exactly the two
checksum-unique pilot PDFs and verifies their duplicate aliases without running
OCR or changing textbook records:

```powershell
python scripts/investigate_pdf_text_layer.py --source-directory "C:\operator-supplied\textbooks" --output-directory "backend/data/textbooks"
```

The ignored JSON report contains per-page structural evidence, character counts,
font subtype/encoding/embedding/ToUnicode findings, image counts, deterministic
sample-page selections, extractor availability, and root-cause classifications.
It intentionally contains no extracted page text or substantial excerpts.
