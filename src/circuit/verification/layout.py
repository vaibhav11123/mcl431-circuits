"""Layout metrics. Log crossings; no optimizer required."""

from __future__ import annotations

import re

_LINE = re.compile(
    r'<line x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"'
)


def _intersect(a, b) -> bool:
    def ccw(p, q, r):
        return (r[1] - p[1]) * (q[0] - p[0]) > (q[1] - p[1]) * (r[0] - p[0])

    p1, p2 = (a[0], a[1]), (a[2], a[3])
    p3, p4 = (b[0], b[1]), (b[2], b[3])
    if p1 == p3 or p1 == p4 or p2 == p3 or p2 == p4:
        return False
    return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)


def layout_metrics(svg: str) -> dict:
    segs = [tuple(map(float, m.groups())) for m in _LINE.finditer(svg)]
    crossings = 0
    for i, a in enumerate(segs):
        for b in segs[i + 1 :]:
            if _intersect(a, b):
                crossings += 1
    return {"lines": len(segs), "crossings": crossings}
