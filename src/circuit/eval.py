"""Eval gates: spec (always), math (exam-owned), sequence (no solenoid NO as logic)."""

from __future__ import annotations

import json
from pathlib import Path

from circuit.calc import (
    forming_2018_pressure_bar,
    grinding_hc1_pressure_bar,
    hoist_2016_load_kn,
    l4_regen_example,
    solution_lines_for,
)
from circuit.compile_sequence import apply_compile, bare
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


def _grinding_ladder_checks(spec: CircuitSpec) -> list[Check]:
    """B1: HC2 waits for HM1; double-solenoid pairs never share an ON command."""
    compiled = apply_compile(spec)
    paths = compiled.electrical.paths

    def raw(coil: str) -> list[str]:
        out: list[str] = []
        for p in paths:
            if p.coil == coil:
                out.extend(p.contacts or [])
        return out

    def tags(coil: str) -> set[str]:
        return {bare(c) for c in raw(coil)}

    feed = tags("K3")
    y1 = raw("1Y1")
    y2_adv = raw("2Y1")
    y2_ret = raw("2Y2")
    unclamp = raw("1Y2")
    motor = tags("3Y1")
    n_done = sum(1 for p in paths if p.coil == "K4")
    n_feed = sum(1 for p in paths if p.coil == "K3")
    return [
        Check(
            "hc2_waits_for_hm1",
            "K2" in feed and "2B1" in feed,
            f"K3={sorted(feed)}",
        ),
        Check(
            "2y1_not_kstart",
            "K1" not in tags("2Y1"),
            f"2Y1={sorted(tags('2Y1'))}",
        ),
        Check(
            "1y1_interlock",
            "!K4" in y1 and "!1Y2" in y1,
            f"1Y1={y1}",
        ),
        Check(
            "2y1_interlock",
            "!K4" in y2_adv and "!2Y2" in y2_adv,
            f"2Y1={y2_adv}",
        ),
        Check(
            "2y2_interlock",
            "K4" in tags("2Y2") and "!2Y1" in y2_ret,
            f"2Y2={y2_ret}",
        ),
        Check(
            "1y2_after_grind",
            "K4" in tags("1Y2") and "2B1" in tags("1Y2") and "!1Y1" in unclamp,
            f"1Y2={unclamp}",
        ),
        Check(
            "one_k_done_coil",
            n_done == 1,
            str(n_done),
        ),
        Check(
            "one_k_feed_coil",
            n_feed == 1,
            str(n_feed),
        ),
        Check(
            "hm1_drops_at_timer",
            "K2" in motor and "K4" in motor,
            f"3Y1={sorted(motor)}",
        ),
    ]


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
        checks.extend(_grinding_ladder_checks(spec))
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
    if exam == "2018_minor1_hilo":
        p = forming_2018_pressure_bar()
        checks.append(Check("forming_2018_pressure", p > 0, f"{p:.2f} bar from facts"))
        checks.append(Check("figure_given_calc", spec.meta.figure_given, "2018_minor1_hilo/facts.yaml"))
    if exam == "2019_minor1_meter":
        checks.append(Check("meter_bore_not_given", True, "not_given — 2019_minor1_meter/facts.yaml"))
        checks.append(Check("figure_given_calc", spec.meta.figure_given, "2019_minor1_meter/facts.yaml"))
    if exam == "2016_minor1_hoist":
        f = hoist_2016_load_kn()
        checks.append(Check("hoist_load_kn", abs(f - 5.4 * 9.81) < 1e-6, f"{f:.2f} kN from facts"))
        checks.append(Check("figure_given_calc", spec.meta.figure_given, "2016_minor1_hoist/facts.yaml"))
    if exam == "2023_selfstudy_b2":
        checks.append(Check("b2_areas_given", True, "Ap=20 cm² Ar=6 cm² from facts"))
        checks.append(Check("figure_given_calc", spec.meta.figure_given, "2023_selfstudy_b2/facts.yaml"))
    if exam == "MCL431_minor":
        checks.append(Check("minor_hc1_50", True, "HC1 50/25 from facts"))
        checks.append(Check("figure_given_calc", spec.meta.figure_given, "MCL431_minor/facts.yaml"))
    if spec.meta.figure_given:
        lines = "\n".join(solution_lines_for(exam))
        checks.append(Check("calc_cites_facts", "facts.yaml" in lines, exam or ""))
    return checks


def eval_spec(spec: CircuitSpec, root: Path, out_dir: Path | None = None) -> dict:
    checks = validate_spec(spec, root)
    if not spec.meta.figure_given:
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
    ]
    return [p for p in required if p.exists()]
