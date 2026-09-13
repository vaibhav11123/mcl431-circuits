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
