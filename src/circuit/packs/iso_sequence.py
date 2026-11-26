"""Public ISO sequence pack: vector glyphs plus the two CC-BY 5/2 and 5/3 rasters."""

from __future__ import annotations

from circuit.spec import CircuitSpec
from circuit.validate import Check


def extra_checks(spec: CircuitSpec) -> list[Check]:
    n52 = sum(1 for v in spec.valves.values() if "5_2" in v.type)
    checks = [
        Check("iso_two_5_2", n52 >= 2 or spec.meta.domain.value.startswith("plc") or spec.meta.domain.value.startswith("hydraulic"), str(n52)),
        Check(
            "iso_sequence_len",
            spec.meta.domain.value.startswith("plc")
            or spec.meta.figure_given
            or spec.meta.domain.value.startswith("hydraulic")
            or len(spec.sequence) >= 4,
            str(len(spec.sequence)),
        ),
    ]
    if (spec.meta.method or "") == "cascade":
        from circuit.cascade import apply_cascade, groups_for

        applied = apply_cascade(spec)
        acts = [
            s.action for s in applied.sequence if s.action.rstrip("+-") in applied.cylinders
        ]
        groups = groups_for(acts)
        have = [f"G{i}" in applied.valves for i, _ in enumerate(groups, 1)]
        checks.append(
            Check("cascade_groups", all(have) and bool(groups), str(len(groups)))
        )
    return checks


def compile_override(spec: CircuitSpec):
    """Step memories so sensors from actuator state cannot fire the wrong solenoid."""
    domain = spec.meta.domain.value
    if domain.startswith("plc") or spec.meta.figure_given:
        return None
    motions = [
        s
        for s in spec.sequence
        if s.action.endswith("+") or s.action.endswith("-") or s.action == "TIMER"
    ]
    if len(motions) < 2 or not spec.cylinders:
        return None

    from circuit.compile_sequence import (
        _opposing_solenoid,
        _renumber,
        _solenoid_for,
        _start_and_latch,
        nc,
    )
    from circuit.spec import CurrentPath

    def complete(step) -> str | None:
        if step.action == "TIMER":
            return None
        cid = step.action[:-1]
        cyl = spec.cylinders.get(cid)
        if not cyl or not cyl.sensors:
            return None
        return cyl.sensors[-1] if step.action.endswith("+") else cyl.sensors[0]

    done_tags: list[str | None] = []
    tcount = 0
    for step in motions:
        if step.action == "TIMER":
            tcount += 1
            done_tags.append(f"T{tcount}")
        else:
            done_tags.append(complete(step))

    start, _latch = _start_and_latch(spec)
    n = len(motions)
    ks = [f"K{i}" for i in range(1, n + 1)]
    paths: list[CurrentPath] = []
    tcount = 0
    for i, step in enumerate(motions):
        ki = ks[i]
        nxt = ks[i + 1] if i + 1 < n else None
        if i == 0:
            set_contacts = list(start)
        else:
            set_contacts = [ks[i - 1]]
            prev_done = done_tags[i - 1]
            if prev_done:
                set_contacts.append(prev_done)
        if nxt:
            set_contacts.append(nc(nxt))
        paths.append(CurrentPath(number=0, kind="control", contacts=set_contacts, coil=ki))
        hold = [ki]
        if nxt:
            hold.append(nc(nxt))
        else:
            last_done = done_tags[i]
            if last_done:
                hold.append(nc(last_done))
        paths.append(CurrentPath(number=0, kind="control", contacts=hold, coil=ki))
        if step.action == "TIMER":
            tcount += 1
            sec = max(int(step.seconds or 1), 1)
            paths.append(
                CurrentPath(
                    number=0,
                    kind="control",
                    contacts=[ki],
                    coil=f"T{tcount}_{sec}s",
                )
            )
            continue
        coil = _solenoid_for(spec, step.action)
        if coil:
            contacts = [ki]
            cid = step.action[:-1]
            valve = spec.valves.get(spec.cylinders[cid].dcv) if cid in spec.cylinders else None
            opp = _opposing_solenoid(coil)
            if valve and opp in valve.solenoids:
                contacts.append(nc(opp))
            paths.append(
                CurrentPath(number=0, kind="main", contacts=contacts, coil=coil)
            )
    return _renumber(paths)


def solution_extra(spec: CircuitSpec) -> list[str]:
    return []


