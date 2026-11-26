from pathlib import Path

from circuit.pack import Pack, using_pack
from circuit.service import draw_yaml
from circuit.spec import CircuitSpec
from circuit.layout.metrics import layout_metrics
from circuit.verification.layout import layout_metrics as line_metrics
from circuit.verification.synthesize import pick_smaller, two_topologies


ROOT = Path(__file__).resolve().parents[1]


def test_layout_metrics_iso() -> None:
    pack = Pack(
        root=ROOT / "src/circuit/packs/iso_sequence",
        atlas_path=ROOT / "src/circuit/packs/iso_sequence/atlas.yaml",
        stamp_dir=ROOT / "src/circuit/packs/iso_sequence/stamps",
        hooks_module="circuit.packs.iso_sequence",
    )
    with using_pack(pack):
        out = draw_yaml((ROOT / "examples/iso_sequence/circuit.yaml").read_text())
    svg = out["sheets"]["pneumatic"]
    m = layout_metrics(svg)
    assert m["lines"] > 0
    assert "crossings" in m
    assert "overlaps" in m
    assert "ms" in m
    assert line_metrics(svg)["crossings"] == m["crossings"]


def test_pick_smaller_topology() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    chosen = pick_smaller(two_topologies(spec))
    assert len(chosen.valves) == len(spec.valves)
