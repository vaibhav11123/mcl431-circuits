"""Step-displacement diagram: L10 p4 method."""

from __future__ import annotations

from pathlib import Path

from circuit.compile_sequence import _start_and_latch
from circuit.spec import CircuitSpec
from circuit.svgdraw import SVG


def _next_state(action: str, act: str, cur: int, *, is_motor: bool = False) -> int:
    if action in {f"{act}+", f"{act}_ON"}:
        return 1
    if action in {f"{act}-", f"{act}_OFF"}:
        return 0
    # Paper never says HM1_OFF; drop the motor when the first retract starts
    # (after 2B2 + timer), not through unclamp.
    if is_motor and cur == 1 and action.endswith("-"):
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
    s.text(left, 46, "  ∧  ".join(_start_and_latch(spec)[0]), 12, "start")

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
        is_motor = act in spec.motors
        for i, st in enumerate(steps):
            nxt = _next_state(st.action, act, cur, is_motor=is_motor)
            x1 = left + i * step_w
            x2 = left + (i + 1) * step_w
            yc = y0 if cur == 0 else y1
            yn = y0 if nxt == 0 else y1
            if is_motor and nxt != cur:
                s.line(x1, yc, x1, yn, 2.4, color)
                s.line(x1, yn, x2, yn, 2.4, color)
            else:
                s.line(x1, yc, x2, yn, 2.4, color)
            if nxt != cur:
                tag = _sensor_at_edge(spec, act, nxt)
                if tag:
                    s.text(x2 + 2, yn - 6 if nxt == 1 else yn + 14, tag, 10, "start", color)
                    s.polyline(
                        [
                            (x2, yn),
                            (x2 + 12, yn),
                            (x2 + 8, yn - 3),
                            (x2 + 12, yn),
                            (x2 + 8, yn + 3),
                        ],
                        1.2,
                        color,
                    )
                elif is_motor and nxt == 0:
                    s.text(x1 + 4, yn + 14, f"{act} OFF", 10, "start", color)
            cur = nxt

    dest.write_text(s.tostring())
    return dest
