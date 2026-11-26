from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PNG = b"\x89PNG\r\n\x1a\n"


def test_iso_pack_filenames_are_not_lecture_crops() -> None:
    stamps = ROOT / "src/circuit/packs/iso_sequence/stamps"
    names = {p.name for p in stamps.iterdir()}
    assert names <= {"dcv_5_2.png", "dcv_5_3.png"}
    assert "cylinder_l10.png" not in names
    assert "cylinder_da.png" not in names


def test_plugin_tree_has_no_lecture_png() -> None:
    plugin = ROOT / "plugin"
    for path in plugin.rglob("*"):
        if path.is_file():
            data = path.read_bytes()[:16]
            assert not data.startswith(PNG)
            text = path.read_text(encoding="utf-8", errors="ignore")
            assert "lecture/crops" not in text


def test_iso_python_has_no_embedded_lecture_png() -> None:
    iso = ROOT / "src/circuit/packs/iso_sequence.py"
    blob = iso.read_bytes()
    assert PNG not in blob
    assert b"lecture/crops" not in blob
