"""Trim and split lecture crops into stampable glyphs."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

CROPS = Path(__file__).parent / "crops"
STAMPS = CROPS / "stamps"
PAGES = Path(__file__).parent / "pages"


def _trim(im: Image.Image, pad: int = 8, thresh: int = 210) -> Image.Image:
    gray = im.convert("L")
    w, h = gray.size
    px = gray.load()
    xs, ys = [], []
    for y in range(h):
        for x in range(w):
            if px[x, y] < thresh:
                xs.append(x)
                ys.append(y)
    if not xs:
        return im
    box = (
        max(0, min(xs) - pad),
        max(0, min(ys) - pad),
        min(w, max(xs) + pad),
        min(h, max(ys) + pad),
    )
    return im.crop(box)


def _save(im: Image.Image, name: str) -> None:
    STAMPS.mkdir(parents=True, exist_ok=True)
    dest = STAMPS / name
    im = _trim(im).convert("RGBA")
    pix = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pix[x, y]
            if r > 210 and g > 210 and b > 210:
                pix[x, y] = (255, 255, 255, 0)
    im.save(dest)
    print(dest.name, dest.stat().st_size)


def _page(stem: str) -> Image.Image:
    return Image.open(PAGES / f"{stem}.png")


def main() -> None:
    STAMPS.mkdir(parents=True, exist_ok=True)

    iso = Image.open(CROPS / "dcv_4_2_iso.png")
    iso = _trim(iso, pad=4)
    w, h = iso.size
    cross = iso.crop((0, 0, w // 2 + 4, h))
    cw, ch = cross.size
    _save(cross.crop((0, int(0.18 * ch), cw, ch)), "envelope_cross.png")
    _save(iso.crop((w // 2 - 4, 0, w, h)), "envelope_parallel.png")
    closed = Image.open(CROPS / "dcv_4_3_closed_center.png")
    clw, clh = closed.size
    _save(closed.crop((0, 0, clw, int(0.62 * clh))), "envelope_closed.png")

    _save(Image.open(CROPS / "cylinder_da.png"), "cylinder_da.png")
    _save(Image.open(CROPS / "prv.png"), "prv.png")
    _save(Image.open(CROPS / "contact_no.png"), "contact_no.png")
    _save(Image.open(CROPS / "contact_nc.png"), "contact_nc.png")
    _save(Image.open(CROPS / "solenoid_coil.png"), "solenoid_coil.png")
    _save(Image.open(CROPS / "relay_coil.png"), "relay_coil.png")
    _save(Image.open(CROPS / "pushbutton.png"), "pushbutton.png")
    _save(Image.open(CROPS / "limit_switch.png"), "limit_switch.png")

    coil = Image.open(CROPS / "solenoid_coil.png")
    # 480×340: box + triangle sit on the right; 1Y1 is to the left
    _save(coil.crop((305, 130, 480, 230)), "solenoid_box.png")

    timer = Image.open(CROPS / "timer_pull_in.png")
    tw, th = timer.size
    _save(timer.crop((0, 0, int(0.42 * tw), th)), "timer_pull_in.png")

    ep = Image.open(CROPS / "dcv_5_2_double_solenoid.png")
    ew, eh = ep.size
    _save(ep.crop((int(0.38 * ew), int(0.28 * eh), int(0.98 * ew), int(0.54 * eh))), "cylinder_l10.png")

    p20 = _page("MCL431_L2_FluidPower_p20")
    _save(p20.crop((200, 1480, 860, 1860)), "motor_fixed.png")

    # L3 p17 crop is 460×700: circle ~y=80–420, Rtn tank ~y=450–540
    pump = Image.open(CROPS / "pump_fixed.png")
    _save(pump.crop((0, 40, 460, 420)), "pump_fixed.png")
    _save(pump.crop((80, 440, 380, 560)), "tank.png")

    p05 = _page("MCL431_L4_Circuits_p05")
    _save(p05.crop((1180, 1680, 1380, 1840)), "filter.png")

    p08 = _page("MCL431_L8_ElectropneumaticCircuitGuidelines_p08")
    _save(p08.crop((880, 1480, 1040, 1760)), "limit_switch.png")
    _save(p08.crop((1980, 680, 2260, 960)), "pushbutton.png")

    # L4 p11 boxed unloader (P top, T tank, dashed pilot); drop leftover check
    uv = Image.open(CROPS / "unloading_valve.png")
    _save(uv.crop((170, 50, 540, 390)), "unloading_valve.png")
    # L3 teaching crop: ISO check only (drop FreeFlow labels)
    cv = Image.open(CROPS / "check_valve.png")
    _save(cv.crop((330, 5, 580, 320)), "check_valve.png")

    # L10 p5 5/2 body only — drop baked-in 1Y1/1Y2 so paper tags can be overlaid
    ep = Image.open(CROPS / "dcv_5_2_double_solenoid.png")
    _save(ep.crop((230, 705, 900, 935)), "dcv_5_2.png")
    ps = Image.open(CROPS / "pressure_switch.png")
    _save(ps.crop((200, 80, 500, 280)), "pressure_switch.png")


if __name__ == "__main__":
    main()
