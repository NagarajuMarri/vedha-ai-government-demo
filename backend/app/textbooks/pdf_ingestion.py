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
class PdfInspection:
    checksum: str
    file_size_bytes: int
    page_count: int
    pages: tuple[InspectedPage, ...]
    is_scanned: bool
    ocr_required: bool
    detection_reason: str | None
    warnings: tuple[str, ...]


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
            warnings=warnings,
        )

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
