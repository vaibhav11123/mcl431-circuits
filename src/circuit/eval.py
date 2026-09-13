"""Eval gates: spec (always), math (exam-owned), sequence (no Y-as-contact)."""

from __future__ import annotations

import json
from pathlib import Path

from circuit.calc import grinding_hc1_pressure_bar, l4_regen_example
from circuit.compile_sequence import apply_compile
from circuit.spec import CircuitSpec, PatternId
from circuit.validate import Check, validate_spec


def _is_solenoid_tag(tag: str) -> bool:
    return "Y" in tag.upper() and any(ch.isdigit() for ch in tag)


def sequence_replay(spec: CircuitSpec) -> list[Check]:
    compiled = apply_compile(spec)
    coils = [p.coil for p in compiled.electrical.paths if p.coil]
    actuator_steps = [s for s in spec.sequence if s.action != "TIMER"]
    y_coils = [c for c in coils if c and _is_solenoid_tag(c)]
    ok = len(y_coils) >= len(actuator_steps)
    timer_ok = (
        any(c and c.startswith("T1") for c in coils)
        if any(s.action == "TIMER" for s in spec.sequence)
        else True
    )
    checks = [Check("electrical_sequence", ok and timer_ok, f"coils={coils}")]

    bad = []
    for path in compiled.electrical.paths:
        for c in path.contacts or []:
            if _is_solenoid_tag(c):
                bad.append(c)
    checks.append(
        Check(
            "no_solenoid_as_contact",
            not bad,
            ",".join(bad) if bad else "ok",
        )
    )
    return checks


def math_checks(spec: CircuitSpec) -> list[Check]:
    checks: list[Check] = []
    exam = spec.meta.exam_id
    if exam == "l4_regen" or PatternId.REGEN in spec.meta.patterns:
        regen = l4_regen_example()
        checks.append(
            Check(
                "golden_l4_regen_ratio",
                abs(regen["speed_ratio"] - 2.0) < 1e-6,
                str(regen["speed_ratio"]),
            )
        )
    if exam == "2023_selfstudy_b1":
        p = grinding_hc1_pressure_bar()
        checks.append(Check("grinding_pressure", p > 0, f"{p:.2f} bar"))
        checks.append(Check("job_sensor", "JOB" in spec.sensors, "JOB"))
        checks.append(Check("one_pump", len(spec.power.pumps) == 1, str(len(spec.power.pumps))))
        checks.append(Check("timer_30", any(s.seconds == 30 for s in spec.sequence), "30"))
    if exam == "2017_minor1_hilo":
        invented = any(c.bore_mm is not None or c.rod_mm is not None for c in spec.cylinders.values())
        checks.append(Check("hilo_bore_not_given", not invented, "bore not_given"))
        force = next((c.force_kn for c in spec.cylinders.values() if c.force_kn), None)
        checks.append(Check("hilo_force_7800", force is not None and abs(force * 1000 - 7800) < 1, str(force)))
    if exam == "2023_minor2_q1":
        n52 = sum(1 for v in spec.valves.values() if "5_2" in v.type)
        checks.append(Check("two_5_2", n52 == 2, str(n52)))
        checks.append(
            Check(
                "domain_pneumatic",
                "pneumatic" in spec.meta.domain.value,
                spec.meta.domain.value,
            )
        )
    return checks


def eval_spec(spec: CircuitSpec, root: Path, out_dir: Path | None = None) -> dict:
    checks = validate_spec(spec, root)
    checks.extend(sequence_replay(spec))
    checks.extend(math_checks(spec))
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


def golden_specs(root: Path) -> list[Path]:
    """Required goldens: B1 grinding and 2017 hi-lo."""
    required = [
        root / "examples/grinding_machine/circuit.yaml",
        root / "examples/hilo_punch_2017/circuit.yaml",
        root / "examples/strip_feed_2023/circuit.yaml",
    ]
    return [p for p in required if p.exists()]
