"""2023 Minor-2 Q2: PLC connection diagram + analog ladder (not L8)."""

from __future__ import annotations

from pathlib import Path

from circuit.calc import plc_2023_q2_scaling
from circuit.catalog import stamp
from circuit.spec import CircuitSpec
from circuit.svgdraw import SVG

_IO = {
    "start": "I0.0",
    "stop": "I0.1",
    "l1": "Q0.0",
    "l2": "Q0.1",
    "l3": "Q0.2",
    "ai": "AI Slot-3 Ch-2",
    "ao": "AO Slot-2 Ch-1",
}


def _title(s: SVG, spec: CircuitSpec, subtitle: str) -> None:
    s.text(540, 28, spec.meta.title, 18)
    s.text(540, 52, subtitle, 13)


def _box(s: SVG, x: float, y: float, w: float, h: float, title: str, lines: list[str]) -> None:
    s.rect(x, y, w, h)
    s.text(x + w / 2, y + 22, title, 13)
    for i, line in enumerate(lines):
        s.text(x + 12, y + 46 + i * 18, line, 12, "start")


def _table(
    s: SVG,
    x: float,
    y: float,
    headers: list[str],
    rows: list[list[str]],
    widths: list[float],
    row_h: float = 26,
) -> float:
    col_x = [x]
    for w in widths:
        col_x.append(col_x[-1] + w)
    total_w = sum(widths)
    n = 1 + len(rows)
    s.rect(x, y, total_w, n * row_h)
    for cx in col_x[1:-1]:
        s.line(cx, y, cx, y + n * row_h)
    for r in range(1, n):
        yy = y + r * row_h
        s.line(x, yy, x + total_w, yy)
    for i, h in enumerate(headers):
        s.text(col_x[i] + widths[i] / 2, y + 18, h, 11)
    for r, row in enumerate(rows):
        yy = y + (r + 1) * row_h
        for i, cell in enumerate(row):
            s.text(col_x[i] + widths[i] / 2, yy + 18, cell, 11)
    return y + n * row_h


