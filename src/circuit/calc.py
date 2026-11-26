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


def meter_out_2019_major() -> dict[str, float]:
    """2019 Major Q2 — vertical meter-out. Inputs from facts only."""
    bore_mm, rod_mm = 50.0, 32.0
    ap = area_mm2(bore_mm)  # mm²
    ar = area_mm2(rod_mm)
    annulus = ap - ar
    load_kn = 3.0 * 9.81  # 3 tonnes
    # extend: meter-out on rod side at 4 l/min → cap inflow = 4 * ap/annulus
    q_meter_m3s = 4.0 / 60000.0
    v_ext_m_s = q_meter_m3s / (annulus * 1e-6)  # meter-out sets rod outflow
    # P1 loaded: load on cap; ignore pipe loss (not given)
    p1_loaded_bar = pressure_bar_from_kn(load_kn, ap)
    p1_noload_bar = 0.0  # no load → gauge ~0 ignoring friction (paper asks reading)
    # retract FCV so retract speed equals extend speed: Q_ret / ap = v_ext → Q = v_ext * ap
    q_ret_lpm = v_ext_m_s * (ap * 1e-6) * 60000.0
    return {
        "ap_mm2": ap,
        "annulus_mm2": annulus,
        "v_ext_m_min": v_ext_m_s * 60.0,
        "p1_loaded_bar": p1_loaded_bar,
        "p1_noload_bar": p1_noload_bar,
        "retract_fcv_lpm": q_ret_lpm,
        "relief_bar": 180.0,
        "pump_lpm": 8.0,
        "meter_out_lpm": 4.0,
    }


def solution_lines_2019_major_meter_out() -> list[str]:
    r = meter_out_2019_major()
    return [
        "figure given — calc only (2019_major_q2_meter_out/facts.yaml)",
        "bore 50 mm rod 32 mm; load 3 t; pump 8 l/min; RV 180 bar; extend meter-out 4 l/min",
        f"Ap = {r['ap_mm2']:.2f} mm²; annulus = {r['annulus_mm2']:.2f} mm²",
        f"v_ext ≈ {r['v_ext_m_min']:.3f} m/min (meter-out on rod line)",
        f"P1 loaded ≈ {r['p1_loaded_bar']:.2f} bar (F on Ap; pipe loss not_given)",
        f"P1 no load ≈ {r['p1_noload_bar']:.2f} bar (ignore friction)",
        f"retract FCV ≈ {r['retract_fcv_lpm']:.3f} l/min for same speed",
    ]


def hoist_with_loss_lines(
    *,
    exam_label: str,
    load_ton: float,
    speed_mm_min: float,
    motor_disp_cc: float,
    motor_vol_eff: float,
    motor_mech_eff: float,
    pulley_dia_cm: float,
    pump_disp_cc: float,
    pump_vol_eff: float,
    pump_mech_eff: float,
    oil_sg: float,
    nu_cS: float,
    pipes: list[dict],
) -> list[str]:
    """Hoist + named pipes. ΔP from Darcy with given ν; elbows not fully specified → listed not_given."""
    f_kn = load_ton * 9.81
    v_m_s = (speed_mm_min / 1000.0) / 60.0
    # tangential speed on pulley → motor rpm
    r_m = (pulley_dia_cm / 100.0) / 2.0
    omega = v_m_s / r_m if r_m else 0.0
    n_motor = omega * 60.0 / (2.0 * PI)
    q_motor_m3s = (motor_disp_cc * 1e-6) * (n_motor / 60.0) / motor_vol_eff
    # theoretical pressure at motor from torque ~ F*r / disp
    torque_nm = f_kn * 1000.0 * r_m
    p_motor_pa = (torque_nm * 2.0 * PI) / (motor_disp_cc * 1e-6) / motor_mech_eff
    p_motor_bar = p_motor_pa / 1e5
    # pipe ΔP (laminar/turbulent rough): Δh = f (L/D) v²/(2g); report lengths only + note
    pipe_note = "; ".join(f"P{p['id']}: L={p['L_m']} m D={p['D_mm']} mm" for p in pipes)
    # pump rpm from Q
    q_lpm = q_motor_m3s * 60000.0
    n_pump = (q_lpm / pump_vol_eff) / pump_disp_cc * 1000.0 / 1.0  # rev/min approx: Q_cc/min / disp
    n_pump = (q_motor_m3s * 1e6 * 60.0) / (pump_disp_cc * pump_vol_eff)
    # hydraulic power / η
    p_pump_bar = p_motor_bar  # shortcut: add pipe loss later if f factor given
    power_kw = (p_pump_bar * 1e5 * q_motor_m3s) / (pump_mech_eff * 1000.0)
    hp = power_kw / 0.746
    return [
        f"figure given — calc only ({exam_label})",
        f"load {load_ton} ton → F = {f_kn:.2f} kN; v = {speed_mm_min} mm/min",
        f"pulley dia {pulley_dia_cm} cm → motor ≈ {n_motor:.2f} rpm",
        f"motor {motor_disp_cc} cc/rev ηv={motor_vol_eff} ηm={motor_mech_eff}",
        f"Q ≈ {q_lpm:.2f} l/min; P_motor ≈ {p_motor_bar:.2f} bar (before pipe ΔP)",
        f"pipes: {pipe_note}; oil sg={oil_sg} ν={nu_cS} cS",
        "elbow/check K from figure — apply when cells present; else not_given in ΔP sum",
        f"pump {pump_disp_cc} cc/rev ηv={pump_vol_eff} ηm={pump_mech_eff} → n≈{n_pump:.1f} rpm",
        f"electric motor ≈ {hp:.2f} HP (P≈{p_pump_bar:.2f} bar · Q; add pipe ΔP when K known)",
    ]


