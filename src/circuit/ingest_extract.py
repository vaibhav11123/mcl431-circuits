"""Pure draft rules from markdown / Docling dict. No Docling import."""

from __future__ import annotations

import re
from typing import Any

QUARANTINE_CHARS_PER_PAGE = 40

_MARKS = re.compile(r"\[?\s*(\d+)\s*Marks?\s*\]?", re.I)

_ID_ACT = re.compile(r"\b(\d+A\d*|HC\d+|HM\d+)\b")
_ID_SW = re.compile(r"\b(S\d+|START|STOP|JOB)\b")
_ID_VALVE = re.compile(r"\b(RV\d+|UV|DCV\d+|PA|PB|P\d+)\b")
_SEQ_TOKEN = re.compile(r"(?<![A-Za-z0-9])((?:\d+A\d*|HC\d+|HM\d+)[+\-−])(?![A-Za-z0-9])")
_GLUED_UNIT = re.compile(
    r"(\d+(?:\.\d+)?)(RPM|bar|kg|mm|cm|kN|MPa|HP|s|%|m/min|l/min|cm³|cm3)",
    re.I,
)
_QTY = re.compile(
    r"(?P<value>\d+(?:\.\d+)?)\s*"
    r"(?P<unit>RPM|bar|kg|mm|cm|kN(?:-cm)?|MPa|HP|s|%|m/min|l/min|cm³|cm3|Marks?)\b",
    re.I,
)
_RANGE = re.compile(
    r"(?P<a>\d+(?:\.\d+)?)\s*[-–]\s*(?P<b>\d+(?:\.\d+)?)\s*"
    r"(?P<unit>RPM|bar|kg|mm|cm|kN|MPa)?",
    re.I,
)

_LOCKED_PHRASES = ("5/2", "4/2", "port 1", "exhaust", "FRL", "current path")

# Spike-proven OCR / wording variants. Exact phrase → found; synonym → found_synonym.
_PHRASE_SYNONYMS: dict[str, tuple[str, ...]] = {
    "5/2": ("5/2", "5-2"),
    "4/2": ("4/2", "4-2", "4 portion", "4 port"),
    "port 1": ("port 1", "port1", "ports/"),
    "exhaust": ("exhaust", "to atmosphere"),
    "FRL": ("frl", "filter regulator", "lubricator"),
    "current path": ("current path", "current paths", "multiplecurrent paths"),
}


def normalize_number(raw: str | int | float) -> str:
    """Decimal-normalize so 2.50 == 2.5; keep integers as integer strings."""
    s = str(raw).strip().replace(",", "")
    try:
        f = float(s)
    except ValueError:
        return s
    if f == int(f) and "." not in s and "e" not in s.lower():
        return str(int(f))
    # Strip trailing zeros from decimals without inventing magnitude.
    out = f"{f:.12g}"
    return out


def numbers_equal(a: str | int | float, b: str | int | float) -> bool:
    return normalize_number(a) == normalize_number(b)


def is_quarantine(markdown: str, page_count: int) -> bool:
    """True when the read is empty or a multi-page file is almost blank.

    A one-page exam line (e.g. a short Q1) is valid. Handwritten notes that
    yield almost nothing across many pages are quarantined.
    """
    if page_count < 1:
        return False
    text = (markdown or "").strip()
    if not text:
        return True
    if page_count == 1:
        return len(text) < 8
    return len(text) < QUARANTINE_CHARS_PER_PAGE * page_count


def _find_identifiers(text: str) -> list[str]:
    found: list[str] = []
    for rx in (_ID_ACT, _ID_SW, _ID_VALVE):
        for m in rx.finditer(text):
            tok = m.group(1)
            if tok not in found:
                found.append(tok)
    # Glued OCR pass (no word boundaries).
    for m in re.finditer(r"(?<![A-Za-z0-9])(\d+A\d*|HC\d+|HM\d+|S\d+)(?![A-Za-z0-9])", text):
        tok = m.group(1)
        if tok not in found:
            found.append(tok)
    return found


