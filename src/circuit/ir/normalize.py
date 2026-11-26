from __future__ import annotations

from circuit.spec import CircuitSpec


def normalize(spec: CircuitSpec) -> CircuitSpec:
    out = spec.model_copy(deep=True)
    out.cylinders = dict(sorted(out.cylinders.items()))
    out.valves = dict(sorted(out.valves.items()))
    return out
