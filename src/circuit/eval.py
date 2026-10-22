"""Eval gates: spec (always), math (exam-owned), sequence (no solenoid NO as logic)."""

from __future__ import annotations

import json
from pathlib import Path

from circuit.calc import (
    forming_2018_pressure_bar,
    grinding_hc1_pressure_bar,
    hoist_2016_load_kn,
    l4_regen_example,
    plc_2023_q2_scaling,
    plc_fan_l14_scaling,
    solution_lines_for,
)
from circuit.compile_sequence import apply_compile, bare, is_wait_step
from circuit.spec import CircuitSpec, Domain, PatternId
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


def _plc_all_kinds(spec: CircuitSpec) -> list[str]:
    kinds: list[str] = []
    if not spec.plc:
        return kinds
    for r in spec.plc.rungs:
        for el in list(r.series) + list(r.branch):
            kinds.append(el.kind)
        if r.output:
            kinds.append(r.output.kind)
    return kinds


def _plc_fan_toggle_checks(spec: CircuitSpec) -> list[Check]:
    """Shared ONS pulse → OTL/OTU; zone bits drive AO and lamps together."""
    kinds = _plc_all_kinds(spec)
    out_kinds = [r.output.kind for r in (spec.plc.rungs if spec.plc else []) if r.output]
    ons_rungs = 0
    pulse_feeds_toggle = False
    zone_tags = {"M0.2", "M0.3", "M0.4"}
    lamp_from_zone = 0
    mov_from_zone = 0
    ao_zero_no_zone = False
    for r in spec.plc.rungs if spec.plc else []:
        if any(e.kind == "ons" for e in r.series):
            ons_rungs += 1
        if r.output and r.output.kind in {"otl", "otu"}:
            if any(e.tag == "M0.1" for e in r.series):
                pulse_feeds_toggle = True
        if r.output and r.output.tag in {"Q0.0", "Q0.1", "Q0.2"}:
            if any(e.tag in zone_tags for e in r.series):
                lamp_from_zone += 1
        if r.output and r.output.kind == "mov" and r.output.value_from:
            if any(e.tag in zone_tags for e in r.series):
                mov_from_zone += 1
        if r.output and r.output.kind == "mov" and r.output.value == 0:
            ncs = [e for e in r.series if e.sense.upper() == "NC" and e.tag in zone_tags]
            if len(ncs) >= 3:
                ao_zero_no_zone = True
    return [
        Check("fan_ons", "ons" in kinds, ",".join(kinds)),
        Check("fan_otl", "otl" in out_kinds, ",".join(out_kinds)),
        Check("fan_otu", "otu" in out_kinds, ",".join(out_kinds)),
        Check("fan_shared_ons_pulse", ons_rungs == 1 and pulse_feeds_toggle, f"ons_rungs={ons_rungs}"),
        Check("fan_lamps_from_zones", lamp_from_zone == 3, f"lamps={lamp_from_zone}"),
        Check("fan_mov_from_zones", mov_from_zone == 3, f"movs={mov_from_zone}"),
        Check("fan_ao_zero_no_zone", ao_zero_no_zone, "MOV 0 when !Z1·!Z2·!Z3"),
    ]


def _plc_counter_checks(spec: CircuitSpec) -> list[Check]:
    kinds = _plc_all_kinds(spec)
    out_kinds = [r.output.kind for r in (spec.plc.rungs if spec.plc else []) if r.output]
    devices = {r.device for r in (spec.plc.io if spec.plc else [])}
    presets = [
        r.output.preset
        for r in (spec.plc.rungs if spec.plc else [])
        if r.output and r.output.kind == "ctu"
    ]
    # Y2 retract must not be gated by DN (else 15th cycle stuck advanced)
    y2_dn_ok = True
    for r in spec.plc.rungs if spec.plc else []:
        if r.output and (r.output.tag == "Q0.1" or "Y2" in (r.output.label or "")):
            if any("DN" in (e.tag or "") or "DN" in (e.label or "") for e in r.series):
                y2_dn_ok = False
    return [
        Check("ctu_present", "ctu" in out_kinds, ",".join(out_kinds)),
        Check("res_present", "res" in out_kinds, ",".join(out_kinds)),
        Check("ctu_preset_15", 15 in presets, str(presets)),
        Check("counter_y1", "Y1" in devices, ",".join(sorted(devices))),
        Check("counter_retract_y2", "Y2" in devices, ",".join(sorted(devices))),
        Check("counter_edge_ons", "ons" in kinds, ",".join(kinds)),
        Check("counter_y2_not_dn_gated", y2_dn_ok, "Y2 retract free of DN"),
    ]


