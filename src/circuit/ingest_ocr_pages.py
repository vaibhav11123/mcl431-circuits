"""Optional second-pass OCR over lecture page rasters (Darwin + ocrmac)."""

from __future__ import annotations

from pathlib import Path


def notes_raster_dir(root: Path, source_stem: str) -> Path | None:
    """Return lecture/notes_<hint>/ if it contains page PNGs for this stem."""
    lecture = root / "lecture"
    if not lecture.is_dir():
        return None
    # Common layout: lecture/notes_wa0000/DOC-..._p01.png
    candidates: list[Path] = []
    for d in sorted(lecture.glob("notes_*")):
        if not d.is_dir():
            continue
        pngs = list(d.glob(f"{source_stem}_p*.png")) + list(d.glob("*_p*.png"))
        if pngs:
            candidates.append(d)
    if not candidates:
        return None
    # Prefer a dir whose filenames include the stem.
    for d in candidates:
        if list(d.glob(f"{source_stem}_p*.png")):
            return d
    return candidates[0]


def ocr_page_rasters(root: Path, source_stem: str) -> str:
    """OCR page PNGs with ocrmac when available; else empty string.

    Never raises for missing ocrmac — CI/Linux stay on Docling-only synonyms.
    """
    try:
        from ocrmac import ocrmac  # type: ignore
    except ImportError:
        return ""

    raster_dir = notes_raster_dir(root, source_stem)
    if raster_dir is None:
        return ""

    pages = sorted(raster_dir.glob(f"{source_stem}_p*.png"))
    if not pages:
        pages = sorted(raster_dir.glob("*_p*.png"))
    if not pages:
        return ""

    chunks: list[str] = []
    for path in pages:
        try:
            anns = ocrmac.OCR(str(path), recognition_level="accurate").recognize()
        except Exception:
            continue
        texts = []
        for a in anns:
            if isinstance(a, (list, tuple)) and a:
                texts.append(str(a[0]))
            else:
                texts.append(str(a))
        chunks.append(" ".join(texts))
    return "\n".join(chunks)
