"""Validate and ingest two bilingual AP Class 10 Mathematics pilot textbooks."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.config import get_settings
from backend.app.textbooks.models import TextbookEdition, TextbookRegistration, TextbookSource
from backend.app.textbooks.pdf_ingestion import PdfInspection, PdfInspector, TextbookValidationError
from backend.app.textbooks.repository import DuplicateTextbookError, JsonTextbookRepository
from backend.app.textbooks.service import TextbookIngestionService
from backend.app.textbooks.storage import LocalTextbookStorage
from backend.app.textbooks.validation import ContentValidation, TextbookContentValidator


@dataclass(frozen=True, slots=True)
class PilotBook:
    canonical_filename: str
    alternate_filename: str
    book_part: str

    @property
    def filenames(self) -> tuple[str, str]:
        return self.canonical_filename, self.alternate_filename


PILOT_BOOKS = (
    PilotBook(
        "AP_Class10_Mathematics_Sem1_English.pdf",
        "AP_Class10_Mathematics_Sem1_Telugu.pdf",
        "semester_1",
    ),
    PilotBook(
        "AP_Class10_Mathematics_Sem2_English.pdf",
        "AP_Class10_Mathematics_Sem2_Telugu.pdf",
        "semester_2",
    ),
)
EXPECTED_FILENAMES = tuple(filename for book in PILOT_BOOKS for filename in book.filenames)


class PilotPreflightError(ValueError):
    def __init__(self, code: str, message: str, *, missing: tuple[str, ...] = (), unreadable: tuple[str, ...] = ()) -> None:
        super().__init__(message)
        self.code = code
        self.missing = missing
        self.unreadable = unreadable


def validate_source_directory(source_directory: Path) -> dict[str, Path]:
    source = source_directory.expanduser().resolve()
    if not source.is_dir():
        raise PilotPreflightError("source_directory_invalid", "The supplied source directory does not exist")
    try:
        tuple(source.iterdir())
    except OSError as exc:
        raise PilotPreflightError("source_directory_unreadable", "The supplied source directory is not readable") from exc
    paths = {filename: source / filename for filename in EXPECTED_FILENAMES}
    missing = tuple(filename for filename, path in paths.items() if not path.is_file())
    unreadable: list[str] = []
    for filename, path in paths.items():
        if filename in missing:
            continue
        try:
            with path.open("rb") as stream:
                stream.read(1)
        except OSError:
            unreadable.append(filename)
    if missing or unreadable:
        raise PilotPreflightError(
            "pilot_files_incomplete",
            "All four pilot source aliases must be present and readable before ingestion",
            missing=missing,
            unreadable=tuple(unreadable),
        )
    return paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ingest two bilingual AP Class 10 Mathematics pilot textbooks.")
    parser.add_argument("--source-directory", type=Path, required=True)
    parser.add_argument("--board")
    parser.add_argument("--academic-year")
    parser.add_argument("--curriculum-version")
    return parser


def _safe_error(exc: Exception) -> dict[str, object]:
    payload: dict[str, object] = {
        "status": "failed",
        "code": getattr(exc, "code", "pilot_validation_failed"),
        "message": "A local filesystem operation failed" if isinstance(exc, OSError) else str(exc),
        "registered_textbooks": 0,
        "ingested_textbooks": 0,
    }
    if isinstance(exc, PilotPreflightError):
        payload["missing_files"] = exc.missing
        payload["unreadable_files"] = exc.unreadable
    return payload


def _migrate_existing(record, book: PilotBook, validation: ContentValidation, inspection: PdfInspection, repository):
    aliases = book.filenames
    provenance = record.provenance.model_copy(update={
        "source_reference": book.canonical_filename,
        "alternate_source_references": (book.alternate_filename,),
    })
    pages = tuple(page.model_copy(update={"provenance": provenance}) for page in record.pages)
    metadata = record.metadata.model_copy(update={
        "medium": "bilingual",
        "language": "en",
        "languages": ("en", "te"),
        "source_reference": book.canonical_filename,
        "updated_at": datetime.now(timezone.utc),
    })
    migrated = record.model_copy(update={
        "detected_language": validation.detected_language,
        "sampled_page_numbers": validation.sampled_page_numbers,
        "pages_with_text": validation.pages_with_text,
        "pages_without_text": validation.pages_without_text,
        "pages_with_warnings": validation.pages_with_warnings,
        "likely_scanned_pages": validation.likely_scanned_pages,
        "image_pages": validation.image_pages,
        "table_pages": validation.table_pages,
        "text_coverage_percent": validation.text_coverage_percent,
        "unicode_valid": validation.unicode_valid,
        "replacement_character_count": validation.replacement_character_count,
        "english_pages": validation.english_pages,
        "telugu_pages": validation.telugu_pages,
        "mixed_language_pages": validation.mixed_language_pages,
        "unreadable_pages": validation.unreadable_pages,
        "english_character_count": validation.english_character_count,
        "telugu_character_count": validation.telugu_character_count,
        "bilingual_coverage_percent": validation.bilingual_coverage_percent,
        "alternating_language_pairs": validation.alternating_language_pairs,
        "warnings": tuple(dict.fromkeys(record.warnings + inspection.warnings + validation.warnings)),
        "pages": pages,
        "metadata": metadata,
        "provenance": provenance,
    })
    repository.replace(migrated)
    return migrated


def _validation_summary(book: PilotBook, inspection: PdfInspection, validation: ContentValidation) -> dict[str, object]:
    return {
        "canonical_filename": book.canonical_filename,
        "alternate_source_filenames": (book.alternate_filename,),
        "checksum": inspection.checksum,
        "file_size_bytes": inspection.file_size_bytes,
        "page_count": inspection.page_count,
        "detected_language": validation.detected_language,
        "english_pages": validation.english_pages,
        "telugu_pages": validation.telugu_pages,
        "mixed_language_pages": validation.mixed_language_pages,
        "unreadable_pages": validation.unreadable_pages,
        "english_character_count": validation.english_character_count,
        "telugu_character_count": validation.telugu_character_count,
        "bilingual_coverage_percent": validation.bilingual_coverage_percent,
        "alternating_language_pairs": validation.alternating_language_pairs,
        "warnings": inspection.warnings + validation.warnings,
    }


def run(args: argparse.Namespace) -> dict[str, object]:
    paths = validate_source_directory(args.source_directory)
    settings = get_settings()
    if not settings.textbook_ingestion_enabled:
        raise PilotPreflightError("ingestion_disabled", "Textbook ingestion is disabled by configuration")
    board = args.board or settings.default_board
    academic_year = args.academic_year or settings.default_academic_year
    curriculum_version = args.curriculum_version or settings.default_curriculum_version
    if not curriculum_version:
        raise PilotPreflightError(
            "curriculum_version_required",
            "Curriculum version must be supplied or configured as DEFAULT_CURRICULUM_VERSION",
        )
    inspector = PdfInspector(
        max_file_size_bytes=settings.textbook_max_file_size_mb * 1024 * 1024,
        allowed_mime_types=settings.textbook_allowed_mime_types,
        scanned_threshold=settings.textbook_scanned_threshold,
        checksum_algorithm=settings.textbook_checksum_algorithm,
    )
    validator = TextbookContentValidator()
    repository = JsonTextbookRepository(settings.textbook_storage_path / ".textbook_repository.json")
    service = TextbookIngestionService(
        inspector=inspector,
        storage=LocalTextbookStorage(settings.textbook_storage_path),
        repository=repository,
    )
    results = []
    validations = []
    unique_checksums: set[str] = set()
    for book in PILOT_BOOKS:
        canonical_inspection = inspector.inspect(paths[book.canonical_filename])
        alternate_inspection = inspector.inspect(paths[book.alternate_filename])
        if canonical_inspection.checksum != alternate_inspection.checksum:
            raise PilotPreflightError(
                "alias_checksum_mismatch",
                f"Bilingual source aliases differ for {book.book_part}",
            )
        if canonical_inspection.checksum in unique_checksums:
            raise PilotPreflightError("semester_checksum_duplicate", "Semester textbooks must be distinct")
        unique_checksums.add(canonical_inspection.checksum)
        validation = validator.validate(canonical_inspection, ("en", "te"))
        existing = repository.get_by_checksum(canonical_inspection.checksum)
        if existing:
            result = _migrate_existing(existing, book, validation, canonical_inspection, repository)
        else:
            registration = TextbookRegistration(
                board=board,
                academic_year=academic_year,
                curriculum_version=curriculum_version,
                class_level=10,
                subject="mathematics",
                medium="bilingual",
                language="en",
                languages=("en", "te"),
                book_part=book.book_part,
                edition=TextbookEdition(),
                title=None,
                source=TextbookSource(
                    source_type="official_textbook_pdf",
                    source_reference=book.canonical_filename,
                    alternate_source_references=(book.alternate_filename,),
                ),
            )
            result = service.ingest(paths[book.canonical_filename], registration)
        results.append(result)
        validations.append(_validation_summary(book, canonical_inspection, validation))
    return {
        "status": "completed_with_extraction_warnings" if any(item["warnings"] for item in validations) else "completed",
        "unique_textbooks": len(results),
        "storage_objects_expected": len(results),
        "files": validations,
        "textbooks": [
            {
                "textbook_id": result.textbook_id,
                "checksum": result.checksum,
                "medium": result.metadata.medium,
                "languages": result.metadata.languages,
                "book_part": result.metadata.book_part,
                "page_records": len(result.pages),
                "alternate_source_filenames": result.provenance.alternate_source_references,
            }
            for result in results
        ],
        "curriculum_version_provenance": "Vedha AI internally configured identifier; not an official government version",
        "openai_calls": 0,
        "embeddings_generated": 0,
    }


def main() -> None:
    args = build_parser().parse_args()
    try:
        report = run(args)
    except (PilotPreflightError, TextbookValidationError, DuplicateTextbookError, OSError, ValueError) as exc:
        print(json.dumps(_safe_error(exc), ensure_ascii=False, indent=2))
        raise SystemExit(1) from exc
    settings = get_settings()
    report_path = settings.textbook_storage_path / "pilot-validation.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = report_path.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, report_path)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
