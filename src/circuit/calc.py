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
    return [
        "F = 7800 N (paper)",
        "v_approach = 15 cm/s; v_punch = 1.5 cm/s; v_return = 25 cm/s (paper)",
        "UV/RV margin = 48% (paper)",
        "line loss rapid-extend high-flow to blank = 695 kPa (paper)",
        "line loss rapid-extend rod-end to tank = 380 kPa (paper)",
        "punching line losses negligibly small (paper)",
        "bore not_given — pick from standard table",
        "Q = A·v and UV/RV set-points need bore; not invented.",
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


def solution_lines_for(exam_id: str | None) -> list[str]:
    return {
        "2023_selfstudy_b1": solution_lines_grinding(),
        "2017_minor1_hilo": solution_lines_hilo_2017(),
        "2018_minor1_hilo": solution_lines_2018_hilo(),
        "2019_minor1_meter": solution_lines_2019_meter(),
        "2016_minor1_hoist": solution_lines_2016_hoist(),
        "2023_selfstudy_b2": solution_lines_2023_b2(),
        "MCL431_minor": solution_lines_mcl431_minor(),
    }.get(exam_id or "", [])