def _find_sequence_tokens(text: str) -> list[str]:
    out: list[str] = []
    for m in _SEQ_TOKEN.finditer(text):
        tok = m.group(1).replace("−", "-")
        if tok not in out:
            out.append(tok)
    return out


_PROSE_CYL_VERB = re.compile(
    r"(?i)\bcylinder\s+(?P<id>\d+A\d*|HC\d+|HM\d+)\s+"
    r"(?P<verb>holds?|releases?|retract(?:s|ed|ing)?|returns?|"
    r"extend(?:s|ed|ing)?|advanc(?:e|es|ed|ing)|forward)"
)

_VERB_SIGN = {
    "hold": "+",
    "holds": "+",
    "extend": "+",
    "extends": "+",
    "extended": "+",
    "extending": "+",
    "advance": "+",
    "advances": "+",
    "advanced": "+",
    "advancing": "+",
    "forward": "+",
    "retract": "-",
    "retracts": "-",
    "retracted": "-",
    "retracting": "-",
    "release": "-",
    "releases": "-",
    "return": "-",
    "returns": "-",
    "returned": "-",
}


def _infer_sequence_from_prose(text: str) -> list[str]:
    """Map narrative cylinder motions to compact tokens (spike-proven on 2023 Q1)."""
    out: list[str] = []
    for m in _PROSE_CYL_VERB.finditer(text or ""):
        cid = m.group("id")
        verb = m.group("verb").lower()
        window = (text or "")[m.start() : m.end() + 40].lower()
        if verb.startswith("return") and "forward" in window:
            sign = "+"
        else:
            sign = _VERB_SIGN.get(verb, "?")
        if sign == "?":
            continue
        tok = f"{cid}{sign}"
        if tok not in out:
            out.append(tok)
    return out


def _merge_sequence_tokens(text: str) -> list[str]:
    """Compact glyphs first, then prose inferences for missing motions."""
    out = _find_sequence_tokens(text)
    for tok in _infer_sequence_from_prose(text):
        if tok not in out:
            out.append(tok)
    return out


def _find_quantities(text: str, page: str | int = "unknown") -> list[dict[str, Any]]:
    qtys: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for m in _RANGE.finditer(text):
        unit = (m.group("unit") or "").strip()
        for key in ("a", "b"):
            val = normalize_number(m.group(key))
            pair = (val, unit.lower())
            if pair in seen:
                continue
            seen.add(pair)
            qtys.append(
                {
                    "value": val,
                    "unit": unit,
                    "raw": m.group(0),
                    "page": page,
                }
            )

    for m in _QTY.finditer(text):
        val = normalize_number(m.group("value"))
        unit = m.group("unit")
        pair = (val, unit.lower())
        if pair in seen:
            continue
        seen.add(pair)
        qtys.append(
            {
                "value": val,
                "unit": unit,
                "raw": m.group(0),
                "page": page,
            }
        )

    for m in _GLUED_UNIT.finditer(text):
        val = normalize_number(m.group(1))
        unit = m.group(2)
        pair = (val, unit.lower())
        if pair in seen:
            continue
        seen.add(pair)
        qtys.append(
            {
                "value": val,
                "unit": unit,
                "raw": m.group(0),
                "page": page,
            }
        )

    return qtys


def _domain_guess(text: str) -> str | None:
    low = text.lower()
    if any(w in low for w in ("plc", "ladder", "analog input")):
        return "plc"
    has_pneumatic = "pneumatic" in low or bool(re.search(r"\b\d+A\d*\b", text))
    has_hydraulic = any(w in low for w in ("relief", "pump", "hydraulic")) or bool(
        re.search(r"\bHC\d+\b", text)
    )
    has_electrical = any(w in low for w in ("relay", "solenoid", "start", "electrical"))
    if has_pneumatic and not has_hydraulic and "relief" not in low and "HC" not in text:
        return "pneumatic_plus_electrical"
    if has_hydraulic and has_electrical:
        return "hydraulic_plus_electrical"
    if has_hydraulic:
        return "hydraulic"
    return None


