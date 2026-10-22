"""Electrical sheet: L8 stamps, de-energized."""

from __future__ import annotations

import re
from pathlib import Path

from circuit.catalog import glyph, stamp
from circuit.compile_sequence import _start_and_latch, apply_compile
from circuit.spec import CircuitSpec, CurrentPath, Domain
from circuit.svgdraw import SVG
from circuit.terminals import bare, contact_actuated, contact_kind, contact_terminals


def _coil_glyph(tag: str) -> str:
    if tag.startswith("H"):
        return "lamp"
    if "Y" in tag:
        return "solenoid_coil"
    if tag.startswith("T1"):
        return "timer_pull_in"
    return "relay_coil"


_MAX_COLS = 14


def _grid(n: int, *, n_control: int = 0, tight: bool = False) -> tuple[int, int]:
    # Notes p24: pneumatic relay sheets — control row, then main row.
    if tight and n <= 16:
        if 0 < n_control <= 8 and n_control < n:
            max_cols = n_control
        else:
            max_cols = 8
    else:
        max_cols = _MAX_COLS
    if n <= max_cols:
        return n, 1
    return max_cols, (n + max_cols - 1) // max_cols


def _sequence_banner(spec: CircuitSpec, *, compact: bool = False) -> str:
    start = "  ∧  ".join(_start_and_latch(spec)[0])
    if compact:
        actions = "  →  ".join(
            "T1"
            if st.action == "TIMER"
            else "PS≥4 bar"
            if st.action in {"PS", "PRESSURE"}
            else st.action.replace("_ON", " ON")
            for st in spec.sequence
        )
        return f"{start}   →   {actions}"
    steps = []
    for i, st in enumerate(spec.sequence, 1):
        if st.action == "TIMER":
            steps.append(f"{i}. T1={int(st.seconds or 0)}s")
        elif st.action in {"PS", "PRESSURE"}:
            steps.append(f"{i}. PS≥4 bar")
        elif st.action.endswith("_ON"):
            steps.append(f"{i}. {st.action.replace('_ON', ' ON')}")
        else:
            steps.append(f"{i}. {st.action}")
    return f"{start}   →   " + "   →   ".join(steps)


def _table_key(coil: str | None) -> str | None:
    if not coil:
        return None
    if re.fullmatch(r"K\d+", coil):
        return coil
    if coil.startswith("T1"):
        return "T1"
    return None


def _k_index_then_bump(c: str, k_index_by_tag: dict[str, int]) -> int:
    name = bare(c)
    if not name.startswith("K"):
        return 0
    idx = k_index_by_tag.get(name, 0)
    k_index_by_tag[name] = idx + 1
    return idx


def _aux_terms_for_coil(paths: list[CurrentPath], coil_name: str) -> str:
    seen: set[str] = set()
    tokens: list[str] = []
    for path in paths:
        k_index_by_tag: dict[str, int] = {}
        for c in path.contacts or []:
            idx = _k_index_then_bump(c, k_index_by_tag)
            if bare(c) != coil_name:
                continue
            a, b = contact_terminals(c, idx)
            token = f"{a}/{b}"
            if token not in seen:
                seen.add(token)
                tokens.append(token)
    return ", ".join(tokens)


