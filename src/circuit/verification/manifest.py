from __future__ import annotations

import hashlib
import json
from pathlib import Path

from circuit.ir.from_spec import from_spec, graph_sha256
from circuit.spec import CircuitSpec
from circuit.verification.refine import verify_spec
from circuit.verification.status import Status


def write_manifest(spec: CircuitSpec, out_dir: Path) -> dict:
    vr = verify_spec(spec)
    payload = {
        "title": spec.meta.title,
        "ok": vr.status is Status.PASS,
        "refine": vr.status.value,
        "physics": "not_evaluated",
        "cex_step": vr.cex_step,
        "stats": vr.stats,
        "sha256_spec": hashlib.sha256(spec.to_yaml().encode()).hexdigest(),
        "graph_sha256": graph_sha256(from_spec(spec)),
        "layout": {"crossings": None, "overlaps": None, "ms": None},
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "verify.json"
    path.write_text(json.dumps(payload, indent=2) + "\n")
    payload["path"] = str(path)
    return payload
