"""SVG layout metrics. Measure crossings before any router."""

from __future__ import annotations

import re
import time

from circuit.verification.layout import layout_metrics as line_metrics

_TEXT = re.compile(
    r'<text[^>]*x="([\d.]+)"[^>]*y="([\d.]+)"[^>]*font-size="([\d.]+)"[^>]*>([^<]*)</text>'
)
_PATH = re.compile(r'<path[^>]*d="([^"]+)"')
_NUM = re.compile(r"[-+]?\d*\.?\d+")


def _overlaps(svg: str) -> int:
    boxes = []
    for m in _TEXT.finditer(svg):
        x, y, size, raw = float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4)
        w = max(len(raw), 1) * size * 0.55
        h = size * 1.2
        boxes.append((x - w / 2, y - h, x + w / 2, y))
    n = 0
    for i, a in enumerate(boxes):
        for b in boxes[i + 1 :]:
            if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
                n += 1
    return n


def _path_length(svg: str) -> float:
    total = 0.0
    for m in _PATH.finditer(svg):
        nums = [float(x) for x in _NUM.findall(m.group(1))]
        pts = list(zip(nums[0::2], nums[1::2]))
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            total += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return total


def layout_metrics(svg: str) -> dict:
    t0 = time.perf_counter()
    base = line_metrics(svg)
    out = {
        "lines": base["lines"],
        "crossings": base["crossings"],
        "overlaps": _overlaps(svg),
        "path_length": round(_path_length(svg), 1),
        "ms": round((time.perf_counter() - t0) * 1000, 3),
    }
    return out