def draw_plc_connection(spec: CircuitSpec, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    sc = plc_2023_q2_scaling()
    s = SVG(1080, 1380)

    _title(s, spec, "PLC connection diagram  ·  analog I/O  ·  30 marks")

    s.text(40, 90, "1. I/O assignment (paper + scan notes)", 14, "start")
    y = _table(
        s,
        40,
        104,
        ["Address", "Device", "Function"],
        [
            [_IO["start"], "START PB", "Start conveyor (NO)"],
            [_IO["stop"], "STOP PB", "Stop conveyor (NC in ladder)"],
            [_IO["ai"], "Load cell", "Weight 0–950 kg, 12-bit"],
            [_IO["ao"], "Speed controller", "0–10 V → 0–4000 RPM, 10-bit"],
            [_IO["l1"], "L1 LOW", "W < 220 kg"],
            [_IO["l2"], "L2 NORMAL", "220 ≤ W ≤ 580 kg (includes 470 kg)"],
            [_IO["l3"], "L3 HIGH", "W > 580 kg"],
        ],
        [160, 180, 400],
    )

    s.text(40, y + 36, "2. Field devices to PLC", 14, "start")

    _box(
        s,
        40,
        y + 52,
        220,
        110,
        "Weight detector",
        ["Load cell 0–950 kg", "Assumed 0–10 V", "(paper: type not given)"],
    )
    _box(
        s,
        380,
        y + 48,
        320,
        230,
        "PLC",
        [
            f"{_IO['start']}  START",
            f"{_IO['stop']}  STOP",
            f"{_IO['ai']}  load cell",
            f"{_IO['ao']}  speed cmd",
            f"{_IO['l1']}  L1 LOW",
            f"{_IO['l2']}  L2 NORMAL",
            f"{_IO['l3']}  L3 HIGH",
        ],
    )
    _box(
        s,
        820,
        y + 52,
        220,
        110,
        "Speed controller",
        ["0–10 V input", "Motor 0–4000 RPM", "AO Channel-1 Slot-2"],
    )

    # Analog arrows into the PLC mid-height
    s.line(260, y + 120, 380, y + 120)
    s.triangle([(372, y + 114), (380, y + 120), (372, y + 126)])
    s.text(320, y + 108, "AI Ch-2", 11)
    s.line(700, y + 120, 820, y + 120)
    s.triangle([(812, y + 114), (820, y + 120), (812, y + 126)])
    s.text(760, y + 108, "AO Ch-1", 11)

    # Pushbuttons and lamps (lecture stamps)
    pb_y = y + 300
    s.text(40, pb_y, "Digital 24 V field", 14, "start")
    s.text(40, pb_y + 22, "+24 V", 12, "start")
    s.line(90, pb_y + 18, 360, pb_y + 18, sw=2.0)

    start_p = stamp(s, "pushbutton", 110, pb_y + 40, w=36, h=52)
    s.text(128, pb_y + 110, "START", 12)
    s.text(128, pb_y + 128, _IO["start"], 11)
    s.line(128, pb_y + 18, start_p["in"][0], start_p["in"][1])
    s.line(start_p["out"][0], start_p["out"][1], 128, pb_y + 160)
    s.line(128, pb_y + 160, 380, pb_y + 160)
    s.text(270, pb_y + 152, "to PLC DI", 11)

    stop_p = stamp(s, "pushbutton", 230, pb_y + 40, w=36, h=52)
    s.text(248, pb_y + 110, "STOP", 12)
    s.text(248, pb_y + 128, _IO["stop"], 11)
    s.line(248, pb_y + 18, stop_p["in"][0], stop_p["in"][1])
    s.line(stop_p["out"][0], stop_p["out"][1], 248, pb_y + 160)

    s.text(40, pb_y + 188, "0 V  ——— PLC COM", 12, "start")

    lamp_x = [820, 900, 980]
    lamp_lbl = [("L1 LOW", _IO["l1"]), ("L2 NORM", _IO["l2"]), ("L3 HIGH", _IO["l3"])]
    s.text(820, pb_y, "Indicator lamps", 14, "start")
    plc_right, plc_bottom = 700, y + 48 + 230
    s.line(plc_right, plc_bottom - 20, 800, plc_bottom - 20)
    s.line(800, plc_bottom - 20, 800, pb_y + 20)
    for (lab, addr), xx in zip(lamp_lbl, lamp_x):
        lp = stamp(s, "lamp", xx, pb_y + 20, w=42, h=62)
        s.text(xx + 21, pb_y + 100, lab, 11)
        s.text(xx + 21, pb_y + 116, addr, 10)
        s.line(800, pb_y + 20, lp["A1"][0], pb_y + 20)
        s.line(lp["A1"][0], pb_y + 20, lp["A1"][0], lp["A1"][1])
    s.text(900, pb_y + 140, "from PLC DO  (Q0.0 / Q0.1 / Q0.2)", 11)

    # Analog wiring detail
    ay = pb_y + 220
    s.text(40, ay, "3. Analog wiring (0–10 V assumed)", 14, "start")
    _box(
        s,
        40,
        ay + 16,
        480,
        120,
        "Load cell → AI Slot-3 Ch-2",
        [
            "Signal (+)  →  AI Ch-2",
            "Signal (−)  →  AI COM",
            "12-bit: 0 → 4095 counts  ≡  0 → 950 kg",
        ],
    )
    _box(
        s,
        560,
        ay + 16,
        480,
        120,
        "AO Slot-2 Ch-1 → speed controller",
        [
            "AO Ch-1 (+)  →  0–10 V INPUT",
            "AO COM       →  Analog COM",
            "10-bit: 0 → 1023 counts  ≡  0 → 10 V  ≡  0 → 4000 RPM",
        ],
    )

    s.text(40, ay + 168, "4. Scaling (nearest integer counts)", 14, "start")
    _table(
        s,
        40,
        ay + 180,
        ["Condition", "AI counts", "Speed", "AO counts", "Voltage", "Lamp"],
        [
            [f"W < 220 kg", f"AI < {sc['ai_220_cmp']}", "1185 RPM", str(sc["ao_1185"]), "2.9625 V", "L1"],
            [f"220–580 kg", f"{sc['ai_220_cmp']}–{sc['ai_580']}", "2250 RPM", str(sc["ao_2250"]), "5.625 V", "L2"],
            [f"W > 580 kg", f"AI > {sc['ai_580']}", "3545 RPM", str(sc["ao_3545"]), "8.8625 V", "L3"],
            ["STOP", "—", "0 RPM", "0", "0 V", "OFF"],
        ],
        [150, 150, 120, 120, 120, 80],
    )
    s.text(
        40,
        ay + 180 + 5 * 26 + 22,
        f"220 kg nearest count = {sc['ai_220']}, so W<220 uses AI<{sc['ai_220_cmp']}.  "
        f"3545 RPM = 906.63 → AO {sc['ao_3545']}.  "
        "Load-cell type not given: 0–10 V assumed (4–20 mA only changes AI wiring).",
        12,
        "start",
    )
    s.text(
        40,
        ay + 180 + 5 * 26 + 44,
        "Weight detector → AI → PLC → AO → speed controller → motor",
        13,
        "start",
    )
    dest.write_text(s.tostring())
    return dest


def _contact(s: SVG, x: float, y: float, label: str, *, nc: bool = False, w: float = 88) -> float:
    s.rect(x, y - 16, w, 32)
    s.text(x + w / 2, y + 5, label, 11)
    if nc:
        s.line(x + 8, y + 12, x + w - 8, y - 12)
    return x + w


def _coil(s: SVG, x: float, y: float, label: str) -> None:
    s.circle(x + 22, y, 18)
    s.text(x + 22, y + 36, label, 11)


def _mov(s: SVG, x: float, y: float, text: str, w: float = 160) -> float:
    s.rect(x, y - 16, w, 32)
    s.text(x + w / 2, y + 5, text, 11)
    return x + w


def draw_plc_ladder(spec: CircuitSpec, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    sc = plc_2023_q2_scaling()
    s = SVG(1080, 1280)
    _title(s, spec, "PLC ladder  ·  three-speed conveyor  ·  M0.0 = RUN")

    s.text(
        40,
        74,
        f"Compare AI < {sc['ai_220_cmp']} (W<220 kg) and AI > {sc['ai_580']} (W>580 kg).  "
        f"MOV AO {sc['ao_1185']} / {sc['ao_2250']} / {sc['ao_3545']}.  STOP writes AO = 0.",
        12,
        "start",
    )

    left, right = 70, 1020
    y0 = 155
    ys = [y0 + i * 125 for i in range(8)]
    s.line(left, ys[0] - 24, left, ys[-1] + 50, sw=2.2)
    s.line(right, ys[0] - 24, right, ys[-1] + 50, sw=2.2)
    s.text(left - 8, ys[0] + 4, "+24 V", 11, "end")
    s.text(right + 8, ys[0] + 4, "COM", 11, "start")

    # Rung 1 — START/STOP latch
    y = ys[0]
    s.text(left + 8, y - 28, "1  Start/stop latch", 12, "start")
    s.line(left, y, 80, y)
    x = _contact(s, 80, y, f"{_IO['start']} START")
    s.line(x, y, 280, y)
    s.line(80, y, 80, y + 44)
    s.line(80, y + 44, 110, y + 44)
    x2 = _contact(s, 110, y + 44, "M0.0 RUN")
    s.line(x2, y + 44, 280, y + 44)
    s.line(280, y + 44, 280, y)
    s.line(280, y, 310, y)
    x = _contact(s, 310, y, f"{_IO['stop']} STOP", nc=True)
    s.line(x, y, right - 70, y)
    _coil(s, right - 70, y, "M0.0 RUN")
    s.line(right - 26, y, right, y)

    # Speed MOV rungs
    zones = [
        (
            2,
            "Low weight  W < 220 kg",
            [("M0.0 RUN", False), (f"AI < {sc['ai_220_cmp']}", False)],
            f"MOV {sc['ao_1185']} → AO",
        ),
        (
            3,
            "Normal  220 ≤ W ≤ 580 kg  (470 kg → 2250 RPM)",
            [
                ("M0.0 RUN", False),
                (f"AI ≥ {sc['ai_220_cmp']}", False),
                (f"AI ≤ {sc['ai_580']}", False),
            ],
            f"MOV {sc['ao_2250']} → AO",
        ),
        (
            4,
            "High weight  W > 580 kg",
            [("M0.0 RUN", False), (f"AI > {sc['ai_580']}", False)],
            f"MOV {sc['ao_3545']} → AO",
        ),
        (5, "Stopped — zero the analog output", [("M0.0 RUN", True)], "MOV 0 → AO"),
    ]
    for idx, (num, caption, contacts, mov) in enumerate(zones):
        y = ys[idx + 1]
        s.text(left + 8, y - 28, f"{num}  {caption}", 12, "start")
        s.line(left, y, 80, y)
        x = 80
        for label, nc in contacts:
            x = _contact(s, x, y, label, nc=nc, w=100 if "AI" in label or "RUN" in label else 88)
            s.line(x, y, x + 16, y)
            x += 16
        x = _mov(s, x, y, mov, 170)
        s.line(x, y, right, y)

    lamps = [
        (6, "L1 LOW", [("M0.0 RUN", False), (f"AI < {sc['ai_220_cmp']}", False)], f"{_IO['l1']} L1"),
        (
            7,
            "L2 NORMAL",
            [
                ("M0.0 RUN", False),
                (f"AI ≥ {sc['ai_220_cmp']}", False),
                (f"AI ≤ {sc['ai_580']}", False),
            ],
            f"{_IO['l2']} L2",
        ),
        (8, "L3 HIGH", [("M0.0 RUN", False), (f"AI > {sc['ai_580']}", False)], f"{_IO['l3']} L3"),
    ]
    for i, (num, caption, contacts, coil) in enumerate(lamps):
        y = ys[i + 5]
        s.text(left + 8, y - 28, f"{num}  {caption}", 12, "start")
        s.line(left, y, 80, y)
        x = 80
        for label, nc in contacts:
            x = _contact(s, x, y, label, nc=nc, w=100)
            s.line(x, y, x + 16, y)
            x += 16
        s.line(x, y, right - 70, y)
        _coil(s, right - 70, y, coil)
        s.line(right - 26, y, right, y)

    s.text(
        40,
        ys[-1] + 80,
        "Only one lamp ON at a time.  Lamps follow the same zones as speed.  "
        "Rung 5 is required: otherwise STOP leaves the last voltage on the speed controller.",
        12,
        "start",
    )
    dest.write_text(s.tostring())
    return dest
