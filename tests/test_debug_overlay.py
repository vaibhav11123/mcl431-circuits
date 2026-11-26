from pathlib import Path

from circuit.pack import Pack, using_pack
from circuit.service import draw_yaml
from circuit.spec import CircuitSpec, CurrentPath


ROOT = Path(__file__).resolve().parents[1]
ISO_PACK = Pack(
    root=ROOT / "src/circuit/packs/iso_sequence",
    atlas_path=ROOT / "src/circuit/packs/iso_sequence/atlas.yaml",
    stamp_dir=ROOT / "src/circuit/packs/iso_sequence/stamps",
    hooks_module="circuit.packs.iso_sequence",
)


def test_planted_draw_yaml_debug_rejected() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    spec.electrical.paths = [
        CurrentPath(number=1, kind="main", contacts=["START"], coil="1Y1"),
        CurrentPath(number=2, kind="main", contacts=["START"], coil="1Y2"),
    ]
    with using_pack(ISO_PACK):
        out = draw_yaml(spec.to_yaml())
    assert out["ok"] is False
    assert "pneumatic" not in out.get("sheets", {})
    debug = out.get("debug") or ""
    assert "REJECTED" in debug
    assert "1Y1" in debug
