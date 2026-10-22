"""Docling conversion + bundle write. Imported only after require_docling()."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

from circuit.ingest_extract import (
    apply_rules_extra_text,
    build_draft,
    format_rules_check,
    is_quarantine,
)
from circuit.ingest_index import diff_row, format_diff, match
from circuit.ingest_ocr_pages import ocr_page_rasters
from circuit.rasterize import _safe_stem

IMAGE_SUFFIXES = {".jpeg", ".jpg", ".png", ".tif", ".tiff"}
PDF_SUFFIXES = {".pdf"}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _docling_version() -> str:
    try:
        import docling

        return getattr(docling, "__version__", "unknown")
    except Exception:
        return "unknown"


def _bundle_dir(root: Path, path: Path) -> Path:
    stem = _safe_stem(path.stem)
    try:
        rel = path.resolve().relative_to(root.resolve())
    except ValueError:
        rel = path
    parts = rel.parts
    if parts and parts[0] == "lecture":
        return root / "lecture" / "ingest" / stem
    if parts and parts[0] == "exams":
        return root / "exams" / "ingest" / stem
    # Heuristic: under lecture path string
    if "lecture" in str(path):
        return root / "lecture" / "ingest" / stem
    return root / "exams" / "ingest" / stem


def _is_lecture(root: Path, path: Path, dest: Path) -> bool:
    return "lecture" in dest.parts


def _pdf_has_text_layer(path: Path) -> bool:
    try:
        import pymupdf as fitz

        doc = fitz.open(path)
        try:
            for page in doc:
                if (page.get_text("text") or "").strip():
                    return True
        finally:
            doc.close()
    except Exception:
        return False
    return False


def _make_converter(*, do_ocr: bool, formula: bool, use_ocrmac: bool):
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    opts = PdfPipelineOptions(
        do_ocr=do_ocr,
        do_table_structure=True,
        do_formula_enrichment=formula,
        generate_page_images=False,
        generate_picture_images=False,
        document_timeout=120,
    )
    if do_ocr and use_ocrmac:
        try:
            from docling.datamodel.pipeline_options import OcrMacOptions

            opts.ocr_options = OcrMacOptions()
        except Exception:
            pass  # fall back to library default

    format_options: dict[Any, Any] = {
        InputFormat.PDF: PdfFormatOption(pipeline_options=opts),
    }
    # Image format uses defaults; OCR applies via image pipeline.
    return DocumentConverter(
        allowed_formats=[InputFormat.PDF, InputFormat.IMAGE],
        format_options=format_options,
    )


def _write_manifest(
    dest: Path,
    *,
    source: Path,
    sha: str,
    page_count: int,
    exit_code: int,
    pipeline: str = "standard",
    note: str = "",
) -> None:
    data = {
        "source": str(source),
        "sha256": sha,
        "docling_version": _docling_version(),
        "pipeline": pipeline,
        "page_count": page_count,
        "exit_code": exit_code,
    }
    if note:
        data["note"] = note
    (dest / "manifest.yaml").write_text(yaml.safe_dump(data, sort_keys=False))


def run_ingest(
    root: Path,
    path: Path,
    *,
    formula: bool = False,
    no_ocr: bool = False,
) -> int:
    path = path.expanduser()
    if str(path).startswith("http://") or str(path).startswith("https://"):
        print("ingest accepts a local path only", file=sys.stderr)
        return 1
    if not path.is_file():
        print(f"missing file: {path}", file=sys.stderr)
        return 1

    suffix = path.suffix.lower()
    if suffix not in PDF_SUFFIXES | IMAGE_SUFFIXES:
        print(f"unsupported type: {suffix}", file=sys.stderr)
        return 1

    sha = _sha256(path)
    dest = _bundle_dir(root, path)
    lecture = _is_lecture(root, path, dest)

    # OCR policy: images/scan PDFs use ocrmac; text-layer PDFs skip OCR.
    use_ocr = True
    use_ocrmac = False
    if no_ocr:
        use_ocr = False
    elif suffix in IMAGE_SUFFIXES:
        use_ocrmac = True
    elif suffix in PDF_SUFFIXES:
        if _pdf_has_text_layer(path):
            use_ocr = False
        else:
            use_ocrmac = True

    try:
        converter = _make_converter(do_ocr=use_ocr, formula=formula, use_ocrmac=use_ocrmac)
        result = converter.convert(str(path))
    except Exception as exc:
        print(f"docling convert failed: {exc}", file=sys.stderr)
        return 1

    status = getattr(result, "status", None)
    status_name = getattr(status, "name", str(status)) if status is not None else "success"
    if status is not None and status_name.lower() not in {"success", "partial_success"}:
        print(f"docling status: {status_name}", file=sys.stderr)
        return 1

    doc = result.document
    try:
        markdown = doc.export_to_markdown()
    except Exception as exc:
        print(f"export_to_markdown failed: {exc}", file=sys.stderr)
        return 1
    try:
        doc_dict = doc.export_to_dict()
    except Exception as exc:
        print(f"export_to_dict failed: {exc}", file=sys.stderr)
        return 1

    page_count = len(getattr(doc, "pages", None) or doc_dict.get("pages") or []) or 1

    with tempfile.TemporaryDirectory(prefix="circuit-ingest-") as tmp:
        tmp_dir = Path(tmp) / dest.name
        tmp_dir.mkdir()
        (tmp_dir / "source.path").write_text(str(path.resolve()) + "\n")

        if is_quarantine(markdown, page_count):
            _write_manifest(
                tmp_dir,
                source=path,
                sha=sha,
                page_count=page_count,
                exit_code=4,
                note="quarantine: markdown shorter than 40 chars per page",
            )
            (tmp_dir / "quarantine.txt").write_text(
                f"page_count={page_count}\n"
                f"markdown_chars={len((markdown or '').strip())}\n"
                f"threshold={40 * page_count}\n"
                "No draft written.\n"
            )
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(tmp_dir, dest)
            print(f"quarantine: {dest}")
            return 4

        (tmp_dir / "document.md").write_text(markdown or "")
        (tmp_dir / "document.json").write_text(json.dumps(doc_dict, indent=2))

        kind = "lecture_notes_draft" if lecture else "ingest_draft"
        draft = build_draft(
            source=path.name,
            markdown=markdown or "",
            docling_dict=doc_dict,
            kind=kind,
            page_count=page_count,
        )

        exit_code = 0
        if not lecture:
            rows = match(root, path.name)
            results = [diff_row(root, row, draft) for row in rows]
            draft["index_matches"] = [
                {
                    "id": r["id"],
                    "facts": r["facts"],
                    "status": r["status"],
                    "ok": r["ok"],
                }
                for r in results
            ]
            diff_text = format_diff(results)
            (tmp_dir / "diff.txt").write_text(diff_text)
            if any(r["status"] == "locked" and not r["ok"] for r in results):
                exit_code = 3
        else:
            figures = draft.get("figures") or []
            (tmp_dir / "figures.yaml").write_text(
                yaml.safe_dump(figures, sort_keys=False)
            )
            extra = ocr_page_rasters(root, _safe_stem(path.stem))
            if extra.strip():
                (tmp_dir / "pages.ocr.md").write_text(extra)
                draft = apply_rules_extra_text(draft, markdown or "", extra)
            rules = draft.get("rules_check") or []
            (tmp_dir / "rules.check.txt").write_text(format_rules_check(rules))

        (tmp_dir / "draft.yaml").write_text(yaml.safe_dump(draft, sort_keys=False))
        _write_manifest(
            tmp_dir,
            source=path,
            sha=sha,
            page_count=page_count,
            exit_code=exit_code,
        )

        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(tmp_dir, dest)

    print(f"wrote {dest} (exit {exit_code})")
    return exit_code
