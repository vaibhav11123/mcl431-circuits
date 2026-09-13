"""Minimal SVG builder — black exam linework, no dependencies."""

from __future__ import annotations

from pathlib import Path


class SVG:
    def __init__(self, w: float, h: float, pad: float = 24) -> None:
        self.w = w
        self.h = h
        self.pad = pad
        self.parts: list[str] = []

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        sw: float = 1.6,
        color: str = "#000",
    ) -> None:
        self.parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" fill="none" stroke-width="{sw}"/>'
        )

    def polyline(
        self,
        pts: list[tuple[float, float]],
        sw: float = 1.6,
        color: str = "#000",
    ) -> None:
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.parts.append(
            f'<polyline points="{d}" stroke="{color}" fill="none" stroke-width="{sw}"/>'
        )

    def rect(self, x: float, y: float, w: float, h: float, sw: float = 1.6, fill: str = "#fff") -> None:
        self.parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'stroke="#000" fill="{fill}" stroke-width="{sw}"/>'
        )

    def circle(self, cx: float, cy: float, r: float, fill: str = "none") -> None:
        self.parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
            f'stroke="#000" fill="{fill}" stroke-width="1.6"/>'
        )

    def text(
        self,
        x: float,
        y: float,
        s: str,
        size: int = 13,
        anchor: str = "middle",
        color: str = "#000",
    ) -> None:
        self.parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="Helvetica, Arial, sans-serif" '
            f'font-size="{size}" text-anchor="{anchor}" fill="{color}">{s}</text>'
        )

    def triangle(self, pts: list[tuple[float, float]], fill: str = "#000") -> None:
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.parts.append(f'<polygon points="{d}" fill="{fill}" stroke="#000" stroke-width="1"/>')

    def dot(self, x: float, y: float, r: float = 3.2) -> None:
        self.circle(x, y, r, fill="#000")

    def image(
        self,
        path: Path,
        x: float,
        y: float,
        w: float,
        h: float,
        *,
        flip_x: bool = False,
    ) -> None:
        """Stamp a lecture crop PNG (copy-paste from the slide)."""
        import base64

        b64 = base64.b64encode(Path(path).read_bytes()).decode("ascii")
        href = (
            f'<image x="0" y="0" width="{w:.1f}" height="{h:.1f}" '
            f'preserveAspectRatio="xMidYMid meet" '
            f'href="data:image/png;base64,{b64}"/>'
        )
        if flip_x:
            self.parts.append(
                f'<g transform="translate({x + w:.1f},{y:.1f}) scale(-1,1)">{href}</g>'
            )
        else:
            self.parts.append(f'<g transform="translate({x:.1f},{y:.1f})">{href}</g>')

    def tostring(self) -> str:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="{-self.pad} {-self.pad} {self.w + 2 * self.pad} {self.h + 2 * self.pad}">'
            f'<rect x="{-self.pad}" y="{-self.pad}" width="{self.w + 2 * self.pad}" '
            f'height="{self.h + 2 * self.pad}" fill="#fff"/>'
            + "".join(self.parts)
            + "</svg>\n"
        )
