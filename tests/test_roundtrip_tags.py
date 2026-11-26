from pathlib import Path

from circuit.draw import draw_all
from circuit.pack import Pack, using_pack
from circuit.provenance import tags_from_spec, tags_from_svg
from circuit.spec import CircuitSpec


ROOT = Path(__file__).resolve().parents[1]
ISO_ROOT = ROOT / "src/circuit/packs/iso_sequence"
ISO_PACK = Pack(
    root=ISO_ROOT,
    atlas_path=ISO_ROOT / "atlas.yaml",
    stamp_dir=ISO_ROOT / "stamps",
    hooks_module="circuit.packs.iso_sequence",
)


def _valve_solenoid_tags(spec: CircuitSpec) -> set[str]:
    tags = set(spec.valves)
    for v in spec.valves.values():
        tags.update(v.solenoids)
    return tags


def test_iso_roundtrip_valves_and_solenoids(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    with using_pack(ISO_PACK):
        written = draw_all(spec, tmp_path)
    union = set()
    for k in ("pneumatic", "electrical"):
        union |= tags_from_svg(written[k].read_text())
    needed = _valve_solenoid_tags(spec)
    assert needed <= union


def test_drop_1y1_roundtrip_mismatch(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    spec.valves["1V"].solenoids = [s for s in spec.valves["1V"].solenoids if s != "1Y1"]
    with using_pack(ISO_PACK):
        written = draw_all(spec, tmp_path)
    union = set()
    for k in ("pneumatic", "electrical"):
        union |= tags_from_svg(written[k].read_text())
    assert "1Y1" in tags_from_spec(
        CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    )
    original = _valve_solenoid_tags(
        CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    )
    assert original - union or "1Y1" not in union
