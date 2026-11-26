"""Print pack: SVG/PNG/PDF/BOM/principle plus a chat preview downscale."""

from __future__ import annotations

import io
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

from circuit.compile_sequence import _solenoid_for
from circuit.png import svg_to_png
from circuit.spec import CircuitSpec


def preview_png(print_png_path: Path | str) -> bytes:
    im = Image.open(print_png_path).convert("RGB")
    w, h = im.size
    if w > 800:
        h = int(h * 800 / w)
        w = 800
        im = im.resize((w, h), Image.Resampling.LANCZOS)
    quality = 85
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    data = buf.getvalue()
    while len(data) > 200_000 and quality > 30:
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=quality, optimize=True)
        data = buf.getvalue()
        quality -= 10
        if len(data) <= 200_000:
            png_buf = io.BytesIO()
            Image.open(io.BytesIO(data)).convert("RGB").save(png_buf, format="PNG", optimize=True)
            if len(png_buf.getvalue()) <= 200_000:
                data = png_buf.getvalue()
            else:
                data = data  # keep jpeg bytes under cap
            break
    if len(data) > 200_000:
        im = im.resize((max(1, w // 2), max(1, h // 2)), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="PNG", optimize=True)
        data = buf.getvalue()
    return data


def bom_text(spec: CircuitSpec) -> str:
    lines = []
    for vid, valve in spec.valves.items():
        lines.append(f"{vid}  {valve.type}  {','.join(valve.solenoids)}")
    for cid, cyl in spec.cylinders.items():
        lines.append(f"{cid}  dcv {cyl.dcv}")
    for s in spec.sensors:
        lines.append(f"sensor {s}")
    return "\n".join(lines) + "\n"


def principle_text(spec: CircuitSpec) -> str:
    lines = []
    for i, step in enumerate(spec.sequence, 1):
        sol = _solenoid_for(spec, step.action) or "—"
        lines.append(f"Step {i}: {step.action} ({step.label}) drives {sol}.")
    return "\n".join(lines) + "\n"


def _svg_to_pdf(svg_path: Path) -> bytes | None:
    rsvg = shutil.which("rsvg-convert")
    if not rsvg:
        return None
    out = Path(tempfile.mkstemp(suffix=".pdf")[1])
    try:
        proc = subprocess.run(
            [rsvg, "-f", "pdf", "-o", str(out), str(svg_path)],
            check=False,
            capture_output=True,
        )
        if proc.returncode != 0 or not out.is_file():
            return None
        data = out.read_bytes()
        return data if data.startswith(b"%PDF") else None
    finally:
        out.unlink(missing_ok=True)


def merge_pdfs(blobs: list[bytes]) -> bytes | None:
    if not blobs:
        return None
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        return blobs[0]
    writer = PdfWriter()
    for blob in blobs:
        reader = PdfReader(io.BytesIO(blob))
        for page in reader.pages:
            writer.add_page(page)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def pack_files_from_draw(
    spec: CircuitSpec,
    sheets: dict[str, str],
    written: dict,
    sentence: str,
    report_svg: str,
) -> dict[str, bytes | str]:
    files: dict[str, bytes | str] = {}
    pdf_blobs: list[bytes] = []
    mapping = {
        "pneumatic": "pneumatic_svg",
        "electrical": "electrical_svg",
        "phase": "phase_svg",
        "hydraulic": "hydraulic_svg",
        "connection": "connection_svg",
        "ladder": "ladder_svg",
        "calc": "calc_svg",
    }
    tmpdir = Path(tempfile.mkdtemp(prefix="circuit-pack-"))
    try:
        for src_key, dst_key in mapping.items():
            if src_key not in sheets:
                continue
            files[dst_key] = sheets[src_key]
            svg_path = tmpdir / f"{src_key}.svg"
            svg_path.write_text(sheets[src_key], encoding="utf-8")
            png = svg_to_png(svg_path)
            if png is not None:
                files[f"{src_key}_png"] = png.read_bytes()
            blob = _svg_to_pdf(svg_path)
            if blob:
                pdf_blobs.append(blob)
        files["bom"] = bom_text(spec)
        files["principle"] = principle_text(spec)
        files["report"] = report_svg
        merged = merge_pdfs(pdf_blobs)
        if merged:
            files["pdf"] = merged
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    return files
