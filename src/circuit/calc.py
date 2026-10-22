"""L4–L6 lecture formulas. No invented inputs."""

from __future__ import annotations

import math

PI = math.pi


def area_mm2(dia_mm: float) -> float:
    return PI * (dia_mm**2) / 4.0


def annulus_mm2(bore_mm: float, rod_mm: float) -> float:
    return area_mm2(bore_mm) - area_mm2(rod_mm)


def pressure_bar_from_kn(force_kn: float, area_mm2_: float) -> float:
    # F[N] = P[bar] * A[mm^2] * 0.1  => P = F / (0.1 A)
    force_n = force_kn * 1000.0
    return force_n / (0.1 * area_mm2_)


def vext(qp_m3s: float, ap_m2: float) -> float:
    return qp_m3s / ap_m2


def vret(qp_m3s: float, ap_m2: float, ar_m2: float) -> float:
    return qp_m3s / (ap_m2 - ar_m2)


def regen_vext(qp_m3s: float, ar_m2: float) -> float:
    return qp_m3s / ar_m2


def regen_force(p_pa: float, ar_m2: float) -> float:
    return p_pa * ar_m2


def l4_regen_example() -> dict[str, float]:
    """L4 p10: 105 bar, Ap=195 cm2, Ar=65 cm2, Q=0.0016 m3/s."""
    ap = 195e-4
    ar = 65e-4
    qp = 0.0016
    p = 105e5
    return {
        "vext_regen": regen_vext(qp, ar),
        "vret": vret(qp, ap, ar),
        "f_ext_regen": regen_force(p, ar),
        "f_ret": p * (ap - ar),
        "speed_ratio": regen_vext(qp, ar) / vret(qp, ap, ar),
        "load_ratio": regen_force(p, ar) / (p * (ap - ar)),
    }


def grinding_hc1_pressure_bar(force_kn: float = 2.5, bore_mm: float = 45.0) -> float:
    return pressure_bar_from_kn(force_kn, area_mm2(bore_mm))


def solution_lines_grinding() -> list[str]:
    ap1 = area_mm2(45)
    ar1 = area_mm2(22.5)
    ap2 = area_mm2(40)
    ar2 = area_mm2(20)
    p = grinding_hc1_pressure_bar()
    return [
        "HC1 Ap = π(45)^2/4 = {:.2f} mm²".format(ap1),
        "HC1 Ar = π(22.5)^2/4 = {:.2f} mm²".format(ar1),
        "HC1 annulus = {:.2f} mm²".format(ap1 - ar1),
        "HC2 Ap = π(40)^2/4 = {:.2f} mm²".format(ap2),
        "HC2 Ar = π(20)^2/4 = {:.2f} mm²".format(ar2),
        "Clamp 2.5 kN on HC1 cap: P = F/(0.1 Ap) = {:.2f} bar".format(p),
        "HM1 400 rpm stated; pump Q not given — not invented.",
        "Timer T1 = 30 s (question).",
    ]


def solution_lines_hilo_2017() -> list[str]:
    """2017 Minor-1 Q1 — paper numbers only. Bore is not in the paper."""
    uv_kpa = 1.48 * (695.0 + 380.0)
    return [
        "F = 7800 N (paper)",
        "v_approach = 15 cm/s; v_punch = 1.5 cm/s; v_return = 25 cm/s (paper)",
        "UV/RV margin = 48% (paper)",
        "line loss rapid-extend high-flow to blank = 695 kPa (paper)",
        "line loss rapid-extend rod-end to tank = 380 kPa (paper)",
        "punching line losses negligibly small (paper)",
        "P1 = large (high-flow); P2 = small (high-pressure); one check on P1; UV unloads P1; RV on P2",
        "Punch: only P2 → Q2 = Ap·vp. Approach: P1+P2 → Q1+Q2 = Ap·va. Return still both pumps (UV resets).",
        "Q1/Q2 = va/vp − 1 = 9. Ar/Ap = 1 − va/vr = 0.40. Dr/Dp = √0.40 = 0.632.",
        "bore and rod mm not_given — paper has no table; not invented.",
        "Q1 = 0.135 Ap, Q2 = 0.015 Ap (Ap in m² → m³/s). Absolute L/min needs bore.",
        f"UV = 1.48×(695+380) = {uv_kpa:.0f} kPa = {uv_kpa/100:.2f} bar (exam sum of the two stated losses).",
        "Punch P = 7800/Ap Pa. RV = 1.48×7800/Ap — needs bore; not invented.",
    ]


