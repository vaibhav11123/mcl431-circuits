from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

from circuit.ingest_promote import promote_bundle


def _write_bundle(tmp: Path, *, quarantine: bool = False, incomplete: bool = False) -> Path:
    tmp.mkdir(parents=True, exist_ok=True)
    if quarantine:
        (tmp / "quarantine.txt").write_text("empty\n")
        (tmp / "manifest.yaml").write_text("sha256: abc\n")
        return tmp
    draft = {
        "kind": "ingest_draft",
        "source": "paper.jpeg",
        "pages": 1,
        "questions": [
            {
                "part": "Q1",
                "identifiers": ["1A"],
                "sequence_tokens": ["1A+", "2A-"],
            }
        ],
        "index_matches": [],
    }
    (tmp / "draft.yaml").write_text(yaml.safe_dump(draft))
    (tmp / "manifest.yaml").write_text("sha256: deadbeef\nsource_sha256: deadbeef\n")
    if incomplete:
        (tmp / "diff.txt").write_text(
            "## 2023_q1  status=locked  ok=False\nmissing identifiers: seq:1A+\n"
        )
    else:
        (tmp / "diff.txt").write_text("## 2023_q1  status=locked  ok=True\n")
    return tmp


def test_promote_writes_proposal(tmp_path: Path) -> None:
    bundle = _write_bundle(tmp_path / "exam")
    lock = tmp_path / "facts.yaml"
    lock.write_text("locked: true\n")
    before = hashlib.sha256(lock.read_bytes()).hexdigest()

    code, msg = promote_bundle(bundle)
    assert code == 0, msg
    prop = bundle / "proposal"
    assert (prop / "checklist.txt").is_file()
    assert (prop / "draft.excerpt.yaml").is_file()
    assert "REVIEW ARTIFACT" in (prop / "checklist.txt").read_text()
    assert hashlib.sha256(lock.read_bytes()).hexdigest() == before


def test_promote_quarantine_refused(tmp_path: Path) -> None:
    bundle = _write_bundle(tmp_path / "bad", quarantine=True)
    code, msg = promote_bundle(bundle)
    assert code == 4
    assert "quarantine" in msg.lower()
    assert not (bundle / "proposal").exists()


def test_promote_incomplete_still_writes(tmp_path: Path) -> None:
    bundle = _write_bundle(tmp_path / "exam", incomplete=True)
    code, msg = promote_bundle(bundle)
    assert code == 0, msg
    text = (bundle / "proposal" / "checklist.txt").read_text()
    assert "incomplete" in text
