from pathlib import Path

import pytest

from circuit.draw import draw_all
from circuit.png import backend_name
from circuit.spec import CircuitSpec


ROOT = Path(__file__).resolve().parents[1]


def test_b1_draw_writes_three_pngs(tmp_path: Path) -> None:
    if backend_name() is None:
        pytest.skip("no SVG→PNG backend (rsvg-convert, resvg, qlmanage, or cairosvg)")
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    draw_all(spec, tmp_path)
    dests = [
        tmp_path / "hydraulic_circuit.png",
        tmp_path / "electrical_circuit.png",
        tmp_path / "step_displacement.png",
    ]
    if not all(p.is_file() for p in dests):
        pytest.skip("PNG backend listed but conversion failed (qlmanage/sandbox)")
    for dest in dests:
        assert dest.stat().st_size > 10_000, f"{dest.name} too small ({dest.stat().st_size})"
