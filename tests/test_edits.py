from pathlib import Path

from circuit.pack import Pack, using_pack
from circuit.service import apply_sequence_edit


ROOT = Path(__file__).resolve().parents[1]
ISO_ROOT = ROOT / "src/circuit/packs/iso_sequence"
ISO_PACK = Pack(
    root=ISO_ROOT,
    atlas_path=ISO_ROOT / "atlas.yaml",
    stamp_dir=ISO_ROOT / "stamps",
    hooks_module="circuit.packs.iso_sequence",
)
ISO_YAML = (ROOT / "examples/iso_sequence/circuit.yaml").read_text()


def test_insert_timer_after_2a() -> None:
    with using_pack(ISO_PACK):
        out = apply_sequence_edit(ISO_YAML, {"op": "insert_timer", "after_action": "2A-", "seconds": 3})
    assert "TIMER" in out["yaml"]
    assert "seconds: 3" in out["yaml"]
    assert out["ok"] is True


def test_undo_restores() -> None:
    with using_pack(ISO_PACK):
        edited = apply_sequence_edit(ISO_YAML, {"op": "insert_timer", "after_action": "2A-", "seconds": 3})
        undone = apply_sequence_edit(edited["yaml"], {"op": "undo", "previous_yaml": ISO_YAML})
    assert undone["yaml"] == ISO_YAML


def test_unknown_op_unchanged() -> None:
    with using_pack(ISO_PACK):
        out = apply_sequence_edit(ISO_YAML, {"op": "add_cascade_group"})
    assert out["ok"] is False
    assert out["yaml"] == ISO_YAML
