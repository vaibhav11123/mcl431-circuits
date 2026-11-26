"""Adapter: spec → CircuitGraph. May call compile_paths. Tracer must not."""

from __future__ import annotations

from circuit.compile_sequence import apply_compile
from circuit.ir.graph import CircuitGraph, GraphEdge, GraphNode
from circuit.ir.ports import Port
from circuit.spec import CircuitSpec


def from_spec(spec: CircuitSpec) -> CircuitGraph:
    compiled = apply_compile(spec)
    nodes: list[GraphNode] = []
    plus: dict[str, str] = {}
    minus: dict[str, str] = {}
    home: dict[str, str] = {}
    end: dict[str, str] = {}
    edges: list[GraphEdge] = []
    for cid, cyl in compiled.cylinders.items():
        nodes.append(GraphNode(id=cid, kind="cylinder", domain="fluid"))
        valve = compiled.valves.get(cyl.dcv)
        sols = list(valve.solenoids) if valve else []
        if sols:
            plus[cid] = sols[0]
            if len(sols) > 1:
                minus[cid] = sols[1]
        if cyl.sensors:
            home[cid] = cyl.sensors[0]
            end[cid] = cyl.sensors[-1] if len(cyl.sensors) > 1 else cyl.sensors[0]
        nodes.append(GraphNode(id=cyl.dcv, kind="valve", domain="fluid"))
        vid = cyl.dcv
        edges.append(
            GraphEdge(
                src=vid,
                src_port="A",
                dst=cid,
                dst_port="cap",
                src_typed=Port(
                    component_id=vid, port_id="A", domain="fluid", role="actuator"
                ),
                dst_typed=Port(
                    component_id=cid, port_id="cap", domain="fluid", role="actuator"
                ),
            )
        )
        edges.append(
            GraphEdge(
                src=vid,
                src_port="B",
                dst=cid,
                dst_port="rod",
                src_typed=Port(
                    component_id=vid, port_id="B", domain="fluid", role="actuator"
                ),
                dst_typed=Port(
                    component_id=cid, port_id="rod", domain="fluid", role="actuator"
                ),
            )
        )
    for p in compiled.electrical.paths:
        if p.coil:
            nodes.append(GraphNode(id=p.coil, kind="coil", domain="electrical"))
    return CircuitGraph(
        nodes=nodes,
        edges=edges,
        paths=list(compiled.electrical.paths),
        solenoid_plus=plus,
        solenoid_minus=minus,
        sensors_home=home,
        sensors_end=end,
    )
