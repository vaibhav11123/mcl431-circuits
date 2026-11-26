from circuit.service import draw_yaml, validate_yaml


def test_nested_yaml_rejected() -> None:
    node = "a: 1"
    for _ in range(30):
        node = "k:\n  " + node.replace("\n", "\n  ")
    out = validate_yaml(node)
    assert out["ok"] is False
    assert out["checks"][0]["name"] in {"depth", "parse"}


def test_too_many_cylinders_rejected() -> None:
    cyls = "\n".join(
        f"  {i}A: {{ dcv: 1V, sensors: [1B1, 1B2] }}" for i in range(1, 12)
    )
    text = f"""
meta: {{ title: too many, domain: pneumatic_plus_electrical }}
sequence:
  - {{ action: 1A+, label: x }}
power: {{ pumps: [], tank: "" }}
cylinders:
{cyls}
valves:
  1V: {{ type: dcv_5_2_double_solenoid, solenoids: [1Y1, 1Y2] }}
sensors: [1B1, 1B2]
electrical: {{ convention: lecture, paths: [] }}
"""
    out = draw_yaml(text)
    assert out["ok"] is False
    assert out["sheets"] == {}
