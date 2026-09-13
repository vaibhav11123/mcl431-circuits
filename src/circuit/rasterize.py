"""Render lecture and exam PDFs to PNG at a fixed DPI."""

from __future__ import annotations

from pathlib import Path

import pymupdf as fitz


def _safe_stem(name: str) -> str:
    return name.replace("[", "").replace("]", "").replace(" ", "_")


def render_pdf(pdf: Path, out_dir: Path, dpi: int) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    doc = fitz.open(pdf)
    try:
        zoom = dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)
        stem = _safe_stem(pdf.stem)
        for i, page in enumerate(doc, start=1):
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            dest = out_dir / f"{stem}_p{i:02d}.png"
            pix.save(dest)
            written.append(dest)
    finally:
        doc.close()
    return written


def copy_image(src: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{_safe_stem(src.stem)}_p01{src.suffix.lower()}"
    dest.write_bytes(src.read_bytes())
    return dest


def rasterize_all(root: Path, dpi: int = 200, only: str = "all") -> int:
    lecture_pdfs = sorted((root / "lecture").glob("*.pdf"))
    exam_pdfs = sorted((root / "exams" / "pyqs").glob("*.pdf"))
    exam_images = sorted((root / "exams" / "pyqs").glob("*.jpeg")) + sorted(
        (root / "exams" / "pyqs").glob("*.jpg")
    )

    written = 0
    if only in {"lecture", "all"}:
        dest = root / "lecture" / "pages"
        for pdf in lecture_pdfs:
            pages = render_pdf(pdf, dest, dpi)
            written += len(pages)
            print(f"lecture {pdf.name}: {len(pages)} pages")

    if only in {"exams", "all"}:
        dest = root / "exams" / "pages"
        for pdf in exam_pdfs:
            pages = render_pdf(pdf, dest, dpi)
            written += len(pages)
            print(f"exam {pdf.name}: {len(pages)} pages")
        for img in exam_images:
            copy_image(img, dest)
            written += 1
            print(f"exam {img.name}: 1 image")

    print(f"total rasters: {written}")
    return 0 if written else 1
