from pathlib import Path

from circuit.compile_sequence import apply_compile, displacement_rows
from circuit.spec import CircuitSpec


def test_grinding_compiles_six_steps_and_timer() -> None:
    spec = CircuitSpec.from_yaml(
        Path(__file__).resolve().parents[1] / "examples/grinding_machine/circuit.yaml"
    )
    compiled = apply_compile(spec)
    coils = [p.coil for p in compiled.electrical.paths if p.coil]
    for name in ("K_START", "1Y1", "3Y1", "2Y1", "T1_30s", "2Y2", "1Y2"):
        assert name in coils, name
    contacts = {c for p in compiled.electrical.paths for c in (p.contacts or [])}
    for name in ("START", "JOB", "K_START", "1B2", "2B1", "2B2", "1B1"):
        assert name in contacts, name
    assert "3Y1" not in contacts
    assert any(p.coil == "K_START" and "K_START" in (p.contacts or []) for p in compiled.electrical.paths)
    kinds = [p.kind for p in compiled.electrical.paths]
    assert kinds == sorted(kinds, key=lambda k: 0 if k != "main" else 1)
    rows = displacement_rows(spec.sequence)
    assert len(rows) == 6
