from pathlib import Path

from circuit.draw import draw_all, draw_hydraulic
from circuit.draw_pneumatic import draw_pneumatic
from circuit.spec import CircuitSpec

ROOT = Path(__file__).resolve().parents[1]


def test_hilo_draw_all_has_no_electrical(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/hilo_punch_2017/circuit.yaml")
    draw_all(spec, tmp_path)
    assert not (tmp_path / "electrical_circuit.svg").exists()
    assert (tmp_path / "hydraulic_circuit.svg").exists()
    assert not (tmp_path / "step_displacement.svg").exists()


def test_b1_draw_all_still_has_electrical(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    draw_all(spec, tmp_path)
    assert (tmp_path / "electrical_circuit.svg").exists()
    assert (tmp_path / "hydraulic_circuit.svg").exists()


def test_b1_hydraulic_has_setpoint_and_actuators(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/grinding_machine/circuit.yaml")
    dest = tmp_path / "hydraulic_circuit.svg"
    draw_hydraulic(spec, dest)
    svg = dest.read_text()
    assert "15.72" in svg or "bar" in svg
    for token in ("HC1", "HC2", "HM1", "RV1", "JOB"):
        assert token in svg, token


def test_fall17_drill_draws_pneumatic_5_3(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/drill_2017/circuit.yaml")
    written = draw_all(spec, tmp_path)
    assert "pneumatic" in written
    assert (tmp_path / "pneumatic_circuit.svg").exists()
    assert (tmp_path / "electrical_circuit.svg").exists()
    assert (tmp_path / "step_displacement.svg").exists()
    svg = (tmp_path / "pneumatic_circuit.svg").read_text()
    for token in ("1V", "2V", "3V", "1Y1", "2Y2", "3Y1", "1A", "2A", "3A", "supply"):
        assert token in svg, token
    sol = (tmp_path / "solution.txt").read_text()
    assert "P1 = 1B1" in sol
    assert "3A+" in sol


def test_draw_pneumatic_stamps_dcv_5_2(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/strip_feed_2023/circuit.yaml")
    dest = tmp_path / "pneumatic_circuit.svg"
    draw_pneumatic(spec, dest)
    svg = dest.read_text()
    for token in ("1V", "2V", "1Y1", "1Y2", "2Y1", "2Y2", "1A", "2A", "supply"):
        assert token in svg, token
    assert (ROOT / "lecture/crops/dcv_5_2.png").is_file()
    assert (ROOT / "lecture/crops/stamps/dcv_5_2.png").is_file()
    assert dest.stat().st_size > 1000


def test_draw_pneumatic_stamps_dcv_5_3(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/drill_2017/circuit.yaml")
    dest = tmp_path / "pneumatic_circuit.svg"
    draw_pneumatic(spec, dest)
    svg = dest.read_text()
    assert "5/3" in svg or "1V" in svg
    assert dest.stat().st_size > 1000


def test_plc_draw_all_has_connection_and_ladder(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/plc_conveyor_2023/circuit.yaml")
    written = draw_all(spec, tmp_path)
    assert "connection" in written
    assert "ladder" in written
    assert not (tmp_path / "hydraulic_circuit.svg").exists()
    assert not (tmp_path / "electrical_circuit.svg").exists()
    assert not (tmp_path / "pneumatic_circuit.svg").exists()
    conn = (tmp_path / "plc_connection.svg").read_text()
    lad = (tmp_path / "plc_ladder.svg").read_text()
    for token in ("Slot-3", "Slot-2", "I0.0", "I0.1", "Q0.0", "949", "2500", "0–10 V"):
        assert token in conn, token
    for token in ("MOV 303", "MOV 575", "MOV 907", "MOV 0", "M0.0", "L1", "L2", "L3"):
        assert token in lad, token
    sol = (tmp_path / "solution.txt").read_text()
    assert "MOV 0 AO" in sol
    assert "949" in sol
    assert "907" in sol


def test_emboss_2016_draws_pneumatic_electrical_phase(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/emboss_2016/circuit.yaml")
    written = draw_all(spec, tmp_path)
    assert "pneumatic" in written
    assert "electrical" in written
    assert "phase" in written
    pneu = (tmp_path / "pneumatic_circuit.svg").read_text()
    for token in ("1A1", "2A1", "1V", "2V", "1Y1", "2Y2", "PS", "4 bar", "Bill of material"):
        assert token in pneu, token
    elec = (tmp_path / "electrical_circuit.svg").read_text()
    for token in ("S1", "S0", "PS", "1Y1", "2Y2", "K4", "K5"):
        assert token in elec, token
    assert "2B2" not in elec
    assert "!K5" not in elec
    assert "!1Y2" not in elec
    phase = (tmp_path / "step_displacement.svg").read_text()
    assert "PS" in phase
    assert "4 bar" in phase
    sol = (tmp_path / "solution.txt").read_text()
    assert "PS≥4 bar" in sol or "4 bar" in sol
    assert "2B2 is position" in sol
