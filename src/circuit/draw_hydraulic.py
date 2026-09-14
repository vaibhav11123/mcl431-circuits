"""Hydraulic sheet: L2–L5 stamps, de-energized."""

from __future__ import annotations

from pathlib import Path

from circuit.catalog import stamp, stamp_dcv_4_3_closed
from circuit.spec import CircuitSpec, PatternId
from circuit.svgdraw import SVG


def _hop_over(s: SVG, x: float, y: float, hop: float = 8) -> None:
    """ISO 1219: crossing without a junction — no filled dot."""
    s.polyline([(x, y - hop), (x + hop, y), (x, y + hop)])


def _draw_single_pump(s: SVG, spec: CircuitSpec) -> tuple[float, float, float, float, float]:
    """One pump + PRV. Returns last_p, last_t, p_rail_y, t_rail_y, x0."""
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
    # Tee on the P-rail, PRV across P→T, dedicated tank drop (L3/L4 power unit).
    rvx, rvy = px + 118, p_rail_y + 48
    prv = stamp(s, "prv", rvx, rvy, anchor="center")
    if spec.meta.exam_id == "2023_selfstudy_b1":
        from circuit.calc import grinding_hc1_pressure_bar

        s.text(rvx, rvy - 44, f"RV1 {grinding_hc1_pressure_bar():.2f} bar", 12)
    else:
        s.text(rvx, rvy - 44, prv_id, 12)
    s.line(px, p_rail_y, prv["P"][0], p_rail_y)
    s.dot(prv["P"][0], p_rail_y)
    s.line(prv["P"][0], p_rail_y, prv["P"][0], prv["P"][1])
    s.dot(*prv["P"])
    s.line(prv["T"][0], prv["T"][1], prv["T"][0], tank["T"][1])
    s.dot(*prv["T"])
    s.line(prv["T"][0], tank["T"][1], tank["T"][0], tank["T"][1])
    s.dot(prv["T"][0], tank["T"][1])
    # Actuator T-rail starts after the PRV so the relief branch is a clear P→T drop.
    t_start = prv["T"][0] + 24
    s.line(t_start, t_rail_y, t_start, tank["T"][1])
    s.dot(t_start, t_rail_y)
    s.dot(t_start, tank["T"][1])
    s.line(prv["T"][0], tank["T"][1], t_start, tank["T"][1])
    # Check on the horizontal P-rail after the PRV tee, before the first DCV.
    cv = stamp(s, "check_valve", t_start + 48, p_rail_y, anchor="center")
    s.line(prv["P"][0], p_rail_y, cv["1"][0], p_rail_y)
    last_p = cv["2"][0]
    return last_p, t_start, p_rail_y, t_rail_y, max(420.0, last_p + 90)


