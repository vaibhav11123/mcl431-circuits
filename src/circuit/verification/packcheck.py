"""Re-check an exported pack against the graph it contains.

This module must not import the synthesizer.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from circuit.ir.graph import CircuitGraph
from circuit.semantics.env_trace import compress_changes, env_trace
from circuit.verification.refine import refine
from circuit.verification.status import Status

_MAX_ZIP_FILES = 64
_MAX_ZIP_UNCOMPRESSED = 8 * 1024 * 1024


def verify_included_graph(
    graph: CircuitGraph, expected: list[dict[str, int]]
) -> dict:
    run = env_trace(graph)
    stats = {
        "transitions": run.get("transitions"),
        "states": run.get("states"),
        "max_steps": run.get("max_steps"),
        "exhausted": run.get("exhausted"),
    }
    if run.get("conflict"):
        return {
            "ok": False,
            "status": Status.FAIL.value,
            "cex": run["conflict"],
            "stats": stats,
        }
    if run.get("exhausted"):
        return {
            "ok": False,
            "status": Status.INCONCLUSIVE.value,
            "stats": stats,
        }
    got = compress_changes(run["rows"])
    want = compress_changes(expected)
    vr = refine(want, got)
    return {
        "ok": vr.status is Status.PASS,
        "status": vr.status.value,
        "cex_step": vr.cex_step,
        "stats": stats,
    }


def _safe_members(zf: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    out = []
    total = 0
    for info in zf.infolist():
        name = info.filename.replace("\\", "/")
        if name.startswith("/") or ".." in Path(name).parts:
            raise ValueError(f"unsafe zip path {name}")
        total += info.file_size
        if total > _MAX_ZIP_UNCOMPRESSED:
            raise ValueError("zip too large")
        out.append(info)
        if len(out) > _MAX_ZIP_FILES:
            raise ValueError("too many zip members")
    return out


def write_circuit_zip(
    dest: Path,
    *,
    source_yaml: str,
    graph: CircuitGraph,
    expected: list[dict],
    verification: dict,
    sheets: dict[str, str] | None = None,
) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source.yaml": source_yaml.encode("utf-8"),
        "circuit-graph.json": graph.model_dump_json(indent=2).encode("utf-8"),
        "expected_trace.json": json.dumps(expected, indent=2).encode("utf-8"),
        "verification.json": json.dumps(verification, indent=2).encode("utf-8"),
        "asset-licenses.txt": (
            b"Public stamps: Wikimedia CC-BY dcv_5_2.png and dcv_5_3.png. "
            b"Other glyphs are vector. Not an ISO certification.\n"
        ),
    }
    for name, svg in (sheets or {}).items():
        payload[f"{name}.svg"] = svg.encode("utf-8")
    sha = {name: hashlib.sha256(blob).hexdigest() for name, blob in payload.items()}
    payload["manifest.json"] = json.dumps(
        {"sha256": sha, "physics": "not_evaluated"}, indent=2
    ).encode("utf-8")
    sha["manifest.json"] = hashlib.sha256(payload["manifest.json"]).hexdigest()
    payload["manifest.json"] = json.dumps(
        {"sha256": {k: v for k, v in sha.items() if k != "manifest.json"}, "physics": "not_evaluated"},
        indent=2,
    ).encode("utf-8")
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, blob in payload.items():
            zf.writestr(name, blob)
    return dest


def verify_zip(path: Path) -> dict:
    """Check hashes and the included graph. Does not rebuild a graph from YAML."""
    with zipfile.ZipFile(path) as zf:
        members = {i.filename: i for i in _safe_members(zf)}
        if "circuit-graph.json" not in members or "expected_trace.json" not in members:
            return {"ok": False, "status": Status.FAIL.value, "reason": "missing graph"}
        graph = CircuitGraph.model_validate_json(zf.read("circuit-graph.json"))
        expected = json.loads(zf.read("expected_trace.json").decode("utf-8"))
        result = verify_included_graph(graph, expected)
        if "manifest.json" in members:
            man = json.loads(zf.read("manifest.json").decode("utf-8"))
            for name, digest in (man.get("sha256") or {}).items():
                if name not in members:
                    result["ok"] = False
                    result["status"] = Status.FAIL.value
                    result["reason"] = f"missing {name}"
                    return result
                got = hashlib.sha256(zf.read(name)).hexdigest()
                if got != digest:
                    result["ok"] = False
                    result["status"] = Status.FAIL.value
                    result["reason"] = f"hash mismatch {name}"
                    return result
        return result
