from pathlib import Path

from circuit.pack import Pack, using_pack
from circuit.service import eval_yaml
from circuit.spec import CircuitSpec


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
