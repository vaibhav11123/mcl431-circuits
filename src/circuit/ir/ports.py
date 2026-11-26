"""Typed ports. Names are not types — domain and role are."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

DomainKind = Literal["fluid", "electrical", "control"]
PortRole = Literal[
    "supply",
    "return",
    "actuator",
    "exhaust",
    "coil",
    "contact",
    "sensor",
    "pilot",
]
Direction = Literal["in", "out", "bidir"]


class Port(BaseModel):
    component_id: str
    port_id: str
    domain: DomainKind
    role: PortRole
    direction: Direction = "bidir"


FLUID_ROLES = {"supply", "return", "actuator", "exhaust", "pilot"}
ELECTRICAL_ROLES = {"coil", "contact", "sensor"}


def compatible(a: Port, b: Port) -> bool:
    if a.domain != b.domain:
        return False
    if a.domain == "fluid":
        return a.role in FLUID_ROLES and b.role in FLUID_ROLES
    return a.role in ELECTRICAL_ROLES and b.role in ELECTRICAL_ROLES
