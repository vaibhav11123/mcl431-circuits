from pathlib import Path

from circuit.ir.from_spec import from_spec
from circuit.pack import Pack, using_pack
from circuit.semantics.env_trace import compress_changes, env_trace
from circuit.spec import CircuitSpec
from circuit.verification.refine import verify_spec
from circuit.verification.status import Status


ROOT = Path(__file__).resolve().parents[1]
ISO_PACK = Pack(
    root=ROOT / "src/circuit/packs/iso_sequence",
    atlas_path=ROOT / "src/circuit/packs/iso_sequence/atlas.yaml",
    stamp_dir=ROOT / "src/circuit/packs/iso_sequence/stamps",
    hooks_module="circuit.packs.iso_sequence",
)


def test_env_trace_file_is_independent() -> None:
    src = (ROOT / "src/circuit/semantics/env_trace.py").read_text()
    assert "compile_paths" not in src
    assert "import circuit.compile" not in src
    assert "from circuit.compile" not in src
    assert "from circuit.semantics.spec_trace" not in src
    assert "_solenoid_for" not in src


def test_iso_env_trace_matches_required_run() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    with using_pack(ISO_PACK):
        graph = from_spec(spec)
        run = env_trace(graph)
        vr = verify_spec(spec)
    assert run["conflict"] is None
    assert run["exhausted"] is False
    rows = compress_changes(run["rows"])
    assert rows[0] == {"1A": 0, "2A": 0}
    assert rows[-1] == {"1A": 0, "2A": 0}
    assert vr.status is Status.PASS


def test_refine_source_does_not_drive_sensors() -> None:
    src = (ROOT / "src/circuit/verification/refine.py").read_text()
    assert "_solenoid_for" not in src
    assert "sensor_envs_from_positions" not in src
