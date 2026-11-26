from pathlib import Path

from circuit.ir.from_spec import from_spec
from circuit.ir.graph import CircuitGraph, GraphNode
from circuit.pack import Pack, using_pack
from circuit.semantics.graph_trace import graph_trace
from circuit.spec import CircuitSpec, CurrentPath


ROOT = Path(__file__).resolve().parents[1]
ISO_ROOT = ROOT / "src/circuit/packs/iso_sequence"
ISO_PACK = Pack(
    root=ISO_ROOT,
    atlas_path=ISO_ROOT / "atlas.yaml",
    stamp_dir=ISO_ROOT / "stamps",
    hooks_module="circuit.packs.iso_sequence",
)


def test_iso_graph_trace_rest() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    with using_pack(ISO_PACK):
        graph = from_spec(spec)
    tgt = graph_trace(graph, [{"START": False, "1B1": True, "2B1": True}])
    assert tgt[0]["1A"] == 0
    assert tgt[0]["2A"] == 0
    src = (ROOT / "src/circuit/semantics/graph_trace.py").read_text()
    assert "compile_paths" not in src
    assert "spec_trace" not in src
    assert "SeqStep" not in src


def test_graph_follows_coils_not_action_strings() -> None:
    graph = CircuitGraph(
        nodes=[GraphNode(id="1A", kind="cylinder", domain="fluid")],
        paths=[CurrentPath(number=1, kind="main", contacts=["GO"], coil="YY")],
        solenoid_plus={"1A": "YY"},
        solenoid_minus={"1A": "NN"},
        sensors_home={"1A": "1B1"},
        sensors_end={"1A": "1B2"},
    )
    tgt = graph_trace(graph, [{"GO": True}])
    assert tgt[0]["1A"] == 1
