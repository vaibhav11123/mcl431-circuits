from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from circuit.ir.ports import Port
from circuit.spec import CurrentPath

Kind = Literal[
    "cylinder",
    "valve",
    "solenoid",
    "contact",
    "coil",
    "sensor",
    "pump",
    "tank",
    "relief",
]


class GraphNode(BaseModel):
    id: str
    kind: Kind
    domain: str = "fluid"


class GraphEdge(BaseModel):
    src: str
    src_port: str
    dst: str
    dst_port: str
    src_typed: Port | None = None
    dst_typed: Port | None = None


class CircuitGraph(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    paths: list[CurrentPath] = Field(default_factory=list)
    solenoid_plus: dict[str, str] = Field(default_factory=dict)
    solenoid_minus: dict[str, str] = Field(default_factory=dict)
    sensors_home: dict[str, str] = Field(default_factory=dict)
    sensors_end: dict[str, str] = Field(default_factory=dict)