def _split_questions(markdown: str) -> list[tuple[str, str]]:
    """Return list of (part_label, body)."""
    text = markdown or ""
    # Find starts of Qn / PART headings.
    starts = list(re.finditer(r"(?m)^(Q\s*\d+|PART[- ]?[A-Z0-9]*)\b[^\n]*", text, re.I))
    if not starts:
        if text.strip():
            return [("body", text.strip())]
        return []
    out: list[tuple[str, str]] = []
    for i, m in enumerate(starts):
        label_raw = m.group(1).strip()
        qm = re.match(r"Q\s*(\d+)", label_raw, re.I)
        if qm:
            label = f"Q{qm.group(1)}"
        else:
            label = label_raw.upper()
        end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        body = text[m.start() : end].strip()
        out.append((label, body))
    return out


def _table_from_markdown_block(block: str, page: str | int = "unknown") -> dict[str, Any] | None:
    lines = [ln.strip() for ln in block.strip().splitlines() if ln.strip()]
    rows: list[list[str]] = []
    for ln in lines:
        if re.match(r"^\|?[\s\-:|]+\|?$", ln):
            continue
        if "|" not in ln:
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if cells:
            rows.append(cells)
    if not rows:
        return None
    return {"page": page, "rows": rows}


def _extract_markdown_tables(text: str, page: str | int = "unknown") -> list[dict[str, Any]]:
    tables: list[dict[str, Any]] = []
    # Consecutive lines containing |
    buf: list[str] = []
    for ln in text.splitlines():
        if "|" in ln:
            buf.append(ln)
        else:
            if buf:
                t = _table_from_markdown_block("\n".join(buf), page=page)
                if t:
                    tables.append(t)
                buf = []
    if buf:
        t = _table_from_markdown_block("\n".join(buf), page=page)
        if t:
            tables.append(t)
    return tables


def _page_from_prov(item: dict[str, Any]) -> str | int:
    prov = item.get("prov") or item.get("provenance") or []
    if isinstance(prov, list) and prov:
        first = prov[0]
        if isinstance(first, dict):
            page = first.get("page_no") or first.get("page")
            if page is not None:
                return page
    page = item.get("page_no") or item.get("page")
    return page if page is not None else "unknown"


def _tables_from_docling_dict(doc: dict[str, Any]) -> list[dict[str, Any]]:
    tables: list[dict[str, Any]] = []
    for i, t in enumerate(doc.get("tables") or []):
        if not isinstance(t, dict):
            continue
        page = _page_from_prov(t)
        data = t.get("data") or {}
        rows: list[list[str]] = []
        grid = data.get("grid") or data.get("table_cells")
        if isinstance(grid, list) and grid and isinstance(grid[0], list):
            for row in grid:
                cells = []
                for cell in row:
                    if isinstance(cell, dict):
                        cells.append(str(cell.get("text") or cell.get("bbox") or ""))
                    else:
                        cells.append(str(cell))
                rows.append(cells)
        elif isinstance(data.get("num_rows"), int):
            # Flat cell list with row/col indices
            n_r = int(data["num_rows"])
            n_c = int(data.get("num_cols") or 0)
            cells_list = data.get("table_cells") or []
            grid2 = [["" for _ in range(n_c)] for _ in range(n_r)]
            for cell in cells_list:
                if not isinstance(cell, dict):
                    continue
                r = int(cell.get("start_row_offset_idx") or cell.get("row") or 0)
                c = int(cell.get("start_col_offset_idx") or cell.get("col") or 0)
                if 0 <= r < n_r and 0 <= c < n_c:
                    grid2[r][c] = str(cell.get("text") or "")
            rows = grid2
        text_fallback = t.get("text") or ""
        if not rows and text_fallback:
            md_tables = _extract_markdown_tables(str(text_fallback), page=page)
            tables.extend(md_tables)
            continue
        if rows:
            tables.append({"page": page, "rows": rows, "index": i})
    return tables


