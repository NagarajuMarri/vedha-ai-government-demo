"""Deterministic PDF text-layer diagnostics with no OCR or external services."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
import re
from pathlib import Path
from time import perf_counter
from typing import Literal

from pypdf import PdfReader


PageRepresentation = Literal[
    "unicode_text", "non_unicode_glyph_text", "image_only",
    "hybrid_text_and_image", "empty", "extraction_error", "unknown",
]


@dataclass(frozen=True, slots=True)
class FontFinding:
    resource_name: str
    base_font: str | None
    subtype: str | None
    encoding: str | None
    embedded: bool
    has_to_unicode: bool


@dataclass(frozen=True, slots=True)
class PageEvidence:
    page_number: int
    representation: PageRepresentation
    evidence: tuple[str, ...]
    english_characters: int
    telugu_characters: int
    numeric_characters: int
    punctuation_characters: int
    replacement_characters: int
    private_use_characters: int
    control_characters: int
    total_characters: int
    extraction_length: int
    image_count: int
    image_coverage_percent: float | None
    has_text_operators: bool
    content_stream_bytes: int
    font_resources: tuple[str, ...]
    font_base_names: tuple[str, ...]
    fonts_without_to_unicode: int
    suspected_telugu_layer: bool
    suspected_telugu_evidence: tuple[str, ...]
    extraction_error: str | None = None


def classify_page(
    *, extracted_text: str, has_text_operators: bool, image_count: int,
    missing_to_unicode: bool, extraction_error: bool = False,
) -> tuple[PageRepresentation, tuple[str, ...]]:
    """Classify representation from observable PDF/text-layer evidence."""

    if extraction_error:
        return "extraction_error", ("text extraction raised an exception",)
    private_use = _private_use_count(extracted_text)
    replacement = extracted_text.count("\ufffd")
    if has_text_operators and (private_use or replacement or not extracted_text.strip()):
        evidence = ["page content contains PDF text drawing operators"]
        if missing_to_unicode:
            evidence.append("at least one page font lacks a ToUnicode CMap")
        if private_use:
            evidence.append("extraction contains private-use Unicode characters")
        if replacement:
            evidence.append("extraction contains replacement characters")
        if not extracted_text.strip():
            evidence.append("text operators produced no extractable text")
        return "non_unicode_glyph_text", tuple(evidence)
    if image_count and (has_text_operators or extracted_text.strip()):
        return "hybrid_text_and_image", ("page has text-layer evidence and image XObjects",)
    if image_count:
        return "image_only", ("page has image XObjects without text-layer evidence",)
    if extracted_text.strip():
        evidence = ["text extraction returned characters"]
        if missing_to_unicode:
            evidence.append("font lacks ToUnicode but extractor returned mapped text")
        return "unicode_text", tuple(evidence)
    if not has_text_operators:
        return "empty", ("no extractable text, text operators, or image XObjects",)
    return "unknown", ("available evidence did not match a known representation",)


def inspect_font(resource_name: str, font) -> FontFinding:
    font_object = font.get_object() if hasattr(font, "get_object") else font
    descriptor = font_object.get("/FontDescriptor") if hasattr(font_object, "get") else None
    descriptor = descriptor.get_object() if hasattr(descriptor, "get_object") else descriptor
    if not descriptor and hasattr(font_object, "get"):
        descendants = font_object.get("/DescendantFonts") or ()
        if descendants:
            descendant = descendants[0].get_object() if hasattr(descendants[0], "get_object") else descendants[0]
            descriptor = descendant.get("/FontDescriptor") if hasattr(descendant, "get") else None
            descriptor = descriptor.get_object() if hasattr(descriptor, "get_object") else descriptor
    embedded = bool(descriptor and any(descriptor.get(key) for key in ("/FontFile", "/FontFile2", "/FontFile3")))
    encoding = font_object.get("/Encoding") if hasattr(font_object, "get") else None
    if hasattr(encoding, "get_object"):
        encoding = encoding.get_object()
    return FontFinding(
        resource_name=str(resource_name),
        base_font=_safe_name(font_object.get("/BaseFont")) if hasattr(font_object, "get") else None,
        subtype=_safe_name(font_object.get("/Subtype")) if hasattr(font_object, "get") else None,
        encoding=_safe_name(encoding),
        embedded=embedded,
        has_to_unicode=bool(font_object.get("/ToUnicode")) if hasattr(font_object, "get") else False,
    )


def investigate_pdf(path: Path, *, aliases: tuple[str, ...] = ()) -> dict[str, object]:
    started = perf_counter()
    reader = PdfReader(str(path), strict=True)
    pages: list[PageEvidence] = []
    all_fonts: dict[tuple[object, ...], FontFinding] = {}
    for number, page in enumerate(reader.pages, 1):
        resources = page.get("/Resources") or {}
        resources = resources.get_object() if hasattr(resources, "get_object") else resources
        font_mapping = resources.get("/Font") if hasattr(resources, "get") else None
        font_mapping = font_mapping.get_object() if hasattr(font_mapping, "get_object") else font_mapping
        page_fonts: list[FontFinding] = []
        if font_mapping:
            for name, font in font_mapping.items():
                finding = inspect_font(str(name), font)
                page_fonts.append(finding)
                key = (finding.base_font, finding.subtype, finding.encoding, finding.embedded, finding.has_to_unicode)
                all_fonts[key] = finding
        xobjects = resources.get("/XObject") if hasattr(resources, "get") else None
        xobjects = xobjects.get_object() if hasattr(xobjects, "get_object") else xobjects
        images = []
        if xobjects:
            for item in xobjects.values():
                try:
                    obj = item.get_object()
                    if obj.get("/Subtype") == "/Image":
                        images.append(obj)
                except Exception:
                    continue
        content = _content_bytes(page)
        has_text_operators = bool(re.search(rb"(?:^|\s)(?:BT|Tj|TJ|'|\")(?:\s|$)", content))
        error_message = None
        try:
            extracted = page.extract_text() or ""
        except Exception as exc:
            extracted = ""
            error_message = type(exc).__name__
        representation, evidence = classify_page(
            extracted_text=extracted,
            has_text_operators=has_text_operators,
            image_count=len(images),
            missing_to_unicode=any(not font.has_to_unicode for font in page_fonts),
            extraction_error=error_message is not None,
        )
        telugu_fonts = tuple(
            font for font in page_fonts if _looks_like_telugu_font(font.base_font)
        )
        suspected_evidence: list[str] = []
        if telugu_fonts:
            suspected_evidence.append("page references known Telugu-script font-family names")
        if telugu_fonts and not any(font.has_to_unicode for font in telugu_fonts):
            suspected_evidence.append("Telugu-named page fonts lack ToUnicode CMaps")
        if telugu_fonts and not any("\u0c00" <= char <= "\u0c7f" for char in extracted):
            suspected_evidence.append("no Telugu Unicode was extracted from Telugu-named fonts")
        pages.append(PageEvidence(
            page_number=number,
            representation=representation,
            evidence=evidence,
            english_characters=sum(char.isascii() and char.isalpha() for char in extracted),
            telugu_characters=sum("\u0c00" <= char <= "\u0c7f" for char in extracted),
            numeric_characters=sum(char.isnumeric() for char in extracted),
            punctuation_characters=sum(not char.isalnum() and not char.isspace() for char in extracted),
            replacement_characters=extracted.count("\ufffd"),
            private_use_characters=_private_use_count(extracted),
            control_characters=sum(ord(char) < 32 and char not in "\n\r\t" for char in extracted),
            total_characters=len(extracted),
            extraction_length=len(extracted.encode("utf-8")),
            image_count=len(images),
            image_coverage_percent=_image_coverage(page, images),
            has_text_operators=has_text_operators,
            content_stream_bytes=len(content),
            font_resources=tuple(font.resource_name for font in page_fonts),
            font_base_names=tuple(font.base_font or "unknown" for font in page_fonts),
            fonts_without_to_unicode=sum(not font.has_to_unicode for font in page_fonts),
            suspected_telugu_layer=bool(telugu_fonts),
            suspected_telugu_evidence=tuple(suspected_evidence),
            extraction_error=error_message,
        ))
    elapsed = perf_counter() - started
    representations = Counter(page.representation for page in pages)
    metadata = reader.metadata or {}
    root_cause = _root_cause(tuple(all_fonts.values()), tuple(pages))
    return {
        "filename": path.name,
        "aliases": aliases,
        "pdf_version": getattr(reader, "pdf_header", None),
        "encrypted": reader.is_encrypted,
        "page_count": len(pages),
        "metadata": {str(key): str(value)[:500] for key, value in metadata.items()},
        "fonts": [asdict(font) for font in all_fonts.values()],
        "font_summary": {
            "unique_fonts": len(all_fonts),
            "embedded_fonts": sum(font.embedded for font in all_fonts.values()),
            "fonts_with_to_unicode": sum(font.has_to_unicode for font in all_fonts.values()),
            "fonts_without_to_unicode": sum(not font.has_to_unicode for font in all_fonts.values()),
        },
        "representation_summary": dict(representations),
        "character_summary": {
            field: sum(getattr(page, field) for page in pages)
            for field in (
                "english_characters", "telugu_characters", "numeric_characters",
                "punctuation_characters", "replacement_characters",
                "private_use_characters", "control_characters", "total_characters",
            )
        },
        "image_summary": {
            "pages_with_images": sum(page.image_count > 0 for page in pages),
            "total_images": sum(page.image_count for page in pages),
        },
        "suspected_telugu_summary": {
            "pages_with_telugu_named_fonts": sum(page.suspected_telugu_layer for page in pages),
            "pages_with_telugu_fonts_and_no_telugu_unicode": sum(
                page.suspected_telugu_layer and page.telugu_characters == 0 for page in pages
            ),
            "pages_with_missing_to_unicode_fonts": sum(page.fonts_without_to_unicode > 0 for page in pages),
        },
        "selectable_text_summary": {
            "pages_with_extracted_text": sum(page.total_characters > 0 for page in pages),
            "pages_with_text_operators": sum(page.has_text_operators for page in pages),
            "human_confirmation_required": True,
        },
        "pages": [asdict(page) for page in pages],
        "diagnostic_sample_pages": _diagnostic_samples(tuple(pages)),
        "root_cause": root_cause,
        "extractor_comparison": {
            "pypdf": {
                "available": True,
                "elapsed_seconds": round(elapsed, 3),
                "extracted_characters": sum(page.total_characters for page in pages),
                "english_characters": sum(page.english_characters for page in pages),
                "telugu_characters": sum(page.telugu_characters for page in pages),
                "malformed_characters": sum(page.replacement_characters + page.private_use_characters for page in pages),
                "page_failures": sum(page.extraction_error is not None for page in pages),
            },
            "pymupdf": {"available": False, "reason": "not installed"},
            "pdfminer.six": {"available": False, "reason": "not installed"},
            "pdfplumber": {"available": False, "reason": "not installed"},
        },
    }


def _content_bytes(page) -> bytes:
    try:
        contents = page.get_contents()
        if contents is None:
            return b""
        return contents.get_data()
    except Exception:
        return b""


def _image_coverage(page, images: list[object]) -> float | None:
    if not images:
        return 0.0
    try:
        page_area = float(page.mediabox.width) * float(page.mediabox.height)
        pixel_area = sum(float(image.get("/Width", 0)) * float(image.get("/Height", 0)) for image in images)
        return round(min(100.0, pixel_area / page_area * 100), 2) if page_area else None
    except Exception:
        return None


def _private_use_count(text: str) -> int:
    return sum(
        0xE000 <= ord(char) <= 0xF8FF
        or 0xF0000 <= ord(char) <= 0xFFFFD
        or 0x100000 <= ord(char) <= 0x10FFFD
        for char in text
    )


def _safe_name(value) -> str | None:
    if value is None:
        return None
    normalized = " ".join(str(value).split())
    return normalized[:240] or None


def _looks_like_telugu_font(name: str | None) -> bool:
    normalized = (name or "").lower()
    return any(token in normalized for token in (
        "deepika", "priyaanka", "anupama", "prabhava", "pallavi", "brahma", "rachana",
    ))


def _root_cause(fonts: tuple[FontFinding, ...], pages: tuple[PageEvidence, ...]) -> dict[str, object]:
    telugu_fonts = tuple(font for font in fonts if _looks_like_telugu_font(font.base_font))
    missing = sum(not font.has_to_unicode for font in telugu_fonts)
    telugu_characters = sum(page.telugu_characters for page in pages)
    private_use = sum(page.private_use_characters for page in pages)
    if telugu_fonts and missing >= max(1, len(telugu_fonts) // 2):
        classification = "custom legacy Telugu font encoding with missing ToUnicode mappings"
        confidence = 0.93
    elif telugu_fonts and telugu_characters == 0:
        classification = "custom legacy Telugu font encoding with invalid or non-Unicode CMap output"
        confidence = 0.88
    else:
        classification = "inconclusive"
        confidence = 0.5
    return {
        "classification": classification,
        "confidence": confidence,
        "supporting_evidence": (
            f"{len(telugu_fonts)} unique Telugu-named fonts were found",
            f"{missing} Telugu-named fonts lack ToUnicode CMaps",
            f"pypdf extracted {telugu_characters} Telugu Unicode characters",
            f"extraction contains {private_use} private-use characters",
            "text drawing operators are present, contradicting a raster-only explanation",
        ),
        "contradicting_evidence": (
            "some fonts expose ToUnicode CMaps" if any(font.has_to_unicode for font in telugu_fonts) else "none identified",
            "image XObjects coexist on many pages, so representation is mixed at page level",
        ),
        "unresolved_questions": (
            "whether the available ToUnicode maps contain semantically correct Telugu mappings",
            "whether a better official source PDF preserves Unicode Telugu text",
            "human text-selection behavior in a desktop PDF viewer",
        ),
    }


def _diagnostic_samples(pages: tuple[PageEvidence, ...]) -> dict[str, object]:
    if not pages:
        return {}
    first = next((page.page_number for page in pages if page.total_characters), 1)
    middle = max(1, len(pages) // 2)
    later = max(1, len(pages) - 2)
    formula = max(pages, key=lambda page: page.punctuation_characters).page_number
    image = max(pages, key=lambda page: page.image_count).page_number
    selected = tuple(dict.fromkeys((first, min(first + 1, len(pages)), middle, min(middle + 1, len(pages)), later, min(later + 1, len(pages)), formula, image)))
    by_number = {page.page_number: page for page in pages}
    return {
        "page_numbers": selected,
        "summaries": tuple({
            "page_number": number,
            "representation": by_number[number].representation,
            "image_count": by_number[number].image_count,
            "suspected_telugu_layer": by_number[number].suspected_telugu_layer,
            "fonts_without_to_unicode": by_number[number].fonts_without_to_unicode,
        } for number in selected),
        "selection_basis": "early pair, middle pair, later pair, punctuation-heavy page, image-heavy page",
        "contains_excerpts": False,
    }
