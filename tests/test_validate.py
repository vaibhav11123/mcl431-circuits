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


def test_drill_2017_5_3_crop_present() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/drill_2017/circuit.yaml")
    checks = validate_spec(spec, ROOT)
    failed = [c for c in checks if not c.ok]
    assert not failed, [f"{c.name}: {c.detail}" for c in failed]
    assert (ROOT / "lecture/crops/dcv_5_3.png").is_file()
    assert (ROOT / "lecture/crops/stamps/dcv_5_3.png").is_file()
    assert all(c.name.endswith("_crop") is False or c.ok for c in checks)


def test_strip_feed_5_2_crop_present() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/strip_feed_2023/circuit.yaml")
    checks = validate_spec(spec, ROOT)
    failed = [c for c in checks if not c.ok]
    assert not failed, [f"{c.name}: {c.detail}" for c in failed]
    assert (ROOT / "lecture/crops/dcv_5_2.png").is_file()
    assert (ROOT / "lecture/crops/stamps/dcv_5_2.png").is_file()


def test_emboss_2016_validates() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/emboss_2016/circuit.yaml")
    checks = validate_spec(spec, ROOT)
    failed = [c for c in checks if not c.ok]
    assert not failed, [f"{c.name}: {c.detail}" for c in failed]
    assert spec.cylinders["1A1"].dcv == "1V"
    assert "PS" in spec.sensors
    assert "S0" in spec.sensors
