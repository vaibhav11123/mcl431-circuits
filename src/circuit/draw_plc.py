"""PLC connection diagram + ladder from spec.plc IR (not L8)."""

from __future__ import annotations

import re
from pathlib import Path

from circuit.calc import resolve_plc_counts
from circuit.catalog import stamp
from circuit.spec import CircuitSpec, PlcBlock, PlcElement, PlcRung
from circuit.svgdraw import SVG

# Operator pushbuttons get PB stamp; LS/prox/analog get plain field boxes.
_PB_DEVICE = re.compile(
    r"^(PB|START|STOP|S\d+|GO|RESET|ESTOP|E-STOP)(_.*)?$",
    re.IGNORECASE,
)


def _is_operator_pb(device: str, function: str = "") -> bool:
    d = (device or "").strip()
    if _PB_DEVICE.match(d):
        return True
    fl = (function or "").lower()
    return "push" in fl or "button" in fl or fl.startswith("alternate")


def _sub_counts(text: str, counts: dict[str, int]) -> str:
    out = text
    for k, v in counts.items():
        out = out.replace("{" + k + "}", str(v))
    return out


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


def _require_plc(spec: CircuitSpec) -> PlcBlock:
    if spec.plc is None:
        raise ValueError(f"domain plc requires plc: block ({spec.meta.exam_id})")
    return spec.plc


def _fmt_elem(el: PlcElement, counts: dict[str, int]) -> str:
    if el.kind == "contact":
        return el.label or el.tag or el.kind
    if el.kind == "cmp":
        right = el.right
        if el.right_from:
            right = str(counts.get(el.right_from, el.right_from))
        op = el.op or "CMP"
        left = el.left or "AI"
        return f"{left} {op} {right}"
    if el.kind == "mov":
        val: str | int | float | None = el.value
        if el.value_from:
            val = counts.get(el.value_from, el.value_from)
        dest = el.dest or "AO"
        return f"MOV {val} → {dest}"
    if el.kind == "ctu":
        preset = el.preset if el.preset is not None else "?"
        return f"CTU {el.tag or 'C5:0'} PV={preset}"
    if el.kind == "ton":
        preset = el.preset if el.preset is not None else "?"
        return f"TON {el.tag or 'T4:0'} PT={preset}s"
    if el.kind == "res":
        return f"RES {el.tag or el.label}"
    if el.kind == "ons":
        return el.label or f"ONS {el.tag}".strip() or "ONS"
    if el.kind == "otl":
        return el.label or f"(L) {el.tag}".strip() or "(L)"
    if el.kind == "otu":
        return el.label or f"(U) {el.tag}".strip() or "(U)"
    if el.kind == "coil":
        return el.label or el.tag
    if el.kind == "block":
        return el.text or el.label or el.tag
    return el.label or el.tag or el.kind


