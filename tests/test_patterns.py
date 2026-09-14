from pathlib import Path

from circuit.draw import draw_hydraulic, draw_pneumatic
from circuit.spec import CircuitSpec


ROOT = Path(__file__).resolve().parents[1]


def test_spring_centred_dac_stamps_lecture_glyph(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/lecture_dac_spring/circuit.yaml")
    dest = tmp_path / "h.svg"
    draw_hydraulic(spec, dest)
    svg = dest.read_text()
    assert "1A" in svg
    assert "spring-centred" in svg
    assert "1Y1" in svg


def test_unload_has_uv_and_hilo_still_separate(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/lecture_unload/circuit.yaml")
    svg = (tmp_path / "u.svg")
    draw_hydraulic(spec, svg)
    text = svg.read_text()
    assert "UV" in text
    hilo = CircuitSpec.from_yaml(ROOT / "examples/hilo_punch_2017/circuit.yaml")
    dest = tmp_path / "hilo.svg"
    draw_hydraulic(hilo, dest)
    assert "P1" in dest.read_text() and "P2" in dest.read_text()


def test_meter_in_out_bleed_stamp_fc(tmp_path: Path) -> None:
    for name, token in (
        ("lecture_meter_in", "FC"),
        ("lecture_meter_out", "FC"),
        ("lecture_bleed_off", "bleed"),
        ("lecture_regen", "CV"),
    ):
        spec = CircuitSpec.from_yaml(ROOT / f"examples/{name}/circuit.yaml")
        dest = tmp_path / f"{name}.svg"
        draw_hydraulic(spec, dest)
        assert token in dest.read_text(), name


def test_strip_exhaust_has_triangles(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/strip_feed_2023/circuit.yaml")
    dest = tmp_path / "p.svg"
    draw_pneumatic(spec, dest)
    svg = dest.read_text()
    assert svg.count("<polygon") >= 5
