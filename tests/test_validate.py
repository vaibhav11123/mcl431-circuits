from pathlib import Path

from circuit.spec import CircuitSpec
from circuit.validate import all_ok, validate_spec


ROOT = Path(__file__).resolve().parents[1]


def test_grinding_validates() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    checks = validate_spec(spec, ROOT)
    failed = [c for c in checks if not c.ok]
    assert not failed, [f"{c.name}: {c.detail}" for c in failed]
    assert all_ok(checks)
