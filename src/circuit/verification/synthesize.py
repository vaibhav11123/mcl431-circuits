"""Bounded synthesis: two legal 5/2 topologies, pick fewer valves."""

from __future__ import annotations

from circuit.spec import CircuitSpec, Valve


def two_topologies(spec: CircuitSpec) -> list[CircuitSpec]:
    a = spec.model_copy(deep=True)
    b = spec.model_copy(deep=True)
    vtype = next(iter(spec.valves.values())).type if spec.valves else "dcv_5_2_double_solenoid"
    if "G1" not in b.valves:
        b.valves["G1"] = Valve(type=vtype, solenoids=["G1Y1", "G1Y2"])
    return [a, b]


def pick_smaller(specs: list[CircuitSpec]) -> CircuitSpec:
    return min(specs, key=lambda s: len(s.valves))
