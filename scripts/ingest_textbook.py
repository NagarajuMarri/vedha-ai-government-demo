"""Manually inspect and register one textbook PDF without AI or OCR."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.config import get_settings
from backend.app.textbooks.models import TextbookEdition, TextbookRegistration, TextbookSource
from backend.app.textbooks.pdf_ingestion import PdfInspector
from backend.app.textbooks.repository import JsonTextbookRepository
from backend.app.textbooks.service import TextbookIngestionService
from backend.app.textbooks.storage import LocalTextbookStorage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deterministically ingest one curriculum textbook PDF.")
    parser.add_argument("pdf_path", type=Path)
    parser.add_argument("--board", required=True)
    parser.add_argument("--academic-year", required=True)
    parser.add_argument("--curriculum-version", required=True)
    parser.add_argument("--class-level", required=True, type=int)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--medium", required=True)
    parser.add_argument("--language", required=True)
    parser.add_argument("--book-part", required=True, choices=(
        "full_year", "semester_1", "semester_2", "volume_1", "volume_2",
        "part_1", "part_2", "custom",
    ))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = get_settings()
    if not settings.textbook_ingestion_enabled:
        raise SystemExit("Textbook ingestion is disabled by configuration")
    registration = TextbookRegistration(
        board=args.board,
        academic_year=args.academic_year,
        curriculum_version=args.curriculum_version,
        class_level=args.class_level,
        subject=args.subject,
        medium=args.medium,
        language=args.language,
        book_part=args.book_part,
        edition=TextbookEdition(),
        title=None,
        source=TextbookSource(source_type="official_textbook_pdf", source_reference=args.pdf_path.name),
    )
    service = TextbookIngestionService(
        inspector=PdfInspector(
            max_file_size_bytes=settings.textbook_max_file_size_mb * 1024 * 1024,
            allowed_mime_types=settings.textbook_allowed_mime_types,
            scanned_threshold=settings.textbook_scanned_threshold,
            checksum_algorithm=settings.textbook_checksum_algorithm,
        ),
        storage=LocalTextbookStorage(settings.textbook_storage_path),
        repository=JsonTextbookRepository(settings.textbook_storage_path / ".textbook_repository.json"),
    )
    result = service.ingest(args.pdf_path, registration)
    print(json.dumps({
        "textbook_id": result.textbook_id,
        "checksum": result.checksum,
        "page_count": result.page_count,
        "scanned": result.is_scanned,
        "ocr_required": result.ocr_required,
        "content_language": result.detected_language,
        "sampled_page_numbers": result.sampled_page_numbers,
        "pages_with_text": result.pages_with_text,
        "pages_without_text": result.pages_without_text,
        "pages_with_warnings": result.pages_with_warnings,
        "text_coverage_percent": result.text_coverage_percent,
        "likely_scanned_pages": result.likely_scanned_pages,
        "image_pages": result.image_pages,
        "table_pages": result.table_pages,
        "unicode_valid": result.unicode_valid,
        "replacement_character_count": result.replacement_character_count,
        "detected_chapters": [chapter.model_dump(mode="json") for chapter in result.chapters],
        "warnings": result.warnings,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
