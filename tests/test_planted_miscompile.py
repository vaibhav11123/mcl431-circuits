from pathlib import Path

from circuit.pack import Pack, using_pack
from circuit.service import draw_yaml
from circuit.spec import CircuitSpec, CurrentPath
from circuit.verification.refine import verify_spec


ROOT = Path(__file__).resolve().parents[1]
ISO_ROOT = ROOT / "src/circuit/packs/iso_sequence"
ISO_PACK = Pack(
    root=ISO_ROOT,
    atlas_path=ISO_ROOT / "atlas.yaml",
    stamp_dir=ISO_ROOT / "stamps",
    hooks_module="circuit.packs.iso_sequence",
)


def _planted() -> CircuitSpec:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    spec.electrical.paths = [
        CurrentPath(number=1, kind="main", contacts=["START"], coil="1Y1"),
        CurrentPath(number=2, kind="main", contacts=["START"], coil="1Y2"),
    ]
    return spec


def test_planted_dual_solenoid_caught() -> None:
    spec = _planted()
    with using_pack(ISO_PACK):
        vr = verify_spec(spec)
    assert vr.ok is False
    blob = str(vr.src_row) + str(vr.tgt_row)
    assert "1Y1" in blob and "1Y2" in blob


def test_planted_draw_yaml_no_pneumatic() -> None:
    spec = _planted()
    with using_pack(ISO_PACK):
        out = draw_yaml(spec.to_yaml())
    assert "pneumatic" not in out.get("sheets", {})
