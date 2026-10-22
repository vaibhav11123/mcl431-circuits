"""Optional Mac-only page OCR. Skips on Linux CI without ocrmac."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("ocrmac")

if sys.platform != "darwin":
    pytest.skip("ocrmac page OCR is Darwin-only", allow_module_level=True)

from circuit.ingest_extract import rules_check
from circuit.ingest_ocr_pages import notes_raster_dir, ocr_page_rasters

ROOT = Path(__file__).resolve().parents[1]


def test_ocr_notes_rasters_improve_phrase_recall() -> None:
    stem = "DOC-20260908-WA0000_compressed"
    raster = notes_raster_dir(ROOT, stem)
    if raster is None:
        pytest.skip("lecture notes page rasters not present locally")
    extra = ocr_page_rasters(ROOT, stem)
    assert extra.strip(), "ocrmac returned empty text"
    # Docling-alone miss for FRL/exhaust; union with page OCR should hit synonyms.
    docling_only = "Nominature 5/2 valve. current paths."
    rows = rules_check(docling_only, extra_text=extra)
    statuses = {r["phrase"]: r["status"] for r in rows}
    assert statuses["5/2"] in ("found", "found_synonym")
    assert statuses["FRL"] in ("found", "found_synonym")
    assert statuses["exhaust"] in ("found", "found_synonym")
    assert statuses["4/2"] in ("found", "found_synonym")
