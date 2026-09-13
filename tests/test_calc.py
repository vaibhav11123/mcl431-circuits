import pytest

from circuit.calc import (
    area_mm2,
    grinding_hc1_pressure_bar,
    l4_regen_example,
    solution_lines_for,
    solution_lines_hilo_2017,
)
from circuit.eval import eval_spec
from circuit.spec import CircuitSpec
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_cap_area() -> None:
    assert abs(area_mm2(45) - 1590.431) < 0.01


def test_grinding_pressure_positive() -> None:
    assert grinding_hc1_pressure_bar() > 10


def test_l4_regen_speed_ratio_is_two() -> None:
    # Vext = Q/Ar, Vret = Q/(Ap-Ar); Ap=3 Ar => Vext/Vret = 2
    r = l4_regen_example()
    assert abs(r["speed_ratio"] - 2.0) < 1e-9
    assert abs(r["load_ratio"] - 0.5) < 1e-9


def test_hilo_2017_does_not_invent_bore() -> None:
    lines = "\n".join(solution_lines_hilo_2017())
    assert "7800" in lines
    assert "15 cm/s" in lines
    assert "not_given" in lines
    assert "50" not in lines
    assert "28" not in lines


@pytest.mark.parametrize(
    "exam_id,rel",
    [
        ("2018_minor1_hilo", "examples/hilo_2018/circuit.yaml"),
        ("2019_minor1_meter", "examples/meter_2019/circuit.yaml"),
        ("2016_minor1_hoist", "examples/hoist_2016/circuit.yaml"),
        ("2023_selfstudy_b2", "examples/headloss_2023_b2/circuit.yaml"),
        ("MCL431_minor", "examples/grind_given_2022/circuit.yaml"),
    ],
)
def test_figure_given_calc_cites_facts(exam_id: str, rel: str) -> None:
    spec = CircuitSpec.from_yaml(ROOT / rel)
    assert spec.meta.figure_given
    assert spec.meta.exam_id == exam_id
    lines = "\n".join(solution_lines_for(exam_id))
    assert "facts.yaml" in lines
    assert "not invented" in lines.lower() or "not_given" in lines or "paper" in lines
    report = eval_spec(spec, ROOT)
    failed = [c for c in report["checks"] if not c["ok"]]
    assert report["pass"], failed
