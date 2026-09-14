"""SVG → PNG. Prefer rsvg/resvg; else macOS Quick Look; else cairosvg if cairo loads.

qlmanage -t always emits a square thumbnail and scale-to-fills. A landscape
sheet (hydraulic 1680×800) is cropped on the right unless we pad to a square
first and crop the PNG back to the SVG aspect ratio.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

_SVG_WH = re.compile(
    r"<svg\b[^>]*?\bwidth=['\"]([\d.]+)[^\"]*['\"][^>]*?\bheight=['\"]([\d.]+)",
    re.I | re.S,
)
_SVG_WH_SWAP = re.compile(
    r"<svg\b[^>]*?\bheight=['\"]([\d.]+)[^\"]*['\"][^>]*?\bwidth=['\"]([\d.]+)",
    re.I | re.S,
)
_VIEWBOX = re.compile(
    r'viewBox=["\']\s*[-\d.]+\s+[-\d.]+\s+([\d.]+)\s+([\d.]+)',
    re.I,
)


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


def svg_size(svg_path: Path | str) -> tuple[float, float]:
    """Canvas width, height from the root <svg> (viewBox as fallback)."""
    head = Path(svg_path).read_text(encoding="utf-8")[:4000]
    m = _SVG_WH.search(head)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = _SVG_WH_SWAP.search(head)
    if m:
        return float(m.group(2)), float(m.group(1))
    m = _VIEWBOX.search(head)
    if m:
        return float(m.group(1)), float(m.group(2))
    return 1680.0, 800.0


def _crop_to_aspect(im: Image.Image, width: float, height: float) -> Image.Image:
    """Keep the top-left of a square thumbnail so landscape sheets are not clipped."""
    pw, ph = im.size
    if width <= 0 or height <= 0:
        return im
    src_aspect = width / height
    out_w, out_h = pw, ph
    if pw / ph > src_aspect:
        out_w = max(1, round(ph * src_aspect))
    else:
        out_h = max(1, round(pw / src_aspect))
    return im.crop((0, 0, out_w, out_h))


def _qlmanage_to_png(svg_path: Path, dest: Path) -> None:
    w, h = svg_size(svg_path)
    side = max(w, h)
    size = max(int(round(side)), 1680)
    original = svg_path.read_text(encoding="utf-8").strip()
    wrapped = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{side:.1f}" height="{side:.1f}">'
        f"{original}"
        f"</svg>\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        padded = Path(tmp) / f"{svg_path.stem}.svg"
        padded.write_text(wrapped, encoding="utf-8")
        subprocess.run(
            ["qlmanage", "-t", "-s", str(size), "-o", tmp, str(padded)],
            check=True,
            capture_output=True,
        )
        produced = list(Path(tmp).glob("*.png"))
        if not produced:
            raise OSError("qlmanage wrote no PNG")
        im = Image.open(produced[0])
        _crop_to_aspect(im, w, h).save(dest)


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
            _qlmanage_to_png(svg_path, dest)
        else:
            import cairosvg

            cairosvg.svg2png(url=str(svg_path), write_to=str(dest))
    except (subprocess.CalledProcessError, OSError, ImportError):
        return None
    return dest if dest.is_file() and dest.stat().st_size > 0 else None
