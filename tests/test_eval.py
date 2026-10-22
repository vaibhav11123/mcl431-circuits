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


def test_solenoid_nc_interlock_is_allowed() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    spec.electrical.paths = [
        CurrentPath(number=1, kind="main", contacts=["K1", "!1Y2"], coil="1Y1"),
    ]
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


def test_strip_feed_eval_passes() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/strip_feed_2023/circuit.yaml")
    report = eval_spec(spec, ROOT)
    failed = [c for c in report["checks"] if not c["ok"]]
    assert report["pass"], failed
    from circuit.compile_sequence import apply_compile

    coils = [p.coil for p in apply_compile(spec).electrical.paths if p.coil]
    for name in ("1Y1", "2Y2", "1Y2", "2Y1"):
        assert name in coils, name


def test_fall17_drill_eval_passes() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/drill_2017/circuit.yaml")
    report = eval_spec(spec, ROOT)
    failed = [c for c in report["checks"] if not c["ok"]]
    assert report["pass"], failed
    names = [c["name"] for c in report["checks"]]
    for name in ("three_5_3", "workpiece_s0", "twelve_motions", "spindle_km", "electrical_sequence"):
        assert name in names, name


def test_plc_conveyor_eval_passes() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/plc_conveyor_2023/circuit.yaml")
    report = eval_spec(spec, ROOT)
    failed = [c for c in report["checks"] if not c["ok"]]
    assert report["pass"], failed
    names = [c["name"] for c in report["checks"]]
    for name in (
        "plc_domain",
        "plc_ai_220",
        "plc_ai_220_cmp",
        "plc_ai_580",
        "plc_ao_1185",
        "plc_ao_2250",
        "plc_ao_3545",
        "plc_start_stop",
        "plc_three_lamps",
        "has_pump",
        "has_sequence",
    ):
        assert name in names, name
    assert "electrical_sequence" not in names


def test_emboss_2016_eval_passes() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/emboss_2016/circuit.yaml")
    report = eval_spec(spec, ROOT)
    failed = [c for c in report["checks"] if not c["ok"]]
    assert report["pass"], failed
    names = [c["name"] for c in report["checks"]]
    for name in (
        "two_5_2",
        "domain_pneumatic",
        "workpiece_s0",
        "pressure_switch_ps",
        "hold_until_4_bar",
        "2y2_waits_for_ps_not_2b2",
        "electrical_sequence",
    ):
        assert name in names, name


def test_l4_regen_not_attached_to_b1() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    report = eval_spec(spec, ROOT)
    names = [c["name"] for c in report["checks"]]
    assert "golden_l4_regen_ratio" not in names
