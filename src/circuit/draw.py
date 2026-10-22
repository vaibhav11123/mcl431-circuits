"""Lecture-locked drawings: stamp catalog glyphs, wire the ports."""

from __future__ import annotations

from pathlib import Path

from circuit.calc import plc_2023_q2_scaling, solution_lines_for
from circuit.draw_electrical import draw_electrical
from circuit.draw_hydraulic import draw_hydraulic
from circuit.draw_phase import draw_phase
from circuit.draw_plc import draw_plc_connection, draw_plc_ladder
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
    "draw_plc_connection",
    "draw_plc_ladder",
    "write_solution",
]


def _write_plc_solution(spec: CircuitSpec, dest: Path) -> Path:
    lines = [spec.meta.title, "", "I/O"]
    if spec.plc:
        for row in spec.plc.io:
            lines.append(f"  {row.address}  {row.device}  — {row.function}")
    lines += ["", "Calculations / notes"]
    lines.extend(f"  {ln}" for ln in solution_lines_for(spec.meta.exam_id))
    if spec.meta.exam_id == "2023_minor2_q2":
        sc = plc_2023_q2_scaling()
        lines += [
            "",
            "Zone table (nearest integer counts)",
            f"  W < 220 kg          AI < {sc['ai_220_cmp']}     1185 RPM   AO {sc['ao_1185']}   L1",
            f"  220 ≤ W ≤ 580 kg    AI {sc['ai_220_cmp']}–{sc['ai_580']}   2250 RPM   AO {sc['ao_2250']}   L2",
            f"  W > 580 kg          AI > {sc['ai_580']}    3545 RPM   AO {sc['ao_3545']}   L3",
            "  /RUN → MOV 0 AO  (must zero the speed-controller voltage on STOP)",
        ]
    if spec.plc and spec.plc.notes:
        lines += ["", "Ladder notes"]
        lines.extend(f"  {n}" for n in spec.plc.notes)
    lines += ["", "Components", "  PLC sheet — no hydraulic pump/valves"]
    dest.write_text("\n".join(lines) + "\n")
    return dest


def write_solution(spec: CircuitSpec, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if spec.meta.domain == Domain.PLC:
        return _write_plc_solution(spec, dest)
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
    if spec.meta.exam_id == "2023_minor2_q1":
        lines += [
            "",
            "Step table (enabling condition → solenoid)",
            "  1  1A+ hold     S1∧S3∧1B1∧2B2 → 1Y1",
            "  2  2A− retract  1B2 → 2Y2",
            "  3  1A− release  2B1 → 1Y2",
            "  4  2A+ return   1B1 → 2Y1",
            "  H1 to press when 2B1∧1B1 (after step 3; 2A still back)",
            "",
            "Electrical notes (L8)",
            "  S1 main switch latched on K1; S3 is the punch-up start, not JOB",
            "  Two 5/2 double-solenoid valves (L10 p5); not 5/3",
        ]
    if spec.meta.exam_id == "2016_minor1_emboss":
        lines += [
            "",
            "Step table (enabling condition → solenoid)",
            "  start  S1∧S0∧1B1∧2B1 → K1",
            "  1  1A1+ clamp     K1 → 1Y1",
            "  2  2A1+ emboss    1B2 → K3 → 2Y1",
            "  3  HOLD           PS≥4 bar → K4  (not 2B2)",
            "  4  2A1− retract   K4 → 2Y2",
            "  5  1A1− unclamp   K4∧2B1 → K5 → 1Y2",
            "",
            "Electrical notes (L8)",
            "  Two 5/2 double-solenoid valves; not closed-centre 5/3",
            "  PS on the 2A1+ cap line; 2B2 is position only",
            "  1Y2 is K5, not a raw 2B1 (2B1 is already true at rest)",
        ]
    if spec.meta.exam_id in {"Fall17-Minor2", "MCL431_Minor2_2017-18_Sem1"}:
        lines += [
            "",
            "Positions from 1A/2A end sensors (no extra table sensors)",
            "  P1 = 1B1∧2B1   P2 = 1B2∧2B1   P3 = 1B2∧2B2   P4 = 1B1∧2B2",
            "",
            "Step table (enabling condition → solenoid)",
            "  1  drill1↓   START∧S0∧1B1∧2B1∧3B1 → 3Y1",
            "  2  drill1↑   3B2 → 3Y2",
            "  3  index1→2  3B1 → 1Y1",
            "  4  drill2↓   1B2∧2B1∧3B1 → 3Y1",
            "  5  drill2↑   3B2 → 3Y2",
            "  6  index2→3  3B1 → 2Y1",
            "  7  drill3↓   1B2∧2B2∧3B1 → 3Y1",
            "  8  drill3↑   3B2 → 3Y2",
            "  9  index3→4  3B1 → 1Y2",
            "  10 drill4↓   1B1∧2B2∧3B1 → 3Y1",
            "  11 drill4↑   3B2 → 3Y2",
            "  12 return4→1 3B1 → 2Y2",
            "",
            "Electrical notes (L8)",
            "  K1 = cycle (START∧S0∧homes), not B1-style K2/K3/K4",
            "  K2–K13 = the 12 motions; each holds until the next step (!K{n+1})",
            "  K14 = done (K13∧2B1) and drops K1",
            "  KM = K1 ∧ !K13 (paper: ON from start, OFF after holes / at return)",
            "  Closed-centre ISO 1219 5/3 so the table holds when both solenoids are off",
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
    if spec.meta.domain == Domain.PLC:
        written = {
            "solution": write_solution(spec, out_dir / "solution.txt"),
            "connection": draw_plc_connection(spec, out_dir / "plc_connection.svg"),
            "ladder": draw_plc_ladder(spec, out_dir / "plc_ladder.svg"),
        }
        from circuit.png import svg_to_png

        pngs: dict[str, Path] = {}
        for key in ("connection", "ladder"):
            png = svg_to_png(written[key])
            if png is not None:
                pngs[f"{key}_png"] = png
        if not pngs:
            print("PNG skipped: install librsvg or use macOS")
        written.update(pngs)
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
