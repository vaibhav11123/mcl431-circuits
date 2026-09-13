"""CLI: validate, draw, eval, rasterize."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="circuit",
        description="MCL 431 circuit studio — lecture-locked drawings",
    )
    sub = parser.add_subparsers(dest="cmd", required=False)

    for name, help_ in (
        ("validate", "Validate a circuit.yaml spec"),
        ("draw", "Draw SVG sheets from a spec"),
        ("eval", "Run catalog / graph / sequence / golden checks"),
    ):
        p = sub.add_parser(name, help=help_)
        p.add_argument("spec", nargs="?", help="path to circuit.yaml")
        if name == "eval":
            p.add_argument("--goldens", action="store_true")

    rast = sub.add_parser("rasterize", help="Render lecture and PYQ PDFs to PNG")
    rast.add_argument("--dpi", type=int, default=200)
    rast.add_argument("--only", choices=["lecture", "exams", "all"], default="all")

    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 0

    if args.cmd == "rasterize":
        from circuit.rasterize import rasterize_all

        return rasterize_all(ROOT, dpi=args.dpi, only=args.only)

    spec_path = Path(args.spec) if getattr(args, "spec", None) else (
        ROOT / "examples/grinding_machine/circuit.yaml"
    )
    from circuit.spec import CircuitSpec

    spec = CircuitSpec.from_yaml(spec_path)
    out_dir = ROOT / "output"

    if args.cmd == "validate":
        from circuit.validate import all_ok, validate_spec

        checks = validate_spec(spec, ROOT)
        for c in checks:
            print(f"{'PASS' if c.ok else 'FAIL'} {c.name}  {c.detail}")
        return 0 if all_ok(checks) else 1

    if args.cmd == "draw":
        from circuit.draw import draw_all

        written = draw_all(spec, out_dir)
        for k, p in written.items():
            print(f"{k}: {p}")
        return 0

    if args.cmd == "eval":
        from circuit.eval import eval_spec, format_report

        if getattr(args, "goldens", False):
            specs = [
                ROOT / "examples/grinding_machine/circuit.yaml",
                ROOT / "examples/hilo_punch_2017/circuit.yaml",
            ]
            ok = True
            for path in specs:
                if not path.exists():
                    print(f"SKIP missing {path}")
                    continue
                s = CircuitSpec.from_yaml(path)
                report = eval_spec(s, ROOT, out_dir)
                print(format_report(report))
                ok = ok and report["pass"]
            return 0 if ok else 1
        report = eval_spec(spec, ROOT, out_dir)
        print(format_report(report))
        return 0 if report["pass"] else 1

    return 0