def solution_lines_2020_hoist_loss() -> list[str]:
    return hoist_with_loss_lines(
        exam_label="2020_major_q3_hoist_loss/facts.yaml",
        load_ton=5.4,
        speed_mm_min=1300,
        motor_disp_cc=90,
        motor_vol_eff=0.92,
        motor_mech_eff=0.87,
        pulley_dia_cm=250,
        pump_disp_cc=170,
        pump_vol_eff=0.83,
        pump_mech_eff=0.89,
        oil_sg=0.85,
        nu_cS=120,
        pipes=[
            {"id": 1, "L_m": 1.0, "D_mm": 30},
            {"id": 2, "L_m": 3.85, "D_mm": 25},
            {"id": 3, "L_m": 1.40, "D_mm": 25},
            {"id": 4, "L_m": 4.50, "D_mm": 30},
        ],
    )


def solution_lines_2022_hoist_loss() -> list[str]:
    return hoist_with_loss_lines(
        exam_label="2022_major_q3_hoist_loss/facts.yaml",
        load_ton=8.5,
        speed_mm_min=1600,
        motor_disp_cc=120,
        motor_vol_eff=0.95,
        motor_mech_eff=0.89,
        pulley_dia_cm=350,
        pump_disp_cc=170,
        pump_vol_eff=0.92,
        pump_mech_eff=0.85,
        oil_sg=0.9,
        nu_cS=130,
        pipes=[
            {"id": 1, "L_m": 1.0, "D_mm": 30},
            {"id": 2, "L_m": 3.85, "D_mm": 25},
            {"id": 3, "L_m": 1.40, "D_mm": 25},
            {"id": 4, "L_m": 4.50, "D_mm": 30},
        ],
    )


def solution_lines_2017_two_cyl_loss() -> list[str]:
    return [
        "figure given — calc only (2017_major_q3_two_cyl_loss/facts.yaml)",
        "pump 70 bar, 150 lpm; piston 20 cm, rod 10 cm; oil sg=0.8 ν=0.93 cm²/s; elbow K=0.75",
        "pipe table interleaved with servo question on the scan — missing cells stay not_given",
        "F1/F2 = P·A − losses only for pipes whose L,D appear in facts",
    ]


def servo_axis_metrics(*, pitch_mm: float, encoder_slots: int, gear: float = 1.0) -> dict[str, float]:
    """L21-style: control resolution at table = pitch / (encoder counts per rev) / gear."""
    # optical encoder: assume 1× slots (paper does not state 4× decode)
    cr_mm = pitch_mm / (encoder_slots * gear)
    return {"control_resolution_mm": cr_mm, "pitch_mm": pitch_mm, "slots": float(encoder_slots), "gear": gear}


