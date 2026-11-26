from pathlib import Path

from tests.oracles.expected_trace import expected_trace

from circuit.compile_sequence import apply_compile
from circuit.ir.from_spec import from_spec
from circuit.pack import Pack, using_pack
from circuit.spec import CircuitSpec
from circuit.verification.packcheck import verify_included_graph, verify_zip, write_circuit_zip
from circuit.verification.refine import verify_spec


ROOT = Path(__file__).resolve().parents[1]
ISO_PACK = Pack(
    root=ROOT / "src/circuit/packs/iso_sequence",
    atlas_path=ROOT / "src/circuit/packs/iso_sequence/atlas.yaml",
    stamp_dir=ROOT / "src/circuit/packs/iso_sequence/stamps",
    hooks_module="circuit.packs.iso_sequence",
)


def test_packcheck_source_has_no_synthesizer() -> None:
    src = (ROOT / "src/circuit/verification/packcheck.py").read_text()
    assert "from circuit.compile" not in src
    assert "import circuit.compile" not in src


def test_verify_zip_uses_included_graph(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    with using_pack(ISO_PACK):
        compiled = apply_compile(spec)
        graph = from_spec(compiled)
        vr = verify_spec(compiled)
        assert vr.ok
        expected = expected_trace(
            [s.action for s in spec.sequence], list(spec.cylinders)
        )
        zpath = write_circuit_zip(
            tmp_path / "pack.zip",
            source_yaml=spec.to_yaml(),
            graph=graph,
            expected=expected,
            verification={"status": vr.status.value, "stats": vr.stats},
        )
        out = verify_zip(zpath)
    assert out["ok"] is True
    assert out["status"] == "PASS"


def test_verify_included_graph_catches_swap() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    with using_pack(ISO_PACK):
        compiled = apply_compile(spec)
        graph = from_spec(compiled)
    graph.solenoid_plus["1A"], graph.solenoid_minus["1A"] = (
        graph.solenoid_minus["1A"],
        graph.solenoid_plus["1A"],
    )
    expected = expected_trace(
        [s.action for s in spec.sequence], list(spec.cylinders)
    )
    out = verify_included_graph(graph, expected)
    assert out["ok"] is False
