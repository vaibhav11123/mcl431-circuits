"""SVG → PNG. Prefer rsvg/resvg; else macOS Quick Look; else cairosvg if cairo loads."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


def backend_name() -> str | None:
    if shutil.which("rsvg-convert"):
        return "rsvg-convert"
    if shutil.which("resvg"):
        return "resvg"
    if shutil.which("qlmanage"):
        return "qlmanage"
    try:
        import cairosvg  # noqa: F401

        return "cairosvg"
    except Exception:
        return None


def svg_to_png(svg_path: Path, dest: Path | None = None) -> Path | None:
    """Write dest (default: same stem .png). Returns None if no backend exists."""
    svg_path = Path(svg_path)
    dest = Path(dest) if dest is not None else svg_path.with_suffix(".png")
    name = backend_name()
    if name is None:
        return None
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        if name == "rsvg-convert":
            subprocess.run(
                ["rsvg-convert", "-o", str(dest), str(svg_path)],
                check=True,
                capture_output=True,
            )
        elif name == "resvg":
            subprocess.run(
                ["resvg", str(svg_path), str(dest)],
                check=True,
                capture_output=True,
            )
        elif name == "qlmanage":
            with tempfile.TemporaryDirectory() as tmp:
                subprocess.run(
                    ["qlmanage", "-t", "-s", "1680", "-o", tmp, str(svg_path)],
                    check=True,
                    capture_output=True,
                )
                produced = list(Path(tmp).glob("*.png"))
                if not produced:
                    return None
                dest.write_bytes(produced[0].read_bytes())
        else:
            import cairosvg

            cairosvg.svg2png(url=str(svg_path), write_to=str(dest))
    except (subprocess.CalledProcessError, OSError, ImportError):
        return None
    return dest if dest.is_file() and dest.stat().st_size > 0 else None
