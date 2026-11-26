from pathlib import Path

import json

from circuit.cli import main
from circuit.service import draw_yaml, list_symbols, validate_yaml


ROOT = Path(__file__).resolve().parents[1]


def test_draw_yaml_unknown_symbol_no_sheets() -> None:
    text = """
meta:
  title: bad valve
  domain: pneumatic_plus_electrical
sequence:
  - { action: 1A+, label: out }
power: { pumps: [], tank: "" }
cylinders:
  1A: { dcv: 1V, sensors: [1B1, 1B2] }
valves:
  1V: { type: not_a_symbol, solenoids: [1Y1, 1Y2] }
sensors: [1B1, 1B2]
electrical: { convention: lecture, paths: [] }
"""
    out = draw_yaml(text)
    assert out["ok"] is False
    assert out["sheets"] == {}
    assert out["sentence"] == "That symbol is not in the pack."


def test_draw_yaml_grinding_hydraulic() -> None:
    text = (ROOT / "examples/grinding_machine/circuit.yaml").read_text()
    out = draw_yaml(text)
    assert out["ok"] is True
    assert "<svg" in out["sheets"]["hydraulic"]


def test_draw_yaml_figure_given_calc_only() -> None:
    text = (ROOT / "examples/grind_given_2022/circuit.yaml").read_text()
    out = draw_yaml(text)
    assert "calc" in out["sheets"]
    assert "hydraulic" not in out["sheets"]


def test_draw_yaml_plc_sheets() -> None:
    text = (ROOT / "examples/plc_conveyor_2023/circuit.yaml").read_text()
    out = draw_yaml(text)
    assert "connection" in out["sheets"]
    assert "ladder" in out["sheets"]


def test_list_symbols_checkout_atlas() -> None:
    payload = list_symbols()
    ids = {s["id"]: s["ports"] for s in payload["symbols"]}
    assert "dcv_5_2_double_solenoid" in ids
    assert ids["dcv_5_2_double_solenoid"]


def test_cli_validate_json(capsys) -> None:
    code = main(["validate", "--json", str(ROOT / "examples/grinding_machine/circuit.yaml")])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True


def test_closed_center_no_hydraulic_sheet() -> None:
    path = ROOT / "examples/closed_center/circuit.yaml"
    if not path.is_file():
        return
    out = draw_yaml(path.read_text())
    assert out["ok"] is False
    assert "hydraulic" not in out["sheets"]
    assert "nowhere for the oil to go" in out["card"]
    assert "not a machine-safety certificate" in out["card"]
    assert "FAIL has_prv" in out["report"]
