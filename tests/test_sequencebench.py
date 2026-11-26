from pathlib import Path

from circuit.ir.from_spec import from_spec
from circuit.pack import Pack, using_pack
from circuit.semantics.env_trace import compress_changes, env_trace
from circuit.service import eval_yaml
from circuit.spec import CircuitSpec
from circuit.verification.refine import verify_spec
from circuit.verification.status import Status
from tests.oracles.expected_trace import expected_trace


ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "examples/sequencebench"
ISO_PACK = Pack(
    root=ROOT / "src/circuit/packs/iso_sequence",
    atlas_path=ROOT / "src/circuit/packs/iso_sequence/atlas.yaml",
    stamp_dir=ROOT / "src/circuit/packs/iso_sequence/stamps",
    hooks_module="circuit.packs.iso_sequence",
)


def test_sequencebench_thirty_original() -> None:
    cases = sorted(BENCH.glob("case_*.yaml"))
    assert len(cases) == 30
    text = "\n".join(p.read_text() for p in cases)
    assert "exams/transcribed" not in text
    assert "2023_selfstudy_b1" not in text
    with using_pack(ISO_PACK):
        ok = 0
        for path in cases:
            spec = CircuitSpec.from_yaml(path)
            assert spec.meta.exam_id is None
            report = eval_yaml(path.read_text())
            if report["ok"]:
                ok += 1
    assert ok >= 20


def test_sequencebench_expected_traces_independent() -> None:
    oracle = (ROOT / "tests/oracles/expected_trace.py").read_text()
    assert "spec_trace" not in oracle
    cases = sorted(BENCH.glob("case_*.yaml"))
    matched = 0
    unsupported = 0
    with using_pack(ISO_PACK):
        for path in cases:
            spec = CircuitSpec.from_yaml(path)
            want = expected_trace(
                [s.action for s in spec.sequence],
                list(spec.cylinders),
            )
            vr = verify_spec(spec)
            if vr.status is Status.UNSUPPORTED:
                unsupported += 1
                continue
            if vr.status is Status.PASS:
                graph = from_spec(spec)
                got = compress_changes(env_trace(graph)["rows"])
                assert got == compress_changes(want)
                matched += 1
            else:
                assert vr.status in {Status.FAIL, Status.INCONCLUSIVE}
    assert unsupported >= 1
    assert matched >= 8
