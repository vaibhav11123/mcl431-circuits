from circuit.bench300 import generate_cases, run_bench300, suite_fingerprint
from circuit.cli import main


def test_sequencebench_300_reproducible(capsys) -> None:
    cases = generate_cases()
    assert len(cases) == 300
    ids = [c["id"] for c in cases]
    assert len(set(ids)) == 300
    blob = "\n".join(c["yaml"] for c in cases)
    assert "exams/transcribed" not in blob
    assert "2023_selfstudy" not in blob
    fp = suite_fingerprint(cases)
    assert fp == suite_fingerprint(generate_cases())
    report = run_bench300()
    assert report["n"] == 300
    assert report["fingerprint"] == fp
    assert report["accepted_error_rate"] == 0.0, report["mismatches"]
    assert report["reject_invalid_rate"] == 1.0, report["mismatches"]
    assert report["accept_n"] + report["reject_n"] == 300
    rc = main(["bench", "--suite", "300"])
    assert rc == 0
    printed = capsys.readouterr().out
    assert "accepted_error_rate" in printed
