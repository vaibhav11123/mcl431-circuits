"""SequenceBench v0: score the compiler, not an LLM."""

from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

from circuit.pack import Pack, using_pack
from circuit.service import draw_yaml


def _iso_pack() -> Pack:
    root = Path(__file__).resolve().parent / "packs" / "iso_sequence"
    return Pack(
        root=root,
        atlas_path=root / "atlas.yaml",
        stamp_dir=root / "stamps",
        hooks_module="circuit.packs.iso_sequence",
    )


def _combined_text(yaml_path: Path) -> str:
    text = yaml_path.read_text(encoding="utf-8")
    prompt = yaml_path.with_name(yaml_path.stem + ".prompt.txt")
    if prompt.is_file():
        text = prompt.read_text(encoding="utf-8") + "\n" + text
    return text


def run_bench(root: Path) -> dict:
    cases_dir = root / "cases" if (root / "cases").is_dir() else root
    yamls = sorted(cases_dir.glob("case_*.yaml"))
    accept_n = 0
    accept_fail = 0
    reject_n = 0
    reject_hit = 0
    times: list[float] = []
    rows = []
    pack = _iso_pack()
    with using_pack(pack):
        for path in yamls:
            expected = json.loads(
                path.with_name(path.stem + ".expected.json").read_text(encoding="utf-8")
            )
            want = expected["decision"]
            t0 = time.perf_counter()
            out = draw_yaml(_combined_text(path))
            dt = (time.perf_counter() - t0) * 1000
            times.append(dt)
            got = "accept" if out.get("ok") else "reject"
            if want == "accept":
                accept_n += 1
                if got != "accept":
                    accept_fail += 1
            else:
                reject_n += 1
                if got == "reject":
                    reject_hit += 1
            rows.append(
                {
                    "id": path.stem,
                    "want": want,
                    "got": got,
                    "ms": round(dt, 2),
                    "sentence": out.get("sentence"),
                }
            )
    p50 = statistics.median(times) if times else 0.0
    return {
        "n": len(yamls),
        "accepted_error_rate": (accept_fail / accept_n) if accept_n else 0.0,
        "reject_invalid_rate": (reject_hit / reject_n) if reject_n else 0.0,
        "reject_valid_rate": (accept_fail / accept_n) if accept_n else 0.0,
        "p50_ms": p50,
        "rows": rows,
    }
