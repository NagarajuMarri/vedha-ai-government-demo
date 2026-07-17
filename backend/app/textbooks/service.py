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


class TextbookIngestionService:
    def __init__(self, *, inspector: PdfInspector, storage: TextbookStorage, repository: TextbookRepository) -> None:
        self._inspector = inspector
        self._storage = storage
        self._repository = repository

    def ingest(self, path: Path, registration: TextbookRegistration) -> TextbookIngestionResult:
        inspection = self._inspector.inspect(path)
        if self._repository.get_by_checksum(inspection.checksum):
            raise DuplicateTextbookError("An exact textbook file is already registered")

        now = datetime.now(timezone.utc)
        textbook_id = f"textbook-{uuid4()}"
        job_id = f"ingestion-{uuid4()}"
        filename = path.name
        storage_key = self._storage.store(path, textbook_id, filename)
        provenance = TextbookProvenance(
            source_type=registration.source.source_type,
            source_reference=registration.source.source_reference,
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
        metadata = TextbookMetadata(
            textbook_id=textbook_id,
            board=registration.board,
            academic_year=registration.academic_year,
            curriculum_version=registration.curriculum_version,
            class_level=registration.class_level,
            subject=registration.subject,
            medium=registration.medium,
            language=registration.language,
            book_part=registration.book_part,
            edition=edition.edition,
            publication_year=edition.publication_year,
            publisher=edition.publisher,
            title=registration.title,
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
            chapters=chapters,
            pages=pages,
            warnings=inspection.warnings,
            metadata=metadata,
            provenance=provenance,
        )
        self._repository.add(result)
        return result
