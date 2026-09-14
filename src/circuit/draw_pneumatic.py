"""Pneumatic sheet: L10 p5 stamps, de-energized."""

from __future__ import annotations

from pathlib import Path

from circuit.catalog import stamp, stamp_dcv_5_2
from circuit.spec import CircuitSpec
from circuit.svgdraw import SVG


def draw_pneumatic(spec: CircuitSpec, dest: Path) -> Path:
    """L10 p5: cylinders on top, 5/2 under, filled supply dot, exhaust on the stamp."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    s = SVG(1200, 720)
    s.text(600, 22, spec.meta.title, 18)
    s.text(600, 42, "Pneumatic circuit  ·  lecture L10 p5 stamps  ·  de-energized", 12)

    supply_y = 560
    cols = list(spec.cylinders.items())
    x0, span = 280, 420
    first_1: tuple[float, float] | None = None
    for i, (name, cyl) in enumerate(cols):
        cx = x0 + i * span
        sols = spec.valves[cyl.dcv].solenoids
        ports = stamp_dcv_5_2(s, cx, 360, cyl.dcv, list(sols))
        s.rect(cx - 132, 94, 36, 22, 1.2)
        s.rect(cx - 132, 338, 36, 22, 1.2)
        for pid in ("3", "5"):
            if pid not in ports:
                continue
            px, py = ports[pid]
            s.triangle([(px - 6, py), (px + 6, py), (px, py + 12)])
        for pid in ("4", "2", "1"):
            if pid in ports:
                s.text(
                    ports[pid][0] + (8 if pid != "1" else 12),
                    ports[pid][1] + (0 if pid != "1" else 14),
                    pid,
                    10,
                    "start",
                )
        cports = stamp(s, "cylinder_l10", cx - 70, 70, 200, 80)
        s.text(cx - 86, 110, name, 13, "end")
        if cyl.sensors:
            s.text(cports["cap"][0], 64, cyl.sensors[0], 11)
            if len(cyl.sensors) > 1:
                s.text(cports["rod"][0], 64, cyl.sensors[1], 11)
        s.line(ports["4"][0], ports["4"][1], ports["4"][0], cports["cap"][1])
        s.line(ports["4"][0], cports["cap"][1], cports["cap"][0], cports["cap"][1])
        s.dot(*cports["cap"])
        jog_y = 220
        s.line(ports["2"][0], ports["2"][1], ports["2"][0], jog_y)
        s.line(ports["2"][0], jog_y, cports["rod"][0], jog_y)
        s.line(cports["rod"][0], jog_y, cports["rod"][0], cports["rod"][1])
        s.dot(*cports["rod"])
        s.line(ports["1"][0], ports["1"][1], ports["1"][0], supply_y)
        if first_1 is None:
            first_1 = (ports["1"][0], supply_y)
            s.dot(*first_1)
        else:
            s.line(first_1[0], supply_y, ports["1"][0], supply_y)
            s.dot(ports["1"][0], supply_y)

    if first_1:
        sx, sy = first_1
        s.line(sx, sy, sx, sy + 50)
        s.triangle([(sx - 10, sy + 50), (sx + 10, sy + 50), (sx, sy + 72)])
        s.text(sx + 18, sy + 66, "supply", 11, "start")

    dest.write_text(s.tostring())
    return dest
