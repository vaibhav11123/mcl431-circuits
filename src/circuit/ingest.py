"""Local Docling ingest — exam and lecture drafts. Lazy-imported by the CLI."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def require_docling() -> bool:
    try:
        import docling  # noqa: F401
    except ImportError:
        print("pip install -e '.[ingest]'", file=sys.stderr)
        return False
    return True


def ingest_path(root: Path, path: Path, *, formula: bool = False, no_ocr: bool = False) -> int:
    """Convert one local file. Returns exit code 0/1/2/3/4."""
    if not require_docling():
        return 2
    # Full converter lands in later commits; keep CLI wiring green until then.
    from circuit.ingest_run import run_ingest

    return run_ingest(root, path, formula=formula, no_ocr=no_ocr)


def main(root: Path, paths: list[Path], *, formula: bool = False, no_ocr: bool = False) -> int:
    if not paths:
        print("usage: python -m circuit ingest <local pdf|jpeg|png|tif>", file=sys.stderr)
        return 1
    code = 0
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            files = sorted(
                p
                for p in path.iterdir()
                if p.suffix.lower() in {".pdf", ".jpeg", ".jpg", ".png", ".tif", ".tiff"}
            )
            if not files:
                print(f"no ingestible files in {path}", file=sys.stderr)
                code = max(code, 1)
                continue
            for f in files:
                code = max(code, ingest_path(root, f, formula=formula, no_ocr=no_ocr))
        else:
            code = max(code, ingest_path(root, path, formula=formula, no_ocr=no_ocr))
    return code