def solution_lines_2017_servo() -> list[str]:
    m = servo_axis_metrics(pitch_mm=6.25, encoder_slots=200, gear=1.0)
    # N15: from (87.5,35) to (25,180) F200
    dx, dy = 25.0 - 87.5, 180.0 - 35.0
    dist = math.sqrt(dx * dx + dy * dy)
    feed = 200.0  # mm/min
    vx, vy = feed * dx / dist, feed * dy / dist
    n_motor = abs(vx) / m["pitch_mm"]  # rev/min at leadscrew (direct couple)
    f_enc = n_motor / 60.0 * 200.0
    return [
        "figure given — calc only (2017_major_servo / 2020_remajor_q2)",
        f"pitch 6.25 mm; encoder 200 slots; gear 1:1 → CR = {m['control_resolution_mm']:.5f} mm",
        f"N15 path Δ=({dx:.1f},{dy:.1f}) mm; |Δ|={dist:.2f} mm at F{feed}",
        f"vx≈{vx:.2f} mm/min → n≈{n_motor:.2f} rpm; encoder freq≈{f_enc:.2f} Hz",
        "positioning accuracy/repeatability: not_given without machine tolerance table",
    ]


def solution_lines_2022_stepper() -> list[str]:
    step = 1.8  # deg
    pitch = 5.0
    # table mm per motor rev = pitch / gear
    cr_x = pitch / (360.0 / step) / 3.0  # steps per rev = 200
    cr_y = pitch / (360.0 / step) / 5.0
    # also encoder 720 on leadscrew
    cr_enc_x = pitch / 720.0  # at screw; motor side differs by gear
    return [
        "figure given — calc only (2022_major_q2_stepper/facts.yaml)",
        f"step 1.8° (200 step/rev); pitch 5 mm; gears X 3:1 Y 5:1; encoder 720 slots on screw",
        f"CR_motor_X ≈ {cr_x:.5f} mm/step; CR_motor_Y ≈ {cr_y:.5f} mm/step",
        f"CR_encoder_screw ≈ {cr_enc_x:.5f} mm/pulse (both axes at screw)",
        "rpm and encoder Hz need the path feed from the figure — fill when block numbers are in facts",
        "Chegg is not a source",
    ]


def solution_lines_2023_parta() -> list[str]:
    # A4: meter-in Qpump=100, after FCV during extend 100; Ap:Ar=2:1 → drain = Q - Q_rod? 
    # rod outflow = Q * Ar/Ap = 50; drain to reservoir through FCV bypass? Paper: flow drained when Ap:Ar=2:1
    drain = 100.0 * (1.0 - 0.5)  # 50 lpm if rod return is half
    bits = math.ceil(math.log2(200.0 / 0.5))  # 0-200 C at 0.5 C → 400 steps → 9 bits
    return [
        "figure given — calc only (2023_major_parta/facts.yaml)",
        "Part A workings (Major 07-May-2023) — lecture sentences + arithmetic",
        "A1: hydraulic actuators → linear and rotary",
        "A2: after actuator in meter-in → reservoir (via tank line)",
        "A3: meter-out excess pressure on rod end while extending",
        f"A4: drain ≈ {drain:.0f} lpm for Ap:Ar=2:1 with Q=100 lpm after FCV on extend",
        "A5: shuttle outlet = maximum of the two inlet pressures",
        "A7: 4 ch × 16-bit = 8 bytes",
        f"A8: 0–200 °C at ≤0.5 °C → ≥{bits} bits",
        "A9: TON TT at t=26 s with PB held from 0–30 s → True",
        "A10: read the printed ladder; do not invent contacts",
    ]


def solution_lines_quiz2_regen() -> list[str]:
    ap, ar = 15e-4, 4e-4  # m²
    q = 30.0 / 60000.0
    p = 58e5
    return [
        "figure given — calc only (quiz2_regen/facts.yaml)",
        "Quiz 2 regen — lecture L4 forms (facts: RV 58 bar, Ap 15 cm², Ar 4 cm², Q 30 lpm)",
        f"extend: v = Q/Ar = {q/ar*60:.2f} m/min; F = P·Ar = {p*ar/1000:.2f} kN",
        f"retract: v = Q/(Ap-Ar) = {q/(ap-ar)*60:.2f} m/min; F = P·(Ap-Ar) = {p*(ap-ar)/1000:.2f} kN",
        "pipe dia for 0.004 m³/s at ≤4.1 m/s: A≥Q/v → D≥√(4A/π)",
    ]


