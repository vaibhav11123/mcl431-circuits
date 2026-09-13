"""Lecture-locked drawings: stamp catalog glyphs, wire the ports."""

from __future__ import annotations

from pathlib import Path

from circuit.calc import solution_lines_grinding
from circuit.catalog import stamp, stamp_dcv_4_3_closed
from circuit.compile_sequence import apply_compile
from circuit.spec import CircuitSpec
from circuit.svgdraw import SVG


def _hop_over(s: SVG, x: float, y: float, hop: float = 8) -> None:
    """ISO 1219: crossing without a junction — no filled dot."""
    s.polyline([(x, y - hop), (x + hop, y), (x, y + hop)])


def draw_hydraulic(spec: CircuitSpec, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    s = SVG(1680, 800)
    s.text(840, 22, spec.meta.title, 18)
    s.text(840, 42, "Hydraulic circuit  ·  lecture L2–L5 stamps  ·  de-energized", 12)

    px, py = 100, 620
    p_rail_y, t_rail_y = 450, 530

    pump = stamp(s, "pump_fixed", px, py, anchor="center")
    s.text(px + 48, py + 6, spec.power.pumps[0].id, 14, "start")
    filt = stamp(s, "filter", px, py + 62, anchor="center")
    tank = stamp(s, "tank", px, 742, anchor="center")
    s.text(px + 32, 748, "tank", 12, "start")
    s.line(pump["S"][0], pump["S"][1], filt["in"][0], filt["in"][1])
    s.line(filt["out"][0], filt["out"][1], tank["T"][0], tank["T"][1])
    s.line(pump["P"][0], pump["P"][1], px, p_rail_y)
    s.dot(px, p_rail_y)

    prv_id = spec.power.relief_valves[0].id if spec.power.relief_valves else "RV1"
    rvx, rvy = px + 130, py + 8
    prv = stamp(s, "prv", rvx, rvy, anchor="center")
    s.text(rvx, rvy - 46, prv_id, 12)
    s.line(px, p_rail_y, prv["P"][0], p_rail_y)
    s.dot(prv["P"][0], p_rail_y)
    s.line(prv["P"][0], p_rail_y, prv["P"][0], prv["P"][1])
    # L4: PRV.T returns to tank, not through the DCV T rail
    s.line(prv["T"][0], prv["T"][1], prv["T"][0], tank["T"][1])
    s.line(prv["T"][0], tank["T"][1], tank["T"][0], tank["T"][1])
    s.dot(prv["T"][0], tank["T"][1])
    s.line(px, tank["T"][1], px, t_rail_y)
    s.dot(px, t_rail_y)

    cols: list[tuple[str, object, list[str], str]] = []
    for cid, cyl in spec.cylinders.items():
        cols.append((cid, cyl, spec.valves[cyl.dcv].solenoids, "cyl"))
    for mid, mot in spec.motors.items():
        cols.append((mid, mot, spec.valves[mot.dcv].solenoids, "mot"))

    x0, span = 380, 420
    last_p, last_t = px, px
    for i, (name, obj, sols, kind) in enumerate(cols):
        cx = x0 + i * span
        ports = stamp_dcv_4_3_closed(s, cx, 300, obj.dcv, list(sols))
        s.text(ports["A"][0] - 12, ports["A"][1] - 6, "A", 10)
        s.text(ports["B"][0] + 12, ports["B"][1] - 6, "B", 10)
        s.text(ports["P"][0] - 12, ports["P"][1] + 14, "P", 10)
        s.text(ports["T"][0] + 12, ports["T"][1] + 14, "T", 10)

        if kind == "cyl":
            b1 = obj.sensors[0] if obj.sensors else "B1"
            b2 = obj.sensors[1] if len(obj.sensors) > 1 else "B2"
            cyl_w, cyl_h = 200.0, 80.0
            cports = stamp(s, "cylinder_l10", cx - 70, 58, cyl_w, cyl_h)
            s.text(cx - 86, 98, name, 13, "end")
            s.text(cports["cap"][0], 52, b1, 11)
            s.text(cports["rod"][0], 52, b2, 11)
            s.line(ports["A"][0], ports["A"][1], ports["A"][0], cports["cap"][1])
            s.line(ports["A"][0], cports["cap"][1], cports["cap"][0], cports["cap"][1])
            s.dot(*cports["cap"])
            jog_y = 200
            s.line(ports["B"][0], ports["B"][1], ports["B"][0], jog_y)
            s.line(ports["B"][0], jog_y, cports["rod"][0], jog_y)
            s.line(cports["rod"][0], jog_y, cports["rod"][0], cports["rod"][1])
            s.dot(*cports["rod"])
            if name == "HC1" and spec.sensors and "JOB" in spec.sensors:
                stamp(s, "limit_switch", cports["cap"][0] - 28, 48, anchor="center")
                s.text(cports["cap"][0] - 44, 36, "JOB", 10, "end")
        else:
            mports = stamp(s, "motor_fixed", cx, 100, anchor="center")
            s.text(cx + 58, 88, name, 13, "start")
            s.line(ports["A"][0], ports["A"][1], ports["A"][0], mports["A"][1])
            s.line(ports["A"][0], mports["A"][1], mports["A"][0], mports["A"][1])
            s.dot(*mports["A"])
            s.line(ports["B"][0], ports["B"][1], ports["B"][0], mports["B"][1])
            s.line(ports["B"][0], mports["B"][1], mports["B"][0], mports["B"][1])
            s.dot(*mports["B"])

        s.line(last_p, p_rail_y, ports["P"][0], p_rail_y)
        s.dot(ports["P"][0], p_rail_y)
        s.line(ports["P"][0], p_rail_y, ports["P"][0], ports["P"][1])
        s.line(last_t, t_rail_y, ports["T"][0], t_rail_y)
        s.dot(ports["T"][0], t_rail_y)
        hop = 8
        s.line(ports["T"][0], ports["T"][1], ports["T"][0], p_rail_y - hop)
        _hop_over(s, ports["T"][0], p_rail_y, hop)
        s.line(ports["T"][0], p_rail_y + hop, ports["T"][0], t_rail_y)
        last_p, last_t = ports["P"][0], ports["T"][0]

    s.line(last_p, p_rail_y, last_p + 30, p_rail_y)
    s.line(last_t, t_rail_y, last_t + 30, t_rail_y)

    dest.write_text(s.tostring())
    return dest


def _contact_glyph(tag: str) -> str:
    upper = tag.upper()
    if upper in {"START", "S1"}:
        return "pushbutton"
    if "B" in upper or upper == "JOB":
        return "limit_switch"
    return "contact_no"


def _coil_glyph(tag: str) -> str:
    if "Y" in tag:
        return "solenoid_box"
    if tag.startswith("T1"):
        return "timer_pull_in"
    return "relay_coil"


def draw_electrical(spec: CircuitSpec, dest: Path) -> Path:
    spec = apply_compile(spec)
    dest.parent.mkdir(parents=True, exist_ok=True)
    paths = spec.electrical.paths
    n = max(len(paths), 1)
    col_w = 140
    width = max(90 + n * col_w + 50, 720)
    s = SVG(width, 580)
    s.text(width / 2, 18, "Electrical control circuit  ·  lecture L8 stamps  ·  de-energized", 14)
    y24, y0 = 48, 500
    s.line(36, y24, width - 16, y24, 2)
    s.line(36, y0, width - 16, y0, 2)
    s.circle(36, y24, 3.5)
    s.circle(36, y0, 3.5)
    s.text(28, y24 + 4, "+24 V", 12, "end")
    s.text(28, y0 + 4, "0 V", 12, "end")

    for i, path in enumerate(paths):
        x = 88 + i * col_w
        s.text(x, 40, str(path.number), 13)
        s.dot(x, y24)
        s.line(x, y24, x, 88)
        y = 118
        prev_bottom = 88
        for c in path.contacts or []:
            gid = _contact_glyph(c)
            g = stamp(s, gid, x, y, anchor="center")
            top_y = g.get("in", (x, y - 18))[1]
            bot_y = g.get("out", (x, y + 18))[1]
            s.line(x, prev_bottom, x, top_y)
            s.text(x + 18, y + 4, c, 11, "start")
            prev_bottom = bot_y
            y += 62
        coil_y = 430
        s.line(x, prev_bottom, x, coil_y - 14)
        if path.coil:
            gid = _coil_glyph(path.coil)
            coil = stamp(s, gid, x, coil_y, anchor="center")
            label = path.coil
            if gid == "timer_pull_in":
                s.text(x + 36, coil_y + 5, label, 10, "start")
            elif gid == "solenoid_box":
                s.text(x, coil_y + 24, label, 11)
            else:
                s.text(x, coil_y + 5, label, 9)
            a2_y = coil.get("A2", (x, coil_y + 12))[1]
            s.line(x, a2_y, x, y0)
        else:
            s.line(x, coil_y - 14, x, y0)
        s.dot(x, y0)
        s.text(x, 548, "main" if path.kind == "main" else "control", 9)

    dest.write_text(s.tostring())
    return dest


def _next_state(action: str, act: str, cur: int) -> int:
    if action in {f"{act}+", f"{act}_ON"}:
        return 1
    if action == f"{act}-":
        return 0
    return cur


def _sensor_at_edge(spec: CircuitSpec, act: str, going_to: int) -> str:
    cyl = spec.cylinders.get(act)
    if not cyl or not cyl.sensors:
        return ""
    return cyl.sensors[-1] if going_to == 1 else cyl.sensors[0]


def draw_phase(spec: CircuitSpec, dest: Path) -> Path:
    """L10 p4 method: 0/1 traces. Sequence is arbitrary, so this stays vector."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    steps = spec.sequence
    actuators = list(spec.cylinders) + list(spec.motors)
    colors = ["#c0392b", "#2471a3", "#1e8449", "#7d3c98"]
    left, row_h, step_w = 110, 110, 110
    n = len(steps)
    s = SVG(140 + n * step_w + 90, 100 + row_h * len(actuators))
    s.text(s.w / 2, 22, "Step-displacement diagram  ·  lecture L10", 16)
    s.text(left, 46, "START  ∧  JOB  ∧  1B1  ∧  2B1", 12, "start")

    for i, st in enumerate(steps):
        x = left + i * step_w
        label = f"{i + 1}=1" if i == n - 1 else str(i + 1)
        s.text(x, 68, label, 13)
        s.text(x + 8, 86, st.action, 10, "start")

    for ti, act in enumerate(actuators):
        color = colors[ti % len(colors)]
        y1 = 120 + ti * row_h
        y0 = y1 + 44
        s.text(12, (y1 + y0) / 2 + 4, act, 14, "start", color)
        s.text(84, y1 + 4, "1", 10, "end")
        s.text(84, y0 + 4, "0", 10, "end")
        for i in range(n + 1):
            x = left + i * step_w
            s.line(x, y1 - 6, x, y0 + 8, 0.8, "#bbbbbb")
        s.line(left, y1, left + n * step_w, y1, 0.8, "#bbbbbb")
        s.line(left, y0, left + n * step_w, y0, 0.8, "#bbbbbb")

        cur = 0
        for i, st in enumerate(steps):
            nxt = _next_state(st.action, act, cur)
            x1 = left + i * step_w
            x2 = left + (i + 1) * step_w
            yc = y0 if cur == 0 else y1
            yn = y0 if nxt == 0 else y1
            if act in spec.motors and nxt != cur:
                s.line(x1, yc, x1, yn, 2.4, color)
                s.line(x1, yn, x2, yn, 2.4, color)
            else:
                s.line(x1, yc, x2, yn, 2.4, color)
            if nxt != cur:
                tag = _sensor_at_edge(spec, act, nxt)
                if tag:
                    s.text(x2 + 2, yn - 6 if nxt == 1 else yn + 14, tag, 10, "start", color)
            cur = nxt

    dest.write_text(s.tostring())
    return dest


def write_solution(spec: CircuitSpec, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    lines = [spec.meta.title, "", "Sequence"]
    for i, step in enumerate(spec.sequence, 1):
        extra = f" ({step.seconds} s)" if step.seconds else ""
        lines.append(f"  {i}. {step.action}{extra} — {step.label}")
    lines += ["", "Calculations (lecture forms; no invented Q)"]
    if spec.meta.exam_id == "2023_selfstudy_b1":
        lines.extend(f"  {ln}" for ln in solution_lines_grinding())
    lines += ["", "Components"]
    for p in spec.power.pumps:
        lines.append(f"  pump {p.id}")
    for r in spec.power.relief_valves:
        lines.append(f"  relief {r.id}")
    for cid, cyl in spec.cylinders.items():
        lines.append(f"  {cid} bore {cyl.bore_mm} rod {cyl.rod_mm} dcv {cyl.dcv}")
    for mid, mot in spec.motors.items():
        lines.append(f"  {mid} rpm {mot.rpm} dcv {mot.dcv}")
    dest.write_text("\n".join(lines) + "\n")
    return dest


def draw_all(spec: CircuitSpec, out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    return {
        "hydraulic": draw_hydraulic(spec, out_dir / "hydraulic_circuit.svg"),
        "electrical": draw_electrical(spec, out_dir / "electrical_circuit.svg"),
        "phase": draw_phase(spec, out_dir / "step_displacement.svg"),
        "solution": write_solution(spec, out_dir / "solution.txt"),
    }
