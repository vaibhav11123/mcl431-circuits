"""Pneumatic sheet: L10 p5 layout — cylinder over valve, de-energized."""

from __future__ import annotations

from pathlib import Path

from circuit.catalog import glyph, stamp, stamp_dcv_5_2, stamp_dcv_5_3
from circuit.spec import CircuitSpec
from circuit.svgdraw import SVG


def _exhaust(s: SVG, x: float, y: float) -> None:
    """ISO 1219 exhaust: open triangle below the port stub, not on it."""
    s.triangle([(x - 7, y + 4), (x + 7, y + 4), (x, y + 18)], fill="#fff")


def draw_pneumatic(spec: CircuitSpec, dest: Path) -> Path:
    """Cylinders on top, DCV under; cap over port 4; exhaust under 3/5."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    n = max(len(spec.cylinders), 1)
    five3 = any(v.type == "dcv_5_3" for v in spec.valves.values())
    five2 = any(v.type == "dcv_5_2_double_solenoid" for v in spec.valves.values())
    span = 520 if five3 else 480 if five2 else 420
    width = max(1200, 180 + n * span)
    if spec.meta.exam_id == "2016_minor1_emboss":
        width = max(width, 1480)
    s = SVG(width, 800)
    s.text(width / 2, 22, spec.meta.title, 18)
    if five3:
        subtitle = "Pneumatic circuit  ·  ISO 1219 5/3 closed centre  ·  de-energized"
    elif five2:
        subtitle = "Pneumatic circuit  ·  lecture L10  ·  5/2 de-energized"
    else:
        subtitle = "Pneumatic circuit  ·  lecture L10 p5 stamps  ·  de-energized"
    s.text(width / 2, 42, subtitle, 12)

    supply_y = 640
    valve_y = 430 if (five3 or five2) else 360
    cyl_y = 58
    cyl_g = glyph("cylinder_l10")
    cyl_w, cyl_h = cyl_g.w, cyl_g.h
    cols = list(spec.cylinders.items())
    x0 = 300
    first_1: tuple[float, float] | None = None
    for i, (name, cyl) in enumerate(cols):
        cx = x0 + i * span
        valve = spec.valves[cyl.dcv]
        sols = list(valve.solenoids)
        if valve.type == "dcv_5_3":
            ports = stamp_dcv_5_3(s, cx, valve_y, cyl.dcv, sols)
        else:
            ports = stamp_dcv_5_2(s, cx, valve_y, cyl.dcv, sols)

        # L10: cap sits on port 4 so that run is a vertical drop.
        cap_fx = cyl_g.ports["cap"][0]
        cyl_x = ports["4"][0] - cap_fx * cyl_w
        cports = stamp(s, "cylinder_l10", cyl_x, cyl_y, cyl_w, cyl_h)
        s.text(cyl_x - 10, cyl_y + cyl_h / 2 + 4, name, 13, "end")
        if cyl.sensors:
            s.text(cports["cap"][0], cyl_y - 6, cyl.sensors[0], 11)
            if len(cyl.sensors) > 1:
                s.text(cports["rod"][0], cyl_y - 6, cyl.sensors[1], 11)

        s.line(ports["4"][0], ports["4"][1], cports["cap"][0], cports["cap"][1])
        s.text(ports["4"][0] - 12, ports["4"][1] - 6, "4", 10, "end")
        jog_y = cports["rod"][1] + 36
        s.line(cports["rod"][0], cports["rod"][1], cports["rod"][0], jog_y)
        s.line(cports["rod"][0], jog_y, ports["2"][0], jog_y)
        s.line(ports["2"][0], jog_y, ports["2"][0], ports["2"][1])
        s.text(ports["2"][0] + 10, ports["2"][1] - 6, "2", 10, "start")

        if name == "2A1" and "PS" in spec.sensors:
            tee_y = (cports["cap"][1] + ports["4"][1]) / 2
            p4x = ports["4"][0]
            s.dot(p4x, tee_y)
            g = glyph("pressure_switch")
            p_fx, p_fy = g.ports["P"]
            cx = p4x - 8 - p_fx * g.w + g.w / 2
            cy = tee_y - p_fy * g.h + g.h / 2
            ps = stamp(s, "pressure_switch", cx, cy, anchor="center")
            s.line(p4x, tee_y, ps["P"][0], ps["P"][1])
            s.text(cx, cy + g.h / 2 + 14, "PS  4 bar", 11)
            s.text(cx, cy + g.h / 2 + 28, "RD +24  BU 0 V  BK", 9)

        for pid, label_dx in (("5", -12), ("3", 10)):
            if pid not in ports:
                continue
            px, py = ports[pid]
            _exhaust(s, px, py)
            s.text(px + label_dx, py + 32, pid, 10, "end" if label_dx < 0 else "start")

        s.line(ports["1"][0], ports["1"][1], ports["1"][0], supply_y)
        s.text(ports["1"][0] + 10, ports["1"][1] + 16, "1", 10, "start")
        if first_1 is None:
            first_1 = (ports["1"][0], supply_y)
            s.dot(*first_1)
        else:
            s.line(first_1[0], supply_y, ports["1"][0], supply_y)
            s.dot(ports["1"][0], supply_y)

    if first_1:
        sx, sy = first_1
        s.line(sx, sy, sx, sy + 44)
        s.triangle([(sx - 9, sy + 44), (sx + 9, sy + 44), (sx, sy + 64)], fill="#fff")
        s.text(sx + 16, sy + 60, "compressed air supply", 11, "start")

    if spec.meta.exam_id == "2016_minor1_emboss":
        bx = width - 310
        s.rect(bx, 58, 290, 220)
        s.text(bx + 145, 80, "Bill of material", 13)
        for i, line in enumerate(
            (
                "1A1 clamp DAC    2A1 emboss DAC",
                "1V, 2V  5/2 double solenoid",
                "1Y1/1Y2   2Y1/2Y2",
                "1B1/1B2   2B1/2B2  end sensors",
                "S0 magazine proximity",
                "S1 start",
                "PS P/E converter  4 bar",
                "FRL on supply",
            )
        ):
            s.text(bx + 12, 104 + i * 20, line, 11, "start")

    dest.write_text(s.tostring())
    return dest
