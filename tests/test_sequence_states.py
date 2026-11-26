from pathlib import Path

from circuit.pack import Pack, using_pack
from circuit.service import explain_yaml, sequence_states, suggest_patch, draw_yaml


ROOT = Path(__file__).resolve().parents[1]
ISO_YAML = (ROOT / "examples/iso_sequence/circuit.yaml").read_text()
ISO_PACK = Pack(
    root=ROOT / "src/circuit/packs/iso_sequence",
    atlas_path=ROOT / "src/circuit/packs/iso_sequence/atlas.yaml",
    stamp_dir=ROOT / "src/circuit/packs/iso_sequence/stamps",
    hooks_module="circuit.packs.iso_sequence",
)


def test_iso_initial_and_first_step() -> None:
    with using_pack(ISO_PACK):
        states = sequence_states(ISO_YAML)
    assert states["steps"][0]["actuators"]["1A"] == 0
    assert states["steps"][0]["actuators"]["2A"] == 1 or states["steps"][0]["actuators"]["2A"] == 0
    after = states["steps"][1]
    assert after["action"] == "1A+"
    assert after["actuators"]["1A"] == 1


def test_explain_iso() -> None:
    with using_pack(ISO_PACK):
        exp = explain_yaml(ISO_YAML)
    joined = " ".join(exp["concepts"])
    assert "5/2" in joined or "double-acting" in joined
    assert len(exp["quiz"]) == 3


def test_suggest_patch_closed_center() -> None:
    text = (ROOT / "examples/closed_center/circuit.yaml").read_text()
    patch = suggest_patch(text)
    assert patch["yaml_patch"] and "relief_valves" in patch["yaml_patch"]
    out = draw_yaml(patch["yaml_patch"])
    assert out["ok"] is True
