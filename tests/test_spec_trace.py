from pathlib import Path

from circuit.semantics.spec_trace import spec_trace
from circuit.spec import CircuitSpec


ROOT = Path(__file__).resolve().parents[1]


def test_iso_spec_trace_table() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    rows = spec_trace(spec)
    assert rows[0] == {"1A": 0, "2A": 0}
    assert rows[1]["1A"] == 1
    src = (ROOT / "src/circuit/semantics/spec_trace.py").read_text()
    assert "compile_paths" not in src
    assert "draw_phase" not in src
