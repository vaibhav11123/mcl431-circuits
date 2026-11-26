from __future__ import annotations

from circuit.ir.graph import CircuitGraph, GraphEdge
from circuit.ir.ports import Port, compatible
from circuit.spec import CircuitSpec
from circuit.validate import Check, validate_spec

_FLUID = {"P", "T", "A", "B", "1", "2", "3", "4", "5", "S"}


def typecheck(spec: CircuitSpec, root=None) -> list[Check]:
    from circuit.pack import engine_pack

    pack = engine_pack()
    checks = validate_spec(spec, pack.root if root is None else root)
    for path in spec.electrical.paths:
        coil = path.coil or ""
        if coil in _FLUID:
            checks.append(
                Check(
                    "E210",
                    False,
                    "E210 Compatible fluid-domain port cannot be a coil tag",
                )
            )
    return checks


def _ports_of(edge: GraphEdge) -> tuple[Port | None, Port | None]:
    src = edge.src_typed
    dst = edge.dst_typed
    if src is None and edge.src_port in _FLUID:
        src = Port(
            component_id=edge.src,
            port_id=edge.src_port,
            domain="fluid",
            role="supply" if edge.src_port in {"P", "S"} else "actuator",
        )
    if dst is None and edge.dst_port in _FLUID:
        dst = Port(
            component_id=edge.dst,
            port_id=edge.dst_port,
            domain="fluid",
            role="actuator",
        )
    return src, dst


def typecheck_graph(graph: CircuitGraph) -> list[Check]:
    checks: list[Check] = []
    kinds = {n.id: n.kind for n in graph.nodes}
    domains = {n.id: n.domain for n in graph.nodes}
    for e in graph.edges:
        src_p, dst_p = _ports_of(e)
        if src_p and dst_p and not compatible(src_p, dst_p):
            checks.append(
                Check(
                    "E210",
                    False,
                    "E210 Compatible fluid-domain port mixed with electrical",
                )
            )
            continue
        src_d = domains.get(e.src, src_p.domain if src_p else "fluid")
        dst_d = domains.get(e.dst, dst_p.domain if dst_p else "electrical")
        if src_d != dst_d and {src_d, dst_d} == {"fluid", "electrical"}:
            checks.append(
                Check(
                    "E210",
                    False,
                    "E210 Compatible fluid-domain port mixed with electrical",
                )
            )
        elif e.src_port in _FLUID and kinds.get(e.dst) in {"coil", "contact"}:
            checks.append(
                Check(
                    "E210",
                    False,
                    "E210 Compatible fluid-domain port cannot drive a coil",
                )
            )
    if not any(not c.ok for c in checks):
        checks.append(Check("ports", True, "ok"))
    return checks