def _plc_stamping_checks(spec: CircuitSpec) -> list[Check]:
    devices = {r.device for r in (spec.plc.io if spec.plc else [])}
    need_dev = {"START", "STOP", "LS1", "LS2", "LS3", "LSUP", "LSDN", "Power"}
    # Power lamp rung must include RUN (START latch)
    power_ok = False
    for r in spec.plc.rungs if spec.plc else []:
        if r.output and (r.output.tag == "Q0.3" or "Power" in (r.output.label or "")):
            tags = {e.tag for e in r.series}
            if "M0.0" in tags or any("RUN" in (e.label or "") for e in r.series):
                power_ok = True
    start_sets_run = False
    for r in spec.plc.rungs if spec.plc else []:
        if r.output and (r.output.tag == "M0.0" or "RUN" in (r.output.label or "")):
            tags = {e.tag for e in r.series}
            if any(t.startswith("I0.0") or "START" in (e.label or "") for e, t in ((e, e.tag) for e in r.series)):
                start_sets_run = True
            if "I0.0" in tags or any(e.tag == "I0.0" for e in r.series):
                start_sets_run = True
    conv_coils = 0
    for r in spec.plc.rungs if spec.plc else []:
        if r.output and (r.output.tag == "Q0.2" or "CONV" in (r.output.label or "")):
            conv_coils += 1
    return [
        Check("stamp_devices", need_dev <= devices, str(sorted(devices))),
        Check("stamp_start_run", start_sets_run, "START→RUN"),
        Check("stamp_power_from_run", power_ok, "Power←RUN"),
        Check("stamp_ls123", {"LS1", "LS2", "LS3"} <= devices, str(sorted(devices))),
        Check("stamp_lsup_lsdn", {"LSUP", "LSDN"} <= devices, str(sorted(devices))),
        Check("stamp_single_conv_coil", conv_coils == 1, f"CONV coils={conv_coils}"),
    ]


