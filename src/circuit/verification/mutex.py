from __future__ import annotations

from itertools import product

from circuit.ir.graph import CircuitGraph
from circuit.semantics.graph_trace import _energized


def start_dual_solenoid(graph: CircuitGraph) -> dict:
    """Planted miscompile: START alone energizes both solenoids of one valve."""
    env: dict[str, bool] = {"START": True}
    on = _energized(graph.paths, dict(env))
    for cid, plus in graph.solenoid_plus.items():
        minus = graph.solenoid_minus.get(cid)
        if plus in on and minus and minus in on:
            return {"ok": False, "cex": {"cylinder": cid, "plus": plus, "minus": minus}}
    return {"ok": True, "cex": None}


def mutex_explore(graph: CircuitGraph, timeout_s: float = 2.0) -> dict:
    """Bounded BFS of sensor combinations. Dual solenoids ON is a cex."""
    sensors = sorted({*graph.sensors_home.values(), *graph.sensors_end.values()} - {""})
    sensors = [s for s in sensors if s]
    if len(sensors) > 8:
        sensors = sensors[:8]
    cex = None
    for bits in product([False, True], repeat=len(sensors)):
        env = {"START": True}
        env.update(dict(zip(sensors, bits)))
        on = _energized(graph.paths, dict(env))
        for cid, plus in graph.solenoid_plus.items():
            minus = graph.solenoid_minus.get(cid)
            if plus in on and minus in on:
                cex = {"cylinder": cid, "plus": plus, "minus": minus, "env": env}
                return {"ok": False, "cex": cex}
    return {"ok": True, "cex": None}
