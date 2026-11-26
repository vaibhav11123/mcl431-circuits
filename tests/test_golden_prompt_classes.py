from pathlib import Path

from circuit.pack import Pack, using_pack
from circuit.service import SENTENCE_CASCADE, SENTENCE_UNKNOWN, draw_yaml


ROOT = Path(__file__).resolve().parents[1]
ISO_PACK = Pack(
    root=ROOT / "src/circuit/packs/iso_sequence",
    atlas_path=ROOT / "src/circuit/packs/iso_sequence/atlas.yaml",
    stamp_dir=ROOT / "src/circuit/packs/iso_sequence/stamps",
    hooks_module="circuit.packs.iso_sequence",
)
SKILL = (ROOT / "plugin/skills/draw-sequence/SKILL.md").read_text()


def test_invented_id_class() -> None:
    text = (ROOT / "examples/iso_sequence/circuit.yaml").read_text().replace(
        "dcv_5_2_double_solenoid", "magic_valve"
    )
    with using_pack(ISO_PACK):
        out = draw_yaml(text)
    assert out["ok"] is False
    assert out["sentence"] == SENTENCE_UNKNOWN


def test_simulate_and_ct_in_skill() -> None:
    assert "No pressure physics" in SKILL
    assert "We do not export FluidSIM" in SKILL
    assert "cannot verify a photograph" in SKILL.lower() or "cannot verify a photograph" in (
        ROOT / "plugin/skills/get-started/SKILL.md"
    ).read_text()


def test_cascade_gt3_sentence() -> None:
    assert "three cylinders" in SENTENCE_CASCADE
