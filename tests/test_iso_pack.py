import os
from pathlib import Path

from circuit.draw import draw_all
from circuit.pack import Pack, using_pack
from circuit.service import draw_yaml, eval_yaml
from circuit.spec import CircuitSpec


ROOT = Path(__file__).resolve().parents[1]
ISO_ROOT = ROOT / "src/circuit/packs/iso_sequence"
ISO_PACK = Pack(
    root=ISO_ROOT,
    atlas_path=ISO_ROOT / "atlas.yaml",
    stamp_dir=ISO_ROOT / "stamps",
    hooks_module="circuit.packs.iso_sequence",
)


def _iso_text() -> str:
    return (ROOT / "examples/iso_sequence/circuit.yaml").read_text()


def test_iso_stamps_dir_has_only_cc_by_rasters() -> None:
    names = {p.name for p in (ISO_ROOT / "stamps").iterdir()}
    assert "dcv_5_2.png" in names
    assert "dcv_5_3.png" in names
    assert "cylinder_l10.png" not in names


def test_iso_draw_no_lecture_crops(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    with using_pack(ISO_PACK):
        written = draw_all(spec, tmp_path)
    svg = written["pneumatic"].read_text()
    assert "lecture/crops" not in svg
    assert "cylinder_l10" not in svg
    assert 'data-rest="right"' in svg
    sol = written["solution"].read_text()
    assert "hold strip" in sol
    assert "feed" in sol
    assert "retract feed" in sol
    assert "release" in sol
    assert "enabling condition" not in sol.lower()


def test_iso_draw_yaml() -> None:
    with using_pack(ISO_PACK):
        out = draw_yaml(_iso_text())
    assert out["ok"] is True
    assert "<svg" in out["sheets"]["pneumatic"]
    assert "1V" in out["sheets"]["pneumatic"]


def test_iso_svg_bytes_stable(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")

    def once() -> bytes:
        dest = tmp_path / "a"
        dest.mkdir(exist_ok=True)
        with using_pack(ISO_PACK):
            written = draw_all(spec, dest)
        return written["pneumatic"].read_bytes()

    a = once()
    b = once()
    assert a == b
    assert os.environ.get("CIRCUIT_PACK") is None


def test_iso_eval_ok() -> None:
    with using_pack(ISO_PACK):
        report = eval_yaml(_iso_text())
    assert report["ok"] is True
    names = [c["name"] for c in report["checks"] if c["ok"]]
    assert "no_solenoid_as_contact" in names