def _draw_hilo_power(s: SVG, spec: CircuitSpec) -> tuple[float, float, float, float, float]:
    """L4 p13: P1 (large) + check + UV; P2 (small) + RV; join to system."""
    p1x, p2x, py = 160, 400, 620
    p_rail_y, t_rail_y = 340, 530
    check_y = 400
    tank_x, tank_y = 280, 742
    tank = stamp(s, "tank", tank_x, tank_y, anchor="center")
    s.text(tank_x + 36, 748, "tank", 12, "start")

    def _pump_stack(px: float, pid: str) -> dict[str, tuple[float, float]]:
        pump = stamp(s, "pump_fixed", px, py, anchor="center")
        s.text(px + 48, py + 6, pid, 14, "start")
        filt = stamp(s, "filter", px, py + 62, anchor="center")
        s.line(pump["S"][0], pump["S"][1], filt["in"][0], filt["in"][1])
        s.line(filt["out"][0], filt["out"][1], filt["out"][0], tank["T"][1])
        s.line(filt["out"][0], tank["T"][1], tank["T"][0], tank["T"][1])
        s.dot(filt["out"][0], tank["T"][1])
        s.line(pump["P"][0], pump["P"][1], px, check_y)
        return pump

    pids = [p.id for p in spec.power.pumps]
    _pump_stack(p1x, pids[0] if pids else "P1")
    _pump_stack(p2x, pids[1] if len(pids) > 1 else "P2")

    cv = stamp(s, "check_valve", (p1x + p2x) / 2, check_y, anchor="center")
    s.text((p1x + p2x) / 2, check_y - 28, "CV", 11)
    s.line(p1x, check_y, cv["1"][0], check_y)
    s.dot(p1x, check_y)
    s.line(cv["2"][0], check_y, p2x, check_y)
    s.dot(p2x, check_y)
    s.line(p2x, check_y, p2x, p_rail_y)
    s.dot(p2x, p_rail_y)

    uv = stamp(s, "unloading_valve", 70, 470, anchor="center")
    s.text(70, 422, "UV", 12)
    s.line(p1x, check_y, p1x, uv["P"][1])
    s.line(p1x, uv["P"][1], uv["P"][0], uv["P"][1])
    s.dot(p1x, uv["P"][1])
    s.line(uv["T"][0], uv["T"][1], uv["T"][0], tank["T"][1])
    s.line(uv["T"][0], tank["T"][1], tank["T"][0], tank["T"][1])
    s.dot(uv["T"][0], tank["T"][1])

    prv_id = spec.power.relief_valves[0].id if spec.power.relief_valves else "RV"
    prv = stamp(s, "prv", 560, 380, anchor="center")
    s.text(560, 334, prv_id, 12)
    s.line(p2x, p_rail_y, prv["P"][0], p_rail_y)
    s.dot(prv["P"][0], p_rail_y)
    s.line(prv["P"][0], p_rail_y, prv["P"][0], prv["P"][1])
    s.line(prv["T"][0], prv["T"][1], prv["T"][0], tank["T"][1])
    s.line(prv["T"][0], tank["T"][1], tank["T"][0], tank["T"][1])
    s.dot(prv["T"][0], tank["T"][1])

    s.line(p1x, tank["T"][1], p1x, t_rail_y)
    s.dot(p1x, t_rail_y)
    return p2x, p1x, p_rail_y, t_rail_y, 820.0


def _draw_unload(s: SVG, spec: CircuitSpec) -> tuple[float, float, float, float, float]:
    """L4 p11: one pump, check on P, unloader piloted from downstream of the check."""
    last_p, last_t, p_rail_y, t_rail_y, x0 = _draw_single_pump(s, spec)
    uv = stamp(s, "unloading_valve", 70, 470, anchor="center")
    s.text(70, 422, "UV", 12)
    px = 100.0
    s.line(px, p_rail_y, px, uv["P"][1])
    s.line(px, uv["P"][1], uv["P"][0], uv["P"][1])
    s.dot(px, uv["P"][1])
    tank_y = 742.0
    s.line(uv["T"][0], uv["T"][1], uv["T"][0], tank_y)
    s.dot(uv["T"][0], tank_y)
    return last_p, last_t, p_rail_y, t_rail_y, x0


def _stamp_actuator_dcv(s: SVG, spec: CircuitSpec, obj, cx: float, sols: list[str]) -> dict[str, tuple[float, float]]:
    vtype = spec.valves[obj.dcv].type
    if vtype == "dcv_4_3_spring_centered":
        ports = stamp(s, "dcv_4_3_spring_centered", cx, 300, anchor="center")
        s.text(cx - 118, 268, obj.dcv, 12, "end")
        if sols:
            s.text(cx - 118, 318, sols[0], 11, "end")
        if len(sols) > 1:
            s.text(cx + 118, 318, sols[1], 11, "start")
        return ports
    return stamp_dcv_4_3_closed(s, cx, 300, obj.dcv, list(sols))


