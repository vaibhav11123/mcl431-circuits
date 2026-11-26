"""SequenceBench-LLM: compiler vs naive-parse on fixture 'model outputs'.

No hosted LLM, no API keys, no paid credits. Fixtures in
``benchmarks/sequencebench_llm/`` stand in for typical generator mistakes.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from circuit.bench300 import decide


def naive_accept(text: str) -> bool:
    """A wrapper that treats any parseable YAML as a circuit."""
    try:
        parsed = yaml.safe_load(text)
    except Exception:
        return False
    return parsed is not None


def load_cases(root: Path) -> list[dict]:
    cases_dir = root / "cases" if (root / "cases").is_dir() else root
    out = []
    for path in sorted(cases_dir.glob("llm_*.yaml")):
        expected = json.loads(
            path.with_name(path.stem + ".expected.json").read_text(encoding="utf-8")
        )
        prompt = path.with_name(path.stem + ".prompt.txt")
        out.append(
            {
                "id": path.stem,
                "yaml": path.read_text(encoding="utf-8"),
                "prompt": prompt.read_text(encoding="utf-8") if prompt.is_file() else "",
                "decision": expected["decision"],
                "reason": expected.get("reason", ""),
            }
        )
    return out


def run_bench_llm(root: Path) -> dict:
    cases = load_cases(root)
    compiler_ok = 0
    naive_ok = 0
    invalid = 0
    compiler_caught = 0
    naive_accepted_invalid = 0
    rows = []
    for case in cases:
        want = case["decision"]
        got = decide(case["yaml"])
        naive = "accept" if naive_accept(case["yaml"]) else "reject"
        if want == "reject":
            invalid += 1
            if got == "reject":
                compiler_caught += 1
            if naive == "accept":
                naive_accepted_invalid += 1
        if got == want:
            compiler_ok += 1
        if naive == want:
            naive_ok += 1
        rows.append(
            {
                "id": case["id"],
                "want": want,
                "compiler": got,
                "naive": naive,
                "reason": case["reason"],
            }
        )
    n = len(cases) or 1
    return {
        "n": len(cases),
        "compiler_match_rate": compiler_ok / n,
        "naive_match_rate": naive_ok / n,
        "compiler_reject_invalid_rate": (compiler_caught / invalid) if invalid else 0.0,
        "naive_accept_invalid_rate": (naive_accepted_invalid / invalid) if invalid else 0.0,
        "paid_api_calls": 0,
        "rows": rows,
    }
