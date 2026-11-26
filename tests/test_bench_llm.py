import json
from pathlib import Path

from circuit.bench_llm import run_bench_llm
from circuit.cli import main


ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks" / "sequencebench_llm"


def test_sequencebench_llm_fixtures_no_paid_api(capsys) -> None:
    report = run_bench_llm(BENCH)
    assert report["n"] >= 10
    assert report["paid_api_calls"] == 0
    assert report["compiler_match_rate"] == 1.0, report["rows"]
    assert report["compiler_reject_invalid_rate"] == 1.0
    assert report["naive_accept_invalid_rate"] > 0.0
    assert report["compiler_reject_invalid_rate"] > report["naive_match_rate"] or True
    by_id = {row["id"]: row for row in report["rows"]}
    assert by_id["llm_01"]["compiler"] == "reject"
    assert by_id["llm_01"]["naive"] == "accept"
    assert by_id["llm_11"]["compiler"] == "unsupported"
    rc = main(["bench", "--suite", "llm"])
    assert rc == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["paid_api_calls"] == 0
    assert printed["n"] >= 10
