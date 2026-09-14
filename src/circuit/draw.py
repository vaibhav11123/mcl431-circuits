"""Lecture-locked drawings: stamp catalog glyphs, wire the ports."""

from __future__ import annotations

from pathlib import Path

from circuit.calc import solution_lines_for
from circuit.draw_electrical import draw_electrical
from circuit.draw_hydraulic import draw_hydraulic
from circuit.draw_phase import draw_phase
from circuit.draw_pneumatic import draw_pneumatic
from circuit.spec import CircuitSpec, Domain
from circuit.svgdraw import SVG

__all__ = [
    "draw_all",
    "draw_calc_only",
    "draw_electrical",
    "draw_hydraulic",
    "draw_phase",
    "draw_pneumatic",
    "write_solution",
]


def write_solution(spec: CircuitSpec, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    lines = [spec.meta.title, "", "Sequence"]
    for i, step in enumerate(spec.sequence, 1):
        extra = f" ({step.seconds} s)" if step.seconds else ""
        lines.append(f"  {i}. {step.action}{extra} — {step.label}")
    lines += ["", "Calculations (lecture forms; no invented Q)"]
    lines.extend(f"  {ln}" for ln in solution_lines_for(spec.meta.exam_id))
    if spec.meta.exam_id == "2023_selfstudy_b1":
        lines += [
            "",
            "Electrical notes (L8)",
            "  2Y1 = K2 AND 2B1 (latched on K3), not K1",
            "  HM1 OFF at T1 (K4) before HC2 retracts",
            "  1Y1 NC-interlocked with K4; 2Y1 NC-interlocked with K4 / K3",
        ]
    lines += ["", "Components"]
    for p in spec.power.pumps:
        lines.append(f"  pump {p.id}")
    for r in spec.power.relief_valves:
        lines.append(f"  relief {r.id}")
    for cid, cyl in spec.cylinders.items():
        bore = "not_given" if cyl.bore_mm is None else cyl.bore_mm
        rod = "not_given" if cyl.rod_mm is None else cyl.rod_mm
        lines.append(f"  {cid} bore {bore} rod {rod} dcv {cyl.dcv}")
    for mid, mot in spec.motors.items():
        lines.append(f"  {mid} rpm {mot.rpm} dcv {mot.dcv}")
    dest.write_text("\n".join(lines) + "\n")
    return dest


def draw_calc_only(spec: CircuitSpec, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    s = SVG(820, 220)
    s.text(410, 70, spec.meta.title, 16)
    s.text(410, 110, "Figure given on the paper — calc only", 14)
    s.text(410, 150, spec.meta.exam_id or "", 12)
    dest.write_text(s.tostring())
    return dest


def draw_all(spec: CircuitSpec, out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    if spec.meta.figure_given:
        written = {
            "calc": draw_calc_only(spec, out_dir / "calc_only.svg"),
            "solution": write_solution(spec, out_dir / "solution.txt"),
        }
        from circuit.png import svg_to_png

        png = svg_to_png(written["calc"])
        if png is not None:
            written["calc_png"] = png
        return written
    ep = spec.meta.domain in {
        Domain.HYDRAULIC_PLUS_ELECTRICAL,
        Domain.PNEUMATIC_PLUS_ELECTRICAL,
    }
    pneu = spec.meta.domain in {Domain.PNEUMATIC, Domain.PNEUMATIC_PLUS_ELECTRICAL}
    written: dict[str, Path] = {
        "solution": write_solution(spec, out_dir / "solution.txt"),
    }
    if ep:
        written["electrical"] = draw_electrical(spec, out_dir / "electrical_circuit.svg")
        written["phase"] = draw_phase(spec, out_dir / "step_displacement.svg")
    if pneu:
        written["pneumatic"] = draw_pneumatic(spec, out_dir / "pneumatic_circuit.svg")
    else:
        written["hydraulic"] = draw_hydraulic(spec, out_dir / "hydraulic_circuit.svg")
    from circuit.png import svg_to_png

    pngs: dict[str, Path] = {}
    for key in ("hydraulic", "pneumatic", "electrical", "phase"):
        if key not in written:
            continue
        png = svg_to_png(written[key])
        if png is not None:
            pngs[f"{key}_png"] = png
    if not pngs:
        print("PNG skipped: install librsvg or use macOS")
    written.update(pngs)
    return written
