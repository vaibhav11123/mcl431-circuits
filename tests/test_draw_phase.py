from pathlib import Path

from circuit.draw_phase import draw_phase
from circuit.spec import CircuitSpec

ROOT = Path(__file__).resolve().parents[1]


def test_b1_legend_has_start_job_homes(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    dest = tmp_path / "step_displacement.svg"
    draw_phase(spec, dest)
    svg = dest.read_text()
    for token in ("START", "JOB", "1B1", "2B1"):
        assert token in svg, token


def test_strip_legend_has_s1_s3_not_job(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/strip_feed_2023/circuit.yaml")
    dest = tmp_path / "step_displacement.svg"
    draw_phase(spec, dest)
    svg = dest.read_text()
    assert "S1" in svg
    assert "S3" in svg
    assert "JOB" not in svg
    assert "2B1" in svg
    assert "2B2" in svg


def test_fall17_phase_has_s0_and_four_drill_strokes(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/drill_2017/circuit.yaml")
    dest = tmp_path / "step_displacement.svg"
    draw_phase(spec, dest)
    svg = dest.read_text()
    for token in ("START", "S0", "1B1", "2B1", "3B1", "1A", "2A", "3A"):
        assert token in svg, token
    assert svg.count("3A+") == 4


def test_last_step_labelled_equals_one(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    dest = tmp_path / "step_displacement.svg"
    draw_phase(spec, dest)
    svg = dest.read_text()
    assert "=1" in svg


def test_emboss_phase_holds_until_4_bar(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/emboss_2016/circuit.yaml")
    dest = tmp_path / "step_displacement.svg"
    draw_phase(spec, dest)
    svg = dest.read_text()
    for token in ("S1", "S0", "1B1", "2B1", "1A1", "2A1", "PS"):
        assert token in svg, token
    assert "4 bar" in svg
