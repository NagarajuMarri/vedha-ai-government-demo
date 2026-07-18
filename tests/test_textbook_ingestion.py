"""Sprint 4C textbook repository and deterministic ingestion tests."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import shutil
from types import SimpleNamespace

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
from backend.app.textbooks.validation import TextbookContentValidator
from scripts.ingest_pilot_textbooks import (
    PILOT_BOOKS as COMMAND_PILOT_BOOKS,
    PilotPreflightError,
    _migrate_existing,
    run as run_pilot_ingestion,
    validate_source_directory,
)


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


def test_two_bilingual_semester_textbooks_register_independently(tmp_path: Path) -> None:
    repository = InMemoryTextbookRepository()
    results = []
    for index, pilot in enumerate((PILOT_BOOKS[2], PILOT_BOOKS[3]), 1):
        filename, medium, language, book_part = pilot
        source = tmp_path / filename
        source.write_bytes(b"%PDF-test")
        text = "Chapter 1\nReal Numbers"
        registration = _registration(*pilot).model_copy(update={
            "medium": "bilingual",
            "languages": ("en", "te"),
        })
        result = _service(tmp_path, f"{index:064x}", text, repository).ingest(
            source, registration,
        )
        results.append(result)
    assert len({item.textbook_id for item in results}) == 2
    assert {item.metadata.book_part for item in results} == {"semester_1", "semester_2"}
    assert {item.metadata.medium for item in results} == {"bilingual"}
    assert all(item.metadata.languages == ("en", "te") for item in results)
    assert len(repository.list_all()) == 2


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


def test_filename_does_not_override_detected_content_language(tmp_path: Path) -> None:
    source = tmp_path / PILOT_BOOKS[0][0]
    source.write_bytes(b"%PDF-test")
    service = _service(tmp_path, "d" * 64, "Chapter 1\nThis page contains English mathematics content.")
    with pytest.raises(TextbookValidationError, match="predominantly english"):
        service.ingest(source, _registration(*PILOT_BOOKS[0]))
    assert not tuple((tmp_path / "stored").rglob("*.pdf"))


def test_equal_file_size_with_different_checksums_is_not_a_duplicate(tmp_path: Path) -> None:
    repository = InMemoryTextbookRepository()
    first = tmp_path / PILOT_BOOKS[2][0]
    second = tmp_path / PILOT_BOOKS[3][0]
    first.write_bytes(b"%PDF-one")
    second.write_bytes(b"%PDF-two")
    assert first.stat().st_size == second.stat().st_size
    _service(tmp_path, "1" * 64, "Chapter 1\nEnglish mathematics content", repository).ingest(
        first, _registration(*PILOT_BOOKS[2])
    )
    _service(tmp_path, "2" * 64, "Chapter 2\nEnglish geometry content", repository).ingest(
        second, _registration(*PILOT_BOOKS[3])
    )
    assert len(repository.list_all()) == 2


def test_content_sampling_ignores_blank_pages_and_uses_representative_content() -> None:
    pages = (
        InspectedPage(1, "", (), False, False),
        InspectedPage(2, "Chapter 1 English mathematics introduction", (), False, False),
        InspectedPage(3, "", (), False, False),
        InspectedPage(4, "Chapter 5 Coordinate geometry exercises", (), True, False),
        InspectedPage(5, "Chapter 9 Statistics and probability review", (), False, True),
    )
    inspection = PdfInspection("3" * 64, 500, 5, pages, False, False, None, ())
    result = TextbookContentValidator().validate(inspection, "en")
    assert result.sampled_page_numbers == (2, 4, 5)
    assert result.detected_language == "english"
    assert result.pages_without_text == 2
    assert result.image_pages == 1
    assert result.table_pages == 1


def test_unicode_replacement_character_is_flagged() -> None:
    text = "\u0c05\u0c27\u0c4d\u0c2f\u0c3e\u0c2f\u0c02 \u0c35\u0c3e\u0c38\u0c4d\u0c24\u0c35 \u0c38\u0c02\u0c16\u0c4d\u0c2f\u0c32\u0c41 \ufffd"
    pages = (InspectedPage(1, text, (), False, False),)
    inspection = PdfInspection("4" * 64, 100, 1, pages, False, False, None, ())
    result = TextbookContentValidator().validate(inspection, "te")
    assert result.unicode_valid is False
    assert result.replacement_character_count == 1
    assert result.warnings


def test_repository_failure_removes_stored_file(tmp_path: Path) -> None:
    class FailingRepository(InMemoryTextbookRepository):
        def add(self, result) -> None:
            raise OSError("simulated persistence failure")

    source = tmp_path / PILOT_BOOKS[2][0]
    source.write_bytes(b"%PDF-test")
    with pytest.raises(OSError, match="persistence failure"):
        _service(
            tmp_path,
            "5" * 64,
            "Chapter 1\nEnglish mathematics content",
            FailingRepository(),
        ).ingest(source, _registration(*PILOT_BOOKS[2]))
    assert not tuple((tmp_path / "stored").rglob("*.pdf"))


def test_pilot_command_requires_explicit_existing_source_directory(tmp_path: Path) -> None:
    with pytest.raises(PilotPreflightError, match="does not exist") as error:
        validate_source_directory(tmp_path / "not-provided")
    assert error.value.code == "source_directory_invalid"


def test_pilot_preflight_reports_every_missing_filename(tmp_path: Path) -> None:
    present = tmp_path / COMMAND_PILOT_BOOKS[0].canonical_filename
    _pdf(present)
    with pytest.raises(PilotPreflightError) as error:
        validate_source_directory(tmp_path)
    assert error.value.code == "pilot_files_incomplete"
    assert error.value.missing == tuple(
        filename for book in COMMAND_PILOT_BOOKS for filename in book.filenames if filename != present.name
    )


def test_pilot_preflight_accepts_all_four_generated_fixture_pdfs(tmp_path: Path) -> None:
    for index, book in enumerate(COMMAND_PILOT_BOOKS, 1):
        _pdf(tmp_path / book.canonical_filename, pages=index)
        shutil.copyfile(tmp_path / book.canonical_filename, tmp_path / book.alternate_filename)
    paths = validate_source_directory(tmp_path)
    assert tuple(paths) == tuple(filename for book in COMMAND_PILOT_BOOKS for filename in book.filenames)
    assert all(path.is_file() for path in paths.values())


def test_single_pilot_command_ingests_four_generated_fixtures(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    source = tmp_path / "external"
    source.mkdir()
    for index, book in enumerate(COMMAND_PILOT_BOOKS, 1):
        _pdf(source / book.canonical_filename, pages=index)
        shutil.copyfile(source / book.canonical_filename, source / book.alternate_filename)
    storage = tmp_path / "private-storage"
    monkeypatch.setenv("TEXTBOOK_INGESTION_ENABLED", "true")
    monkeypatch.setenv("TEXTBOOK_STORAGE_PATH", str(storage))
    get_settings.cache_clear()
    report = run_pilot_ingestion(SimpleNamespace(
        source_directory=source,
        curriculum_version="verified-test-version",
        board=None,
        academic_year=None,
    ))
    assert report["status"].startswith("completed")
    assert report["unique_textbooks"] == 2
    assert len(tuple((storage).glob("textbook-*/*.pdf"))) == 2
    records = JsonTextbookRepository(storage / ".textbook_repository.json").list_all()
    assert len(records) == 2
    assert all(record.metadata.medium == "bilingual" for record in records)
    assert all(record.metadata.languages == ("en", "te") for record in records)
    assert all(record.provenance.alternate_source_references for record in records)


def test_all_page_bilingual_and_alternating_language_detection() -> None:
    english = "This page explains algebra and real numbers in English."
    telugu = "\u0c08 \u0c2a\u0c47\u0c1c\u0c40 \u0c2c\u0c40\u0c1c\u0c17\u0c23\u0c3f\u0c24\u0c02 \u0c2e\u0c30\u0c3f\u0c2f\u0c41 \u0c35\u0c3e\u0c38\u0c4d\u0c24\u0c35 \u0c38\u0c02\u0c16\u0c4d\u0c2f\u0c32\u0c28\u0c41 \u0c35\u0c3f\u0c35\u0c30\u0c3f\u0c38\u0c4d\u0c24\u0c41\u0c02\u0c26\u0c3f."
    pages = tuple(
        InspectedPage(index, text, (), False, False)
        for index, text in enumerate((english, telugu, english, telugu), 1)
    )
    inspection = PdfInspection("6" * 64, 400, 4, pages, False, False, None, ())
    result = TextbookContentValidator().validate(inspection, ("en", "te"))
    assert result.detected_language == "bilingual"
    assert result.english_pages == 2
    assert result.telugu_pages == 2
    assert result.alternating_language_pairs == 3
    assert result.bilingual_coverage_percent == 100
    assert result.telugu_character_count > 0


def test_all_page_validation_finds_telugu_outside_representative_sample() -> None:
    english = "English mathematics explanation with enough alphabetic content."
    telugu = "\u0c24\u0c46\u0c32\u0c41\u0c17\u0c41 \u0c05\u0c28\u0c41\u0c35\u0c3e\u0c26\u0c02 \u0c2a\u0c4d\u0c30\u0c24\u0c3f \u0c2a\u0c47\u0c1c\u0c40\u0c32\u0c4b \u0c35\u0c3f\u0c35\u0c30\u0c3f\u0c02\u0c1a\u0c2c\u0c21\u0c3f\u0c02\u0c26\u0c3f."
    texts = (english, telugu, english, english, english, english, english)
    pages = tuple(InspectedPage(index, text, (), False, False) for index, text in enumerate(texts, 1))
    inspection = PdfInspection("7" * 64, 700, 7, pages, False, False, None, ())
    result = TextbookContentValidator().validate(inspection, ("en", "te"))
    assert result.detected_language == "bilingual"
    assert result.sampled_page_numbers == (1, 4, 7)
    assert result.telugu_pages == 1


def test_existing_english_record_migrates_to_bilingual_without_new_id_or_pages(tmp_path: Path) -> None:
    repository = InMemoryTextbookRepository()
    source = tmp_path / PILOT_BOOKS[2][0]
    source.write_bytes(b"%PDF-test")
    original = _service(
        tmp_path,
        "8" * 64,
        "Chapter 1 English mathematics content",
        repository,
    ).ingest(source, _registration(*PILOT_BOOKS[2]))
    book = COMMAND_PILOT_BOOKS[0]
    inspection = FakeInspector("8" * 64, "Chapter 1 English mathematics content").inspect(source)
    validation = TextbookContentValidator().validate(inspection, ("en", "te"))
    migrated = _migrate_existing(original, book, validation, inspection, repository)
    assert migrated.textbook_id == original.textbook_id
    assert migrated.metadata.medium == "bilingual"
    assert migrated.metadata.languages == ("en", "te")
    assert migrated.provenance.alternate_source_references == (book.alternate_filename,)
    assert len(migrated.pages) == len(original.pages)
    assert len(repository.list_all()) == 1
    assert len(tuple((tmp_path / "stored").rglob("*.pdf"))) == 1


def test_pdf_bibliographic_metadata_is_extracted_automatically(tmp_path: Path) -> None:
    path = tmp_path / "metadata.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.add_metadata({
        "/Title": "Class 10 Mathematics",
        "/Publisher": "Official Education Publisher",
        "/Edition": "First Edition",
        "/CreationDate": "D:20250101000000",
    })
    with path.open("wb") as stream:
        writer.write(stream)
    inspection = PdfInspector(max_file_size_bytes=1_000_000).inspect(path)
    assert inspection.book_metadata is not None
    assert inspection.book_metadata.title == "Class 10 Mathematics"
    assert inspection.book_metadata.publisher == "Official Education Publisher"
    assert inspection.book_metadata.edition == "First Edition"
    assert inspection.book_metadata.publication_year == 2025
    assert inspection.book_metadata.warnings == ()


def test_missing_bibliographic_metadata_warns_but_does_not_block_ingestion(tmp_path: Path) -> None:
    source = _pdf(tmp_path / PILOT_BOOKS[2][0])
    registration = _registration(*PILOT_BOOKS[2]).model_copy(update={
        "edition": TextbookEdition(),
        "title": None,
    })
    result = TextbookIngestionService(
        inspector=PdfInspector(max_file_size_bytes=1_000_000),
        storage=LocalTextbookStorage(tmp_path / "private"),
        repository=InMemoryTextbookRepository(),
    ).ingest(source, registration)
    assert result.metadata.title is None
    assert result.metadata.publisher is None
    assert result.metadata.edition is None
    assert result.metadata.publication_year is None
    assert any("could not be determined confidently" in warning for warning in result.warnings)
