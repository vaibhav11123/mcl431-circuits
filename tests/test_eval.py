from pathlib import Path

from circuit.eval import eval_spec
from circuit.spec import CircuitSpec, CurrentPath


ROOT = Path(__file__).resolve().parents[1]


def test_grinding_eval_passes() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    report = eval_spec(spec, ROOT)
    failed = [c for c in report["checks"] if not c["ok"]]
    assert report["pass"], failed


def test_grinding_has_no_solenoid_as_contact() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    report = eval_spec(spec, ROOT)
    row = next(c for c in report["checks"] if c["name"] == "no_solenoid_as_contact")
    assert row["ok"], row


def test_solenoid_as_contact_fails() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    spec.electrical.paths = [
        CurrentPath(number=1, kind="main", contacts=["3Y1"], coil="1Y1"),
    ]
    report = eval_spec(spec, ROOT)
    row = next(c for c in report["checks"] if c["name"] == "no_solenoid_as_contact")
    assert not row["ok"]


def test_hilo_without_uv_fails() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/hilo_punch_2017/circuit.yaml")
    spec.valves = {k: v for k, v in spec.valves.items() if v.type != "unloading_valve"}
    report = eval_spec(spec, ROOT)
    row = next(c for c in report["checks"] if c["name"] == "hilo_has_uv")
    assert not row["ok"], "hi-lo must not pass without an unloading valve"


def test_hilo_golden_has_two_pumps_and_uv() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/hilo_punch_2017/circuit.yaml")
    assert len(spec.power.pumps) == 2
    assert any(v.type == "unloading_valve" for v in spec.valves.values())
    assert all(c.bore_mm is None and c.rod_mm is None for c in spec.cylinders.values())
    report = eval_spec(spec, ROOT)
    failed = [c for c in report["checks"] if not c["ok"]]
    assert report["pass"], failed


def test_l4_regen_not_attached_to_b1() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    report = eval_spec(spec, ROOT)
    names = [c["name"] for c in report["checks"]]
    assert "golden_l4_regen_ratio" not in names
