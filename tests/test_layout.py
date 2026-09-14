import re
from xml.etree import ElementTree as ET

import pytest

_VIEWBOX = re.compile(
    r"<svg\b[^>]*?\bviewBox=['\"]\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)",
    re.I | re.S,
)


def viewbox(svg: str) -> tuple[float, float, float, float]:
    m = _VIEWBOX.search(svg)
    if m is None:
        raise ValueError("root svg has no viewBox")
    return (float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)))


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _inside(x: float, y: float, minx: float, miny: float, w: float, h: float, tol: float = 1.0) -> bool:
    return (minx - tol) <= x <= (minx + w + tol) and (miny - tol) <= y <= (miny + h + tol)


def assert_primitives_inside(svg: str) -> None:
    minx, miny, w, h = viewbox(svg)
    root = ET.fromstring(svg)
    for el in root.iter():
        tag = _local(el.tag)
        if tag == "line":
            for x, y in (
                (float(el.get("x1")), float(el.get("y1"))),
                (float(el.get("x2")), float(el.get("y2"))),
            ):
                if not _inside(x, y, minx, miny, w, h):
                    raise AssertionError(f"line point ({x}, {y}) outside viewBox")
        elif tag == "text":
            x, y = float(el.get("x")), float(el.get("y"))
            if not _inside(x, y, minx, miny, w, h):
                raise AssertionError(f"text ({x}, {y}) outside viewBox")


def test_viewbox_parser_on_synthetic_svg() -> None:
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-24 -24 1728 848"></svg>'
    assert viewbox(svg) == (-24.0, -24.0, 1728.0, 848.0)


def test_assert_primitives_inside_ok() -> None:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 80">'
        '<line x1="0" y1="0" x2="99" y2="79"/>'
        '<text x="10" y="20">ok</text>'
        "</svg>"
    )
    assert_primitives_inside(svg)


def test_assert_primitives_inside_detects_overflow() -> None:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 80">'
        '<line x1="0" y1="0" x2="200" y2="0"/>'
        "</svg>"
    )
    with pytest.raises(AssertionError):
        assert_primitives_inside(svg)


def test_b1_electrical_primitives_inside_viewbox(tmp_path) -> None:
    from pathlib import Path

    from circuit.draw_electrical import draw_electrical
    from circuit.spec import CircuitSpec

    root = Path(__file__).resolve().parents[1]
    spec = CircuitSpec.from_yaml(root / "examples/grinding_machine/circuit.yaml")
    dest = tmp_path / "electrical_circuit.svg"
    draw_electrical(spec, dest)
    assert_primitives_inside(dest.read_text())


def test_b1_hydraulic_primitives_inside_viewbox(tmp_path) -> None:
    from pathlib import Path

    from circuit.draw_hydraulic import draw_hydraulic
    from circuit.spec import CircuitSpec

    root = Path(__file__).resolve().parents[1]
    spec = CircuitSpec.from_yaml(root / "examples/grinding_machine/circuit.yaml")
    dest = tmp_path / "hydraulic_circuit.svg"
    draw_hydraulic(spec, dest)
    assert_primitives_inside(dest.read_text())
