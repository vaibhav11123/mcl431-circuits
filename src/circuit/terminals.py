"""L8 contact classification: kind, terminals, rest-position actuation."""

from __future__ import annotations

import re

_PUSHBUTTONS = frozenset({"START", "S1", "S3"})
_HOME_B1 = re.compile(r"^\d*B1$")
_EXTEND_B2 = re.compile(r"^\d*B2$")


def bare(tag: str) -> str:
    """Strip a leading ``!`` NC marker."""
    return tag[1:] if tag.startswith("!") else tag


def contact_kind(tag: str) -> str:
    name = bare(tag)
    if name in _PUSHBUTTONS:
        return "pushbutton"
    if name.startswith("K"):
        return "contact_no"
    if _HOME_B1.fullmatch(name):
        return "contact_nc"
    if _EXTEND_B2.fullmatch(name) or name == "JOB":
        return "limit_switch"
    if name == "T1":
        return "contact_no"
    return "contact_no"


def contact_terminals(tag: str, k_index: int = 0) -> tuple[str, str]:
    name = bare(tag)
    kind = contact_kind(tag)
    if kind == "pushbutton":
        return ("13", "14")
    if name.startswith("K"):
        if k_index >= 1:
            return ("21", "24")
        return ("11", "14")
    if kind == "contact_nc":
        return ("1", "2")
    if kind == "limit_switch":
        return ("13", "14")
    if name == "T1":
        return ("7", "8")
    return ("13", "14")


def contact_actuated(tag: str) -> bool:
    """Home nB1 sensors are closed at rest (cylinder retracted)."""
    return _HOME_B1.fullmatch(bare(tag)) is not None
