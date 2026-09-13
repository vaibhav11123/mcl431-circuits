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
    for name in (
        "hydraulic_circuit.png",
        "electrical_circuit.png",
        "step_displacement.png",
    ):
        dest = tmp_path / name
        assert dest.is_file(), name
        assert dest.stat().st_size > 10_000, f"{name} too small ({dest.stat().st_size})"
