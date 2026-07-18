"""Investigate the two unique bilingual pilot PDF text layers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.textbooks.pdf_ingestion import PdfInspector
from backend.app.textbooks.text_layer_diagnostics import investigate_pdf
from scripts.ingest_pilot_textbooks import PILOT_BOOKS, validate_source_directory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Diagnose bilingual pilot PDF text layers without OCR.")
    parser.add_argument("--source-directory", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, default=Path("backend/data/textbooks"))
    return parser


def run(source_directory: Path) -> dict[str, object]:
    paths = validate_source_directory(source_directory)
    textbooks = []
    for book in PILOT_BOOKS:
        canonical = paths[book.canonical_filename]
        alias = paths[book.alternate_filename]
        if PdfInspector._checksum(canonical) != PdfInspector._checksum(alias):
            raise ValueError(f"Source alias checksum mismatch for {book.book_part}")
        result = investigate_pdf(canonical, aliases=(book.alternate_filename,))
        result["book_part"] = book.book_part
        textbooks.append(result)
    return {
        "sprint": "4C.4",
        "status": "completed",
        "unique_pdfs_investigated": len(textbooks),
        "duplicate_aliases_analysed_separately": False,
        "textbooks": textbooks,
        "copyright_safety": "No extracted page text or excerpts are included",
        "ocr_calls": 0,
        "openai_calls": 0,
        "embeddings_generated": 0,
    }


def main() -> None:
    args = build_parser().parse_args()
    report = run(args.source_directory)
    output = args.output_directory.resolve()
    output.mkdir(parents=True, exist_ok=True)
    destination = output / "text-layer-investigation.json"
    temporary = destination.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(destination)
    print(json.dumps({
        "status": report["status"],
        "unique_pdfs_investigated": report["unique_pdfs_investigated"],
        "report": destination.name,
    }, indent=2))


if __name__ == "__main__":
    main()