def _figures_from_docling_dict(doc: dict[str, Any]) -> list[dict[str, Any]]:
    figs: list[dict[str, Any]] = []
    for i, pic in enumerate(doc.get("pictures") or []):
        if not isinstance(pic, dict):
            continue
        page = _page_from_prov(pic)
        bbox = None
        prov = pic.get("prov") or []
        if isinstance(prov, list) and prov and isinstance(prov[0], dict):
            bbox = prov[0].get("bbox")
        caption = pic.get("captions") or pic.get("caption") or ""
        if isinstance(caption, list):
            caption = " ".join(str(c) for c in caption)
        figs.append(
            {
                "page": page,
                "bbox": bbox,
                "nearest_text": str(caption)[:200],
                "index": i,
            }
        )
    return figs


def _formulas_from_docling_dict(doc: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in doc.get("texts") or []:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or "").lower()
        if "formula" not in label and item.get("label") != "formula":
            continue
        out.append(
            {
                "latex": item.get("text") or item.get("orig") or "",
                "page": _page_from_prov(item),
            }
        )
    for item in doc.get("formulas") or []:
        if isinstance(item, dict):
            out.append(
                {
                    "latex": item.get("text") or item.get("latex") or "",
                    "page": _page_from_prov(item),
                }
            )
    return out


def _quantities_with_pages_from_docling(doc: dict[str, Any]) -> list[dict[str, Any]]:
    """Prefer per-text-item provenance when Docling JSON is available."""
    qtys: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in doc.get("texts") or []:
        if not isinstance(item, dict):
            continue
        text = str(item.get("text") or "")
        page = _page_from_prov(item)
        for q in _find_quantities(text, page=page):
            pair = (q["value"], str(q["unit"]).lower())
            if pair in seen:
                continue
            seen.add(pair)
            qtys.append(q)
    for t in _tables_from_docling_dict(doc):
        page = t.get("page", "unknown")
        for row in t.get("rows") or []:
            cell_text = " ".join(str(c) for c in row)
            for q in _find_quantities(cell_text, page=page):
                pair = (q["value"], str(q["unit"]).lower())
                if pair in seen:
                    continue
                seen.add(pair)
                qtys.append(q)
    return qtys


def rules_check(markdown: str, extra_text: str = "") -> list[dict[str, str]]:
    """Score locked lecture phrases. Exact → found; synonym → found_synonym.

    ``extra_text`` is optional second-pass OCR (e.g. ocrmac on page rasters)
    unioned with Docling markdown. Loose fuzzy matching is intentionally not used.
    """
    low = f"{markdown or ''}\n{extra_text or ''}".lower()
    rows: list[dict[str, str]] = []
    for phrase in _LOCKED_PHRASES:
        alts = _PHRASE_SYNONYMS.get(phrase, (phrase,))
        status = "missing"
        for alt in alts:
            if alt.lower() not in low:
                continue
            status = "found" if alt.lower() == phrase.lower() else "found_synonym"
            if status == "found":
                break
        rows.append({"phrase": phrase, "status": status})
    return rows


def format_rules_check(rows: list[dict[str, str]]) -> str:
    lines = ["# Locked phrase check (notes drawing law)", ""]
    for r in rows:
        lines.append(f"{r['status']:13}  {r['phrase']}")
    return "\n".join(lines) + "\n"


