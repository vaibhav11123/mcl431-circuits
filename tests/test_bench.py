import json
from pathlib import Path

from circuit.bench import run_bench
from circuit.cli import main


ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks" / "sequencebench"


def test_sequencebench_v0_layout() -> None:
    cases = sorted((BENCH / "cases").glob("case_*.yaml"))
    assert len(cases) == 30
    blob = "\n".join(p.read_text() for p in cases)
    assert "exam_id" not in blob
    assert "2023_selfstudy" not in blob
    assert "emboss_2016" not in blob
    for path in cases:
        expected = json.loads(path.with_name(path.stem + ".expected.json").read_text())
        assert expected["decision"] in {"accept", "reject"}
        assert expected["reason"]


def test_sequencebench_invented_and_legal(capsys) -> None:
    report = run_bench(BENCH)
    by_id = {row["id"]: row for row in report["rows"]}
    assert by_id["case_25"]["got"] == "reject"
    assert by_id["case_00"]["got"] == "accept"
    assert report["n"] == 30
    assert "accepted_error_rate" in report
    rc = main(["bench", str(BENCH)])
    assert rc == 0
    printed = json.loads(capsys.readouterr().out)
    assert "accepted_error_rate" in printed


def test_docs_plan_paths() -> None:
    adr = ROOT / "docs" / "adr"
    for i in range(1, 9):
        text = (adr / f"ADR-{i:03d}.md").read_text()
        assert "Revisit when" in text
    post = (ROOT / "docs" / "postmortems" / "b1-2y1-kstart.md").read_text()
    assert "2Y1" in post and "K_START" in post
    assert (ROOT / "docs" / "interview-narrative.md").is_file()
    assert (ROOT / "docs" / "user-study.md").is_file()
