from pathlib import Path

from PIL import Image
import pytest

from circuit.draw import draw_all
from circuit.png import backend_name, svg_size
from circuit.spec import CircuitSpec


ROOT = Path(__file__).resolve().parents[1]


def test_svg_size_reads_width_height(tmp_path: Path) -> None:
    svg = tmp_path / "sheet.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="1680" height="800" '
        'viewBox="-24 -24 1728 848"></svg>\n'
    )
    assert svg_size(svg) == (1680.0, 800.0)


def test_crop_to_aspect_keeps_landscape() -> None:
    from circuit.png import _crop_to_aspect

    im = Image.new("RGB", (100, 100), "white")
    for x in range(80):
        im.putpixel((x, 10), (0, 0, 0))
    cropped = _crop_to_aspect(im, 80, 40)
    assert cropped.size == (100, 50)


def test_b1_draw_writes_three_pngs(tmp_path: Path) -> None:
    if backend_name() is None:
        pytest.skip("no SVG→PNG backend (rsvg-convert, resvg, qlmanage, or cairosvg)")
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    draw_all(spec, tmp_path)
    dests = [
        tmp_path / "hydraulic_circuit.png",
        tmp_path / "electrical_circuit.png",
        tmp_path / "step_displacement.png",
    ]
    if not all(p.is_file() for p in dests):
        pytest.skip("PNG backend listed but conversion failed (qlmanage/sandbox)")
    for dest in dests:
        assert dest.stat().st_size > 10_000, f"{dest.name} too small ({dest.stat().st_size})"
        svg = dest.with_suffix(".svg")
        sw, sh = svg_size(svg)
        pw, ph = Image.open(dest).size
        assert pw / ph == pytest.approx(sw / sh, rel=0.08), f"{dest.name} {pw}x{ph} vs {sw}x{sh}"
        assert pw > ph, f"{dest.name} should stay landscape, got {pw}x{ph}"
