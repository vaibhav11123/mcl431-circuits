"""A sheet may be drawn only from a sealed verified graph."""

from __future__ import annotations

from dataclasses import dataclass

from circuit.ir.graph import CircuitGraph
from circuit.spec import CircuitSpec
from circuit.verification.refine import VerifyResult
from circuit.verification.status import Status


@dataclass(frozen=True)
class VerifiedCircuit:
    spec: CircuitSpec
    graph: CircuitGraph
    result: VerifyResult


def paths_equal(a: CircuitSpec, graph: CircuitGraph) -> bool:
    left = [p.model_dump() for p in a.electrical.paths]
    right = [p.model_dump() for p in graph.paths]
    return left == right


def seal(spec: CircuitSpec, graph: CircuitGraph, result: VerifyResult) -> VerifiedCircuit:
    if result.status is not Status.PASS:
        raise ValueError("cannot seal a circuit that did not PASS")
    if not paths_equal(spec, graph):
        raise ValueError("compiled spec paths are not the graph that was verified")
    return VerifiedCircuit(spec=spec, graph=graph, result=result)
