from pathlib import Path

from circuit.spec import CircuitSpec, Domain


def test_grinding_yaml_loads() -> None:
    spec = CircuitSpec.from_yaml(
        Path(__file__).resolve().parents[1] / "examples/grinding_machine/circuit.yaml"
    )
    assert spec.meta.domain == Domain.HYDRAULIC_PLUS_ELECTRICAL
    assert spec.cylinders["HC1"].bore_mm == 45
    assert spec.motors["HM1"].rpm == 400
    assert len(spec.sequence) == 6
