"""Independent logical environment. Sensors come from modeled actuator bits.

Do not import the synthesizer. Do not import the source oracle.
Timers are discrete: a coil named T1_3s must stay energized for 3 env steps
before contact T1 becomes true. That is not wall-clock physics.
"""

from __future__ import annotations

import re

from circuit.ir.graph import CircuitGraph
from circuit.semantics.graph_trace import _energized

_TIMER_COIL = re.compile(r"^(T\d+)(?:_(\d+)s)?$")


def sensors_from_state(graph: CircuitGraph, state: dict[str, int]) -> dict[str, bool]:
    env: dict[str, bool] = {}
    for cid, bit in state.items():
        home = graph.sensors_home.get(cid)
        end = graph.sensors_end.get(cid)
        if home:
            env[home] = bit == 0
        if end and end != home:
            env[end] = bit == 1
    return env


def timer_coils(graph: CircuitGraph) -> dict[str, tuple[str, int]]:
    """Map coil id → (done contact, discrete ticks). Independent of spec.sequence."""
    found: dict[str, tuple[str, int]] = {}
    for path in graph.paths:
        coil = path.coil or ""
        m = _TIMER_COIL.match(coil)
        if not m:
            continue
        found[coil] = (m.group(1), max(int(m.group(2) or 1), 1))
    return found


def env_trace(graph: CircuitGraph, *, max_steps: int = 64) -> dict:
    """Press START after rest. Advance from actual state, not the required sequence."""
    cylinders = [n.id for n in graph.nodes if n.kind == "cylinder"]
    rest = {cid: 0 for cid in cylinders}
    state = dict(rest)
    rows = [dict(state)]
    k_hold: dict[str, bool] = {}
    conflict = None
    deadlock = None
    transitions = 0
    exhausted = False
    prev_on: set[str] | None = None
    timers = timer_coils(graph)
    ticks: dict[str, int] = {coil: 0 for coil in timers}
    done: dict[str, bool] = {name: False for name, _ in timers.values()}
    for t in range(max_steps):
        env = dict(k_hold)
        env["START"] = True
        env.update(sensors_from_state(graph, state))
        for name, fired in done.items():
            env[name] = fired
        on = _energized(graph.paths, dict(env))
        charging = False
        for coil, (name, need) in timers.items():
            if coil in on and not done.get(name):
                ticks[coil] += 1
                charging = True
                if ticks[coil] >= need:
                    done[name] = True
            elif coil not in on and not done.get(name):
                ticks[coil] = 0
        nxt = dict(state)
        for cid in cylinders:
            plus = graph.solenoid_plus.get(cid)
            minus = graph.solenoid_minus.get(cid)
            plus_on = bool(plus and plus in on)
            minus_on = bool(minus and minus in on)
            if plus_on and minus_on:
                conflict = {
                    "cylinder": cid,
                    "plus": plus,
                    "minus": minus,
                    "step": t + 1,
                }
                break
            if plus_on:
                nxt[cid] = 1
            elif minus_on:
                nxt[cid] = 0
        k_hold = {k: True for k in on if str(k).startswith("K")}
        rows.append(dict(nxt))
        if conflict:
            break
        if nxt != state:
            transitions += 1
        if nxt == rest and state != rest:
            break
        if nxt == state and prev_on == on and t > 0 and not charging:
            if nxt != rest:
                deadlock = {"step": t + 1, "state": dict(nxt), "on": sorted(on)}
            break
        prev_on = set(on)
        state = nxt
    else:
        exhausted = conflict is None and deadlock is None
    return {
        "rows": rows,
        "conflict": conflict,
        "deadlock": deadlock,
        "transitions": transitions,
        "states": len(rows),
        "exhausted": exhausted,
        "max_steps": max_steps,
        "valve_memory": dict(state),
        "timers_done": dict(done),
    }


def compress_changes(rows: list[dict[str, int]]) -> list[dict[str, int]]:
    if not rows:
        return []
    out = [rows[0]]
    for row in rows[1:]:
        if row != out[-1]:
            out.append(row)
    return out
