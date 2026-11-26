#!/usr/bin/env python3
"""Zip plugin/ for a human to upload. Does not submit anywhere."""

from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "plugin"
DEST = ROOT / "dist" / "sequence-circuit-plugin.zip"
SKIP = {".DS_Store"}


def main() -> None:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(DEST, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in SRC.rglob("*"):
            if not path.is_file() or path.name in SKIP:
                continue
            zf.write(path, arcname=str(path.relative_to(SRC)))
    print(DEST, DEST.stat().st_size)


if __name__ == "__main__":
    main()
