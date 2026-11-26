from pathlib import Path

from circuit.export_pack import bom_text, preview_png, principle_text
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


def test_iso_pack_files_keys() -> None:
    text = (ROOT / "examples/iso_sequence/circuit.yaml").read_text()
    with using_pack(ISO_PACK):
        out = draw_yaml(text)
    files = out["pack_files"]
    for key in (
        "pneumatic_svg",
        "electrical_svg",
        "phase_svg",
        "pneumatic_png",
        "pdf",
        "bom",
        "principle",
        "report",
    ):
        assert key in files, key
    assert files["pdf"][:4] == b"%PDF"
    assert "1V" in files["bom"]
    assert "1A" in files["bom"]
    assert "1A+" in files["principle"]
    assert "1Y" in files["principle"]


def test_preview_png_cap(tmp_path: Path) -> None:
    text = (ROOT / "examples/iso_sequence/circuit.yaml").read_text()
    with using_pack(ISO_PACK):
        out = draw_yaml(text)
    png_bytes = out["pack_files"]["pneumatic_png"]
    src = tmp_path / "print.png"
    src.write_bytes(png_bytes)
    preview = preview_png(src)
    from PIL import Image
    import io

    im = Image.open(io.BytesIO(preview))
    assert im.width <= 800
    assert len(preview) <= 200_000


def test_bom_principle_helpers() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    assert "1V" in bom_text(spec)
    assert "1A+" in principle_text(spec)
    assert "1Y" in principle_text(spec)
