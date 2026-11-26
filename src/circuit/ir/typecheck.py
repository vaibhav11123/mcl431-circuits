from __future__ import annotations

from circuit.ir.graph import CircuitGraph
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


def typecheck_graph(graph: CircuitGraph) -> list[Check]:
    checks: list[Check] = []
    kinds = {n.id: n.kind for n in graph.nodes}
    domains = {n.id: n.domain for n in graph.nodes}
    for e in graph.edges:
        src_d = domains.get(e.src, "fluid" if e.src_port in _FLUID else "electrical")
        dst_d = domains.get(e.dst, "fluid" if e.dst_port in _FLUID else "electrical")
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
