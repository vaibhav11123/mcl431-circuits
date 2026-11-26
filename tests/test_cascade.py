from pathlib import Path

from circuit.cascade import apply_cascade, groups_for
from circuit.pack import Pack, using_pack
from circuit.service import draw_yaml
from circuit.spec import CircuitSpec


ROOT = Path(__file__).resolve().parents[1]
ISO_ROOT = ROOT / "src/circuit/packs/iso_sequence"
ISO_PACK = Pack(
    root=ISO_ROOT,
    atlas_path=ISO_ROOT / "atlas.yaml",
    stamp_dir=ISO_ROOT / "stamps",
    hooks_module="circuit.packs.iso_sequence",
)


def test_two_cyl_cascade_has_g1() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    spec.meta.method = "cascade"
    out = apply_cascade(spec)
    assert "G1" in out.valves
    with using_pack(ISO_PACK):
        drawn = draw_yaml(out.to_yaml())
    svg = drawn["sheets"].get("pneumatic", "")
    assert "G1" in svg


def test_four_cyl_cascade_refused() -> None:
    text = (ROOT / "examples/iso_sequence/circuit.yaml").read_text()
    text = text.replace("method:", "method: cascade\n  x:")
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    spec.meta.method = "cascade"
    spec.cylinders["3A"] = spec.cylinders["1A"].model_copy()
    spec.cylinders["3A"].dcv = "3V"
    spec.valves["3V"] = spec.valves["1V"].model_copy()
    spec.cylinders["4A"] = spec.cylinders["1A"].model_copy()
    spec.cylinders["4A"].dcv = "4V"
    spec.valves["4V"] = spec.valves["1V"].model_copy()
    with using_pack(ISO_PACK):
        out = draw_yaml(spec.to_yaml())
    assert out["ok"] is False
    assert "pneumatic" not in out["sheets"]
    assert "Cascade for more than three cylinders" in out["sentence"]


def test_no_fluidpyplc_in_src() -> None:
    """GPL FluidPyPLC must not be vendored. Search in-process so CI needs no rg."""
    skip = {"__pycache__", ".pytest_cache"}
    hits = []
    for path in (ROOT / "src").rglob("*"):
        if not path.is_file() or any(part in skip for part in path.parts):
            continue
        if path.suffix.lower() not in {".py", ".md", ".txt", ".yaml", ".yml"}:
            continue
        if "FluidPyPLC" in path.read_text(encoding="utf-8", errors="ignore"):
            hits.append(str(path.relative_to(ROOT)))
    assert hits == []