def forming_2018_pressure_bar() -> float:
    return pressure_bar_from_kn(6.5, area_mm2(37.5))


def solution_lines_2018_hilo() -> list[str]:
    p = forming_2018_pressure_bar()
    return [
        "figure given — calc only (2018_minor1_hilo/facts.yaml)",
        "bore 37.5 mm rod 12.5 mm (paper)",
        "F = 6.5 kN (paper)",
        f"forming P = F/(0.1 Ap) = {p:.2f} bar",
        "P1 = 25 L/min, P2 = 5 L/min (paper)",
        "UV/RV margin = 50% (paper)",
        "pump η = 75% (paper)",
        "approach = 25 cm (paper)",
    ]


def solution_lines_2019_meter() -> list[str]:
    return [
        "figure given — calc only (2019_minor1_meter/facts.yaml)",
        "forward thrust 100 kN, reverse 10 kN (paper)",
        "Ap:Ar ≈ 2:1 (paper)",
        "retract ≈ 5 m/min on full pump flow (paper)",
        "RV margin 10%, max pump 160 bar (paper)",
        "bore not_given — pick from paper table 50/63/80/100/125 mm",
    ]


def hoist_2016_load_kn() -> float:
    return 5.4 * 9.81


def solution_lines_2016_hoist() -> list[str]:
    f = hoist_2016_load_kn()
    return [
        "figure given — calc only (2016_minor1_hoist/facts.yaml)",
        "load = 5.4 ton (paper)",
        f"F = 5.4 × 9.81 = {f:.2f} kN",
        "v_avg = 1300 mm/min (paper)",
        "motor 90 cm³/rev, ηv=92%, ηm=87% (paper)",
        "pump 170 cm³/rev, ηv=83%, ηm=89% (paper)",
        "pulley dia = 250 cm (paper)",
    ]


def solution_lines_2023_b2() -> list[str]:
    return [
        "figure given — calc only (2023_selfstudy_b2/facts.yaml)",
        "Ap = 20 cm², Ar = 6 cm² (paper)",
        "F_deform = 6 kN, packing friction = 1.3 kN (paper)",
        "P1 = 400 cm³/s, P2 = 70 cm³/s (paper)",
        "approach = 11 cm, cup R = 19 cm (paper)",
        "K tee/elbow/check/DCV and pipe lengths from facts — no invented Q",
    ]


def solution_lines_mcl431_minor() -> list[str]:
    p = pressure_bar_from_kn(2.50 + 1.50, area_mm2(50))
    return [
        "figure given — calc only (MCL431_minor/facts.yaml)",
        "HC1 50/25 mm clamp 2.50 kN + friction 1.50 kN (paper)",
        f"HC1 P = (2.50+1.50) kN / (0.1 Ap) = {p:.2f} bar",
        "HC2 40/25 mm approach 45 cm (paper)",
        "HM1 600 rpm, 5 cm³/rev, ηv=80% (paper)",
        "grind 35 s, 60 parts/h, RV margin 10% (paper)",
        "PA unloaded during grind; only PB working (paper)",
    ]


