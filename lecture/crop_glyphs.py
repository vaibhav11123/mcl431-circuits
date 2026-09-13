"""Cut lecture glyphs from 200 dpi page rasters. Boxes are page pixels (2845×2134)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

PAGES = Path(__file__).parent / "pages"
CROPS = Path(__file__).parent / "crops"

# (page_stem, left, top, right, bottom, dest_name)
BOXES = [
    # L3 p4 — ISO 4/2 two envelopes (X | parallel). Ports A B / P T.
    ("MCL431_L3_ControlValves_p04", 980, 1180, 1860, 1780, "dcv_4_2_iso.png"),
    # L3 p6 — ISO glyphs sit left of the cutaways, not on the hardware.
    ("MCL431_L3_ControlValves_p06", 40, 500, 720, 760, "dcv_4_2_spring_offset.png"),
    ("MCL431_L3_ControlValves_p06", 40, 1160, 780, 1420, "dcv_4_3_spring_centered.png"),
    # L3 p7 — four centre-condition boxes
    ("MCL431_L3_ControlValves_p07", 140, 500, 520, 860, "dcv_4_3_closed_center.png"),
    ("MCL431_L3_ControlValves_p07", 1480, 500, 1860, 860, "dcv_4_3_float.png"),
    ("MCL431_L3_ControlValves_p07", 140, 900, 520, 1260, "dcv_4_3_open.png"),
    ("MCL431_L3_ControlValves_p07", 1480, 900, 1860, 1260, "dcv_4_3_tandem.png"),
    # L3 p17 — ISO PRV and fixed pump+tank
    ("MCL431_L3_ControlValves_p17", 1580, 360, 2280, 820, "prv.png"),
    ("MCL431_L3_ControlValves_p17", 60, 980, 520, 1680, "pump_fixed.png"),
    # L2 p20 — ISO actuators (left column; ignore hardware photos)
    ("MCL431_L2_FluidPower_p20", 560, 600, 1180, 820, "cylinder_sa.png"),
    ("MCL431_L2_FluidPower_p20", 560, 860, 1180, 1120, "cylinder_da.png"),
    ("MCL431_L2_FluidPower_p20", 160, 1200, 980, 1680, "motor_fixed.png"),
    # L8 p8 — glyph column to the right of the labels
    ("MCL431_L8_ElectropneumaticCircuitGuidelines_p08", 780, 540, 980, 760, "contact_no.png"),
    ("MCL431_L8_ElectropneumaticCircuitGuidelines_p08", 780, 780, 980, 1000, "contact_nc.png"),
    ("MCL431_L8_ElectropneumaticCircuitGuidelines_p08", 760, 1040, 1020, 1260, "contact_changeover.png"),
    ("MCL431_L8_ElectropneumaticCircuitGuidelines_p08", 760, 1480, 1000, 1760, "limit_switch.png"),
    ("MCL431_L8_ElectropneumaticCircuitGuidelines_p08", 1980, 520, 2280, 780, "pushbutton.png"),
    ("MCL431_L8_ElectropneumaticCircuitGuidelines_p08", 2140, 1480, 2680, 1860, "pressure_switch.png"),
    # L8 p9 — coil rectangle at the start of the relay row
    ("MCL431_L8_ElectropneumaticCircuitGuidelines_p09", 1680, 480, 1960, 640, "relay_coil.png"),
    # L8 p13 — full current-path template
    ("MCL431_L8_ElectropneumaticCircuitGuidelines_p13", 80, 280, 2760, 1960, "current_path_rail.png"),
    # L9 p4 — solenoid coil + SAC + 3/2
    ("MCL431_L9_ElectropneumaticRelayCircuits_p04", 1880, 1180, 2360, 1520, "solenoid_coil.png"),
    ("MCL431_L9_ElectropneumaticRelayCircuits_p04", 80, 520, 1320, 1680, "l9_p04_sac_direct.png"),
    # L9 p5 — indirect SAC + electrical
    ("MCL431_L9_ElectropneumaticRelayCircuits_p05", 80, 400, 2760, 1880, "l9_p05_indirect.png"),
    # L10 p4 / p5
    ("MCL431_L10_ElectropneumaticSequenceCircuits_p04", 1480, 420, 2720, 1780, "step_displacement_l10.png"),
    ("MCL431_L10_ElectropneumaticSequenceCircuits_p05", 200, 620, 1420, 1680, "dcv_5_2_double_solenoid.png"),
    ("MCL431_L10_ElectropneumaticSequenceCircuits_p05", 200, 420, 1420, 700, "cylinder_da_l10.png"),
]


def main() -> None:
    CROPS.mkdir(parents=True, exist_ok=True)
    for stem, l, t, r, b, dest in BOXES:
        src = PAGES / f"{stem}.png"
        im = Image.open(src)
        im.crop((l, t, r, b)).save(CROPS / dest)
        print(dest, r - l, "x", b - t)


if __name__ == "__main__":
    main()