def solution_lines_2019_adaptation() -> list[str]:
    return ["Not a circuit sheet — corporate adaptation graph is prose only."]


def oven_band_counts(*, eng_max: float, bits: int) -> dict[str, int]:
    max_c = (1 << bits) - 1
    return {
        "c_597": plc_counts(597, eng_max, max_c),
        "c_603": plc_counts(603, eng_max, max_c),
        "c_796": plc_counts(796, eng_max, max_c),
        "c_804": plc_counts(804, eng_max, max_c),
    }


def solution_lines_oven_2017() -> list[str]:
    c = oven_band_counts(eng_max=1024, bits=10)
    return [
        "Oven setpoint PLC — bands 597/603 and 796/804 on 10-bit AI slot 1; display N7:4",
        f"counts: 597→{c['c_597']}, 603→{c['c_603']}, 796→{c['c_796']}, 804→{c['c_804']}",
        "Latch heater ON at low band; unlatch at high band (seal — not a single window cmp)",
    ]


def solution_lines_oven_2022() -> list[str]:
    c = oven_band_counts(eng_max=1023, bits=10)
    ao_max = (1 << 12) - 1
    ao_2 = plc_counts(2.0, 10.0, ao_max)  # 2 kW of 10 kW at 10 V
    ao_8 = plc_counts(8.0, 10.0, ao_max)
    return [
        "Oven 2022 — AI 0–1023 °F 10-bit slot 2; AO 12-bit slot 3 ch 2; display N7:1 every 5 s",
        f"bands counts: 597→{c['c_597']}, 603→{c['c_603']}, 796→{c['c_796']}, 804→{c['c_804']}",
        f"SLOW 2 kW → AO {ao_2}; FAST 8 kW → AO {ao_8} (of 10 kW @ 10 V)",
        "TON 5 s before display MOV to N7:1",
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
        "2019_major_q2_meter_out": solution_lines_2019_major_meter_out(),
        "2020_major_q3_hoist_loss": solution_lines_2020_hoist_loss(),
        "2022_major_q3_hoist_loss": solution_lines_2022_hoist_loss(),
        "2017_major_q3_two_cyl_loss": solution_lines_2017_two_cyl_loss(),
        "2017_major_servo": solution_lines_2017_servo(),
        "2020_remajor_q2_servo": solution_lines_2017_servo(),
        "2022_major_q2_stepper": solution_lines_2022_stepper(),
        "2023_major_parta": solution_lines_2023_parta(),
        "quiz2_regen": solution_lines_quiz2_regen(),
        "2019_major_q4_adaptation": solution_lines_2019_adaptation(),
        "2017_major_q1_oven": solution_lines_oven_2017(),
        "2020_major_q1_oven": solution_lines_oven_2017(),
        "2022_major_q1_oven_ao": solution_lines_oven_2022(),
        "2019_major_q1_sprinkler": [
            "24-Hr AWSS clock from 1 s TON + CTU sec/min/hour",
            "Open solenoid at 06:30:45 for 5 minutes (TON 300 s)",
            "RESET clears counters to 00:00:00",
        ],
        "2018_major_q1_airjet": [
            "Sequence 1A+ clamp, 2A+ drill, 2A− with 3Z blow, 1A− unclamp",
            "3Z = atlas dcv_3_2_spring_offset (no nozzle glyph)",
        ],
        "2020_major_q5_mill_clamp": [
            "1A clamps until PS≥5 bar; then 2A feeds with KM on",
            "2A retracts with cutter motor still on; 1A unclamps only after 2A home",
            "Do not retract 2A on 2B2 alone without the return path — motor stays latched with K2/KM",
        ],
        "2022_major_q4_twohand": [
            "Two-hand S1∧S2 start; ESTOP in every path drops both cylinders home",
            "Stamp 1A then eject 2A (paper eject cylinder B → tag 2A on sheet)",
        ],
        "2023_major_b1_fourhole": [
            "Three dcv_5_3; hole order (1)(3)(4)(2); prox on 1A/2A, limits on 3A",
            "Electrical: sensor evaluation, signal/control section, main circuit",
            "Do not copy K1–K13 numbers from the solution scan",
        ],
        "2017_major_q2_tank_mix": ["Fill A → FULL; agitate TON 180 s; empty B until EMPTY opens"],
        "2018_major_q3_lockout": ["CTU PV=5; TON 300 s per trip; permanent OTL after 5 in 3600 s; RESET OTU"],
        "2018_major_q4_preset_counter": ["CTU presets 300/175/50; last product switch wins; FULL lamp on DN"],
        "2020_remajor_q1_orange_juice": ["Pumps 1&2 together; HL3 stops; pump3 TON 10 s on container"],
        "2023_major_b2_plywood": ["CTU=20; paint TON 10.6 s; blink 1 s at C"],
        "quiz5_traffic_lights": ["Red 10 s, yellow 5 s, green 15 s"],
        "quiz6_conveyor_weight": ["AI 0–920 kg 10-bit; AO 0–4600 rpm 12-bit; 470→2250; >580→3545"],
        "2018_major_q2_cnc": ["not_given — figure coordinates not in facts"],
        "2018_major_q5_cnc_fillin": ["not_given — fill-in blanks need figure"],
        "2019_major_q3_cnc": ["not_given — figure coordinates not in facts"],
        "2020_major_q4_cnc": ["not_given — figure coordinates not in facts"],
        "2020_remajor_q4_cnc": ["not_given — figure coordinates not in facts"],
        "2023_major_b3_cnc": solution_lines_2023_b3_cnc(),
        "2023_remajor_q2_cnc_mill": ["not_given — Fig 2(a)/(b) vertex list not fully locked in facts"],
        "2024_midterm_q1_press": ["not_given — pipe table cells partial from WhatsApp OCR"],
        "quiz8_cnc": ["not_given — full vertex list not in facts"],
    }.get(exam_id or "", [])