def build_draft(
    *,
    source: str,
    markdown: str,
    docling_dict: dict[str, Any] | None = None,
    kind: str = "ingest_draft",
    page_count: int | None = None,
) -> dict[str, Any]:
    """Build draft.yaml content. kind is ingest_draft or lecture_notes_draft."""
    md = markdown or ""
    pages = page_count
    if pages is None and docling_dict is not None:
        pages = len(docling_dict.get("pages") or []) or 1
    if pages is None:
        pages = 1

    questions_out: list[dict[str, Any]] = []
    for part, body in _split_questions(md):
        marks_m = _MARKS.search(body)
        marks = int(marks_m.group(1)) if marks_m else None
        identifiers = _find_identifiers(body)
        seq = _merge_sequence_tokens(body)
        qtys = _find_quantities(body, page="unknown")
        tables = _extract_markdown_tables(body, page="unknown")
        formulas: list[dict[str, Any]] = []
        domain = _domain_guess(body)
        q: dict[str, Any] = {
            "part": part,
            "marks": marks,
            "text": body,
            "identifiers": identifiers,
            "sequence_tokens": seq,
            "quantities": qtys,
            "tables": tables,
            "formulas": formulas,
            "figure_boxes": [],
        }
        if domain:
            q["domain_guess"] = domain
        questions_out.append(q)

    figures: list[dict[str, Any]] = []
    if docling_dict:
        # Prefer Docling tables / quantities with pages.
        d_tables = _tables_from_docling_dict(docling_dict)
        d_qtys = _quantities_with_pages_from_docling(docling_dict)
        d_forms = _formulas_from_docling_dict(docling_dict)
        figures = _figures_from_docling_dict(docling_dict)
        if d_qtys:
            # Merge into questions: replace unknown-page qtys with provenanced ones.
            all_ids = _find_identifiers(md)
            all_seq = _merge_sequence_tokens(md)
            if questions_out:
                questions_out[0]["quantities"] = d_qtys
                if d_tables:
                    questions_out[0]["tables"] = d_tables
                if d_forms:
                    questions_out[0]["formulas"] = d_forms
                # Keep union of identifiers from full text.
                for tok in all_ids:
                    if tok not in questions_out[0]["identifiers"]:
                        questions_out[0]["identifiers"].append(tok)
                for tok in all_seq:
                    if tok not in questions_out[0]["sequence_tokens"]:
                        questions_out[0]["sequence_tokens"].append(tok)
            else:
                questions_out.append(
                    {
                        "part": "body",
                        "marks": None,
                        "text": md,
                        "identifiers": all_ids,
                        "sequence_tokens": all_seq,
                        "quantities": d_qtys,
                        "tables": d_tables,
                        "formulas": d_forms,
                        "figure_boxes": [],
                    }
                )
        elif d_tables and questions_out:
            questions_out[0]["tables"] = d_tables
        if figures and questions_out:
            questions_out[0]["figure_boxes"] = [
                {"page": f["page"], "bbox": f["bbox"]} for f in figures
            ]

    draft: dict[str, Any] = {
        "version": 1,
        "kind": kind,
        "source": source,
        "pages": pages,
        "questions": questions_out,
        "index_matches": [],
    }
    if kind == "lecture_notes_draft":
        draft["figures"] = figures
        draft["rules_check"] = rules_check(md)
        draft["rules_extra_text"] = ""
    return draft


def apply_rules_extra_text(
    draft: dict[str, Any], markdown: str, extra_text: str
) -> dict[str, Any]:
    """Re-score lecture rules using Docling md unioned with page OCR text."""
    if draft.get("kind") != "lecture_notes_draft":
        return draft
    draft["rules_extra_text"] = extra_text or ""
    draft["rules_check"] = rules_check(markdown or "", extra_text=extra_text or "")
    return draft


def draft_all_quantities(draft: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for q in draft.get("questions") or []:
        out.extend(q.get("quantities") or [])
    return out


def draft_all_identifiers(draft: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for q in draft.get("questions") or []:
        for tok in q.get("identifiers") or []:
            if tok not in out:
                out.append(tok)
    return out


def draft_all_table_cells(draft: dict[str, Any]) -> list[str]:
    cells: list[str] = []
    for q in draft.get("questions") or []:
        for t in q.get("tables") or []:
            for row in t.get("rows") or []:
                for c in row:
                    cells.append(str(c))
    return cells


def draft_number_pool(draft: dict[str, Any]) -> set[str]:
    """Normalized number strings from quantities and table cells."""
    pool: set[str] = set()
    for q in draft_all_quantities(draft):
        pool.add(normalize_number(q["value"]))
    for cell in draft_all_table_cells(draft):
        for m in re.finditer(r"\d+(?:\.\d+)?", cell):
            pool.add(normalize_number(m.group(0)))
    # Also scan question text for bare numbers that facts may cite.
    for q in draft.get("questions") or []:
        for m in re.finditer(r"\d+(?:\.\d+)?", str(q.get("text") or "")):
            pool.add(normalize_number(m.group(0)))
    return pool
