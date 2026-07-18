"""Deterministic local validation of extracted textbook content."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from backend.app.textbooks.pdf_ingestion import InspectedPage, PdfInspection, TextbookValidationError


DetectedLanguage = Literal["telugu", "english", "bilingual", "mixed", "unreadable", "empty", "scanned"]


@dataclass(frozen=True, slots=True)
class ContentValidation:
    detected_language: DetectedLanguage
    sampled_page_numbers: tuple[int, ...]
    pages_with_text: int
    pages_without_text: int
    pages_with_warnings: int
    likely_scanned_pages: int
    image_pages: int
    table_pages: int
    text_coverage_percent: float
    replacement_character_count: int
    unicode_valid: bool
    english_pages: int
    telugu_pages: int
    mixed_language_pages: int
    unreadable_pages: int
    english_character_count: int
    telugu_character_count: int
    bilingual_coverage_percent: float
    alternating_language_pairs: int
    warnings: tuple[str, ...]


class TextbookContentValidator:
    """Classify representative extracted text without AI or external services."""

    _TELUGU_START = ord("\u0c00")
    _TELUGU_END = ord("\u0c7f")

    def validate(self, inspection: PdfInspection, expected_language: str | tuple[str, ...]) -> ContentValidation:
        content_pages = tuple(page for page in inspection.pages if len(page.text.strip()) >= 20)
        sampled_pages = self._representative_pages(content_pages)
        sample_text = "\n".join(page.text for page in sampled_pages)
        page_languages = tuple(self.detect_language(page.text) for page in inspection.pages)
        english_pages = page_languages.count("english")
        telugu_pages = page_languages.count("telugu")
        mixed_pages = page_languages.count("mixed")
        unreadable_pages = sum(value in {"empty", "unreadable"} for value in page_languages)
        expected = self._canonical_expected_language(expected_language)
        if inspection.is_scanned:
            detected: DetectedLanguage = "scanned"
        elif english_pages and telugu_pages and min(english_pages, telugu_pages) >= max(1, int(inspection.page_count * 0.05)):
            detected = "bilingual"
        elif mixed_pages and (english_pages or telugu_pages):
            detected = "mixed"
        else:
            detected = self.detect_language(sample_text)
        full_text = "\n".join(page.text for page in inspection.pages)
        replacement_count = full_text.count("\ufffd")
        english_characters = sum(character.isascii() and character.isalpha() for character in full_text)
        telugu_characters = sum(self._TELUGU_START <= ord(character) <= self._TELUGU_END for character in full_text)
        alternating_pairs = sum(
            {left, right} == {"english", "telugu"}
            for left, right in zip(page_languages, page_languages[1:])
        )
        represented_pages = english_pages + telugu_pages + mixed_pages
        bilingual_coverage = (
            round((2 * min(english_pages, telugu_pages) + mixed_pages) / represented_pages * 100, 2)
            if represented_pages else 0.0
        )
        warnings: list[str] = []
        if replacement_count:
            warnings.append("Extracted text contains Unicode replacement characters")
        if detected in {"empty", "unreadable", "scanned"}:
            warnings.append("Representative content language could not be verified")
        elif expected == "bilingual" and detected != "bilingual":
            warnings.append("Extracted text did not independently confirm bilingual Unicode coverage")
        elif detected not in {"mixed", expected}:
            raise TextbookValidationError(
                f"Extracted content is predominantly {detected}, not the registered {expected} language"
            )

        total_pages = inspection.page_count
        pages_with_text = sum(bool(page.text.strip()) for page in inspection.pages)
        low_text_pages = sum(len(page.text.strip()) < 20 for page in inspection.pages)
        return ContentValidation(
            detected_language=detected,
            sampled_page_numbers=tuple(page.page_number for page in sampled_pages),
            pages_with_text=pages_with_text,
            pages_without_text=total_pages - pages_with_text,
            pages_with_warnings=sum(bool(page.warnings) for page in inspection.pages),
            likely_scanned_pages=low_text_pages,
            image_pages=sum(page.has_images for page in inspection.pages),
            table_pages=sum(page.has_tables for page in inspection.pages),
            text_coverage_percent=round(pages_with_text / total_pages * 100, 2),
            replacement_character_count=replacement_count,
            unicode_valid=replacement_count == 0,
            english_pages=english_pages,
            telugu_pages=telugu_pages,
            mixed_language_pages=mixed_pages,
            unreadable_pages=unreadable_pages,
            english_character_count=english_characters,
            telugu_character_count=telugu_characters,
            bilingual_coverage_percent=bilingual_coverage,
            alternating_language_pairs=alternating_pairs,
            warnings=tuple(warnings),
        )

    @classmethod
    def detect_language(cls, text: str) -> DetectedLanguage:
        stripped = text.strip()
        if not stripped:
            return "empty"
        telugu = sum(cls._TELUGU_START <= ord(character) <= cls._TELUGU_END for character in stripped)
        english = sum(character.isascii() and character.isalpha() for character in stripped)
        if telugu == 0 and english < 10:
            return "unreadable"
        if telugu >= 10 and english >= 10:
            if telugu >= english * 2:
                return "telugu"
            if english >= telugu * 2:
                return "english"
            return "mixed"
        if telugu >= 10:
            return "telugu"
        return "english"

    @staticmethod
    def _representative_pages(pages: tuple[InspectedPage, ...]) -> tuple[InspectedPage, ...]:
        if not pages:
            return ()
        indexes = (0, len(pages) // 2, len(pages) - 1)
        return tuple(pages[index] for index in dict.fromkeys(indexes))

    @staticmethod
    def _canonical_expected_language(language: str | tuple[str, ...]) -> Literal["telugu", "english", "bilingual"]:
        if isinstance(language, tuple):
            normalized_values = {value.strip().lower() for value in language}
            if normalized_values == {"en", "te"} or normalized_values == {"english", "telugu"}:
                return "bilingual"
            if len(normalized_values) != 1:
                raise TextbookValidationError("Registered textbook languages are unsupported")
            normalized = next(iter(normalized_values))
        else:
            normalized = language.strip().lower()
        if normalized in {"te", "telugu"}:
            return "telugu"
        if normalized in {"en", "english"}:
            return "english"
        raise TextbookValidationError("Registered textbook language is unsupported")
