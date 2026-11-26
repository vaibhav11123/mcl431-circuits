"""SVG tag provenance. P001/P002 — independent of drawing style."""

from __future__ import annotations

import re

from circuit.spec import CircuitSpec

_TAG = re.compile(r">([0-9A-Z][0-9A-Z._-]{0,7})</text>")
_SKIP = {"STEP", "CHECKED", "PASS", "FAIL", "START", "TANK", "ISO"}


def tags_from_spec(spec: CircuitSpec) -> set[str]:
    tags: set[str] = set()
    tags.update(spec.cylinders)
    tags.update(spec.valves)
    for v in spec.valves.values():
        tags.update(v.solenoids)
    tags.update(spec.sensors)
    return {t for t in tags if t}


def tags_from_svg(svg: str) -> set[str]:
    found = set(_TAG.findall(svg))
    return {t for t in found if t.upper() not in _SKIP}


def p001(spec: CircuitSpec, svgs: list[str]) -> bool:
    """Every spec tag appears in at least one sheet."""
    union = set()
    for svg in svgs:
        union |= tags_from_svg(svg)
    needed = tags_from_spec(spec)
    return needed <= union


def p002(spec: CircuitSpec, svgs: list[str]) -> bool:
    """Every captured SVG solenoid-like tag exists on the spec."""
    spec_tags = tags_from_spec(spec)
    for svg in svgs:
        for tag in tags_from_svg(svg):
            if "Y" in tag and tag not in spec_tags:
                return False
    return True
