from pathlib import Path

from circuit.draw import draw_all, draw_hydraulic
from circuit.spec import CircuitSpec

ROOT = Path(__file__).resolve().parents[1]


def test_hilo_draw_all_has_no_electrical(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/hilo_punch_2017/circuit.yaml")
    draw_all(spec, tmp_path)
    assert not (tmp_path / "electrical_circuit.svg").exists()
    assert (tmp_path / "hydraulic_circuit.svg").exists()
    assert not (tmp_path / "step_displacement.svg").exists()


def test_b1_draw_all_still_has_electrical(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    draw_all(spec, tmp_path)
    assert (tmp_path / "electrical_circuit.svg").exists()
    assert (tmp_path / "hydraulic_circuit.svg").exists()


def test_b1_hydraulic_has_setpoint_and_actuators(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    dest = tmp_path / "hydraulic_circuit.svg"
    draw_hydraulic(spec, dest)
    svg = dest.read_text()
    assert "15.72" in svg or "bar" in svg
    for token in ("HC1", "HC2", "HM1", "RV1", "JOB"):
        assert token in svg, token
