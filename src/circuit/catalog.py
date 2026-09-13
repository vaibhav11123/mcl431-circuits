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
        210,
        86,
        {"cap": (0.38, 0.98), "rod": (0.84, 0.98)},
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
        {"A": (0.48, 0.02), "B": (0.48, 0.98)},
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
