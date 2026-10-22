"""Lecture stamp catalog: crop PNGs plus fractional port anchors.

The drawer stamps these glyphs and draws wires between the returned ports.
Never invent a box, envelope, contact, or coil — if an id is missing, stop.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from circuit.svgdraw import SVG

ROOT = Path(__file__).resolve().parents[2]
STAMPS = ROOT / "lecture" / "crops" / "stamps"


@dataclass(frozen=True)
class Glyph:
    file: str
    w: float
    h: float
    ports: dict[str, tuple[float, float]] = field(default_factory=dict)

    @property
    def path(self) -> Path:
        return STAMPS / self.file


# Port fractions are (fx, fy) of the placed bbox, origin top-left.
GLYPHS: dict[str, Glyph] = {
    "envelope_cross": Glyph("envelope_cross.png", 54, 58),
    "envelope_parallel": Glyph("envelope_parallel.png", 54, 58),
    "envelope_closed": Glyph(
        "envelope_closed.png",
        54,
        58,
        {"A": (0.32, 0.04), "B": (0.64, 0.04), "P": (0.32, 0.96), "T": (0.64, 0.96)},
    ),
    "cylinder_l10": Glyph(
        "cylinder_l10.png",
        240,
        76,
        {"cap": (0.051, 0.99), "rod": (0.846, 0.99)},
    ),
    "cylinder_da": Glyph(
        "cylinder_da.png",
        180,
        52,
        {"cap": (0.18, 1.00), "rod": (0.82, 1.00)},
    ),
    "motor_fixed": Glyph(
        "motor_fixed.png",
        96,
        92,
        {"A": (0.28, 1.00), "B": (0.72, 1.00)},
    ),
    "pump_fixed": Glyph(
        "pump_fixed.png",
        78,
        78,
        {"P": (0.50, 0.00), "S": (0.50, 1.00)},
    ),
    "tank": Glyph("tank.png", 42, 22, {"T": (0.50, 0.00)}),
    "filter": Glyph(
        "filter.png",
        36,
        50,
        {"in": (0.50, 0.00), "out": (0.50, 0.92)},
    ),
    "prv": Glyph(
        "prv.png",
        150,
        72,
        {"P": (0.06, 0.58), "T": (0.94, 0.58)},
    ),
    "solenoid_box": Glyph(
        "solenoid_box.png",
        50,
        26,
        {"in": (0.00, 0.50), "out": (1.00, 0.50)},
    ),
    "solenoid_coil": Glyph(
        "solenoid_coil.png",
        72,
        48,
        {"A1": (0.58, 0.00), "A2": (0.58, 1.00)},
    ),
    "relay_coil": Glyph(
        "relay_coil.png",
        64,
        28,
        {"A1": (0.50, 0.00), "A2": (0.50, 1.00)},
    ),
    "timer_pull_in": Glyph(
        "timer_pull_in.png",
        58,
        24,
        {"A1": (0.45, 0.00), "A2": (0.45, 1.00)},
    ),
    "contact_no": Glyph(
        "contact_no.png",
        20,
        34,
        {"in": (0.45, 0.00), "out": (0.55, 1.00)},
    ),
    "contact_nc": Glyph(
        "contact_nc.png",
        22,
        36,
        {"in": (0.20, 0.00), "out": (0.20, 1.00)},
    ),
    "pushbutton": Glyph(
        "pushbutton.png",
        30,
        44,
        {"in": (0.62, 0.00), "out": (0.72, 1.00)},
    ),
    "limit_switch": Glyph(
        "limit_switch.png",
        28,
        44,
        {"in": (0.72, 0.00), "out": (0.72, 1.00)},
    ),
    "unloading_valve": Glyph(
        "unloading_valve.png",
        110,
        78,
        {"P": (0.50, 0.02), "T": (0.50, 0.98)},
    ),
    "check_valve": Glyph(
        "check_valve.png",
        56,
        44,
        {"1": (0.00, 0.50), "2": (1.00, 0.50)},
    ),
    "dcv_5_2": Glyph(
        "dcv_5_2.png",
        200,
        151,
        {
            "4": (0.660, 0.038),
            "2": (0.840, 0.038),
            "1": (0.750, 0.962),
            "5": (0.660, 0.962),
            "3": (0.840, 0.962),
        },
    ),
    "dcv_5_3": Glyph(
        "dcv_5_3.png",
        280,
        146,
        {
            "4": (0.44, 0.02),
            "2": (0.56, 0.02),
            "1": (0.50, 1.00),
            "5": (0.44, 0.98),
            "3": (0.56, 0.98),
        },
    ),
    "pressure_switch": Glyph(
        "pressure_switch.png",
        72,
        69,
        {
            "in": (0.80, 0.10),
            "out": (0.84, 0.92),
            "P": (0.10, 0.52),
        },
    ),
    "lamp": Glyph("lamp.png", 69, 103, {"A1": (0.50, 0.00), "A2": (0.50, 1.00)}),
    "dcv_4_3_spring_centered": Glyph(
        "dcv_4_3_spring_centered.png",
        210,
        82,
        {
            "A": (0.48, 0.42),
            "B": (0.57, 0.42),
            "P": (0.48, 0.82),
            "T": (0.57, 0.82),
        },
    ),
    "flow_control": Glyph(
        "flow_control.png",
        48,
        58,
        {"1": (0.00, 0.48), "2": (1.00, 0.48)},
    ),
}


def glyph(gid: str) -> Glyph:
    if gid not in GLYPHS:
        raise KeyError(f"unknown lecture stamp {gid!r} — do not invent a glyph")
    g = GLYPHS[gid]
    if not g.path.is_file():
        raise FileNotFoundError(f"missing lecture stamp {g.path}")
    return g


def stamp(
    svg: SVG,
    gid: str,
    x: float,
    y: float,
    w: float | None = None,
    h: float | None = None,
    *,
    anchor: str = "nw",
    flip_x: bool = False,
) -> dict[str, tuple[float, float]]:
    """Place a lecture PNG. Returns port name → sheet coordinates."""
    g = glyph(gid)
    ww = g.w if w is None else w
    hh = g.h if h is None else h
    if anchor == "center":
        x -= ww / 2
        y -= hh / 2
    svg.image(g.path, x, y, ww, hh, flip_x=flip_x)
    ports = {name: (x + fx * ww, y + fy * hh) for name, (fx, fy) in g.ports.items()}
    if flip_x:
        ports = {name: (x + ww - (sx - x), sy) for name, (sx, sy) in ports.items()}
    return ports


def stamp_dcv_4_3_closed(
    svg: SVG,
    cx: float,
    cy: float,
    tag: str,
    solenoids: list[str],
) -> dict[str, tuple[float, float]]:
    """L3 p4/p7: X | closed centre | parallel, ports on the centre envelope (L3 p5)."""
    env_w, env_h = 54.0, 58.0
    sol_w, sol_h = 50.0, 26.0
    total = 3 * env_w
    x0 = cx - total / 2
    y_env = cy - env_h / 2
    svg.rect(x0, y_env, total, env_h, 1.8)

    stamp(svg, "envelope_cross", x0, y_env, env_w, env_h)
    ports = stamp(svg, "envelope_closed", x0 + env_w, y_env, env_w, env_h)
    stamp(svg, "envelope_parallel", x0 + 2 * env_w, y_env, env_w, env_h)

    left = x0 - sol_w - 6
    right = x0 + total + 6
    if solenoids:
        stamp(svg, "solenoid_box", left, cy - sol_h / 2, sol_w, sol_h)
        svg.line(left + sol_w, cy, x0, cy, 1.4)
        svg.text(left + sol_w / 2, cy + sol_h / 2 + 14, solenoids[0], 11)
    if len(solenoids) > 1:
        stamp(svg, "solenoid_box", right, cy - sol_h / 2, sol_w, sol_h, flip_x=True)
        svg.line(x0 + total, cy, right, cy, 1.4)
        svg.text(right + sol_w / 2, cy + sol_h / 2 + 14, solenoids[1], 11)

    svg.text(x0 - 4, y_env - 8, tag, 12, "start")
    return ports


def _stamp_solenoid_operators(
    svg: SVG,
    x0: float,
    cy: float,
    body_w: float,
    solenoids: list[str],
    *,
    sol_h: float = 42.0,
) -> None:
    """Lecture solenoid_box flush on the envelopes (notes p22, L10 p5)."""
    sol_w = sol_h * 1.75
    left = x0 - sol_w + 4
    right = x0 + body_w - 4
    if solenoids:
        stamp(svg, "solenoid_box", left, cy - sol_h / 2, sol_w, sol_h)
        svg.text(left + sol_w / 2, cy + sol_h / 2 + 14, solenoids[0], 11)
    if len(solenoids) > 1:
        stamp(svg, "solenoid_box", right, cy - sol_h / 2, sol_w, sol_h, flip_x=True)
        svg.text(right + sol_w / 2, cy + sol_h / 2 + 14, solenoids[1], 11)


def stamp_dcv_5_2(
    svg: SVG,
    cx: float,
    cy: float,
    tag: str,
    solenoids: list[str],
) -> dict[str, tuple[float, float]]:
    """ISO 1219-1 5/2; ports on the rest (right) envelope. Lecture solenoid_box."""
    g = glyph("dcv_5_2")
    body_w, body_h = g.w, g.h
    ports = stamp(svg, "dcv_5_2", cx, cy, body_w, body_h, anchor="center")
    x0 = cx - body_w / 2
    y_env = cy - body_h / 2
    _stamp_solenoid_operators(svg, x0, cy, body_w, solenoids, sol_h=42.0)
    svg.text(x0 - 4, y_env - 10, tag, 12, "start")
    return ports


def stamp_dcv_5_3(
    svg: SVG,
    cx: float,
    cy: float,
    tag: str,
    solenoids: list[str],
) -> dict[str, tuple[float, float]]:
    """ISO 1219-1 closed-centre 5/3; ports on the rest (centre) envelope."""
    body_w, body_h = 280.0, 146.0
    ports = stamp(svg, "dcv_5_3", cx, cy, body_w, body_h, anchor="center")
    x0 = cx - body_w / 2
    y_env = cy - body_h / 2
    _stamp_solenoid_operators(svg, x0, cy, body_w, solenoids, sol_h=44.0)
    svg.text(x0 - 4, y_env - 10, tag, 12, "start")
    return ports
