import hashlib
from pathlib import Path

from circuit.pack import Pack, using_pack
from circuit.spec import CircuitSpec
from circuit.verification.manifest import write_manifest


ROOT = Path(__file__).resolve().parents[1]


def test_cli_vs_inprocess_hash(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    pack = Pack(
        root=ROOT / "src/circuit/packs/iso_sequence",
        atlas_path=ROOT / "src/circuit/packs/iso_sequence/atlas.yaml",
        stamp_dir=ROOT / "src/circuit/packs/iso_sequence/stamps",
        hooks_module="circuit.packs.iso_sequence",
    )
    with using_pack(pack):
        a = write_manifest(spec, tmp_path / "a")
        b = write_manifest(spec, tmp_path / "b")
    assert a["sha256_spec"] == b["sha256_spec"]
    assert a["sha256_spec"] == hashlib.sha256(spec.to_yaml().encode()).hexdigest()