def draw_hydraulic(spec: CircuitSpec, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    n = len(spec.cylinders) + len(spec.motors)
    w = max(1680, 380 + n * 420 + 80)
    s = SVG(w, 800)
    s.text(w / 2, 22, spec.meta.title, 18)
    rest = "4/3 spring-centred rest" if any(
        spec.valves[obj.dcv].type == "dcv_4_3_spring_centered"
        for obj in list(spec.cylinders.values()) + list(spec.motors.values())
    ) else "4/3 closed-centre rest"
    s.text(w / 2, 42, f"Hydraulic circuit  ·  lecture L2–L5  ·  {rest}  ·  de-energized", 12)

    if PatternId.HILO_DOUBLE_PUMP in spec.meta.patterns:
        last_p, last_t, p_rail_y, t_rail_y, x0 = _draw_hilo_power(s, spec)
    elif PatternId.UNLOAD in spec.meta.patterns:
        last_p, last_t, p_rail_y, t_rail_y, x0 = _draw_unload(s, spec)
    else:
        last_p, last_t, p_rail_y, t_rail_y, x0 = _draw_single_pump(s, spec)
    span = 420.0

    cols: list[tuple[str, object, list[str], str]] = []
    for cid, cyl in spec.cylinders.items():
        cols.append((cid, cyl, spec.valves[cyl.dcv].solenoids, "cyl"))
    for mid, mot in spec.motors.items():
        cols.append((mid, mot, spec.valves[mot.dcv].solenoids, "mot"))

    for i, (name, obj, sols, kind) in enumerate(cols):
        cx = x0 + i * span
        ports = _stamp_actuator_dcv(s, spec, obj, cx, list(sols))
        s.text(ports["A"][0] - 12, ports["A"][1] - 6, "A", 10)
        s.text(ports["B"][0] + 12, ports["B"][1] - 6, "B", 10)
        s.text(ports["P"][0] - 12, ports["P"][1] + 14, "P", 10)
        s.text(ports["T"][0] + 12, ports["T"][1] + 14, "T", 10)

        if kind == "cyl":
            cyl_w, cyl_h = 200.0, 80.0
            cports = stamp(s, "cylinder_da", cx - 70, 58, cyl_w, cyl_h)
            s.text(cx - 86, 98, name, 13, "end")
            if obj.sensors:
                s.text(cports["cap"][0], 52, obj.sensors[0], 11)
                if len(obj.sensors) > 1:
                    s.text(cports["rod"][0], 52, obj.sensors[1], 11)
            s.line(ports["A"][0], ports["A"][1], ports["A"][0], cports["cap"][1])
            s.line(ports["A"][0], cports["cap"][1], cports["cap"][0], cports["cap"][1])
            if PatternId.METER_IN in spec.meta.patterns:
                fcv = stamp(s, "flow_control", ports["A"][0], (ports["A"][1] + cports["cap"][1]) / 2, anchor="center")
                s.text(fcv["2"][0] + 8, fcv["2"][1], "FC", 9, "start")
            s.dot(*cports["cap"])
            jog_y = 200
            s.line(ports["B"][0], ports["B"][1], ports["B"][0], jog_y)
            s.line(ports["B"][0], jog_y, cports["rod"][0], jog_y)
            s.line(cports["rod"][0], jog_y, cports["rod"][0], cports["rod"][1])
            if PatternId.METER_OUT in spec.meta.patterns:
                fcv = stamp(s, "flow_control", (ports["B"][0] + cports["rod"][0]) / 2, jog_y, anchor="center")
                s.text(fcv["2"][0], fcv["2"][1] - 16, "FC", 9)
            s.dot(*cports["rod"])
            if PatternId.REGEN in spec.meta.patterns:
                cv = stamp(s, "check_valve", ports["T"][0] + 36, t_rail_y, anchor="center")
                s.text(cv["1"][0], t_rail_y - 20, "CV", 9)
                s.line(cports["rod"][0], jog_y, ports["P"][0], p_rail_y)
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
        if PatternId.BLEED_OFF in spec.meta.patterns:
            bx = ports["P"][0] + 36
            s.line(ports["P"][0], p_rail_y, bx, p_rail_y)
            s.dot(bx, p_rail_y)
            s.line(bx, p_rail_y, bx, t_rail_y)
            s.dot(bx, t_rail_y)
            stamp(s, "flow_control", bx, (p_rail_y + t_rail_y) / 2, anchor="center")
            s.text(bx + 16, (p_rail_y + t_rail_y) / 2, "bleed", 9, "start")
        last_p, last_t = ports["P"][0], ports["T"][0]

    s.line(last_p, p_rail_y, last_p + 30, p_rail_y)
    s.line(last_t, t_rail_y, last_t + 30, t_rail_y)

    dest.write_text(s.tostring())
    return dest
