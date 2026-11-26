from pathlib import Path

from circuit.pack import Pack, using_pack
from circuit.service import apply_sequence_edit


ROOT = Path(__file__).resolve().parents[1]
ISO_PACK = Pack(
    root=ROOT / "src/circuit/packs/iso_sequence",
    atlas_path=ROOT / "src/circuit/packs/iso_sequence/atlas.yaml",
    stamp_dir=ROOT / "src/circuit/packs/iso_sequence/stamps",
    hooks_module="circuit.packs.iso_sequence",
)


def test_iso_timer_electrical() -> None:
    text = (ROOT / "examples/iso_sequence/circuit.yaml").read_text()
    with using_pack(ISO_PACK):
        out = apply_sequence_edit(text, {"op": "insert_timer", "after_action": "2A-", "seconds": 3})
    assert out["ok"] is True
    elec = out["sheets"].get("electrical", "")
    assert "T1" in elec
    assert "3" in elec