def solution_lines_fall17_minor2() -> list[str]:
    return [
        "Paper requires 5/3 DCVs on 1A, 2A, 3A. Closed-centre ISO 1219-1 5/3 (Wikimedia mid-position-closed; lecture solenoid_box).",
        "Assumed closed-centre 5/3 (holds table). No drill time given: 3A− starts at 3B2.",
        "P1=(1B1,2B1) P2=(1B2,2B1) P3=(1B2,2B2) P4=(1B1,2B2).",
        "Sequence: 3A+ 3A− 1A+ 3A+ 3A− 2A+ 3A+ 3A− 1A− 3A+ 3A− 2A−.",
        "KM latches with K1 (paper: spindle from start of sequence until all holes done), not only during 3A+.",
        "Step table: 1 drill1↓ START∧S0∧1B1∧2B1∧3B1 → 3Y1; 2 drill1↑ 3B2 → 3Y2; 3 index1→2 3B1 → 1Y1;",
        "4 drill2↓ 1B2∧2B1∧3B1 → 3Y1; 5 drill2↑ 3B2 → 3Y2; 6 index2→3 3B1 → 2Y1;",
        "7 drill3↓ 1B2∧2B2∧3B1 → 3Y1; 8 drill3↑ 3B2 → 3Y2; 9 index3→4 3B1 → 1Y2;",
        "10 drill4↓ 1B1∧2B2∧3B1 → 3Y1; 11 drill4↑ 3B2 → 3Y2; 12 return4→1 3B1 → 2Y2.",
    ]


def plc_counts(eng: float, eng_max: float, max_count: int) -> int:
    """Integer analog counts. 12-bit AI uses 4095; 10-bit AO uses 1023."""
    return int(round(eng / eng_max * max_count))


def resolve_plc_counts(scaling: object | None) -> dict[str, int]:
    """Merge explicit counts with checkpoint→count conversion from plc.scaling."""
    if scaling is None:
        return {}
    out: dict[str, int] = dict(getattr(scaling, "counts", None) or {})
    checkpoints = getattr(scaling, "checkpoints", None) or {}
    ai = getattr(scaling, "ai", None)
    ao = getattr(scaling, "ao", None)
    for name, eng in checkpoints.items():
        if name in out:
            continue
        if name.startswith("ai_") and ai is not None:
            max_c = (1 << int(ai.bits)) - 1
            out[name] = plc_counts(float(eng), float(ai.eng_max), max_c)
        elif name.startswith("ao_") and ao is not None:
            max_c = (1 << int(ao.bits)) - 1
            out[name] = plc_counts(float(eng), float(ao.eng_max), max_c)
        elif name.startswith("t_") or name.startswith("rh_"):
            # 16-bit 0–100 eng (fan T/RH)
            out[name] = plc_counts(float(eng), 100.0, 65535)
    return out


def plc_fan_ao_counts(rpm: float) -> int:
    """L14 fan AO: 100 rpm @ 1 V, 1000 rpm @ 10 V, 10-bit (0–10 V → 0–1023)."""
    voltage = 1.0 + (rpm - 100.0) / 900.0 * 9.0
    return plc_counts(voltage, 10.0, 1023)


def plc_fan_l14_scaling() -> dict[str, int]:
    """L14 fan controller analog counts (16-bit T/RH, 10-bit AO)."""
    return {
        "t_30": plc_counts(30, 100, 65535),
        "t_40": plc_counts(40, 100, 65535),
        "t_50": plc_counts(50, 100, 65535),
        "rh_40": plc_counts(40, 100, 65535),
        "rh_50": plc_counts(50, 100, 65535),
        "ao_200": plc_fan_ao_counts(200),
        "ao_500": plc_fan_ao_counts(500),
        "ao_800": plc_fan_ao_counts(800),
    }


def plc_2023_q2_scaling() -> dict[str, int]:
    """2023 Minor-2 Q2: photo values 0–4000 RPM (not the OCR 40000).

    220 kg is 948.32 counts, so W<220 is AI<949 (AI=948 is still 219.93 kg).
    """
    return {
        "ai_220": plc_counts(220, 950, 4095),
        "ai_220_cmp": 949,
        "ai_580": plc_counts(580, 950, 4095),
        "ao_1185": plc_counts(1185, 4000, 1023),
        "ao_2250": plc_counts(2250, 4000, 1023),
        "ao_3545": plc_counts(3545, 4000, 1023),
    }


