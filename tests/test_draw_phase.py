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


def test_last_step_labelled_equals_one(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    dest = tmp_path / "step_displacement.svg"
    draw_phase(spec, dest)
    svg = dest.read_text()
    assert "=1" in svg
