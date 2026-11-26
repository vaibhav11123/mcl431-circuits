from pathlib import Path

from circuit.cli import main
from circuit.spec import CircuitSpec, CurrentPath


ROOT = Path(__file__).resolve().parents[1]
ISO = str(ROOT / "src/circuit/packs/iso_sequence")


def test_cli_draw_planted_miscompile_exits_one(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    spec.electrical.paths = [
        CurrentPath(number=1, kind="main", contacts=["START"], coil="1Y1"),
        CurrentPath(number=2, kind="main", contacts=["START"], coil="1Y2"),
    ]
    case = tmp_path / "planted_fail" / "circuit.yaml"
    case.parent.mkdir()
    case.write_text(spec.to_yaml())
    code = main(["draw", "--pack", ISO, str(case)])
    assert code == 1
    out = ROOT / "output" / "planted_fail"
    assert not (out / "pneumatic_circuit.svg").exists()


def test_cli_draw_unverified_watermarks(tmp_path: Path) -> None:
    case = tmp_path / "unverified_iso" / "circuit.yaml"
    case.parent.mkdir()
    case.write_text((ROOT / "examples/iso_sequence/circuit.yaml").read_text())
    code = main(["draw", "--unverified", "--pack", ISO, str(case)])
    assert code == 0
    out = ROOT / "output" / "unverified_iso"
    svg = (out / "pneumatic_circuit.svg").read_text()
    assert "UNVERIFIED" in svg
