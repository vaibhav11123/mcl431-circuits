from circuit.service import SENTENCE_CT, SENTENCE_PHYSICS, draw_yaml


ISO = """meta:
  title: t
  domain: pneumatic_plus_electrical
  patterns: [ep_dac_5_2, sequence_double_solenoid]
sequence:
  - { action: 1A+, label: a }
  - { action: 2A+, label: b }
  - { action: 2A-, label: c }
  - { action: 1A-, label: d }
power: { pumps: [], tank: "" }
cylinders:
  1A: { dcv: 1V, sensors: [1B1, 1B2] }
  2A: { dcv: 2V, sensors: [2B1, 2B2] }
motors: {}
valves:
  1V: { type: dcv_5_2_double_solenoid, solenoids: [1Y1, 1Y2] }
  2V: { type: dcv_5_2_double_solenoid, solenoids: [2Y1, 2Y2] }
sensors: [1B1, 1B2, 2B1, 2B2]
electrical: { convention: lecture, paths: [] }
"""


def test_refuse_fluidsim_ct() -> None:
    out = draw_yaml("# export FluidSIM .ct\n" + ISO)
    assert out["ok"] is False
    assert out["sentence"] == SENTENCE_CT
    assert not out.get("sheets")


def test_refuse_simulate_pressure() -> None:
    out = draw_yaml("simulate pressure drop\n" + ISO)
    assert out["ok"] is False
    assert out["sentence"] == SENTENCE_PHYSICS