def _instr_lines(el: PlcElement, counts: dict[str, int]) -> tuple[str, str]:
    """Top title + bottom operand line for instruction blocks."""
    if el.kind == "cmp":
        right = el.right
        if el.right_from:
            right = str(counts.get(el.right_from, el.right_from))
        return "CMP", f"{el.left or 'AI'} {el.op or ''} {right}".strip()
    if el.kind == "mov":
        val: str | int | float | None = el.value
        if el.value_from:
            val = counts.get(el.value_from, el.value_from)
        return "MOV", f"{val} → {el.dest or 'AO'}"
    if el.kind == "ctu":
        preset = el.preset if el.preset is not None else "?"
        return "CTU", f"{el.tag or 'C5:0'}  PV={preset}"
    if el.kind == "ton":
        preset = el.preset if el.preset is not None else "?"
        return "TON", f"{el.tag or 'T4:0'}  PT={preset}s"
    if el.kind == "res":
        return "RES", el.tag or el.label or ""
    if el.kind == "ons":
        return "ONS", el.tag or el.label or ""
    if el.kind == "block":
        text = el.text or el.label or el.tag
        parts = text.split(None, 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return text, ""
    return el.kind.upper(), el.label or el.tag or ""


def _contact(s: SVG, x: float, y: float, label: str, *, nc: bool = False, w: float = 72) -> float:
    """IEC-ish NO/NC: two vertical ticks + gap; NC adds diagonal slash."""
    tick = 14.0
    gap = 10.0
    mid = x + w / 2
    left_tick = mid - gap / 2 - 1
    right_tick = mid + gap / 2 + 1
    s.line(x, y, left_tick - tick / 2, y)
    s.line(left_tick - tick / 2, y - tick / 2, left_tick - tick / 2, y + tick / 2)
    s.line(right_tick + tick / 2, y - tick / 2, right_tick + tick / 2, y + tick / 2)
    s.line(right_tick + tick / 2, y, x + w, y)
    if nc:
        s.line(mid - 10, y + 12, mid + 10, y - 12)
    s.text(mid, y - 22, label, 10)
    return x + w


def _coil(s: SVG, x: float, y: float, label: str, *, style: str = "coil") -> None:
    """Circle coil; OTL/OTU show L/U inside."""
    cx, cy, r = x + 22, y, 18
    s.circle(cx, cy, r)
    if style == "otl":
        s.text(cx, cy + 5, "L", 14)
    elif style == "otu":
        s.text(cx, cy + 5, "U", 14)
    else:
        s.text(cx, cy + 5, ")", 12)  # hint of ( ) pair; left paren drawn below
        s.text(cx - 8, cy + 5, "(", 12)
    s.text(cx, cy + 36, label, 10)


def _block(s: SVG, x: float, y: float, title: str, detail: str = "", w: float = 160) -> float:
    """Instruction block: kind on top line, operands below."""
    h = 36 if detail else 28
    s.rect(x, y - h / 2, w, h)
    if detail:
        s.text(x + w / 2, y - 4, title, 11)
        s.text(x + w / 2, y + 12, detail, 10)
    else:
        s.text(x + w / 2, y + 5, title, 11)
    return x + w


def _elem_width(el: PlcElement, counts: dict[str, int]) -> float:
    if el.kind == "contact":
        lab = _fmt_elem(el, counts)
        return min(120, max(64, 10 + 6.5 * len(lab)))
    if el.kind in {"cmp", "mov", "ctu", "ton", "res", "ons", "block"}:
        title, detail = _instr_lines(el, counts)
        span = max(len(title), len(detail), 8)
        return min(200, max(100, 12 + 6.5 * span))
    lab = _fmt_elem(el, counts)
    return min(130, max(88, 12 + 7 * len(lab)))


def _draw_series_elem(
    s: SVG,
    el: PlcElement,
    x: float,
    y: float,
    counts: dict[str, int],
) -> float:
    if el.kind == "contact":
        nc = el.sense.upper() == "NC"
        return _contact(s, x, y, _fmt_elem(el, counts), nc=nc, w=_elem_width(el, counts))
    if el.kind in {"cmp", "mov", "ctu", "ton", "res", "ons", "block"}:
        title, detail = _instr_lines(el, counts)
        return _block(s, x, y, title, detail, w=_elem_width(el, counts))
    # fallback
    return _block(s, x, y, _fmt_elem(el, counts), w=_elem_width(el, counts))


def draw_plc_connection(spec: CircuitSpec, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    plc = _require_plc(spec)
    counts = resolve_plc_counts(plc.scaling) if plc.scaling else {}
    n_io = max(len(plc.io), 1)
    height = max(1100, 420 + n_io * 28 + len(plc.field) * 140 + len(plc.scale_table) * 30)
    s = SVG(1080, height)

    _title(s, spec, plc.subtitle_connection)

    s.text(40, 90, "1. I/O assignment", 14, "start")
    rows = [[r.address, r.device, r.function] for r in plc.io]
    y = _table(s, 40, 104, ["Address", "Device", "Function"], rows, [180, 180, 400])

    s.text(40, y + 36, "2. Field devices to PLC", 14, "start")
    field_y = y + 52
    if plc.field:
        box_w = min(300, 980 // max(len(plc.field), 1))
        for i, fb in enumerate(plc.field):
            x = 40 + i * (box_w + 24)
            h = 46 + 18 * max(len(fb.lines), 1)
            _box(s, x, field_y, box_w, h, fb.title, fb.lines)
        field_bottom = field_y + 46 + 18 * max(max(len(f.lines) for f in plc.field), 1) + 20
    else:
        plc_lines = [f"{r.address}  {r.device}" for r in plc.io[:12]]
        _box(s, 380, field_y, 320, 46 + 18 * max(len(plc_lines), 1), "PLC", plc_lines)
        field_bottom = field_y + 46 + 18 * max(len(plc_lines), 1) + 20

    discrete_in = [r for r in plc.io if r.address.startswith("I")]
    discrete_out = [r for r in plc.io if r.address.startswith("Q")]
    pb_y = field_bottom + 24
    if discrete_in:
        s.text(40, pb_y, "Digital 24 V field", 14, "start")
        s.text(40, pb_y + 22, "+24 V", 12, "start")
        s.line(90, pb_y + 18, 520, pb_y + 18, sw=2.0)
        for i, row in enumerate(discrete_in[:5]):
            xx = 110 + i * 100
            if _is_operator_pb(row.device, row.function):
                start_p = stamp(s, "pushbutton", xx, pb_y + 40, w=36, h=52)
                s.line(xx + 18, pb_y + 18, start_p["in"][0], start_p["in"][1])
                s.line(start_p["out"][0], start_p["out"][1], xx + 18, pb_y + 160)
            else:
                # Limit / prox / sensor — labeled box, not PB glyph
                s.rect(xx, pb_y + 48, 56, 40)
                s.text(xx + 28, pb_y + 72, row.device[:6], 10)
                s.line(xx + 28, pb_y + 18, xx + 28, pb_y + 48)
                s.line(xx + 28, pb_y + 88, xx + 28, pb_y + 160)
            s.text(xx + 18, pb_y + 110, row.device[:10], 11)
            s.text(xx + 18, pb_y + 128, row.address, 10)
        s.line(110, pb_y + 160, 520, pb_y + 160)
        s.text(300, pb_y + 152, "to PLC DI", 11)
        s.text(40, pb_y + 188, "0 V  ——— PLC COM", 12, "start")

    if discrete_out:
        lamp_y = pb_y
        s.text(620, lamp_y, "Discrete outputs", 14, "start")
        for i, row in enumerate(discrete_out[:6]):
            xx = 620 + (i % 3) * 90
            yy = lamp_y + 20 + (i // 3) * 120
            stamp(s, "lamp", xx, yy, w=42, h=62)
            s.text(xx + 21, yy + 80, row.device[:8], 10)
            s.text(xx + 21, yy + 96, row.address, 10)

    ay = pb_y + 220
    if plc.scale_table:
        s.text(40, ay, "3. Scaling / zone table", 14, "start")
        headers = plc.scale_headers or [f"C{i}" for i in range(len(plc.scale_table[0]))]

        def _sub(cell: str) -> str:
            out = cell
            for k, v in counts.items():
                out = out.replace("{" + k + "}", str(v))
            return out

        rendered = [[_sub(c) for c in row] for row in plc.scale_table]
        widths = [max(80, 900 // max(len(headers), 1))] * len(headers)
        if len(headers) == 5:
            widths = [80, 280, 80, 120, 80]
        elif len(headers) == 6:
            widths = [150, 150, 120, 120, 120, 80]
        y2 = _table(s, 40, ay + 16, headers, rendered, widths)
        ay = y2 + 20
    elif plc.scaling and counts:
        s.text(40, ay, "3. Resolved analog counts", 14, "start")
        count_rows = [[k, str(v)] for k, v in sorted(counts.items())]
        ay = _table(s, 40, ay + 16, ["Name", "Counts"], count_rows, [220, 120]) + 20

    note_y = ay + 24
    for i, note in enumerate(plc.notes):
        s.text(40, note_y + i * 20, _sub_counts(note, counts), 12, "start")

    dest.write_text(s.tostring())
    return dest


def _rung_span(rung: PlcRung, counts: dict[str, int]) -> float:
    """Rough horizontal demand for dynamic spacing."""
    w = 80.0
    for el in rung.series:
        w += _elem_width(el, counts) + 14
    if rung.branch:
        w += 40
    w += 100  # coil / instruction
    return w


def _draw_rung(
    s: SVG,
    rung: PlcRung,
    *,
    left: float,
    right: float,
    y: float,
    counts: dict[str, int],
) -> None:
    s.text(left + 8, y - 28, f"{rung.id}  {rung.caption}", 12, "start")
    s.line(left, y, 80, y)
    x = 80.0

    if rung.branch and rung.series:
        first = rung.series[0]
        x_end = _draw_series_elem(s, first, x, y, counts)
        merge_x = max(x_end + 20, 280)
        s.line(x_end, y, merge_x, y)
        s.line(x, y, x, y + 44)
        bx = x + 30
        s.line(x, y + 44, bx, y + 44)
        for bel in rung.branch:
            bx = _draw_series_elem(s, bel, bx, y + 44, counts)
            s.line(bx, y + 44, bx + 12, y + 44)
            bx += 12
        s.line(bx, y + 44, merge_x, y + 44)
        s.line(merge_x, y + 44, merge_x, y)
        x = merge_x
        rest = rung.series[1:]
    else:
        rest = rung.series

    for el in rest:
        x = _draw_series_elem(s, el, x, y, counts)
        s.line(x, y, x + 14, y)
        x += 14

    out = rung.output
    if out is None:
        s.line(x, y, right, y)
        return

    if out.kind == "coil":
        s.line(x, y, right - 70, y)
        _coil(s, right - 70, y, _fmt_elem(out, counts), style="coil")
        s.line(right - 26, y, right, y)
    elif out.kind == "otl":
        s.line(x, y, right - 70, y)
        _coil(s, right - 70, y, _fmt_elem(out, counts), style="otl")
        s.line(right - 26, y, right, y)
    elif out.kind == "otu":
        s.line(x, y, right - 70, y)
        _coil(s, right - 70, y, _fmt_elem(out, counts), style="otu")
        s.line(right - 26, y, right, y)
    elif out.kind in {"mov", "ctu", "ton", "res", "ons", "block", "cmp"}:
        title, detail = _instr_lines(out, counts)
        w = min(200, max(140, 10 + 7 * max(len(title), len(detail))))
        if x + w + 20 > right:
            w = max(100, right - x - 20)
        x = _block(s, x, y, title, detail, w=w)
        s.line(x, y, right, y)
    else:
        s.line(x, y, right - 70, y)
        _coil(s, right - 70, y, _fmt_elem(out, counts))
        s.line(right - 26, y, right, y)


def draw_plc_ladder(spec: CircuitSpec, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    plc = _require_plc(spec)
    counts = resolve_plc_counts(plc.scaling) if plc.scaling else {}
    n = max(len(plc.rungs), 1)
    # Dynamic rung pitch from contact density (fan CMP chains need room)
    pitches: list[float] = []
    for rung in plc.rungs:
        span = _rung_span(rung, counts)
        base = 118.0
        if rung.branch:
            base += 36
        if span > 900:
            base += 20
        n_cmp = sum(1 for e in rung.series if e.kind == "cmp")
        if n_cmp >= 3:
            base += 12
        pitches.append(base)
    if not pitches:
        pitches = [125.0]
    height = max(900, 180 + int(sum(pitches)) + 100)
    s = SVG(1080, height)
    _title(s, spec, plc.subtitle_ladder)

    if plc.notes:
        s.text(40, 74, _sub_counts(plc.notes[0], counts)[:140], 12, "start")

    left, right = 70, 1020
    y0 = 155.0
    ys: list[float] = []
    y = y0
    for i, p in enumerate(pitches):
        ys.append(y)
        if i + 1 < len(pitches):
            y += p
    s.line(left, ys[0] - 24, left, ys[-1] + 50, sw=2.2)
    s.line(right, ys[0] - 24, right, ys[-1] + 50, sw=2.2)
    s.text(left - 8, ys[0] + 4, "+24 V", 11, "end")
    s.text(right + 8, ys[0] + 4, "COM", 11, "start")

    for i, rung in enumerate(plc.rungs):
        _draw_rung(s, rung, left=left, right=right, y=ys[i], counts=counts)

    if len(plc.notes) > 1:
        s.text(40, ys[-1] + 80, _sub_counts(plc.notes[1], counts)[:160], 12, "start")

    dest.write_text(s.tostring())
    return dest
