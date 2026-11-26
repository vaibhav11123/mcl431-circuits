from pathlib import Path

from circuit.ir.from_spec import from_spec
from circuit.pack import Pack, using_pack
from circuit.service import draw_yaml
from circuit.spec import CircuitSpec, CurrentPath
from circuit.verification.refine import verify_spec
from circuit.verification.status import Status


ROOT = Path(__file__).resolve().parents[1]
ISO = Pack(
    root=ROOT / "src/circuit/packs/iso_sequence",
    atlas_path=ROOT / "src/circuit/packs/iso_sequence/atlas.yaml",
    stamp_dir=ROOT / "src/circuit/packs/iso_sequence/stamps",
    hooks_module="circuit.packs.iso_sequence",
)


def test_timer_sequence_verifies() -> None:
    spec = CircuitSpec.from_yaml(
        ROOT / "benchmarks/sequencebench/cases/case_15.yaml"
    )
    with using_pack(ISO):
        vr = verify_spec(spec)
        out = draw_yaml(spec.to_yaml())
    assert vr.status is Status.PASS, vr.stats
    assert out["ok"] is True
    assert "T1" in (out["sheets"].get("electrical") or "")


def test_pressure_wait_still_unsupported() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    spec.sequence[1].action = "PS"
    with using_pack(ISO):
        vr = verify_spec(spec)
    assert vr.status is Status.UNSUPPORTED
    assert vr.stats.get("reason") == "pressure wait"


def test_cascade_two_cylinder_verifies() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    spec.meta.method = "cascade"
    with using_pack(ISO):
        vr = verify_spec(spec)
        out = draw_yaml(spec.to_yaml())
    assert vr.status is Status.PASS, vr.stats
    assert out["ok"] is True
    assert "G1" in (out["sheets"].get("pneumatic") or "")


def test_deadlock_fail_not_pass() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    spec.electrical.paths = [
        CurrentPath(number=1, kind="main", contacts=["START"], coil="1Y1"),
    ]
    with using_pack(ISO):
        vr = verify_spec(spec)
        graph = from_spec(spec)
        from circuit.semantics.env_trace import env_trace

        run = env_trace(graph)
    assert vr.ok is False
    assert vr.status is Status.FAIL
    assert run.get("deadlock") or vr.stats.get("check") in {
        "deadlock",
        "env_trace",
        "start_dual_solenoid",
    }
