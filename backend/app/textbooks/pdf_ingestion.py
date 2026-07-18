"""Deterministic PDF inspection, extraction, and chapter detection."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from backend.app.textbooks.models import TextbookChapter


class TextbookValidationError(ValueError):
    """A textbook file failed safe deterministic validation."""


@dataclass(frozen=True, slots=True)
class InspectedPage:
    page_number: int
    text: str
    warnings: tuple[str, ...]
    has_images: bool
    has_tables: bool


@dataclass(frozen=True, slots=True)
class ExtractedBookMetadata:
    title: str | None
    publisher: str | None
    edition: str | None
    publication_year: int | None
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PdfInspection:
    checksum: str
    file_size_bytes: int
    page_count: int
    pages: tuple[InspectedPage, ...]
    is_scanned: bool
    ocr_required: bool
    detection_reason: str | None
    warnings: tuple[str, ...]
    book_metadata: ExtractedBookMetadata | None = None


class ChapterDetector:
    """Find explicit English or Telugu chapter headings with explainable confidence."""

    _PATTERN = re.compile(
        r"(?im)^\s*((?:chapter|unit)\s+(?:\d+|[ivxlcdm]+)[^\n]*|"
        r"(?:అధ్యాయం|పాఠం)\s*(?:\d+|[౦-౯]+)?[^\n]*)\s*$"
    )

    def detect(self, pages: tuple[InspectedPage, ...]) -> tuple[TextbookChapter, ...]:
        chapters: list[TextbookChapter] = []
        for page in pages:
            for match in self._PATTERN.finditer(page.text):
                heading = " ".join(match.group(1).split())
                confidence = 0.95 if re.match(r"(?i)^(chapter|unit)\s+\w+", heading) else 0.9
                chapters.append(TextbookChapter(
                    name=heading,
                    page_number=page.page_number,
                    confidence=confidence,
                ))
        return tuple(chapters)


class PdfInspector:
    """Validate and extract a PDF one page at a time without OCR."""

    def __init__(
        self,
        *,
        max_file_size_bytes: int,
        allowed_mime_types: tuple[str, ...] = ("application/pdf",),
        scanned_threshold: float = 0.8,
        checksum_algorithm: str = "sha256",
    ) -> None:
        if checksum_algorithm != "sha256":
            raise ValueError("Only sha256 is supported")
        if not 0 <= scanned_threshold <= 1:
            raise ValueError("Scanned threshold must be between zero and one")
        self._max_size = max_file_size_bytes
        self._allowed_mime_types = allowed_mime_types
        self._scanned_threshold = scanned_threshold

    def inspect(self, path: Path) -> PdfInspection:
        resolved = path.resolve()
        if not resolved.is_file():
            raise TextbookValidationError("Textbook file does not exist")
        if resolved.suffix.lower() != ".pdf":
            raise TextbookValidationError("Textbook file must use the .pdf extension")
        size = resolved.stat().st_size
        if size <= 0 or size > self._max_size:
            raise TextbookValidationError("Textbook file size is not allowed")
        with resolved.open("rb") as stream:
            header = stream.read(5)
        if header != b"%PDF-" or "application/pdf" not in self._allowed_mime_types:
            raise TextbookValidationError("Textbook content is not an allowed PDF")
        checksum = self._checksum(resolved)
        try:
            reader = PdfReader(str(resolved), strict=True)
            if reader.is_encrypted:
                raise TextbookValidationError("Encrypted textbooks are not supported")
            if not reader.pages:
                raise TextbookValidationError("Textbook PDF contains no pages")
            pages = tuple(self._extract_page(page, number) for number, page in enumerate(reader.pages, 1))
            book_metadata = self._extract_book_metadata(reader.metadata, pages)
        except TextbookValidationError:
            raise
        except (PdfReadError, OSError, ValueError, TypeError) as exc:
            raise TextbookValidationError("Textbook PDF is corrupt or unreadable") from exc

        low_text_pages = sum(len(page.text.strip()) < 20 for page in pages)
        low_text_ratio = low_text_pages / len(pages)
        scanned = low_text_ratio >= self._scanned_threshold
        reason = "Most pages contain insufficient extractable text" if scanned else None
        warnings = ("OCR is required but was not executed",) if scanned else ()
        return PdfInspection(
            checksum=checksum,
            file_size_bytes=size,
            page_count=len(pages),
            pages=pages,
            is_scanned=scanned,
            ocr_required=scanned,
            detection_reason=reason,
            warnings=warnings + book_metadata.warnings,
            book_metadata=book_metadata,
        )

    @staticmethod
    def _extract_book_metadata(document_metadata, pages: tuple[InspectedPage, ...]) -> ExtractedBookMetadata:
        metadata = document_metadata or {}
        front_matter = "\n".join(page.text for page in pages[:8])

        def clean(value) -> str | None:
            if value is None:
                return None
            normalized = " ".join(str(value).replace("\x00", " ").split())
            return normalized[:240] or None

        title = clean(metadata.get("/Title"))
        publisher = clean(metadata.get("/Publisher"))
        edition = clean(metadata.get("/Edition"))
        publication_year: int | None = None

        if not publisher:
            match = re.search(r"(?im)^\s*(?:published\s+by|publisher)\s*[:\-]?\s*(.{3,200})\s*$", front_matter)
            publisher = clean(match.group(1)) if match else None
        if not edition:
            match = re.search(
                r"(?i)\b((?:first|second|third|fourth|revised|\d+(?:st|nd|rd|th))\s+edition)\b",
                front_matter,
            )
            edition = clean(match.group(1)) if match else None
        year_match = re.search(
            r"(?i)(?:copyright|©|published|publication|edition)[^\n]{0,50}\b((?:19|20)\d{2})\b",
            front_matter,
        )
        if year_match:
            publication_year = int(year_match.group(1))
        elif metadata.get("/CreationDate"):
            date_match = re.search(r"((?:19|20)\d{2})", str(metadata.get("/CreationDate")))
            publication_year = int(date_match.group(1)) if date_match else None

        if not title:
            boilerplate = re.compile(r"(?i)^(copyright|published\s+by|publisher|first\s+edition|contents?)\b")
            for line in front_matter.splitlines():
                candidate = clean(line)
                if candidate and 5 <= len(candidate) <= 200 and not boilerplate.match(candidate):
                    if sum(character.isalpha() for character in candidate) >= 4:
                        title = candidate
                        break

        missing = tuple(
            name for name, value in (
                ("title", title),
                ("publisher", publisher),
                ("edition", edition),
                ("publication year", publication_year),
            ) if value is None
        )
        warnings = tuple(f"Textbook {name} could not be determined confidently" for name in missing)
        return ExtractedBookMetadata(title, publisher, edition, publication_year, warnings)

    @staticmethod
    def _checksum(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    @staticmethod
    def _extract_page(page, page_number: int) -> InspectedPage:
        warnings: list[str] = []
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
            warnings.append("Page text extraction failed")
        resources = page.get("/Resources") or {}
        xobjects = resources.get("/XObject") if hasattr(resources, "get") else None
        has_images = False
        if xobjects:
            try:
                has_images = any(obj.get_object().get("/Subtype") == "/Image" for obj in xobjects.get_object().values())
            except Exception:
                warnings.append("Page image inspection was incomplete")
        table_markers = text.count("|") >= 4 or bool(re.search(r"\S+\s{3,}\S+\s{3,}\S+", text))
        return InspectedPage(page_number, text, tuple(warnings), has_images, table_markers)
