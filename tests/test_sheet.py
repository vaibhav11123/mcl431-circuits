import re
from pathlib import Path

from circuit.draw import draw_electrical, draw_hydraulic, draw_pneumatic
from circuit.spec import CircuitSpec, CurrentPath, Domain, Electrical, Meta, Power, Pump


ROOT = Path(__file__).resolve().parents[1]


def test_b1_hydraulic_svg_has_actuators_and_envelopes(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    dest = tmp_path / "hydraulic_circuit.svg"
    draw_hydraulic(spec, dest)
    svg = dest.read_text()
    for token in ("HC1", "HC2", "HM1", "1Y1", "RV1", "JOB", "closed-centre"):
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
    for token in ("K1", "K2", "K3", "K4", "START", "JOB", "A1", "A2", "control", "main"):
        assert token in svg, token
    assert 'data-tag="K1"' in svg
    assert 'data-tag="K2"' in svg
    assert 'data-tag="K3"' in svg
    assert 'data-tag="K4"' in svg
    assert 'data-terms="1,2"' in svg
    assert 'data-terms="11,14"' in svg
    assert 'data-tag="1B1"' in svg
    assert 'data-actuated="true"' in svg
    assert "HC1+" in svg
    assert "T1=30s" in svg
    assert svg.count("3Y1") == 1
    assert "A1/A2" in svg


def test_electrical_grows_with_six_contacts(tmp_path: Path) -> None:
    spec = CircuitSpec(
        meta=Meta(title="tall ladder", domain=Domain.HYDRAULIC_PLUS_ELECTRICAL),
        sequence=[],
        power=Power(pumps=[Pump(id="P1")]),
        electrical=Electrical(paths=[
            CurrentPath(number=1, kind="control",
                        contacts=["START", "JOB", "K1", "1B1", "2B2", "K2"],
                        coil="K1"),
        ]),
    )
    dest = tmp_path / "tall.svg"
    draw_electrical(spec, dest)
    svg = dest.read_text()
    m = re.search(r'<svg[^>]*\bheight="([^"]+)"', svg)
    assert m is not None
    assert float(m.group(1)) >= 700


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


def test_strip_electrical_has_h1_s1_s3(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/strip_feed_2023/circuit.yaml")
    dest = tmp_path / "electrical_circuit.svg"
    draw_electrical(spec, dest)
    svg = dest.read_text()
    assert 'data-tag="S1"' in svg
    assert 'data-tag="S3"' in svg
    assert ">H1<" in svg or "H1</text>" in svg
    assert svg.count("H1") >= 1
