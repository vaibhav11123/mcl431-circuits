from pathlib import Path

from circuit.draw import draw_hydraulic
from circuit.spec import CircuitSpec


ROOT = Path(__file__).resolve().parents[1]


def test_b1_hydraulic_svg_has_actuators_and_envelopes(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    dest = tmp_path / "hydraulic_circuit.svg"
    draw_hydraulic(spec, dest)
    svg = dest.read_text()
    for token in ("HC1", "HC2", "HM1", "1Y1", "RV1", "JOB"):
        assert token in svg, token
    assert svg.count("<image") >= 12
    assert "envelope" not in svg  # images are raw PNG, not filenames
    # three envelope stamps + solenoids + cylinders + motor + power
    assert svg.count("href=\"data:image/png") >= 12