def solution_lines_plc_2023() -> list[str]:
    s = plc_2023_q2_scaling()
    return [
        "facts.yaml + paper photo: 0–950 kg, 12-bit AI slot 3 ch 2; 0–10 V / 0–4000 RPM, 10-bit AO slot 2 ch 1",
        f"AI = W/950 × 4095  →  220 kg → {s['ai_220']} (W<220 ⇒ AI<{s['ai_220_cmp']}),  580 kg → {s['ai_580']}",
        f"AO = N/4000 × 1023 →  1185 RPM → {s['ao_1185']},  2250 RPM → {s['ao_2250']},  3545 RPM → {s['ao_3545']} (906.63, nearest)",
        "Zones: W<220 low (L1), 220≤W≤580 normal incl. 470 kg (L2), W>580 high (L3)",
        "STOP writes AO=0 so the speed controller does not hold the last voltage",
        "Load-cell signal type not given — 0–10 V assumed (4–20 mA would only change the AI card wiring)",
        "I/O from scan notes: START I:0.0/0, STOP I:0.0/1, L1 O:0.0/0, L2 O:0.0/1, L3 O:0.0/2",
    ]


def solution_lines_emboss_2016() -> list[str]:
    return [
        "not_given — paper asks diagrams only; no force/Q/size",
        "Sequence 1A1+ clamp, 2A1+ emboss, HOLD until PS≥4 bar, 2A1−, 1A1−.",
        "Start only if S1 ∧ S0 (magazine proximity) ∧ 1B1 ∧ 2B1 (both home).",
        "Do not retract 2A1 on 2B2 — 2B2 is position; PS is embossing pressure.",
        "P/E converter: pressure-switch mode, Pset=4 bar, RD +24 V, BU 0 V, BK signal.",
    ]


def solution_lines_strip_feed_2023() -> list[str]:
    return [
        "not_given — paper asks diagrams only; no force/Q/pressure",
        "Sequence 1A+ (hold) 2A− (retract feed) 1A− (release) 2A+ (return forward).",
        "S1 = main switch (latched). S3 = punch-tool upper, simulated by pushbutton (start).",
        "H1 optical indicator to the press when 2B1 ∧ 1B1 (2A retracted and 1A released).",
    ]


def solution_lines_plc_fan_l14() -> list[str]:
    s = plc_fan_l14_scaling()
    return [
        "L14: T/RH 0–100 on 16-bit AI Slot 2; AO Slot 1 10-bit, 100 rpm@1 V … 1000 rpm@10 V",
        f"T counts: 30→{s['t_30']}, 40→{s['t_40']}, 50→{s['t_50']}",
        f"RH counts: 40→{s['rh_40']}, 50→{s['rh_50']}",
        f"AO: 200 rpm→{s['ao_200']}, 500→{s['ao_500']}, 800→{s['ao_800']}",
        "Alternate single PB toggles RUN; three lamps for speed zones; CMP/MOV in subroutine style",
    ]


def solution_lines_for(exam_id: str | None) -> list[str]:
    return {
        "2023_selfstudy_b1": solution_lines_grinding(),
        "2017_minor1_hilo": solution_lines_hilo_2017(),
        "2018_minor1_hilo": solution_lines_2018_hilo(),
        "2019_minor1_meter": solution_lines_2019_meter(),
        "2016_minor1_hoist": solution_lines_2016_hoist(),
        "2023_selfstudy_b2": solution_lines_2023_b2(),
        "MCL431_minor": solution_lines_mcl431_minor(),
        "Fall17-Minor2": solution_lines_fall17_minor2(),
        "MCL431_Minor2_2017-18_Sem1": solution_lines_fall17_minor2(),
        "2023_minor2_q1": solution_lines_strip_feed_2023(),
        "2023_minor2_q2": solution_lines_plc_2023(),
        "2016_minor1_emboss": solution_lines_emboss_2016(),
        "plc_l14_fan_controller": solution_lines_plc_fan_l14(),
    }.get(exam_id or "", [])
