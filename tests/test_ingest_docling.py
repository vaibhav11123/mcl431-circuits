"""Optional live Docling smoke. Skips when the ingest extra is not installed."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytest.importorskip("docling")

from circuit.ingest_run import run_ingest  # noqa: E402


def test_ingest_one_page_pdf(tmp_path: Path) -> None:
    import pymupdf as fitz

    root = tmp_path / "repo"
    (root / "exams" / "pyqs").mkdir(parents=True)
    (root / "exams" / "index.yaml").write_text("version: 1\nquestions: []\n")
    pdf = root / "exams" / "pyqs" / "smoke_q1.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Q1 Cylinder 1A+ [30 Marks]")
    doc.save(pdf)
    doc.close()

    code = run_ingest(root, pdf)
    assert code in (0, 3)
    dest = root / "exams" / "ingest" / "smoke_q1"
    assert dest.is_dir()
    manifest = yaml.safe_load((dest / "manifest.yaml").read_text())
    import hashlib

    h = hashlib.sha256(pdf.read_bytes()).hexdigest()
    assert manifest["sha256"] == h
    draft = yaml.safe_load((dest / "draft.yaml").read_text())
    tokens = []
    for q in draft.get("questions") or []:
        tokens.extend(q.get("sequence_tokens") or [])
    assert "1A+" in tokens
    assert draft["kind"] == "ingest_draft"
