from pathlib import Path

from circuit.compile_sequence import apply_compile
from circuit.pack import Pack, using_pack
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


def _compiled():
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    with using_pack(ISO_PACK):
        return apply_compile(spec)


def test_swap_plus_minus_coils_fails() -> None:
    spec = _compiled()
    for path in spec.electrical.paths:
        if path.coil == "1Y1":
            path.coil = "1Y2"
        elif path.coil == "1Y2":
            path.coil = "1Y1"
    with using_pack(ISO_PACK):
        vr = verify_spec(spec)
    assert vr.status is Status.FAIL
    assert vr.ok is False


def test_drop_latch_fails_or_unsupported() -> None:
    spec = _compiled()
    spec.electrical.paths = [p for p in spec.electrical.paths if p.coil != "K1"]
    with using_pack(ISO_PACK):
        vr = verify_spec(spec)
    assert vr.status in {Status.FAIL, Status.INCONCLUSIVE}
    assert vr.ok is False


def test_drop_last_transition_fails() -> None:
    spec = _compiled()
    spec.electrical.paths = spec.electrical.paths[:-1]
    with using_pack(ISO_PACK):
        vr = verify_spec(spec)
    assert vr.ok is False


def test_rewire_completion_sensor_fails() -> None:
    spec = _compiled()
    for path in spec.electrical.paths:
        contacts = [c.replace("1B2", "2B2") for c in (path.contacts or [])]
        path.contacts = contacts
    with using_pack(ISO_PACK):
        vr = verify_spec(spec)
    assert vr.ok is False


def test_flip_nc_to_no_fails() -> None:
    spec = _compiled()
    flipped = False
    for path in spec.electrical.paths:
        contacts = list(path.contacts or [])
        for i, c in enumerate(contacts):
            if c.startswith("!"):
                contacts[i] = c[1:]
                path.contacts = contacts
                flipped = True
                break
        if flipped:
            break
    assert flipped
    with using_pack(ISO_PACK):
        vr = verify_spec(spec)
    assert vr.ok is False


def test_drop_timer_coil_fails() -> None:
    spec = CircuitSpec.from_yaml(
        ROOT / "benchmarks/sequencebench/cases/case_15.yaml"
    )
    with using_pack(ISO_PACK):
        compiled = apply_compile(spec)
        compiled.electrical.paths = [
            p for p in compiled.electrical.paths if "T1" not in (p.coil or "")
        ]
        vr = verify_spec(compiled)
    assert vr.status is Status.FAIL
    assert vr.ok is False


def test_cascade_group_valves_exist_fluid_topology_not_claimed() -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    spec.meta.method = "cascade"
    from circuit.cascade import apply_cascade

    applied = apply_cascade(spec)
    assert "G1" in applied.valves
    with using_pack(ISO_PACK):
        vr = verify_spec(spec)
    assert vr.status is Status.PASS
    assert vr.stats.get("physics") not in {"PASS", "pass"}
