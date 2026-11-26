#!/usr/bin/env python3
"""Copy the ISO-safe circuit package into web/circuit and zip it for Pyodide."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "circuit"
DEST = ROOT / "web" / "circuit"
ZIP_PATH = ROOT / "web" / "circuit-iso.zip"

SKIP_NAMES = {
    "ingest.py",
    "ingest_extract.py",
    "ingest_index.py",
    "ingest_ocr_pages.py",
    "ingest_promote.py",
    "ingest_run.py",
    "rasterize.py",
    "png.py",
    "export_pack.py",
    "mcp_server.py",
    "web_server.py",
    "cli.py",
    "lecture_connect.py",
    "__main__.py",
}


def main() -> None:
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    for path in SRC.rglob("*"):
        rel = path.relative_to(SRC)
        if any(part.startswith(".") for part in rel.parts):
            continue
        if path.is_dir():
            continue
        if path.name in SKIP_NAMES or path.name.startswith("ingest_"):
            continue
        if path.suffix not in {".py", ".yaml", ".png", ".svg", ".txt", ".md"}:
            continue
        target = DEST / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in DEST.rglob("*"):
            if path.is_file():
                zf.write(path, arcname=str(Path("circuit") / path.relative_to(DEST)))
    print(DEST, "files", sum(1 for _ in DEST.rglob("*.py")))
    print(ZIP_PATH, ZIP_PATH.stat().st_size)


if __name__ == "__main__":
    main()
