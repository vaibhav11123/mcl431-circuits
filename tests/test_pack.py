from pathlib import Path

import pytest

from circuit.catalog import glyph
from circuit.draw import draw_all
from circuit.pack import resolve_pack, using_pack
from circuit.spec import CircuitSpec
from circuit.validate import all_ok, load_atlas_ids, validate_spec


ROOT = Path(__file__).resolve().parents[1]


def test_resolve_pack_temp_atlas(tmp_path: Path) -> None:
    (tmp_path / "atlas.yaml").write_text("symbols:\n- id: dcv_5_2\n  ports: [1, 2, 3, 4, 5]\n")
    pack = resolve_pack(tmp_path)
    assert load_atlas_ids(pack.root) == {"dcv_5_2"}


def test_resolve_pack_default_is_checkout() -> None:
    pack = resolve_pack()
    assert pack.root == ROOT
    assert "dcv_5_2_double_solenoid" in load_atlas_ids(pack.root)


def test_validate_grinding_with_no_pack_flag() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    checks = validate_spec(spec, ROOT)
    assert all_ok(checks)


def test_using_pack_draw_grinding_svg(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    with using_pack(resolve_pack()):
        written = draw_all(spec, tmp_path)
    svg = written["hydraulic"].read_text()
    assert "<svg" in svg


def test_using_pack_missing_stamp_raises(tmp_path: Path) -> None:
    (tmp_path / "atlas.yaml").write_text("symbols: []\n")
    (tmp_path / "stamps").mkdir()
    pack = resolve_pack(tmp_path)
    with using_pack(pack):
        with pytest.raises(FileNotFoundError, match="cylinder_da.png"):
            glyph("cylinder_da")
