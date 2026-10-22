from __future__ import annotations

from pathlib import Path

from circuit.ingest_extract import build_draft
from circuit.ingest_index import diff_row, format_diff, match

ROOT = Path(__file__).resolve().parents[1]


def test_match_2023_jpeg_basename() -> None:
    rows = match(ROOT, "MCL431_Minor2_2022-23.jpeg")
    ids = {r["id"] for r in rows}
    assert "2023_minor2_q1" in ids
    assert "2023_minor2_q2" in ids


def test_diff_missing_3545_is_miss() -> None:
    rows = match(ROOT, "MCL431_Minor2_2022-23.jpeg")
    q2 = next(r for r in rows if r["id"] == "2023_minor2_q2")
    # Draft with most speeds but not 3545
    md = (
        "PLC conveyor 0-4000 RPM, 2250 RPM at 470 kg, "
        "1185 RPM below 220 kg, load cell 0-950 kg, START STOP. Missing high band."
    )
    draft = build_draft(source="MCL431_Minor2_2022-23.jpeg", markdown=md)
    result = diff_row(ROOT, q2, draft)
    assert result["status"] == "locked"
    assert result["ok"] is False
    assert "3545" in result["missing_numbers"]


def test_diff_q1_prose_sequence_satisfies_seq_ids() -> None:
    rows = match(ROOT, "MCL431_Minor2_2022-23.jpeg")
    q1 = next(r for r in rows if r["id"] == "2023_minor2_q1")
    md = (
        "Q1. Cylinder 1A holds the sheet metal strip and cylinder 2A retracts. "
        "Cylinder 1A releases the strip and cylinder 2A returns to the forward "
        "end position. Main switch S1. Push button S3. [30 Marks]"
    )
    draft = build_draft(source="MCL431_Minor2_2022-23.jpeg", markdown=md)
    result = diff_row(ROOT, q1, draft)
    assert result["status"] == "locked"
    assert not any(m.startswith("seq:") for m in result["missing_identifiers"]), result


def test_diff_all_speeds_clean() -> None:
    rows = match(ROOT, "MCL431_Minor2_2022-23.jpeg")
    q2 = next(r for r in rows if r["id"] == "2023_minor2_q2")
    md = (
        "START STOP. Load cell 0-950 kg. Analog 0-10 V. Speeds 0-4000 RPM. "
        "At 470 kg use 2250 RPM. Above 580 kg use 3545 RPM. "
        "Below 220 kg use 1185 RPM. Lamps L1 L2 L3."
    )
    draft = build_draft(source="MCL431_Minor2_2022-23.jpeg", markdown=md)
    # Ensure identifiers from index appear
    draft["questions"][0]["identifiers"] = list(
        dict.fromkeys(draft["questions"][0]["identifiers"] + ["START", "STOP"])
    )
    result = diff_row(ROOT, q2, draft)
    assert result["status"] == "locked"
    assert result["missing_numbers"] == [], result
    assert result["ok"] is True


def test_4000_does_not_satisfy_40000() -> None:
    from circuit.ingest_extract import numbers_equal

    assert not numbers_equal("4000", "40000")
    rows = match(ROOT, "MCL431_Minor2_2022-23.jpeg")
    q2 = next(r for r in rows if r["id"] == "2023_minor2_q2")
    # Only 40000 — must miss 4000
    md = "Motor 0-40000 RPM. START STOP. 950 kg. 2250 3545 1185 220 470 580."
    draft = build_draft(source="MCL431_Minor2_2022-23.jpeg", markdown=md)
    draft["questions"][0]["identifiers"] = ["START", "STOP"]
    result = diff_row(ROOT, q2, draft)
    assert "4000" in result["missing_numbers"]


def test_missing_facts_path_does_not_raise(tmp_path: Path) -> None:
    row = {
        "id": "ghost",
        "file": "exams/transcribed/does_not_exist_folder",
        "identifiers": ["HC1"],
        "source": "ghost.pdf",
    }
    draft = build_draft(source="ghost.pdf", markdown="HC1 clamp")
    result = diff_row(ROOT, row, draft)
    assert result["status"] == "new"
    assert result["ok"] is True or "HC1" not in result["missing_identifiers"]


def test_format_diff_no_row() -> None:
    assert "no index row" in format_diff([])
