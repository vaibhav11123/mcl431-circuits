from pathlib import Path

from circuit.compile_sequence import apply_compile
from circuit.ir.from_spec import from_spec
from circuit.pack import Pack, using_pack
from circuit.spec import CircuitSpec
from circuit.verification.artifact import seal
from circuit.verification.refine import verify_spec
from circuit.verification.status import Status


ROOT = Path(__file__).resolve().parents[1]
ISO_PACK = Pack(
    root=ROOT / "src/circuit/packs/iso_sequence",
    atlas_path=ROOT / "src/circuit/packs/iso_sequence/atlas.yaml",
    stamp_dir=ROOT / "src/circuit/packs/iso_sequence/stamps",
    hooks_module="circuit.packs.iso_sequence",
)


def test_seal_requires_same_paths() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    with using_pack(ISO_PACK):
        compiled = apply_compile(spec)
        graph = from_spec(compiled)
        vr = verify_spec(compiled)
        sealed = seal(compiled, graph, vr)
    assert vr.status is Status.PASS
    assert sealed.spec.electrical.paths == graph.paths
