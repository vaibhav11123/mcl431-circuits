"""CLI: validate, draw, eval, rasterize, ingest."""

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

    ing = sub.add_parser(
        "ingest",
        help="Draft exam/lecture text from a local PDF or scan (needs .[ingest])",
    )
    ing.add_argument(
        "paths",
        nargs="*",
        help="local pdf/jpeg/png/tif, or a directory of those files",
    )
    ing.add_argument(
        "--formula",
        action="store_true",
        help="enable Docling formula enrichment (off by default)",
    )
    ing.add_argument(
        "--no-ocr",
        action="store_true",
        help="skip OCR even on image scans",
    )

    prom = sub.add_parser(
        "promote",
        help="Write a proposal/ review folder from an ingest draft (never edits locks)",
    )
    prom.add_argument(
        "paths",
        nargs="*",
        help="exams/ingest/<stem> or lecture/ingest/<stem> directories",
    )

    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 0

    if args.cmd == "rasterize":
        from circuit.rasterize import rasterize_all

        return rasterize_all(ROOT, dpi=args.dpi, only=args.only)

    if args.cmd == "ingest":
        from circuit.ingest import main as ingest_main

        return ingest_main(
            ROOT,
            [Path(p) for p in (args.paths or [])],
            formula=bool(getattr(args, "formula", False)),
            no_ocr=bool(getattr(args, "no_ocr", False)),
        )

    if args.cmd == "promote":
        from circuit.ingest_promote import main as promote_main

        return promote_main(ROOT, [Path(p) for p in (args.paths or [])])

    spec_path = Path(args.spec) if getattr(args, "spec", None) else (
        ROOT / "examples/grinding_machine/circuit.yaml"
    )
    from circuit.spec import CircuitSpec, question_output_dir

    spec = CircuitSpec.from_yaml(spec_path)
    out_dir = question_output_dir(ROOT, spec, spec_path)

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
            from circuit.eval import golden_specs

            ok = True
            for path in golden_specs(ROOT):
                s = CircuitSpec.from_yaml(path)
                golden_out = question_output_dir(ROOT, s, path)
                report = eval_spec(s, ROOT, golden_out)
                print(format_report(report))
                ok = ok and report["pass"]
            return 0 if ok else 1
        report = eval_spec(spec, ROOT, out_dir)
        print(format_report(report))
        return 0 if report["pass"] else 1

    return 0
