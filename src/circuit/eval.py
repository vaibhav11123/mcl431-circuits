"""Eval gates: spec (always), math (exam-owned), sequence (no solenoid NO as logic)."""

from __future__ import annotations

import json
from pathlib import Path

from circuit.calc import solution_lines_for
from circuit.compile_sequence import apply_compile, is_wait_step
from circuit.spec import CircuitSpec, Domain
from circuit.validate import Check, validate_spec


def _is_solenoid_tag(tag: str) -> bool:
    return "Y" in tag.upper() and any(ch.isdigit() for ch in tag)


def sequence_replay(spec: CircuitSpec) -> list[Check]:
    compiled = apply_compile(spec)
    coils = [p.coil for p in compiled.electrical.paths if p.coil]
    actuator_steps = [s for s in spec.sequence if not is_wait_step(s.action)]
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
            # NC of an opposing solenoid is interlocking. A NO Y contact used
            # as sequence logic (e.g. 3Y1 → 2Y1) is not.
            if not c.startswith("!") and _is_solenoid_tag(c):
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
    if spec.meta.domain == Domain.PLC and spec.plc is not None:
        addrs = [r.address for r in spec.plc.io]
        checks.append(Check("plc_has_io", bool(addrs), str(len(addrs))))
        checks.append(Check("plc_has_rungs", bool(spec.plc.rungs), str(len(spec.plc.rungs))))
    if spec.meta.figure_given:
        lines = "\n".join(solution_lines_for(spec.meta.exam_id))
        checks.append(Check("calc_cites_facts", "facts.yaml" in lines, spec.meta.exam_id or ""))
    return checks


def eval_spec(spec: CircuitSpec, root: Path, out_dir: Path | None = None) -> dict:
    from circuit.pack import call_hook, pack_from_root, using_pack

    pack = pack_from_root(root)

    def _run() -> dict:
        checks = validate_spec(spec, pack.root)
        if not spec.meta.figure_given and spec.meta.domain != Domain.PLC:
            checks.extend(sequence_replay(spec))
        checks.extend(math_checks(spec))
        extra = call_hook("extra_checks", spec, default=[]) or []
        checks.extend(extra)
        report = {
            "title": spec.meta.title,
            "pass": all(c.ok for c in checks),
            "checks": [{"name": c.name, "ok": c.ok, "detail": c.detail} for c in checks],
        }
        if out_dir:
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "eval.json").write_text(json.dumps(report, indent=2))
        return report

    with using_pack(pack):
        return _run()


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
        root / "examples/hilo_2018/circuit.yaml",
        root / "examples/meter_2019/circuit.yaml",
        root / "examples/hoist_2016/circuit.yaml",
        root / "examples/headloss_2023_b2/circuit.yaml",
        root / "examples/grind_given_2022/circuit.yaml",
        root / "examples/lecture_dac_spring/circuit.yaml",
        root / "examples/lecture_regen/circuit.yaml",
        root / "examples/lecture_unload/circuit.yaml",
        root / "examples/lecture_meter_in/circuit.yaml",
        root / "examples/lecture_meter_out/circuit.yaml",
        root / "examples/lecture_bleed_off/circuit.yaml",
        root / "examples/drill_2017/circuit.yaml",
        root / "examples/plc_conveyor_2023/circuit.yaml",
        root / "examples/emboss_2016/circuit.yaml",
        root / "examples/plc_l14_fan_controller/circuit.yaml",
        root / "examples/plc_l14_counter_eject/circuit.yaml",
        root / "examples/plc_l14_stamping/circuit.yaml",
        root / "examples/plc_l14_apple_packing/circuit.yaml",
    ]
    return [p for p in required if p.exists()]
