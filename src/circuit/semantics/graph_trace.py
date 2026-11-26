"""Target interpreter. Independent of the synthesizer and of the source oracle."""

from __future__ import annotations

from circuit.ir.graph import CircuitGraph
from circuit.spec import CurrentPath


def _contact_true(tag: str, env: dict[str, bool]) -> bool:
    if tag.startswith("!"):
        return not env.get(tag[1:], False)
    return bool(env.get(tag, False))


def _energized(paths: list[CurrentPath], env: dict[str, bool]) -> set[str]:
    on: set[str] = set()
    changed = True
    while changed:
        changed = False
        for path in paths:
            if not path.coil:
                continue
            if all(_contact_true(c, env) for c in (path.contacts or [])):
                if path.coil not in on:
                    on.add(path.coil)
                    env[path.coil] = True
                    changed = True
    return on


def graph_trace(graph: CircuitGraph, sensor_envs: list[dict[str, bool]]) -> list[dict[str, int]]:
    """Walk sensor assignments. Cylinder bit follows +/− solenoids, else hold."""
    cylinders = [n.id for n in graph.nodes if n.kind == "cylinder"]
    state = {cid: 0 for cid in cylinders}
    rows = []
    env_hold: dict[str, bool] = {}
    for sensors in sensor_envs:
        env = dict(env_hold)
        env.update(sensors)
        on = _energized(graph.paths, env)
        for cid in cylinders:
            plus = graph.solenoid_plus.get(cid)
            minus = graph.solenoid_minus.get(cid)
            if plus and plus in on and minus and minus in on:
                state[cid] = 0
            elif plus and plus in on:
                state[cid] = 1
            elif minus and minus in on:
                state[cid] = 0
        env_hold = {k: v for k, v in env.items() if k.startswith("K")}
        rows.append(dict(state))
    return rows


def sensor_envs_from_positions(
    graph: CircuitGraph,
    positions: list[dict[str, int]],
) -> list[dict[str, bool]]:
    envs = []
    for pos in positions:
        env: dict[str, bool] = {"START": True}
        for cid, bit in pos.items():
            home = graph.sensors_home.get(cid)
            end = graph.sensors_end.get(cid)
            if home:
                env[home] = bit == 0
            if end and end != home:
                env[end] = bit == 1
        envs.append(env)
    return envs
