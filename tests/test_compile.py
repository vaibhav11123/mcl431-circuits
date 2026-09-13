from pathlib import Path

from circuit.compile_sequence import apply_compile, displacement_rows
from circuit.spec import CircuitSpec


def test_grinding_compiles_six_steps_and_timer() -> None:
    spec = CircuitSpec.from_yaml(
        Path(__file__).resolve().parents[1] / "examples/grinding_machine/circuit.yaml"
    )
    compiled = apply_compile(spec)
    coils = [p.coil for p in compiled.electrical.paths if p.coil]
    assert "1Y1" in coils
    assert "3Y1" in coils
    assert "2Y1" in coils
    assert any(c and c.startswith("T1") for c in coils)
    assert "2Y2" in coils
    assert "1Y2" in coils
    rows = displacement_rows(spec.sequence)
    assert len(rows) == 6