def draw_electrical(spec: CircuitSpec, dest: Path) -> Path:
    spec = apply_compile(spec)
    dest.parent.mkdir(parents=True, exist_ok=True)
    paths = spec.electrical.paths
    n = max(len(paths), 1)
    n_control = sum(1 for p in paths if p.kind != "main")
    tight = spec.meta.domain == Domain.PNEUMATIC_PLUS_ELECTRICAL
    n_cols, n_rows = _grid(n, n_control=n_control, tight=tight)
    col_w = 128 if n > 10 else 140
    width = max(90 + n_cols * col_w + 50, 980)
    max_c = max((len(p.contacts or []) for p in paths), default=0)
    coil_y_base = max(430, 128 + max_c * 62 + 36)
    table_h = 72 if any(_table_key(p.coil) for p in paths) else 0
    y0 = coil_y_base + 70
    row_pitch = y0 + 48 + table_h + 36
    height = n_rows * row_pitch
    s = SVG(width, height)
    s.text(width / 2, 16, "Electrical control circuit  ·  lecture L8 stamps  ·  de-energized", 14)
    s.text(width / 2, 36, _sequence_banner(spec, compact=n_rows > 1), 11)
    y24 = 62
    for r in range(n_rows):
        dy = r * row_pitch
        s.line(36, y24 + dy, width - 16, y24 + dy, 2)
        s.line(36, y0 + dy, width - 16, y0 + dy, 2)
        s.circle(36, y24 + dy, 3.5)
        s.circle(36, y0 + dy, 3.5)
        s.text(28, y24 + dy + 4, "+24 V", 12, "end")
        s.text(28, y0 + dy + 4, "0 V", 12, "end")

    for i, path in enumerate(paths):
        r, c = divmod(i, n_cols)
        dy = r * row_pitch
        x = 88 + c * col_w
        s.text(x, 54 + dy, str(path.number), 13)
        s.dot(x, y24 + dy)
        s.line(x, y24 + dy, x, 100 + dy)
        y = 128 + dy
        prev_bottom = 100 + dy
        k_index_by_tag: dict[str, int] = {}
        for contact in path.contacts or []:
            kind = contact_kind(contact)
            gid = "contact_nc" if contact.startswith("!") and kind != "contact_nc" else kind
            k_index = _k_index_then_bump(contact, k_index_by_tag)
            a, b = contact_terminals(contact, k_index)
            act = contact_actuated(contact)
            gdef = glyph(gid)
            fx, fy_in = gdef.ports.get("in", (0.5, 0.0))
            fy_out = gdef.ports.get("out", (0.5, 1.0))[1]
            cx = x - (fx - 0.5) * gdef.w
            top_y = y - gdef.h / 2 + fy_in * gdef.h
            bot_y = y - gdef.h / 2 + fy_out * gdef.h
            s.line(x, prev_bottom, x, top_y)
            s.g_open(
                data_tag=bare(contact),
                data_terms=f"{a},{b}",
                data_actuated=str(act).lower(),
            )
            g = stamp(s, gid, cx, y, anchor="center")
            top_y = g.get("in", (x, top_y))[1]
            bot_y = g.get("out", (x, bot_y))[1]
            s.text(x - 12, top_y + 8, a, 8, "end")
            s.text(x - 12, bot_y + 2, b, 8, "end")
            s.text(x + 18, y + 4, bare(contact), 11, "start")
            if act:
                s.polyline([(x - 24, y - 3), (x - 18, y), (x - 24, y + 3)], sw=1.2)
            s.g_close()
            prev_bottom = bot_y
            y += 62
        coil_y = max(430 + dy, prev_bottom + 36)
        s.line(x, prev_bottom, x, coil_y - 14)
        rail_0 = y0 + dy
        if path.coil:
            gid = _coil_glyph(path.coil)
            coil = stamp(s, gid, x, coil_y, anchor="center")
            label = path.coil
            if gid == "timer_pull_in":
                s.text(x + 36, coil_y + 5, label, 10, "start")
            else:
                s.text(x + 28, coil_y + 5, label, 10, "start")
            a1 = coil.get("A1", (x, coil_y - 12))
            a2 = coil.get("A2", (x, coil_y + 12))
            s.text(a1[0] - 10, a1[1] + 8, "A1", 8, "end")
            s.text(a2[0] - 10, a2[1] + 2, "A2", 8, "end")
            s.line(x, a2[1], x, rail_0)
        else:
            s.line(x, coil_y - 14, x, rail_0)
        s.dot(x, rail_0)

    for i, path in enumerate(paths):
        key = _table_key(path.coil)
        if not key:
            continue
        r, c = divmod(i, n_cols)
        dy = r * row_pitch
        x = 88 + c * col_w
        title = "T1" if key == "T1" else path.coil or key
        aux = _aux_terms_for_coil(paths, key)
        ty = y0 + dy + 18
        s.text(x, ty, title, 9)
        s.text(x, ty + 14, "A1/A2", 8)
        if aux:
            s.text(x, ty + 28, aux, 8)

    n_control = sum(1 for p in paths if p.kind != "main")
    if 0 < n_control < len(paths):
        if n_rows == 1:
            split_x = 88 + n_control * col_w - col_w / 2 + 70
            s.line(split_x, 56, split_x, y0 + 8, 0.8, "#888888")
            label_y = y0 + (table_h + 8 if table_h else 36)
            s.text((88 + (n_control - 1) * col_w + 88) / 2, label_y, "signal / control section", 11)
            s.text(
                (88 + n_control * col_w + 88 + (len(paths) - 1) * col_w) / 2,
                label_y,
                "main ckt",
                11,
            )
        elif n_cols == n_control:
            s.text(width / 2, y0 + (table_h + 8 if table_h else 20), "signal / control section", 11)
            s.text(width / 2, y0 + row_pitch + 20, "main ckt", 11)
        else:
            s.text(width / 2, height - 14, "signal / control section  ·  main ckt", 11)

    dest.write_text(s.tostring())
    return dest
