from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from circuit.ingest_extract import (
    build_draft,
    draft_number_pool,
    is_quarantine,
    normalize_number,
    numbers_equal,
    rules_check,
)
from circuit.spec import CircuitSpec

FIXTURE = Path(__file__).parent / "fixtures" / "docling_min.json"

SPEED_MD = (
    "The conveyor speed controller takes 0-10 V input controlling RPM "
    "from 0-4000. Move at 2250 RPM when 470 kg. If weight greater than "
    "580 kg, speed increases to 3545 RPM. If weight falls below 220 kg, "
    "speed is reduced to 1185 RPM. Load cell measuring 0-950 kg."
)


def test_normalize_and_equality() -> None:
    assert normalize_number("2.50") == normalize_number("2.5")
    assert numbers_equal("2.50", "2.5")
    assert not numbers_equal("4000", "40000")
    assert "40000" not in {normalize_number("4000")}


def test_2023_speeds_from_markdown() -> None:
    draft = build_draft(source="x.jpeg", markdown=SPEED_MD, kind="ingest_draft")
    pool = draft_number_pool(draft)
    for n in ("4000", "2250", "3545", "1185", "950", "220", "470", "580"):
        assert n in pool, f"missing {n} in {sorted(pool)}"
    assert "40000" not in pool


def test_explicit_sequence_tokens_merge_prose_without_inventing_extend() -> None:
    """Compact glyphs win; prose may add retract but not invent 2A+."""
    draft = build_draft(
        source="x.pdf",
        markdown="Motion: 1A+ 2A- then cylinder 2A retracts.",
        kind="ingest_draft",
    )
    tokens = draft["questions"][0]["sequence_tokens"]
    assert "1A+" in tokens
    assert "2A-" in tokens
    assert "2A+" not in tokens


def test_prose_infers_2023_q1_sequence_tokens() -> None:
    md = (
        "Q1. Cylinder 1A holds the sheet metal strip and cylinder 2A retracts. "
        "Cylinder 1A releases the strip and cylinder 2A returns to the forward "
        "end position. [30 Marks]"
    )
    draft = build_draft(source="2023.jpeg", markdown=md, kind="ingest_draft")
    tokens = draft["questions"][0]["sequence_tokens"]
    assert tokens == ["1A+", "2A-", "1A-", "2A+"], tokens


def test_size_table_stays_rows_no_bore_pick() -> None:
    md = """
Q1. Choose a cylinder from the table.
| Piston Dia (mm) | 50 | 63 | 80 | 100 | 125 |
| Rod Dia Small (mm) | 28 | 36 | 45 | 56 | 70 |
"""
    draft = build_draft(source="meter.pdf", markdown=md, kind="ingest_draft")
    tables = draft["questions"][0]["tables"]
    assert tables
    assert any("50" in row for t in tables for row in t["rows"])
    # No invented single bore field
    assert "bore_mm" not in draft["questions"][0]


def test_q1_q2_split() -> None:
    md = "Header\n\nQ1. First question [30 Marks]\n\nQ2. Second question [30 Marks]\n"
    draft = build_draft(source="paper.pdf", markdown=md, kind="ingest_draft")
    parts = [q["part"] for q in draft["questions"]]
    assert "Q1" in parts
    assert "Q2" in parts
    assert draft["questions"][0]["marks"] == 30


def test_circuit_spec_rejects_draft_kinds() -> None:
    for kind in ("ingest_draft", "lecture_notes_draft"):
        draft = build_draft(source="x.pdf", markdown="Q1. HC1+", kind=kind)
        with pytest.raises(ValidationError):
            CircuitSpec.model_validate(draft)


def test_quarantine_short_markdown() -> None:
    assert is_quarantine("", page_count=1)
    assert is_quarantine("hi", page_count=2)
    assert not is_quarantine("Q1 Cylinder 1A+ [30 Marks]", page_count=1)
    assert not is_quarantine("x" * 100, page_count=2)


def test_docling_fixture_provenance_and_figures() -> None:
    doc = json.loads(FIXTURE.read_text())
    md = "\n".join(t["text"] for t in doc["texts"] if t.get("label") != "formula")
    draft = build_draft(
        source="fixture.pdf",
        markdown=md,
        docling_dict=doc,
        kind="lecture_notes_draft",
        page_count=2,
    )
    qtys = draft["questions"][0]["quantities"]
    assert qtys
    assert all("page" in q for q in qtys)
    assert any(q["page"] == 1 for q in qtys)
    # Table present, no atlas id on figures
    assert draft["questions"][0]["tables"]
    figs = draft["figures"]
    assert figs
    assert figs[0]["page"] == 2
    assert figs[0]["bbox"] is not None
    assert "atlas" not in json.dumps(figs).lower()
    assert "dcv_" not in json.dumps(figs)


def test_quantity_without_prov_is_unknown_page() -> None:
    draft = build_draft(
        source="x.pdf",
        markdown="Set relief at 160 bar.",
        kind="ingest_draft",
    )
    assert draft["questions"][0]["quantities"][0]["page"] == "unknown"


def test_rules_check_phrases() -> None:
    rows = rules_check("Use a 5/2 valve. Port 1 is supply. Exhaust triangles. FRL on the line.")
    statuses = {r["phrase"]: r["status"] for r in rows}
    assert statuses["5/2"] == "found"
    assert statuses["port 1"] == "found"
    assert statuses["exhaust"] == "found"
    assert statuses["FRL"] == "found"
    assert statuses["4/2"] == "missing"
    assert statuses["current path"] == "missing"


def test_rules_check_ocr_synonyms() -> None:
    noisy = "Nominature: 4 portion valve. Ports/ Positions. multiplecurrent paths"
    rows = rules_check(noisy)
    statuses = {r["phrase"]: r["status"] for r in rows}
    assert statuses["4/2"] == "found_synonym"
    assert statuses["port 1"] == "found_synonym"
    # "current path" is a substring of "current paths" / "multiplecurrent paths"
    assert statuses["current path"] in ("found", "found_synonym")
    assert statuses["5/2"] == "missing"


def test_rules_check_three_two_is_not_four_two() -> None:
    """False-positive gate: 3/2 must not count as 4/2."""
    rows = rules_check("A 3/2 valve is shown. No four-two wording.")
    statuses = {r["phrase"]: r["status"] for r in rows}
    assert statuses["4/2"] == "missing"
    assert statuses["5/2"] == "missing"


def test_rules_check_extra_text_union() -> None:
    docling = "Use a 5/2 valve and current paths."
    ocrmac = "4/2  filter Regulator → Lubricator  Open loop to atmosphere."
    rows = rules_check(docling, extra_text=ocrmac)
    statuses = {r["phrase"]: r["status"] for r in rows}
    assert statuses["5/2"] == "found"
    assert statuses["4/2"] == "found"
    assert statuses["FRL"] == "found_synonym"
    assert statuses["exhaust"] == "found_synonym"
    assert statuses["current path"] in ("found", "found_synonym")
