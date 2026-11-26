"""ORACLE: do not use in synthesize."""

from __future__ import annotations

from circuit.spec import CircuitSpec


def spec_trace(spec: CircuitSpec) -> list[dict[str, int]]:
    state = {cid: 0 for cid in spec.cylinders}
    rows = [dict(state)]
    for step in spec.sequence:
        act = step.action
        if act.endswith("+") or act.endswith("_ON"):
            cid = act[: -1 if act.endswith("+") else -3]
            if cid in state:
                state[cid] = 1
        elif act.endswith("-") or act.endswith("_OFF"):
            cid = act[: -1 if act.endswith("-") else -4]
            if cid in state:
                state[cid] = 0
        rows.append(dict(state))
    return rows
