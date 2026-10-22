"""Trim and split lecture crops into stampable glyphs."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

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
    _save(Image.open(CROPS / "lamp.png"), "lamp.png")
    _save(Image.open(CROPS / "dcv_4_3_spring_centered.png"), "dcv_4_3_spring_centered.png")
    _save(Image.open(CROPS / "flow_control.png"), "flow_control.png")

    coil = Image.open(CROPS / "solenoid_coil.png")
    # 480×340: box + triangle sit on the right; 1Y1 is to the left
    _save(coil.crop((305, 130, 480, 230)), "solenoid_box.png")

    timer = Image.open(CROPS / "timer_pull_in.png")
    tw, th = timer.size
    _save(timer.crop((0, 0, int(0.42 * tw), th)), "timer_pull_in.png")

    ep = Image.open(CROPS / "dcv_5_2_double_solenoid.png")
    ew, eh = ep.size
    # Barrel + port stems only. 0.38 still contains the 1A nameplate.
    cyl = ep.crop((int(0.38 * ew), int(0.28 * eh), int(0.98 * ew), int(0.54 * eh)))
    # drop leftover 1A nameplate (gap at x≈71–120) and the long L10 port stems
    cyl = cyl.crop((118, 0, 612, 156))
    _save(cyl, "cylinder_l10.png")

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

    # L10 p5 still supplies the cylinder crop; 5/2 body is generated ISO (see _make_dcv_5_2)
    ps = Image.open(CROPS / "pressure_switch.png")
    _save(ps.crop((200, 80, 500, 280)), "pressure_switch.png")
    _make_dcv_5_2()
    _make_dcv_5_3()


def _save_iso_body(im: Image.Image, name: str) -> None:
    """Keep stub geometry so catalog port fractions stay valid."""
    STAMPS.mkdir(parents=True, exist_ok=True)
    im = im.convert("RGBA")
    pix = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pix[x, y]
            if r > 210 and g > 210 and b > 210:
                pix[x, y] = (255, 255, 255, 0)
    im.save(CROPS / name)
    im.save(STAMPS / name)
    print(name, im.size)


def _arrow(draw: ImageDraw.ImageDraw, x1: float, y1: float, x2: float, y2: float, w: int = 3) -> None:
    draw.line((x1, y1, x2, y2), fill=(0, 0, 0, 255), width=w)
    ang = math.atan2(y2 - y1, x2 - x1)
    length = 11
    spread = 0.42
    p1 = (x2 - length * math.cos(ang - spread), y2 - length * math.sin(ang - spread))
    p2 = (x2 - length * math.cos(ang + spread), y2 - length * math.sin(ang + spread))
    draw.polygon([(x2, y2), p1, p2], fill=(0, 0, 0, 255))


def _tee(draw: ImageDraw.ImageDraw, x: float, y: float, inward: str, stem: int = 16, bar: int = 14) -> None:
    """ISO closed port: stem from the envelope edge, T-bar inside."""
    black = (0, 0, 0, 255)
    if inward == "down":
        draw.line((x, y, x, y + stem), fill=black, width=4)
        draw.line((x - bar, y + stem, x + bar, y + stem), fill=black, width=4)
    elif inward == "up":
        draw.line((x, y, x, y - stem), fill=black, width=4)
        draw.line((x - bar, y - stem, x + bar, y - stem), fill=black, width=4)


def _make_dcv_5_2() -> None:
    """ISO 1219-1 5/2 body, L10 p5 rest envelope.

    Commons File:Symbol_5-2_ski_selector_valve.svg (MovGP0, CC-BY-3.0).
    Shared wall; ports on the right (rest) square. Solenoids are lecture stamps.
    Left (14): 1→4, 2→3, 5 closed.  Right rest (12): 1→2, 4→5, 3 closed.
    """
    env = 140
    stub = 28
    pad = 8
    w = 2 * env
    h = pad + stub + env + stub + pad
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    y0 = pad + stub
    y1 = y0 + env
    black = (0, 0, 0, 255)
    d.rectangle((2, y0, w - 2, y1), outline=black, width=4)
    d.line((env, y0, env, y1), fill=black, width=4)

    # Left (14): 1→4 up-left, 2→3 down, 5 closed
    _arrow(d, env * 0.52, y1 - 30, env * 0.30, y0 + 24)
    _arrow(d, env * 0.72, y0 + 26, env * 0.72, y1 - 26)
    _tee(d, env * 0.22, y1, "up")

    # Right rest: 1→2 up-right, 4→5 down, 3 closed; stems on this square
    rx = env
    _arrow(d, rx + env * 0.48, y1 - 30, rx + env * 0.70, y0 + 24)
    _arrow(d, rx + env * 0.30, y0 + 26, rx + env * 0.30, y1 - 26)
    _tee(d, rx + env * 0.72, y1, "up")
    for fx in (0.32, 0.68):
        d.line((rx + env * fx, y0, rx + env * fx, pad), fill=black, width=4)
    for fx in (0.32, 0.50, 0.68):
        d.line((rx + env * fx, y1, rx + env * fx, y1 + stub), fill=black, width=4)

    _save_iso_body(im, "dcv_5_2.png")
    print("dcv_5_2 crop", im.size)


def _make_dcv_5_3() -> None:
    """ISO 1219-1 closed-centre 5/3 body (Wikimedia mid-position-closed layout).

    Commons File:Symbol_5-3_ski_selector_valve_(mid-position_closed).svg
    (MovGP0, CC-BY-3.0). Solenoids are lecture stamps, overlaid at draw time.
    """
    env = 140
    stub = 32
    pad = 10
    w = 3 * env
    h = stub + env + stub + pad * 2
    im = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    d = ImageDraw.Draw(im)
    y0 = pad + stub
    y1 = y0 + env
    black = (0, 0, 0, 255)
    for i in range(3):
        x = i * env
        d.rectangle((x + 2, y0, x + env, y1), outline=black, width=4)

    # Left (14): 1→4 diagonal up, 2→3 down, 5 closed
    _arrow(d, env * 0.38, y1 - 22, env * 0.28, y0 + 18)
    _arrow(d, env * 0.78, y0 + 18, env * 0.78, y1 - 18)
    _tee(d, env * 0.22, y1, "up")

    # Centre rest: 4, 2, 5, 1, 3 closed; stems numbered on this square
    cx0 = env
    for fx in (0.32, 0.68):
        _tee(d, cx0 + env * fx, y0, "down")
        d.line((cx0 + env * fx, y0, cx0 + env * fx, pad), fill=black, width=4)
    for fx in (0.32, 0.50, 0.68):
        _tee(d, cx0 + env * fx, y1, "up")
        d.line((cx0 + env * fx, y1, cx0 + env * fx, y1 + stub), fill=black, width=4)

    # Right (12): 1→2 up, 4→5 down, 3 closed
    rx = 2 * env
    _arrow(d, rx + env * 0.62, y1 - 22, rx + env * 0.72, y0 + 18)
    _arrow(d, rx + env * 0.22, y0 + 18, rx + env * 0.22, y1 - 18)
    _tee(d, rx + env * 0.78, y1, "up")

    crop = CROPS / "dcv_5_3.png"
    im.save(crop)
    _save(im, "dcv_5_3.png")
    print("dcv_5_3 crop", im.size)


if __name__ == "__main__":
    main()
