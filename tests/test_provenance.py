from pathlib import Path

from circuit.draw import draw_all
from circuit.pack import Pack, using_pack
from circuit.provenance import p001, p002, tags_from_spec, tags_from_svg
from circuit.spec import CircuitSpec


ROOT = Path(__file__).resolve().parents[1]
ISO_ROOT = ROOT / "src/circuit/packs/iso_sequence"
ISO_PACK = Pack(
    root=ISO_ROOT,
    atlas_path=ISO_ROOT / "atlas.yaml",
    stamp_dir=ISO_ROOT / "stamps",
    hooks_module="circuit.packs.iso_sequence",
)


def test_p001_iso_sheets(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    with using_pack(ISO_PACK):
        written = draw_all(spec, tmp_path)
    svgs = [written[k].read_text() for k in ("pneumatic", "electrical") if k in written]
    assert p001(spec, svgs)
    assert p002(spec, svgs)
