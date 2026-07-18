"""Application service for deterministic textbook ingestion."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from backend.app.textbooks.models import (
    TextbookFile,
    TextbookIngestionResult,
    TextbookMetadata,
    TextbookPage,
    TextbookProvenance,
    TextbookRegistration,
)
from backend.app.textbooks.pdf_ingestion import ChapterDetector, PdfInspector
from backend.app.textbooks.repository import DuplicateTextbookError, TextbookRepository
from backend.app.textbooks.storage import TextbookStorage
from backend.app.textbooks.validation import TextbookContentValidator


class TextbookIngestionService:
    def __init__(self, *, inspector: PdfInspector, storage: TextbookStorage, repository: TextbookRepository) -> None:
        self._inspector = inspector
        self._storage = storage
        self._repository = repository

    def ingest(self, path: Path, registration: TextbookRegistration) -> TextbookIngestionResult:
        inspection = self._inspector.inspect(path)
        if self._repository.get_by_checksum(inspection.checksum):
            raise DuplicateTextbookError("An exact textbook file is already registered")
        expected_languages = registration.languages or (registration.language,)
        content_validation = TextbookContentValidator().validate(inspection, expected_languages)
        extracted_metadata = inspection.book_metadata

        now = datetime.now(timezone.utc)
        textbook_id = f"textbook-{uuid4()}"
        job_id = f"ingestion-{uuid4()}"
        filename = path.name
        storage_key = self._storage.store(path, textbook_id, filename)
        provenance = TextbookProvenance(
            source_type=registration.source.source_type,
            source_reference=registration.source.source_reference,
            alternate_source_references=registration.source.alternate_source_references,
            checksum=inspection.checksum,
            ingested_at=now,
            ingestion_job_id=job_id,
        )
        textbook_file = TextbookFile(
            filename=filename,
            mime_type="application/pdf",
            file_size_bytes=inspection.file_size_bytes,
            checksum=inspection.checksum,
            storage_key=storage_key,
        )
        pages = tuple(TextbookPage(
            page_number=page.page_number,
            extracted_text=page.text,
            warnings=page.warnings,
            has_images=page.has_images,
            has_tables=page.has_tables,
            provenance=provenance,
        ) for page in inspection.pages)
        chapters = ChapterDetector().detect(inspection.pages)
        edition = registration.edition
        resolved_title = registration.title or (extracted_metadata.title if extracted_metadata else None)
        resolved_edition = edition.edition or (extracted_metadata.edition if extracted_metadata else None)
        resolved_year = edition.publication_year or (extracted_metadata.publication_year if extracted_metadata else None)
        resolved_publisher = edition.publisher or (extracted_metadata.publisher if extracted_metadata else None)
        metadata = TextbookMetadata(
            textbook_id=textbook_id,
            board=registration.board,
            academic_year=registration.academic_year,
            curriculum_version=registration.curriculum_version,
            class_level=registration.class_level,
            subject=registration.subject,
            medium=registration.medium,
            language=registration.language,
            languages=registration.languages or (registration.language,),
            book_part=registration.book_part,
            edition=resolved_edition,
            publication_year=resolved_year,
            publisher=resolved_publisher,
            title=resolved_title,
            source_type=registration.source.source_type,
            source_reference=registration.source.source_reference,
            filename=textbook_file.filename,
            mime_type=textbook_file.mime_type,
            file_size_bytes=textbook_file.file_size_bytes,
            checksum=textbook_file.checksum,
            page_count=inspection.page_count,
            created_at=now,
            updated_at=now,
        )
        result = TextbookIngestionResult(
            textbook_id=textbook_id,
            checksum=inspection.checksum,
            page_count=inspection.page_count,
            is_scanned=inspection.is_scanned,
            ocr_required=inspection.ocr_required,
            detection_reason=inspection.detection_reason,
            detected_language=content_validation.detected_language,
            sampled_page_numbers=content_validation.sampled_page_numbers,
            pages_with_text=content_validation.pages_with_text,
            pages_without_text=content_validation.pages_without_text,
            pages_with_warnings=content_validation.pages_with_warnings,
            likely_scanned_pages=content_validation.likely_scanned_pages,
            image_pages=content_validation.image_pages,
            table_pages=content_validation.table_pages,
            text_coverage_percent=content_validation.text_coverage_percent,
            unicode_valid=content_validation.unicode_valid,
            replacement_character_count=content_validation.replacement_character_count,
            english_pages=content_validation.english_pages,
            telugu_pages=content_validation.telugu_pages,
            mixed_language_pages=content_validation.mixed_language_pages,
            unreadable_pages=content_validation.unreadable_pages,
            english_character_count=content_validation.english_character_count,
            telugu_character_count=content_validation.telugu_character_count,
            bilingual_coverage_percent=content_validation.bilingual_coverage_percent,
            alternating_language_pairs=content_validation.alternating_language_pairs,
            chapters=chapters,
            pages=pages,
            warnings=inspection.warnings + content_validation.warnings,
            metadata=metadata,
            provenance=provenance,
        )
        try:
            self._repository.add(result)
        except Exception:
            self._storage.remove(storage_key)
            raise
        return result