def draw_glyph(svg, gid: str, x: float, y: float, w: float, h: float, flip_x: bool = False) -> None:
    """ISO vector fallback when a lecture PNG is absent from the pack stamps dir."""
    if flip_x:
        svg.g_open(transform=f"translate({x + w:.1f},{y:.1f}) scale(-1,1)")
        x, y = 0.0, 0.0
    if gid in {"cylinder_l10", "cylinder_da"}:
        body_w = w * 0.78
        svg.rect(x, y + h * 0.18, body_w, h * 0.64, 1.8)
        svg.rect(x + body_w, y + h * 0.38, w - body_w, h * 0.24, 1.6)
        svg.line(x + w * 0.05, y + h, x + w * 0.05, y + h * 0.82)
        svg.line(x + w * 0.85, y + h, x + w * 0.85, y + h * 0.62)
    elif gid == "solenoid_box":
        svg.rect(x, y, w, h, 1.4)
        svg.rect(x + w * 0.15, y + h * 0.2, w * 0.7, h * 0.6, 1.2)
    elif gid == "contact_no":
        svg.line(x + w * 0.45, y, x + w * 0.45, y + h * 0.28)
        svg.line(x + w * 0.2, y + h * 0.28, x + w * 0.8, y + h * 0.28)
        svg.line(x + w * 0.2, y + h * 0.72, x + w * 0.8, y + h * 0.72)
        svg.line(x + w * 0.55, y + h * 0.72, x + w * 0.55, y + h)
    elif gid == "contact_nc":
        svg.line(x + w * 0.2, y, x + w * 0.2, y + h * 0.28)
        svg.line(x + w * 0.05, y + h * 0.28, x + w * 0.55, y + h * 0.28)
        svg.line(x + w * 0.05, y + h * 0.72, x + w * 0.55, y + h * 0.72)
        svg.line(x + 2, y + h * 0.18, x + w - 2, y + h * 0.82)
        svg.line(x + w * 0.2, y + h * 0.72, x + w * 0.2, y + h)
    elif gid == "pushbutton":
        svg.rect(x + w * 0.25, y + h * 0.35, w * 0.5, h * 0.4, 1.4)
        svg.line(x + w * 0.5, y, x + w * 0.5, y + h * 0.35)
        svg.line(x + w * 0.5, y + h * 0.75, x + w * 0.5, y + h)
    elif gid == "limit_switch":
        svg.rect(x + w * 0.3, y + h * 0.2, w * 0.5, h * 0.6, 1.4)
        svg.line(x + w * 0.72, y, x + w * 0.72, y + h)
    elif gid == "solenoid_coil":
        svg.rect(x + w * 0.2, y + 4, w * 0.6, h - 8, 1.6)
        svg.line(x + w * 0.58, y, x + w * 0.58, y + 4)
        svg.line(x + w * 0.58, y + h - 4, x + w * 0.58, y + h)
    elif gid == "relay_coil":
        svg.rect(x + 8, y + 2, w - 16, h - 4, 1.6)
        svg.circle(x + w / 2, y + h / 2, min(w, h) * 0.18)
    elif gid == "timer_pull_in":
        svg.rect(x, y, w, h, 1.4)
        svg.text(x + w / 2, y + h * 0.7, "T", 10)
    elif gid == "lamp":
        svg.circle(x + w / 2, y + h * 0.45, min(w, h) * 0.28)
        svg.line(x + w / 2, y, x + w / 2, y + h * 0.17)
        svg.line(x + w / 2, y + h * 0.73, x + w / 2, y + h)
    elif gid == "pump_fixed":
        svg.circle(x + w / 2, y + h / 2, min(w, h) * 0.42)
        svg.triangle(
            [
                (x + w * 0.35, y + h * 0.7),
                (x + w * 0.65, y + h * 0.7),
                (x + w * 0.5, y + h * 0.28),
            ],
            fill="#fff",
        )
    elif gid == "tank":
        svg.line(x, y, x + w, y)
        svg.line(x + 4, y + h * 0.45, x + w - 4, y + h * 0.45)
        svg.line(x + 10, y + h * 0.85, x + w - 10, y + h * 0.85)
    elif gid == "filter":
        svg.rect(x + w * 0.2, y, w * 0.6, h, 1.4)
        svg.line(x + w * 0.2, y + h * 0.5, x + w * 0.8, y + h * 0.5)
    elif gid == "prv":
        svg.rect(x, y + h * 0.25, w, h * 0.5, 1.6)
        svg.line(x + w * 0.06, y + h * 0.5, x + w * 0.94, y + h * 0.5)
    elif gid == "envelope_closed":
        svg.rect(x, y, w, h, 1.6)
        svg.line(x + w * 0.32, y + 2, x + w * 0.32, y + h - 2)
        svg.line(x + w * 0.64, y + 2, x + w * 0.64, y + h - 2)
    elif gid in {"envelope_cross", "envelope_parallel"}:
        svg.rect(x, y, w, h, 1.4)
        svg.line(x + 6, y + 6, x + w - 6, y + h - 6)
        if gid == "envelope_cross":
            svg.line(x + w - 6, y + 6, x + 6, y + h - 6)
        else:
            svg.line(x + 6, y + h * 0.35, x + w - 6, y + h * 0.35)
            svg.line(x + 6, y + h * 0.65, x + w - 6, y + h * 0.65)
    else:
        svg.rect(x, y, w, h, 1.2)
    if flip_x:
        svg.g_close()
