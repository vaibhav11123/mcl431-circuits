from pathlib import Path

from circuit.spec import CircuitSpec, PatternId
from circuit.validate import all_ok, validate_spec


ROOT = Path(__file__).resolve().parents[1]


def test_grinding_validates() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    checks = validate_spec(spec, ROOT)
    failed = [c for c in checks if not c.ok]
    assert not failed, [f"{c.name}: {c.detail}" for c in failed]
    assert all_ok(checks)
    names = [c.name for c in checks]
    assert "coil_tag_bijection" in names
    bij = next(c for c in checks if c.name == "coil_tag_bijection")
    assert bij.ok, bij.detail


def test_sequence_valve_pattern_not_drawable() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    spec.meta.patterns.append(PatternId.SEQUENCE_VALVE)
    checks = validate_spec(spec, ROOT)
    row = next(c for c in checks if c.name == "pattern_drawable")
    assert not row.ok
    assert "sequence_valve" in row.detail


def test_meter_2019_figure_given_skips_drawable() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/meter_2019/circuit.yaml")
    checks = validate_spec(spec, ROOT)
    names = [c.name for c in checks]
    assert "pattern_drawable" not in names
    assert all_ok(checks)


def test_dcv_5_3_refuses_without_crop() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/strip_feed_2023/circuit.yaml")
    spec.valves["1V"].type = "dcv_5_3"
    checks = validate_spec(spec, ROOT)
    row = next(c for c in checks if c.name == "valve_1V_crop")
    assert not row.ok
    assert "atlas crop missing: dcv_5_3" in row.detail
