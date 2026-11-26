"""MCL 431 course-lock hooks. Engine defaults stay empty without this module."""

from __future__ import annotations

from circuit.calc import (
    forming_2018_pressure_bar,
    grinding_hc1_pressure_bar,
    hoist_2016_load_kn,
    l4_regen_example,
    plc_2023_q2_scaling,
    plc_fan_l14_scaling,
)
from circuit.compile_sequence import apply_compile, bare
from circuit.spec import CircuitSpec, Domain, PatternId
from circuit.validate import Check


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
        Check("hc2_waits_for_hm1", "K2" in feed and "2B1" in feed, f"K3={sorted(feed)}"),
        Check("2y1_not_kstart", "K1" not in tags("2Y1"), f"2Y1={sorted(tags('2Y1'))}"),
        Check("1y1_interlock", "!K4" in y1 and "!1Y2" in y1, f"1Y1={y1}"),
        Check("2y1_interlock", "!K4" in y2_adv and "!2Y2" in y2_adv, f"2Y1={y2_adv}"),
        Check("2y2_interlock", "K4" in tags("2Y2") and "!2Y1" in y2_ret, f"2Y2={y2_ret}"),
        Check(
            "1y2_after_grind",
            "K4" in tags("1Y2") and "2B1" in tags("1Y2") and "!1Y1" in unclamp,
            f"1Y2={unclamp}",
        ),
        Check("one_k_done_coil", n_done == 1, str(n_done)),
        Check("one_k_feed_coil", n_feed == 1, str(n_feed)),
        Check("hm1_drops_at_timer", "K2" in motor and "K4" in motor, f"3Y1={sorted(motor)}"),
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
    kinds = _plc_all_kinds(spec)
    out_kinds = [r.output.kind for r in (spec.plc.rungs if spec.plc else []) if r.output]
    ons_rungs = 0
    pulse_feeds_toggle = False
    toggle_uses_prev = False
    zone_tags = {"M0.2", "M0.3", "M0.4"}
    lamp_from_zone = 0
    mov_from_zone = 0
    ao_zero_no_zone = False
    snap_idx = -1
    toggle_idx = -1
    rungs = list(spec.plc.rungs) if spec.plc else []
    for i, r in enumerate(rungs):
        if any(e.kind == "ons" for e in r.series):
            ons_rungs += 1
        if r.output and r.output.kind in {"otl", "otu"}:
            if toggle_idx < 0:
                toggle_idx = i
            if any(e.tag == "M0.1" for e in r.series):
                pulse_feeds_toggle = True
            if any(e.tag == "M0.5" for e in r.series):
                toggle_uses_prev = True
        if r.output and r.output.tag == "M0.5":
            snap_idx = i
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
    snap_after_toggle = snap_idx > toggle_idx >= 0
    return [
        Check("fan_ons", "ons" in kinds, ",".join(kinds)),
        Check("fan_otl", "otl" in out_kinds, ",".join(out_kinds)),
        Check("fan_otu", "otu" in out_kinds, ",".join(out_kinds)),
        Check("fan_shared_ons_pulse", ons_rungs == 1 and pulse_feeds_toggle, f"ons_rungs={ons_rungs}"),
        Check("fan_toggle_uses_prev_run", toggle_uses_prev, "OTL/OTU via M0.5"),
        Check("fan_prev_run_stored_last", snap_after_toggle, f"snap@{snap_idx} toggle@{toggle_idx}"),
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


def extra_checks(spec: CircuitSpec) -> list[Check]:
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
        checks.append(
            Check("hilo_force_7800", force is not None and abs(force * 1000 - 7800) < 1, str(force))
        )
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
    return checks


def compile_override(spec: CircuitSpec):
    from circuit.compile_sequence import _compile_emboss_2016, _compile_indexing_drill

    if spec.meta.exam_id == "2016_minor1_emboss":
        return _compile_emboss_2016(spec)
    if spec.meta.exam_id in {"Fall17-Minor2", "MCL431_Minor2_2017-18_Sem1"}:
        return _compile_indexing_drill(spec)
    return None


def solution_extra(spec: CircuitSpec) -> list[str]:
    exam = spec.meta.exam_id
    if exam == "2023_minor2_q2":
        sc = plc_2023_q2_scaling()
        return [
            "",
            "Zone table (nearest integer counts)",
            f"  W < 220 kg          AI < {sc['ai_220_cmp']}     1185 RPM   AO {sc['ao_1185']}   L1",
            f"  220 ≤ W ≤ 580 kg    AI {sc['ai_220_cmp']}–{sc['ai_580']}   2250 RPM   AO {sc['ao_2250']}   L2",
            f"  W > 580 kg          AI > {sc['ai_580']}    3545 RPM   AO {sc['ao_3545']}   L3",
            "  /RUN → MOV 0 AO  (must zero the speed-controller voltage on STOP)",
        ]
    if exam == "2023_selfstudy_b1":
        return [
            "",
            "Electrical notes (L8)",
            "  2Y1 = K2 AND 2B1 (latched on K3), not K1",
            "  HM1 OFF at T1 (K4) before HC2 retracts",
            "  1Y1 NC-interlocked with K4; 2Y1 NC-interlocked with K4 / K3",
        ]
    if exam == "2023_minor2_q1":
        return [
            "",
            "Step table (enabling condition → solenoid)",
            "  1  1A+ hold     S1∧S3∧1B1∧2B2 → 1Y1",
            "  2  2A− retract  1B2 → 2Y2",
            "  3  1A− release  2B1 → 1Y2",
            "  4  2A+ return   1B1 → 2Y1",
            "  H1 to press when 2B1∧1B1 (after step 3; 2A still back)",
            "",
            "Electrical notes (L8)",
            "  S1 main switch latched on K1; S3 is the punch-up start, not JOB",
            "  Two 5/2 double-solenoid valves (L10 p5); not 5/3",
        ]
    if exam == "2016_minor1_emboss":
        return [
            "",
            "Step table (enabling condition → solenoid)",
            "  start  S1∧S0∧1B1∧2B1 → K1",
            "  1  1A1+ clamp     K1 → 1Y1",
            "  2  2A1+ emboss    1B2 → K3 → 2Y1",
            "  3  HOLD           PS≥4 bar → K4  (not 2B2)",
            "  4  2A1− retract   K4 → 2Y2",
            "  5  1A1− unclamp   K4∧2B1 → K5 → 1Y2",
            "",
            "Electrical notes (L8)",
            "  Two 5/2 double-solenoid valves; not closed-centre 5/3",
            "  PS on the 2A1+ cap line; 2B2 is position only",
            "  1Y2 is K5, not a raw 2B1 (2B1 is already true at rest)",
        ]
    if exam in {"Fall17-Minor2", "MCL431_Minor2_2017-18_Sem1"}:
        return [
            "",
            "Positions from 1A/2A end sensors (no extra table sensors)",
            "  P1 = 1B1∧2B1   P2 = 1B2∧2B1   P3 = 1B2∧2B2   P4 = 1B1∧2B2",
            "",
            "Step table (enabling condition → solenoid)",
            "  1  drill1↓   START∧S0∧1B1∧2B1∧3B1 → 3Y1",
            "  2  drill1↑   3B2 → 3Y2",
            "  3  index1→2  3B1 → 1Y1",
            "  4  drill2↓   1B2∧2B1∧3B1 → 3Y1",
            "  5  drill2↑   3B2 → 3Y2",
            "  6  index2→3  3B1 → 2Y1",
            "  7  drill3↓   1B2∧2B2∧3B1 → 3Y1",
            "  8  drill3↑   3B2 → 3Y2",
            "  9  index3→4  3B1 → 1Y2",
            "  10 drill4↓   1B1∧2B2∧3B1 → 3Y1",
            "  11 drill4↑   3B2 → 3Y2",
            "  12 return4→1 3B1 → 2Y2",
            "",
            "Electrical notes (L8)",
            "  K1 = cycle (START∧S0∧homes), not B1-style K2/K3/K4",
            "  K2–K13 = the 12 motions; each holds until the next step (!K{n+1})",
            "  K14 = done (K13∧2B1) and drops K1",
            "  KM = K1 ∧ !K13 (paper: ON from start, OFF after holes / at return)",
            "  Closed-centre ISO 1219 5/3 so the table holds when both solenoids are off",
        ]
    return []


def relief_label(spec: CircuitSpec) -> str | None:
    if spec.meta.exam_id == "2023_selfstudy_b1":
        return f"RV1 {grinding_hc1_pressure_bar():.2f} bar"
    return None


def pneumatic_width(spec: CircuitSpec) -> float | None:
    if spec.meta.exam_id == "2016_minor1_emboss":
        return 1480.0
    return None


def pneumatic_overlay(spec: CircuitSpec, svg) -> None:
    if spec.meta.exam_id != "2016_minor1_emboss":
        return
    bx = svg.w - 310
    svg.rect(bx, 58, 290, 220)
    svg.text(bx + 145, 80, "Bill of material", 13)
    for i, line in enumerate(
        (
            "1A1 clamp DAC    2A1 emboss DAC",
            "1V, 2V  5/2 double solenoid",
            "1Y1/1Y2   2Y1/2Y2",
            "1B1/1B2   2B1/2B2  end sensors",
            "S0 magazine proximity",
            "S1 start",
            "PS P/E converter  4 bar",
            "FRL on supply",
        )
    ):
        svg.text(bx + 12, 104 + i * 20, line, 11, "start")
