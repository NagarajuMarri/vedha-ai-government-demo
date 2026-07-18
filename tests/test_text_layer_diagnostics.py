"""Sprint 4C.4 deterministic PDF text-layer diagnostic tests."""

from __future__ import annotations

import json
from pathlib import Path
import shutil

from pypdf import PdfWriter

from backend.app.textbooks.text_layer_diagnostics import classify_page, inspect_font, investigate_pdf
from scripts.ingest_pilot_textbooks import PILOT_BOOKS
from scripts.investigate_pdf_text_layer import run


def _pdf(path: Path, pages: int = 1) -> Path:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=612, height=792)
    with path.open("wb") as stream:
        writer.write(stream)
    return path


def test_unicode_text_page_classification() -> None:
    result, evidence = classify_page(
        extracted_text="English and తెలుగు Unicode text", has_text_operators=True,
        image_count=0, missing_to_unicode=False,
    )
    assert result == "unicode_text"
    assert evidence


def test_non_unicode_glyph_page_classification_and_private_use_detection() -> None:
    result, evidence = classify_page(
        extracted_text="\ue001\ue002", has_text_operators=True,
        image_count=0, missing_to_unicode=True,
    )
    assert result == "non_unicode_glyph_text"
    assert any("private-use" in item for item in evidence)


def test_malformed_replacement_character_classification() -> None:
    result, evidence = classify_page(
        extracted_text="bad \ufffd mapping", has_text_operators=True,
        image_count=0, missing_to_unicode=True,
    )
    assert result == "non_unicode_glyph_text"
    assert any("replacement" in item for item in evidence)


def test_image_only_page_classification() -> None:
    result, _ = classify_page(
        extracted_text="", has_text_operators=False, image_count=1,
        missing_to_unicode=False,
    )
    assert result == "image_only"


def test_hybrid_page_classification() -> None:
    result, _ = classify_page(
        extracted_text="Selectable text", has_text_operators=True, image_count=1,
        missing_to_unicode=False,
    )
    assert result == "hybrid_text_and_image"


def test_missing_to_unicode_font_detection() -> None:
    finding = inspect_font("/F1", {
        "/BaseFont": "/SyntheticFont",
        "/Subtype": "/Type0",
        "/Encoding": "/Identity-H",
    })
    assert finding.has_to_unicode is False
    assert finding.subtype == "/Type0"


def test_extractor_comparison_result_structure(tmp_path: Path) -> None:
    report = investigate_pdf(_pdf(tmp_path / "synthetic.pdf"))
    comparison = report["extractor_comparison"]
    assert comparison["pypdf"]["available"] is True
    assert comparison["pymupdf"]["available"] is False
    assert "elapsed_seconds" in comparison["pypdf"]


def test_duplicate_aliases_are_not_analysed_as_separate_textbooks(tmp_path: Path) -> None:
    for index, book in enumerate(PILOT_BOOKS, 1):
        _pdf(tmp_path / book.canonical_filename, pages=index)
        shutil.copyfile(tmp_path / book.canonical_filename, tmp_path / book.alternate_filename)
    report = run(tmp_path)
    assert report["unique_pdfs_investigated"] == 2
    assert report["duplicate_aliases_analysed_separately"] is False
    assert len(report["textbooks"]) == 2


def test_report_contains_no_extracted_source_text(tmp_path: Path) -> None:
    report = investigate_pdf(_pdf(tmp_path / "copyright-safe.pdf"))
    json.dumps(report)
    assert all("text" not in page and "excerpt" not in page for page in report["pages"])
    assert report["diagnostic_sample_pages"]["contains_excerpts"] is False


def test_diagnostics_do_not_modify_existing_textbook_ids(tmp_path: Path) -> None:
    for index, book in enumerate(PILOT_BOOKS, 1):
        _pdf(tmp_path / book.canonical_filename, pages=index)
        shutil.copyfile(tmp_path / book.canonical_filename, tmp_path / book.alternate_filename)
    run(tmp_path)
    script = Path("scripts/investigate_pdf_text_layer.py").read_text(encoding="utf-8")
    assert "JsonTextbookRepository" not in script
    assert "TextbookIngestionService" not in script
