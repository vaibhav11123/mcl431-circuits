"""Lecture diagrams.yaml connect recipes — ports only, no invented nets."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DIAGRAMS = ROOT / "lecture" / "diagrams.yaml"


def connect_recipes(path: Path | None = None) -> dict:
    data = yaml.safe_load((path or DIAGRAMS).read_text()) or {}
    return data.get("connect") or {}
