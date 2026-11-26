"""Fail-closed product API. CLI `--json` and MCP call these, not draw_all directly."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from circuit.pack import current_pack, pack_from_root, resolve_pack, using_pack
from circuit.spec import CircuitSpec
from circuit.validate import Check, all_ok, load_atlas_ids, validate_spec

MAX_YAML_BYTES = 256 * 1024
MAX_YAML_DEPTH = 24
MAX_CYLINDERS = 8
MAX_SEQUENCE = 32
MAX_VALVES = 16

SENTENCE_HAS_PRV = (
    "A fixed pump needs a relief valve. This sheet has nowhere for the oil to go."
)
SENTENCE_UNKNOWN = "That symbol is not in the pack."
SENTENCE_TOO_LARGE = "spec too large"
SENTENCE_CASCADE = (
    "Cascade for more than three cylinders is not in this pack. "
    "Here is the electropneumatic 5/2 equivalent."
)
SENTENCE_OK = "All executed checks passed."
SENTENCE_CT = "We do not export FluidSIM .ct files."
SENTENCE_PHYSICS = "No pressure physics. Use the sequence explorer for 0/1 actuator states."
FOOTER_SAFETY = "Logical checks only — not a machine-safety certificate."


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [text]


def sentence_for(checks: list[Check] | list[dict]) -> str:
    for c in checks:
        name = c.name if isinstance(c, Check) else c.get("name", "")
        ok = c.ok if isinstance(c, Check) else c.get("ok", True)
        detail = c.detail if isinstance(c, Check) else c.get("detail", "")
        if ok:
            continue
        if name == "has_prv":
            return SENTENCE_HAS_PRV
        if name.endswith("_in_atlas") or name == "unknown_symbol":
            return SENTENCE_UNKNOWN
        if name == "size":
            return SENTENCE_TOO_LARGE
        if name == "cascade_limit":
            return SENTENCE_CASCADE
        if detail:
            return str(detail)
        return name
    return SENTENCE_OK


def _depth(obj, n: int = 0) -> int:
    if isinstance(obj, dict):
        return max([n, *(_depth(v, n + 1) for v in obj.values())], default=n)
    if isinstance(obj, list):
        return max([n, *(_depth(v, n + 1) for v in obj)], default=n)
    return n


def _reject(sentence: str, name: str) -> dict:
    return {
        "ok": False,
        "sentence": sentence,
        "checks": [{"name": name, "ok": False, "detail": sentence}],
        "sheets": {},
        "card": "",
        "report": "",
    }


def _load_spec(text: str) -> tuple[CircuitSpec | None, dict | None]:
    raw = text.encode("utf-8")
    if len(raw) > MAX_YAML_BYTES:
        return None, _reject(SENTENCE_TOO_LARGE, "size")
    low = text.lower()
    if ".ct" in low or "fluidsim" in low:
        return None, _reject(SENTENCE_CT, "refuse_ct")
    if "simulate pressure" in low or "pressure drop" in low:
        return None, _reject(SENTENCE_PHYSICS, "refuse_physics")
    import yaml

    try:
        parsed = yaml.safe_load(text)
    except Exception as exc:
        return None, _reject(str(exc), "parse")
    if parsed is not None and _depth(parsed) > MAX_YAML_DEPTH:
        return None, _reject("spec too deep", "depth")
    tmp = tempfile.NamedTemporaryFile(suffix=".yaml", delete=False)
    path = Path(tmp.name)
    try:
        tmp.write(raw)
        tmp.close()
        spec = CircuitSpec.from_yaml(path)
    except Exception as exc:
        return None, _reject(str(exc), "parse")
    finally:
        path.unlink(missing_ok=True)
    if len(spec.cylinders) > MAX_CYLINDERS:
        return None, _reject("too many cylinders", "limits")
    if len(spec.sequence) > MAX_SEQUENCE:
        return None, _reject("sequence too long", "limits")
    if len(spec.valves) > MAX_VALVES:
        return None, _reject("too many valves", "limits")
    return spec, None


def _active_or_resolved():
    return current_pack() or resolve_pack()


def list_symbols() -> dict:
    pack = _active_or_resolved()
    with using_pack(pack):
        import yaml

        atlas = yaml.safe_load(pack.atlas_path.read_text()) or {}
        symbols = []
        for row in atlas.get("symbols") or []:
            sid = row.get("id")
            if not sid:
                continue
            symbols.append({"id": sid, "ports": list(row.get("ports") or [])})
        return {"symbols": symbols}


def validate_yaml(text: str) -> dict:
    spec, err = _load_spec(text)
    if err:
        return {"ok": False, "checks": err["checks"], "sentence": err["sentence"]}
    pack = _active_or_resolved()
    with using_pack(pack):
        checks = validate_spec(spec, pack.root)
        return {
            "ok": all_ok(checks),
            "checks": [{"name": c.name, "ok": c.ok, "detail": c.detail} for c in checks],
            "sentence": sentence_for(checks),
        }


def eval_yaml(text: str) -> dict:
    spec, err = _load_spec(text)
    if err:
        return {"ok": False, "checks": err["checks"], "sentence": err["sentence"]}
    pack = _active_or_resolved()
    with using_pack(pack):
        from circuit.eval import eval_spec

        report = eval_spec(spec, pack.root)
        checks = report["checks"]
        return {
            "ok": bool(report["pass"]),
            "checks": checks,
            "sentence": sentence_for(checks),
            "title": report["title"],
        }


def _card_svg(spec: CircuitSpec | None, sentence: str, ok: bool) -> str:
    from circuit.svgdraw import SVG

    s = SVG(720, 280)
    title = spec.meta.title if spec else "Circuit"
    s.text(360, 28, title, 16)
    y = 56
    if spec:
        for i, step in enumerate(spec.sequence[:8], 1):
            s.text(24, y, f"{i}. {step.action}  {step.label}", 12, "start")
            y += 18
    s.text(24, min(y + 18, 210), sentence, 12, "start")
    s.text(24, 252, FOOTER_SAFETY, 11, "start")
    status = "PASS" if ok else "FAIL"
    s.text(696, 28, status, 14, "end")
    return s.tostring()


def _report_svg(checks: list[dict], sentence: str, assumptions: list[str]) -> str:
    from circuit.svgdraw import SVG

    n = max(len(checks), 1)
    h = max(360, 90 + n * 18 + 80)
    s = SVG(820, h)
    s.text(410, 24, "Verification report", 16)
    y = 52
    for c in checks:
        flag = "PASS" if c.get("ok") else "FAIL"
        detail = c.get("detail") or sentence
        name = c.get("name", "")
        s.text(16, y, f"{flag} {name} — {detail}", 11, "start")
        y += 16
    y += 10
    s.text(16, y, "Assumptions", 13, "start")
    y += 18
    for a in assumptions or ["5/2 double solenoid, de-energized"]:
        s.text(16, y, a, 11, "start")
        y += 16
    y += 8
    s.text(16, y, "Not certified", 13, "start")
    y += 18
    s.text(16, y, "Physical pressure simulation not performed.", 11, "start")
    y += 20
    s.text(16, y, FOOTER_SAFETY, 11, "start")
    return s.tostring()


def _rejected_debug_svg(spec: CircuitSpec, hot: set[str] | None = None) -> str:
    try:
        from circuit.draw_electrical import draw_electrical
        from circuit.svgdraw import watermark_svg

        dbg_dir = Path(tempfile.mkdtemp(prefix="circuit-debug-"))
        dbg_path = draw_electrical(
            spec, dbg_dir / "debug.svg", highlight=hot or set()
        )
        return watermark_svg(dbg_path.read_text(encoding="utf-8"), "REJECTED")
    except Exception:
        return ""


def _assumptions(spec: CircuitSpec) -> list[str]:
    types = {v.type for v in spec.valves.values()}
    out = []
    if any("5_2" in t for t in types):
        out.append("5/2 double solenoid, de-energized")
    if any("5_3" in t for t in types):
        out.append("5/3 closed centre, de-energized")
    if not out:
        out.append("de-energized rest position")
    return out


def draw_yaml(text: str) -> dict:
    spec, err = _load_spec(text)
    if err:
        err["card"] = _card_svg(None, err["sentence"], False)
        err["report"] = _report_svg(err["checks"], err["sentence"], [])
        return err
    if (spec.meta.method or "") == "cascade" and len(spec.cylinders) > 3:
        checks = [{"name": "cascade_limit", "ok": False, "detail": SENTENCE_CASCADE}]
        sentence = SENTENCE_CASCADE
        return {
            "ok": False,
            "sentence": sentence,
            "sheets": {},
            "card": _card_svg(spec, sentence, False),
            "report": _report_svg(checks, sentence, []),
            "checks": checks,
        }
    if (spec.meta.method or "") == "cascade":
        from circuit.cascade import apply_cascade

        spec = apply_cascade(spec)
    pack = _active_or_resolved()
    with using_pack(pack):
        from circuit.compile_sequence import apply_compile
        from circuit.draw import draw_all
        from circuit.eval import eval_spec
        from circuit.ir.from_spec import from_spec
        from circuit.verification.status import Status

        spec = apply_compile(spec)
        val = validate_spec(spec, pack.root)
        ev = eval_spec(spec, pack.root)
        checks = ev["checks"]
        ok = all_ok(val) and bool(ev["pass"])
        sentence = sentence_for(val if not all_ok(val) else checks)
        skip_verify = any(s.action in {"PS", "PRESSURE"} for s in spec.sequence)
        sealed = None
        if ok and pack.hooks_module == "circuit.packs.iso_sequence" and not skip_verify:
            from circuit.verification.artifact import seal
            from circuit.verification.refine import verify_spec

            vr = verify_spec(spec)
            if vr.status is not Status.PASS:
                sentence = (
                    f"Generated control graph does not preserve the sequence at step {vr.cex_step}."
                    if vr.status is Status.FAIL
                    else f"Verification {vr.status.value}."
                )
                checks = list(checks) + [
                    {
                        "name": "refine",
                        "ok": False,
                        "detail": sentence,
                        "status": vr.status.value,
                    }
                ]
                hot: set[str] = set()
                row = vr.src_row if isinstance(vr.src_row, dict) else {}
                for key in ("plus", "minus"):
                    if row.get(key):
                        hot.add(str(row[key]))
                debug_svg = _rejected_debug_svg(spec, hot)
                return {
                    "ok": False,
                    "sentence": sentence,
                    "sheets": {},
                    "debug": debug_svg,
                    "card": _card_svg(spec, sentence, False),
                    "report": _report_svg(checks, sentence, _assumptions(spec)),
                    "checks": checks,
                    "cex": {"step": vr.cex_step, "src": vr.src_row, "tgt": vr.tgt_row},
                    "status": vr.status.value,
                    "stats": vr.stats,
                }
            sealed = seal(spec, from_spec(spec), vr)
            spec = sealed.spec
        card = _card_svg(spec, sentence, ok)
        report = _report_svg(checks, sentence, _assumptions(spec))
        result: dict[str, Any] = {
            "ok": ok,
            "sentence": sentence,
            "sheets": {},
            "card": card,
            "report": report,
            "checks": checks,
        }
        if not ok:
            if pack.hooks_module == "circuit.packs.iso_sequence" and spec.electrical.paths:
                result["debug"] = _rejected_debug_svg(
                    spec, {p.coil for p in spec.electrical.paths if p.coil}
                )
            return result
        tmpdir = Path(tempfile.mkdtemp(prefix="circuit-draw-"))
        try:
            written = draw_all(spec, tmpdir, verified=sealed)
            sheets: dict[str, str] = {}
            for key, path in written.items():
                if key.endswith("_png"):
                    continue
                if path.suffix in {".svg", ".txt"}:
                    sheets[key] = path.read_text(encoding="utf-8")
            result["sheets"] = sheets
            try:
                from circuit.export_pack import pack_files_from_draw

                result["pack_files"] = pack_files_from_draw(spec, sheets, written, sentence, report)
            except Exception:
                result["pack_files"] = {}
        finally:
            import shutil

            shutil.rmtree(tmpdir, ignore_errors=True)
        return result


def get_sheet(text: str, name: str) -> bytes:
    from circuit.png import svg_to_png
    from circuit.export_pack import preview_png

    drawn = draw_yaml(text)
    if name == "card":
        svg = drawn.get("card") or ""
    elif name == "report":
        svg = drawn.get("report") or ""
    else:
        svg = (drawn.get("sheets") or {}).get(name) or ""
    if not svg:
        return b""
    tmp = tempfile.NamedTemporaryFile(suffix=".svg", delete=False)
    path = Path(tmp.name)
    try:
        tmp.write(svg.encode("utf-8"))
        tmp.close()
        png = svg_to_png(path)
        if png is None:
            return b""
        return preview_png(png)
    finally:
        path.unlink(missing_ok=True)
        if png is not None:
            Path(png).unlink(missing_ok=True)


def dumps(payload: dict) -> str:
    return json.dumps(payload, indent=2)


def sequence_states(text: str) -> dict:
    spec, err = _load_spec(text)
    if err or spec is None:
        return {"ok": False, "steps": []}
    from circuit.semantics.spec_trace import spec_trace

    rows = spec_trace(spec)
    steps = [{"action": "rest", "label": "de-energized", "actuators": rows[0]}]
    for st, row in zip(spec.sequence, rows[1:]):
        steps.append({"action": st.action, "label": st.label, "actuators": row})
    return {"ok": True, "steps": steps}


def apply_sequence_edit(text: str, edit: dict) -> dict:
    op = (edit or {}).get("op")
    if op == "undo":
        prev = edit.get("previous_yaml")
        if not prev:
            return {"ok": False, "sentence": "nothing to undo", "yaml": text}
        drawn = draw_yaml(prev)
        drawn["yaml"] = prev
        return drawn
    spec, err = _load_spec(text)
    if err or spec is None:
        err = err or {}
        err["yaml"] = text
        return err
    if op == "insert_timer":
        after = edit.get("after_action")
        seconds = int(edit.get("seconds") or 0)
        seq = list(spec.sequence)
        inserted = False
        from circuit.spec import SeqStep

        new_seq = []
        for st in seq:
            new_seq.append(st)
            if st.action == after and not inserted:
                new_seq.append(SeqStep(action="TIMER", label="wait", seconds=seconds))
                inserted = True
        spec.sequence = new_seq
    elif op == "replace_sequence":
        from circuit.spec import SeqStep

        spec.sequence = [SeqStep.model_validate(s) for s in edit.get("sequence") or []]
    else:
        return {"ok": False, "sentence": f"unsupported edit {op!r}", "yaml": text}
    new_text = spec.to_yaml()
    drawn = draw_yaml(new_text)
    drawn["yaml"] = new_text
    return drawn


def suggest_patch(text: str) -> dict:
    spec, err = _load_spec(text)
    if err or spec is None:
        return {"check": "parse", "sentence": err["sentence"] if err else "parse", "yaml_patch": None}
    pack = _active_or_resolved()
    with using_pack(pack):
        checks = validate_spec(spec, pack.root)
    failed = [c for c in checks if not c.ok]
    if any(c.name == "has_prv" for c in failed):
        from circuit.spec import Relief

        pump = spec.power.pumps[0].id if spec.power.pumps else "P1"
        spec.power.relief_valves = list(spec.power.relief_valves) + [Relief(id="PRV", pump=pump)]
        return {
            "check": "has_prv",
            "sentence": SENTENCE_HAS_PRV,
            "yaml_patch": spec.to_yaml(),
        }
    if any(c.name.endswith("_in_atlas") for c in failed):
        return {"check": "unknown_symbol", "sentence": SENTENCE_UNKNOWN, "yaml_patch": None}
    return {
        "check": failed[0].name if failed else "ok",
        "sentence": sentence_for(checks),
        "yaml_patch": None,
    }


def explain_yaml(text: str) -> dict:
    spec, err = _load_spec(text)
    if err or spec is None:
        return {"concepts": [], "steps": [], "quiz": []}
    types = " ".join(v.type for v in spec.valves.values())
    concepts = []
    if "5_2" in types:
        concepts.append("5/2 — five ports, two positions")
    if "5_3" in types:
        concepts.append("5/3 closed centre — five ports, three positions")
    if spec.cylinders:
        concepts.append("double-acting cylinder")
    steps = [f"{s.action} {s.label}" for s in spec.sequence]
    plus = next((s.action for s in spec.sequence if s.action.endswith("+")), "1A+")
    cyl = plus[:-1]
    valve = spec.cylinders[cyl].dcv if cyl in spec.cylinders else "1V"
    sol = spec.valves[valve].solenoids[0] if valve in spec.valves and spec.valves[valve].solenoids else "1Y1"
    quiz = [
        {
            "q": "How many ports does a 5/2 valve have?",
            "choices": ["3", "4", "5", "6"],
            "answer_index": 2,
        },
        {
            "q": "Where is the rest envelope on a 5/2 in this pack?",
            "choices": ["left", "right", "centre", "top"],
            "answer_index": 1,
        },
        {
            "q": f"Which solenoid drives {plus}?",
            "choices": [sol, "START", "TANK", "PRV"],
            "answer_index": 0,
        },
    ]
    return {"concepts": concepts, "steps": steps, "quiz": quiz}
