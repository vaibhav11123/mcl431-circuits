from pathlib import Path

from circuit.ir.graph import CircuitGraph, GraphEdge, GraphNode
from circuit.ir.ports import Port
from circuit.ir.typecheck import typecheck, typecheck_graph
from circuit.pack import Pack, using_pack
from circuit.spec import CircuitSpec, CurrentPath
from circuit.validate import all_ok


ROOT = Path(__file__).resolve().parents[1]
ISO_ROOT = ROOT / "src/circuit/packs/iso_sequence"
ISO_PACK = Pack(
    root=ISO_ROOT,
    atlas_path=ISO_ROOT / "atlas.yaml",
    stamp_dir=ISO_ROOT / "stamps",
    hooks_module="circuit.packs.iso_sequence",
)


def test_iso_typecheck_ok() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    with using_pack(ISO_PACK):
        checks = typecheck(spec, ISO_ROOT)
    assert all_ok(checks)


def test_fluid_port_as_coil_e210() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    spec.electrical.paths = [CurrentPath(number=1, kind="main", contacts=["START"], coil="1")]
    with using_pack(ISO_PACK):
        checks = typecheck(spec, ISO_ROOT)
    failed = [c for c in checks if not c.ok]
    assert any("E210" in (c.name + c.detail) and "Compatible fluid-domain port" in c.detail for c in failed)
    src = (ROOT / "src/circuit/ir/typecheck.py").read_text()
    assert "invalid circuit" not in src


def test_typed_port_fluid_to_coil_e210() -> None:
    graph = CircuitGraph(
        nodes=[
            GraphNode(id="P1", kind="pump", domain="fluid"),
            GraphNode(id="K1", kind="coil", domain="electrical"),
        ],
        edges=[
            GraphEdge(
                src="P1",
                src_port="P",
                dst="K1",
                dst_port="A1",
                src_typed=Port(
                    component_id="P1",
                    port_id="P",
                    domain="fluid",
                    role="supply",
                ),
                dst_typed=Port(
                    component_id="K1",
                    port_id="A1",
                    domain="electrical",
                    role="coil",
                ),
            )
        ],
    )
    failed = [c for c in typecheck_graph(graph) if not c.ok]
    assert any(
        "E210" in (c.name + c.detail) and "Compatible fluid-domain port" in c.detail
        for c in failed
    )
