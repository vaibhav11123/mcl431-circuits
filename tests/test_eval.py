from pathlib import Path

from circuit.eval import eval_spec
from circuit.spec import CircuitSpec


ROOT = Path(__file__).resolve().parents[1]


def test_grinding_eval_passes() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    report = eval_spec(spec, ROOT)
    failed = [c for c in report["checks"] if not c["ok"]]
    assert report["pass"], failed
