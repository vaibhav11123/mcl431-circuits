from pathlib import Path

from circuit.draw import draw_electrical, draw_hydraulic, draw_pneumatic
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


def test_b1_electrical_svg_has_latch_and_l8_terminals(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    dest = tmp_path / "electrical_circuit.svg"
    draw_electrical(spec, dest)
    svg = dest.read_text()
    for token in ("K_START", "START", "JOB", "A1", "A2", "13", "14", "control", "main"):
        assert token in svg, token
    assert "3Y1" in svg
    # solenoid id appears as a coil label, not as a lone contact token next to 13/14
    assert svg.count("3Y1") == 1


def test_hilo_hydraulic_svg_has_p1_p2_uv(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/hilo_punch_2017/circuit.yaml")
    dest = tmp_path / "hydraulic_circuit.svg"
    draw_hydraulic(spec, dest)
    svg = dest.read_text()
    for token in ("P1", "P2", "UV", "RV", "HC1"):
        assert token in svg, token


def test_strip_feed_pneumatic_svg_has_two_5_2(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/strip_feed_2023/circuit.yaml")
    dest = tmp_path / "pneumatic_circuit.svg"
    draw_pneumatic(spec, dest)
    svg = dest.read_text()
    for token in ("1A", "2A", "1Y1", "2Y2", "4", "2", "1"):
        assert token in svg, token
    assert svg.count('href="data:image/png') >= 4