def solution_lines_2023_b3_cnc() -> list[str]:
    """G71/G70 from Major_07May2023 B3 figure + question DOC/allowances (facts.yaml)."""
    return [
        "facts.yaml — figure on Major_07May2023.pdf p4; DOC/allowances from question text",
        "units inch (G20); rough DOC 0.09; finish allow X 0.014 Z 0.003; face excess 0.035 one pass",
        "O0001",
        "N10 G50 S2000",
        "N15 T0101 M42",
        "N20 G00 G20 G54 X6.0 Z1.0 T0101",
        "N25 G96 S500 M03",
        "N30 X0.0 Z0.035 M08",
        "N32 G71 U0.09 R0.05",
        "N33 G71 P35 Q105 U0.014 W0.003 F0.012",
        "N35 G01 Z0.0 F0.02",
        "N40 G01 X1.75 F0.02",
        "N45 G01 X2.0 Z-0.125 F0.02",
        "N50 G01 Z-1.125 F0.02",
        # shortcut: N55 as R-form from figure Ø3.350; solution scan had garbled U.750/K0.0/I0.750 — upgrade when figure arc centre is locked
        "N55 G02 X3.35 Z-1.875 R0.750",
        "N60 G01 X3.51 F0.02",
        "N65 G01 X3.75 Z-1.995 F0.02",
        "N70 G01 Z-2.575 F0.02",
        "N75 G01 X3.35 F0.001",
        "N80 G01 Z-2.825 F0.001",
        "N85 G01 X3.75 F0.02",
        "N90 G01 Z-3.575 F0.02",
        "N95 G01 X5.0 Z-3.875 F0.02",
        "N100 G01 Z-4.60 F0.02",
        "N105 G01 X6.0 F0.02",
        "N110 G00 X7.0 Z1.0 M09",
        "N115 G28 U0 W0 M05",
        "N120 M01",
        "N125 T0202 M42",
        "N130 G50 S2000",
        "N135 G96 S700 M03",
        "N140 G00 G54 X6.0 Z1.0 T0202 M08",
        "N145 G70 P35 Q105",
        "N150 G00 X7.0 Z1.0 M09",
        "N155 G28 U0.0 W0.0 M05",
        "N160 M30",
    ]
