"""Sprint 4C textbook repository and deterministic ingestion tests."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from pypdf import PdfWriter

from backend.app.core.config import get_settings
from backend.app.textbooks.models import (
    TextbookEdition,
    TextbookRegistration,
    TextbookSource,
)
from backend.app.textbooks.pdf_ingestion import (
    ChapterDetector,
    InspectedPage,
    PdfInspection,
    PdfInspector,
    TextbookValidationError,
)
from backend.app.textbooks.repository import DuplicateTextbookError, InMemoryTextbookRepository, JsonTextbookRepository
from backend.app.textbooks.service import TextbookIngestionService
from backend.app.textbooks.storage import LocalTextbookStorage, TextbookStorage


PILOT_BOOKS = (
    ("AP_Class10_Mathematics_Sem1_Telugu.pdf", "telugu", "te", "semester_1"),
    ("AP_Class10_Mathematics_Sem2_Telugu.pdf", "telugu", "te", "semester_2"),
    ("AP_Class10_Mathematics_Sem1_English.pdf", "english", "en", "semester_1"),
    ("AP_Class10_Mathematics_Sem2_English.pdf", "english", "en", "semester_2"),
)


def _registration(filename: str, medium: str, language: str, book_part: str) -> TextbookRegistration:
    return TextbookRegistration(
        board="andhra_pradesh_state_board",
        academic_year="2025-2026",
        curriculum_version="ap-2025-v1",
        class_level=10,
        subject="mathematics",
        medium=medium,
        language=language,
        book_part=book_part,
        edition=TextbookEdition(edition="first", publication_year=2025, publisher="AP Government"),
        title=Path(filename).stem,
        source=TextbookSource(source_type="government_portal", source_reference=filename),
    )


def _pdf(path: Path, pages: int = 2) -> Path:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=612, height=792)
    with path.open("wb") as stream:
        writer.write(stream)
    return path


class FakeInspector:
    def __init__(self, checksum: str, text: str) -> None:
        self.checksum = checksum
        self.text = text

    def inspect(self, path: Path) -> PdfInspection:
        page = InspectedPage(1, self.text, (), False, "| x | y |" in self.text)
        return PdfInspection(self.checksum, 100, 1, (page,), False, False, None, ())


def _service(tmp_path: Path, checksum: str, text: str, repository=None) -> TextbookIngestionService:
    return TextbookIngestionService(
        inspector=FakeInspector(checksum, text),
        storage=LocalTextbookStorage(tmp_path / "stored"),
        repository=repository or InMemoryTextbookRepository(),
    )


def test_four_pilot_textbooks_register_independently(tmp_path: Path) -> None:
    repository = InMemoryTextbookRepository()
    results = []
    for index, pilot in enumerate(PILOT_BOOKS, 1):
        filename, medium, language, book_part = pilot
        source = tmp_path / filename
        source.write_bytes(b"%PDF-test")
        result = _service(tmp_path, f"{index:064x}", "Chapter 1\nReal Numbers", repository).ingest(
            source, _registration(*pilot)
        )
        results.append(result)
    assert len({item.textbook_id for item in results}) == 4
    assert {item.metadata.book_part for item in results} == {"semester_1", "semester_2"}
    assert {item.metadata.medium for item in results} == {"telugu", "english"}
    assert len(repository.list_all()) == 4


def test_only_exact_checksum_duplicate_is_rejected(tmp_path: Path) -> None:
    repository = InMemoryTextbookRepository()
    source = tmp_path / PILOT_BOOKS[0][0]
    source.write_bytes(b"%PDF-test")
    service = _service(tmp_path, "a" * 64, "Chapter 1", repository)
    service.ingest(source, _registration(*PILOT_BOOKS[0]))
    with pytest.raises(DuplicateTextbookError):
        service.ingest(source, _registration(*PILOT_BOOKS[1]))


def test_local_metadata_repository_persists_duplicate_detection(tmp_path: Path) -> None:
    metadata_file = tmp_path / "private" / "repository.json"
    source = tmp_path / PILOT_BOOKS[0][0]
    source.write_bytes(b"%PDF-test")
    first_repository = JsonTextbookRepository(metadata_file)
    _service(tmp_path, "c" * 64, "Chapter 1", first_repository).ingest(
        source, _registration(*PILOT_BOOKS[0])
    )
    second_repository = JsonTextbookRepository(metadata_file)
    assert second_repository.get_by_checksum("c" * 64) is not None
    with pytest.raises(DuplicateTextbookError):
        _service(tmp_path, "c" * 64, "Chapter 1", second_repository).ingest(
            source, _registration(*PILOT_BOOKS[0])
        )


def test_page_extraction_checksum_and_scanned_detection(tmp_path: Path) -> None:
    path = _pdf(tmp_path / "blank.pdf", pages=2)
    result = PdfInspector(max_file_size_bytes=1_000_000, scanned_threshold=0.8).inspect(path)
    assert result.page_count == 2
    assert len(result.pages) == 2
    assert result.pages[0].page_number == 1
    assert len(result.checksum) == 64
    assert result.is_scanned is True
    assert result.ocr_required is True


def test_unicode_mathematics_and_page_provenance_are_preserved(tmp_path: Path) -> None:
    text = "అధ్యాయం 1\nవాస్తవ సంఖ్యలు: x² + y² = z², √16 = 4"
    source = tmp_path / PILOT_BOOKS[0][0]
    source.write_bytes(b"%PDF-test")
    result = _service(tmp_path, "b" * 64, text).ingest(source, _registration(*PILOT_BOOKS[0]))
    assert result.pages[0].extracted_text == text
    assert result.pages[0].provenance.checksum == "b" * 64
    assert result.provenance.source_reference == PILOT_BOOKS[0][0]
    assert result.chapters[0].name.startswith("అధ్యాయం")


@pytest.mark.parametrize("heading", ["Chapter 3 Fractions", "Unit IV Algebra", "అధ్యాయం ౨ బహుపదులు", "పాఠం 3 జ్యామితి"])
def test_bilingual_chapter_detection(heading: str) -> None:
    chapters = ChapterDetector().detect((InspectedPage(7, heading, (), False, False),))
    assert chapters[0].page_number == 7
    assert chapters[0].confidence >= 0.9
    assert chapters[0].manually_corrected is False


def test_pdf_validation_rejects_bad_extension_content_size_and_missing_file(tmp_path: Path) -> None:
    inspector = PdfInspector(max_file_size_bytes=10)
    bad = tmp_path / "book.exe"
    bad.write_bytes(b"MZ")
    with pytest.raises(TextbookValidationError):
        inspector.inspect(bad)
    fake = tmp_path / "book.pdf"
    fake.write_bytes(b"MZ executable")
    with pytest.raises(TextbookValidationError):
        inspector.inspect(fake)
    with pytest.raises(TextbookValidationError):
        inspector.inspect(tmp_path / "missing.pdf")


def test_pdf_validation_rejects_encrypted_and_corrupt_pdf(tmp_path: Path) -> None:
    encrypted = tmp_path / "encrypted.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.encrypt("secret")
    with encrypted.open("wb") as stream:
        writer.write(stream)
    inspector = PdfInspector(max_file_size_bytes=1_000_000)
    with pytest.raises(TextbookValidationError, match="Encrypted"):
        inspector.inspect(encrypted)

    corrupt = tmp_path / "corrupt.pdf"
    corrupt.write_bytes(b"%PDF-this-is-not-a-readable-document")
    with pytest.raises(TextbookValidationError, match="corrupt or unreadable"):
        inspector.inspect(corrupt)


def test_local_storage_blocks_traversal_and_returns_opaque_key(tmp_path: Path) -> None:
    source = tmp_path / "safe.pdf"
    source.write_bytes(b"%PDF-safe")
    storage: TextbookStorage = LocalTextbookStorage(tmp_path / "private")
    key = storage.store(source, "textbook-1", "safe.pdf")
    assert key == "textbook-1/safe.pdf"
    assert str(tmp_path) not in key
    with pytest.raises(ValueError):
        storage.store(source, "textbook-1", "../unsafe.pdf")


def test_textbook_configuration(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("TEXTBOOK_STORAGE_PATH", str(tmp_path / "books"))
    monkeypatch.setenv("TEXTBOOK_MAX_FILE_SIZE_MB", "25")
    monkeypatch.setenv("TEXTBOOK_ALLOWED_MIME_TYPES", "application/pdf")
    monkeypatch.setenv("TEXTBOOK_CHECKSUM_ALGORITHM", "sha256")
    monkeypatch.setenv("TEXTBOOK_INGESTION_ENABLED", "true")
    monkeypatch.setenv("TEXTBOOK_SCANNED_THRESHOLD", "0.75")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.textbook_storage_path == (tmp_path / "books").resolve()
    assert settings.textbook_max_file_size_mb == 25
    assert settings.textbook_ingestion_enabled is True
    assert settings.textbook_scanned_threshold == 0.75


def test_no_textbook_module_imports_openai() -> None:
    root = Path("backend/app/textbooks")
    assert all("openai" not in path.read_text(encoding="utf-8").lower() for path in root.glob("*.py"))