def _plc_apple_checks(spec: CircuitSpec) -> list[Check]:
    kinds = _plc_all_kinds(spec)
    out_kinds = [r.output.kind for r in (spec.plc.rungs if spec.plc else []) if r.output]
    ctu_p = [
        r.output.preset
        for r in (spec.plc.rungs if spec.plc else [])
        if r.output and r.output.kind == "ctu"
    ]
    ton_p = [
        r.output.preset
        for r in (spec.plc.rungs if spec.plc else [])
        if r.output and r.output.kind == "ton"
    ]
    box_conv_coils = 0
    for r in spec.plc.rungs if spec.plc else []:
        if r.output and (r.output.tag == "Q0.0" or "BOX_CONV" in (r.output.label or "")):
            box_conv_coils += 1
    return [
        Check("apple_ton", "ton" in out_kinds, ",".join(out_kinds)),
        Check("apple_ctu", "ctu" in out_kinds, ",".join(out_kinds)),
        Check("apple_count_12", 12 in ctu_p, str(ctu_p)),
        Check("apple_ton_5", 5 in ton_p, str(ton_p)),
        Check("apple_edge_ons", "ons" in kinds, ",".join(kinds)),
        Check("apple_single_box_conv", box_conv_coils == 1, f"BOX_CONV coils={box_conv_coils}"),
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
    if exam == "2016_minor1_emboss":
        n52 = sum(1 for v in spec.valves.values() if "5_2" in v.type)
        compiled = apply_compile(spec)
        y2_ret = next((p.contacts or [] for p in compiled.electrical.paths if p.coil == "2Y2"), [])
        y2_adv = next((p.contacts or [] for p in compiled.electrical.paths if p.coil == "2Y1"), [])
        k1_set = next(
            (p.contacts or [] for p in compiled.electrical.paths if p.coil == "K1" and "S1" in (p.contacts or [])),
            [],
        )
        checks.append(Check("two_5_2", n52 == 2, str(n52)))
        checks.append(
            Check(
                "domain_pneumatic",
                "pneumatic" in spec.meta.domain.value,
                spec.meta.domain.value,
            )
        )
        checks.append(Check("workpiece_s0", "S0" in spec.sensors, "S0"))
        checks.append(Check("pressure_switch_ps", "PS" in spec.sensors, "PS"))
        checks.append(
            Check(
                "hold_until_4_bar",
                any(s.action == "PS" for s in spec.sequence),
                ",".join(s.action for s in spec.sequence),
            )
        )
        checks.append(
            Check(
                "start_homes_and_s0",
                all(t in k1_set for t in ("S1", "S0", "1B1", "2B1")),
                ",".join(k1_set),
            )
        )
        checks.append(
            Check(
                "2y2_waits_for_ps_not_2b2",
                "PS" in {bare(c) for p in compiled.electrical.paths for c in (p.contacts or [])}
                and "2B2" not in y2_ret
                and "K4" in y2_ret
                and "!2Y1" in y2_ret,
                f"2Y2={y2_ret}",
            )
        )
        checks.append(
            Check(
                "2y1_not_on_2b2",
                "2B2" not in y2_adv,
                f"2Y1={y2_adv}",
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
    if exam in {"Fall17-Minor2", "MCL431_Minor2_2017-18_Sem1"}:
        n53 = sum(1 for v in spec.valves.values() if v.type == "dcv_5_3")
        checks.append(Check("three_5_3", n53 == 3, str(n53)))
        checks.append(Check("workpiece_s0", "S0" in spec.sensors, "S0"))
        checks.append(Check("twelve_motions", len(spec.sequence) == 12, str(len(spec.sequence))))
        compiled = apply_compile(spec)
        coils = [p.coil for p in compiled.electrical.paths if p.coil]
        checks.append(Check("spindle_km", "KM" in coils, ",".join(c for c in coils if c)))
    if exam == "2023_minor2_q2":
        s = plc_2023_q2_scaling()
        checks.append(Check("plc_domain", spec.meta.domain == Domain.PLC, spec.meta.domain.value))
        checks.append(Check("plc_ai_220", s["ai_220"] == 948, str(s["ai_220"])))
        checks.append(Check("plc_ai_220_cmp", s["ai_220_cmp"] == 949, str(s["ai_220_cmp"])))
        checks.append(Check("plc_ai_580", s["ai_580"] == 2500, str(s["ai_580"])))
        checks.append(Check("plc_ao_1185", s["ao_1185"] == 303, str(s["ao_1185"])))
        checks.append(Check("plc_ao_2250", s["ao_2250"] == 575, str(s["ao_2250"])))
        checks.append(Check("plc_ao_3545", s["ao_3545"] == 907, str(s["ao_3545"])))
        checks.append(
            Check(
                "plc_start_stop",
                "START" in spec.sensors and "STOP" in spec.sensors,
                ",".join(spec.sensors),
            )
        )
        checks.append(
            Check(
                "plc_three_lamps",
                all(t in spec.sensors for t in ("L1", "L2", "L3")),
                ",".join(spec.sensors),
            )
        )
    if spec.meta.domain == Domain.PLC and spec.plc is not None:
        addrs = [r.address for r in spec.plc.io]
        checks.append(Check("plc_has_io", bool(addrs), str(len(addrs))))
        checks.append(Check("plc_has_rungs", bool(spec.plc.rungs), str(len(spec.plc.rungs))))
    if exam == "plc_l14_fan_controller":
        s = plc_fan_l14_scaling()
        checks.append(Check("fan_ao_200", s["ao_200"] == 205, str(s["ao_200"])))
        checks.append(Check("fan_ao_500", s["ao_500"] == 512, str(s["ao_500"])))
        checks.append(Check("fan_ao_800", s["ao_800"] == 818, str(s["ao_800"])))
        checks.append(Check("fan_pb", "PB" in spec.sensors, ",".join(spec.sensors)))
        checks.append(
            Check(
                "fan_three_lamps",
                all(t in spec.sensors for t in ("L1", "L2", "L3")),
                ",".join(spec.sensors),
            )
        )
        checks.extend(_plc_fan_toggle_checks(spec))
    if exam == "plc_l14_counter_eject":
        checks.extend(_plc_counter_checks(spec))
    if exam == "plc_l14_stamping":
        checks.extend(_plc_stamping_checks(spec))
    if exam == "plc_l14_apple_packing":
        checks.extend(_plc_apple_checks(spec))
    if spec.meta.figure_given:
        lines = "\n".join(solution_lines_for(exam))
        checks.append(Check("calc_cites_facts", "facts.yaml" in lines, exam or ""))
    return checks


def eval_spec(spec: CircuitSpec, root: Path, out_dir: Path | None = None) -> dict:
    checks = validate_spec(spec, root)
    if not spec.meta.figure_given and spec.meta.domain != Domain.PLC:
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
        root / "examples/drill_2017/circuit.yaml",
        root / "examples/plc_conveyor_2023/circuit.yaml",
        root / "examples/emboss_2016/circuit.yaml",
        root / "examples/plc_l14_fan_controller/circuit.yaml",
        root / "examples/plc_l14_counter_eject/circuit.yaml",
        root / "examples/plc_l14_stamping/circuit.yaml",
        root / "examples/plc_l14_apple_packing/circuit.yaml",
    ]
    return [p for p in required if p.exists()]
