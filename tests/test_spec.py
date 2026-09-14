from pathlib import Path

from circuit.spec import CircuitSpec, Domain, Meta, Power, Pump, question_output_dir


ROOT = Path(__file__).resolve().parents[1]


def test_grinding_yaml_loads() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    assert spec.meta.domain == Domain.HYDRAULIC_PLUS_ELECTRICAL
    assert spec.cylinders["HC1"].bore_mm == 45
    assert spec.motors["HM1"].rpm == 400
    assert len(spec.sequence) == 6


def _bare_spec(**meta_kw) -> CircuitSpec:
    return CircuitSpec(
        meta=Meta(title="Untitled plant", domain=Domain.HYDRAULIC, **meta_kw),
        sequence=[],
        power=Power(pumps=[Pump(id="P1")]),
    )


def test_output_dir_uses_exam_id() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    dest = question_output_dir(ROOT, spec, ROOT / "examples/grinding_machine/circuit.yaml")
    assert dest == ROOT / "output" / "2023_selfstudy_b1"


def test_output_dir_falls_back_to_yaml_parent() -> None:
    spec = _bare_spec()
    dest = question_output_dir(ROOT, spec, ROOT / "examples/grinding_machine/circuit.yaml")
    assert dest == ROOT / "output" / "grinding_machine"


def test_output_dir_sanitizes_title() -> None:
    spec = _bare_spec()
    spec.meta.title = "B1: grind / clamp"
    dest = question_output_dir(ROOT, spec)
    assert dest == ROOT / "output" / "B1_grind_clamp"


def test_golden_output_folders_are_unique() -> None:
    from circuit.eval import golden_specs

    slugs = []
    for path in golden_specs(ROOT):
        spec = CircuitSpec.from_yaml(path)
        slugs.append(spec.output_slug(path))
    assert slugs
    assert len(slugs) == len(set(slugs))
