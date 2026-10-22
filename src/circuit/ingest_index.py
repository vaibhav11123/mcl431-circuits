"""Match exams/index.yaml and subset-diff locked facts. Read only."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from circuit.ingest_extract import (
    draft_all_identifiers,
    draft_number_pool,
    normalize_number,
    numbers_equal,
)

_SEQ_TOKEN = re.compile(r"^(?:\d+A\d*|HC\d+|HM\d+)[+\-]$")
_NUM = re.compile(r"-?\d+(?:\.\d+)?")

# Metadata keys that are not exam magnitudes (skip when walking facts).
_SKIP_KEYS = {
    "year",
    "date",
    "id",
    "paper",
    "source_page",
    "readable",
    "part",
    "domain",
    "identifier_style",
    "course_version",
    "sequence_note",
    "note",
    "tags",
    "channel",
    "slot",
    "resolution_bits",
    "lamps",
    "pumps",
    "marks",
    "timer_s",
    "role",
}


def load_index(root: Path) -> list[dict[str, Any]]:
    data = yaml.safe_load((root / "exams" / "index.yaml").read_text()) or {}
    return list(data.get("questions") or [])


def match(root: Path, filename: str) -> list[dict[str, Any]]:
    """Return every index row whose source basename equals filename."""
    name = Path(filename).name
    hits: list[dict[str, Any]] = []
    for row in load_index(root):
        src = row.get("source") or ""
        if Path(str(src)).name == name:
            hits.append(row)
    return hits


def _walk_numbers(obj: Any, out: list[str], *, skip_keys: bool = True) -> None:
    if obj is None or isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        out.append(normalize_number(obj))
        return
    if isinstance(obj, str):
        for m in _NUM.finditer(obj):
            out.append(normalize_number(m.group(0)))
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if skip_keys and str(k) in _SKIP_KEYS:
                continue
            _walk_numbers(v, out, skip_keys=skip_keys)
        return
    if isinstance(obj, list):
        for v in obj:
            _walk_numbers(v, out, skip_keys=skip_keys)


def _pick_question(facts: dict[str, Any], row: dict[str, Any]) -> dict[str, Any] | None:
    qs = facts.get("questions")
    if not isinstance(qs, list):
        return None
    exam_id = str(row.get("id") or "").lower()
    domain = str(row.get("domain") or "").lower()
    for q in qs:
        if not isinstance(q, dict):
            continue
        part = str(q.get("part") or "").lower().replace(" ", "")
        qdom = str(q.get("domain") or "").lower()
        if domain and domain == qdom:
            return q
        if part and part in exam_id.replace("_", ""):
            return q
        if part == "q1" and exam_id.endswith("q1"):
            return q
        if part == "q2" and exam_id.endswith("q2"):
            return q
    return None


def facts_numbers(facts: dict[str, Any], row: dict[str, Any] | None = None) -> list[str]:
    scope: Any = facts
    if row is not None:
        picked = _pick_question(facts, row)
        if picked is not None:
            scope = picked
    out: list[str] = []
    _walk_numbers(scope, out)
    seen: set[str] = set()
    uniq: list[str] = []
    for n in out:
        if n not in seen:
            seen.add(n)
            uniq.append(n)
    return uniq


def diff_row(
    root: Path,
    row: dict[str, Any],
    draft: dict[str, Any],
) -> dict[str, Any]:
    """Subset-diff one index row against a draft. Never writes facts."""
    exam_id = row.get("id") or ""
    file_rel = row.get("file") or ""
    facts_path = root / file_rel / "facts.yaml" if file_rel else None
    status = "new"
    missing_ids: list[str] = []
    missing_nums: list[str] = []

    draft_ids = set(draft_all_identifiers(draft))
    for ident in row.get("identifiers") or []:
        if str(ident) not in draft_ids:
            missing_ids.append(str(ident))

    # Sequence tokens only when they look like 1A+
    for step in row.get("sequence") or []:
        s = str(step).strip()
        if _SEQ_TOKEN.match(s):
            # Look in draft sequence_tokens
            tokens = []
            for q in draft.get("questions") or []:
                tokens.extend(q.get("sequence_tokens") or [])
            if s not in tokens:
                missing_ids.append(f"seq:{s}")

    if facts_path and facts_path.is_file():
        status = "locked"
        facts = yaml.safe_load(facts_path.read_text()) or {}
        pool = draft_number_pool(draft)
        for n in facts_numbers(facts, row):
            if n not in pool and not any(numbers_equal(n, p) for p in pool):
                missing_nums.append(n)

    ok = not missing_ids and not missing_nums
    return {
        "id": exam_id,
        "facts": str(facts_path.relative_to(root)) if facts_path and facts_path.is_file() else None,
        "status": status,
        "ok": ok,
        "missing_identifiers": missing_ids,
        "missing_numbers": missing_nums,
    }


def format_diff(results: list[dict[str, Any]]) -> str:
    if not results:
        return "no index row\n"
    lines: list[str] = []
    for r in results:
        lines.append(f"## {r['id']}  status={r['status']}  ok={r['ok']}")
        if r.get("facts"):
            lines.append(f"facts: {r['facts']}")
        if r["missing_identifiers"]:
            lines.append("missing identifiers: " + ", ".join(r["missing_identifiers"]))
        if r["missing_numbers"]:
            lines.append("missing numbers: " + ", ".join(r["missing_numbers"]))
        if r["ok"]:
            lines.append("all locked identifiers and numbers present in draft")
        lines.append("")
    return "\n".join(lines)
