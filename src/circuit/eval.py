"""Four-gate eval: catalog, hydraulic, sequence, goldens/maths."""

from __future__ import annotations

import json
from pathlib import Path

from circuit.calc import grinding_hc1_pressure_bar, l4_regen_example
from circuit.compile_sequence import apply_compile
from circuit.spec import CircuitSpec
from circuit.validate import Check, validate_spec


def sequence_replay(spec: CircuitSpec) -> Check:
    compiled = apply_compile(spec)
    coils = [p.coil for p in compiled.electrical.paths if p.coil]
    needed = []
    for step in spec.sequence:
        if step.action.endswith("+") or step.action.endswith("-") or step.action.endswith("_ON"):
            needed.append(step.action)
        if step.action == "TIMER":
            needed.append("TIMER")
    # walk: every actuator step produced a coil
    actuator_steps = [s for s in spec.sequence if s.action != "TIMER"]
    y_coils = [c for c in coils if c and (c.startswith("1Y") or c.startswith("2Y") or c.startswith("3Y"))]
    ok = len(y_coils) >= len(actuator_steps)
    timer_ok = any(c and c.startswith("T1") for c in coils) if any(s.action == "TIMER" for s in spec.sequence) else True
    return Check("electrical_sequence", ok and timer_ok, f"coils={coils}")


def eval_spec(spec: CircuitSpec, root: Path, out_dir: Path | None = None) -> dict:
    checks = validate_spec(spec, root)
    checks.append(sequence_replay(spec))

    # maths: grinding pressure defined; L4 regen identity
    regen = l4_regen_example()
    checks.append(Check("golden_l4_regen_ratio", abs(regen["speed_ratio"] - 2.0) < 1e-6, str(regen["speed_ratio"])))
    if spec.meta.exam_id == "2023_selfstudy_b1":
        p = grinding_hc1_pressure_bar()
        checks.append(Check("grinding_pressure", p > 0, f"{p:.2f} bar"))
        checks.append(Check("job_sensor", "JOB" in spec.sensors, "JOB"))
        checks.append(Check("one_pump", len(spec.power.pumps) == 1, str(len(spec.power.pumps))))
        checks.append(Check("timer_30", any(s.seconds == 30 for s in spec.sequence), "30"))

    report = {
        "title": spec.meta.title,
        "pass": all(c.ok for c in checks),
        "checks": [{"name": c.name, "ok": c.ok, "detail": c.detail} for c in checks],
    }
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "eval.json").write_text(json.dumps(report, indent=2))
    return report


def format_report(report: dict) -> str:
    lines = ["PASS" if report["pass"] else "FAIL", report["title"]]
    for c in report["checks"]:
        flag = "PASS" if c["ok"] else "FAIL"
        lines.append(f"{flag} {c['name']}  {c['detail']}")
    return "\n".join(lines)
