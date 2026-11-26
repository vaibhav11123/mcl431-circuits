import hashlib
from pathlib import Path

from circuit.cli import main
from circuit.pack import Pack, using_pack
from circuit.spec import CircuitSpec
from circuit.verification.manifest import write_manifest


ROOT = Path(__file__).resolve().parents[1]
ISO_PACK = Pack(
    root=ROOT / "src/circuit/packs/iso_sequence",
    atlas_path=ROOT / "src/circuit/packs/iso_sequence/atlas.yaml",
    stamp_dir=ROOT / "src/circuit/packs/iso_sequence/stamps",
    hooks_module="circuit.packs.iso_sequence",
)


def test_verify_manifest(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    with using_pack(ISO_PACK):
        man = write_manifest(spec, tmp_path)
    assert man["physics"] == "not_evaluated"
    assert man["refine"] in {"passed", "failed"}
    data = (tmp_path / "verify.json").read_text()
    assert "not_evaluated" in data
    assert hashlib.sha256(spec.to_yaml().encode()).hexdigest() == man["sha256_spec"]


def test_cli_verify_help() -> None:
    try:
        main(["verify", "--help"])
    except SystemExit as exc:
        assert exc.code == 0
