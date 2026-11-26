from pathlib import Path

from circuit.pack import Pack, using_pack
from circuit.service import draw_yaml
from circuit.spec import CircuitSpec, CurrentPath
from circuit.verification.refine import refine, verify_spec


ROOT = Path(__file__).resolve().parents[1]
ISO_ROOT = ROOT / "src/circuit/packs/iso_sequence"
ISO_PACK = Pack(
    root=ISO_ROOT,
    atlas_path=ISO_ROOT / "atlas.yaml",
    stamp_dir=ISO_ROOT / "stamps",
    hooks_module="circuit.packs.iso_sequence",
)


def test_iso_verify_ok() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    with using_pack(ISO_PACK):
        assert verify_spec(spec).ok is True


def test_refine_mismatch_step_zero() -> None:
    from circuit.verification.status import Status

    r = refine([{"1A": 0, "2A": 0}], [{"1A": 1, "2A": 0}])
    assert r.ok is False
    assert r.status is Status.FAIL
    assert r.cex_step == 0


def test_draw_yaml_stubbed_mismatch_no_sheets() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    spec.electrical.paths = [
        CurrentPath(number=1, kind="main", contacts=["START"], coil="1Y1"),
        CurrentPath(number=2, kind="main", contacts=["START"], coil="1Y2"),
    ]
    with using_pack(ISO_PACK):
        out = draw_yaml(spec.to_yaml())
    assert out["ok"] is False
    assert "pneumatic" not in out["sheets"]
