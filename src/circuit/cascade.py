"""Cascade group split using existing 5/2 valves only."""

from __future__ import annotations

from circuit.spec import CircuitSpec, Valve


def groups_for(actions: list[str]) -> list[list[str]]:
    groups: list[list[str]] = [[]]
    seen: set[str] = set()
    for act in actions:
        letter = act.rstrip("+-")
        if not letter:
            groups[-1].append(act)
            continue
        if letter in seen:
            groups.append([act])
            seen = {letter}
        else:
            groups[-1].append(act)
            seen.add(letter)
    return [g for g in groups if g]


def apply_cascade(spec: CircuitSpec) -> CircuitSpec:
    out = spec.model_copy(deep=True)
    acts = [s.action for s in out.sequence if s.action.rstrip("+-") in out.cylinders]
    groups = groups_for(acts)
    vtype = next(iter(out.valves.values())).type if out.valves else "dcv_5_2_double_solenoid"
    for i, _ in enumerate(groups, 1):
        gid = f"G{i}"
        if gid not in out.valves:
            out.valves[gid] = Valve(type=vtype, solenoids=[f"{gid}Y1", f"{gid}Y2"])
    return out
