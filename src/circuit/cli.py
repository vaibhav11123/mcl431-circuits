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

    compile_p = sub.add_parser("compile", help="Synthesize CircuitGraph and print graph_sha256")
    compile_p.add_argument("spec", help="path to circuit.yaml")
    compile_p.add_argument("--pack", help="symbol pack directory")
    compile_p.add_argument("--json", action="store_true", help="print the compile dict")

    bench_p = sub.add_parser("bench", help="Score SequenceBench v0 (compiler, not LLM)")
    bench_p.add_argument("root", help="benchmarks/sequencebench")

    for name, help_ in (
        ("validate", "Validate a circuit.yaml spec"),
        ("draw", "Draw SVG sheets from a spec"),
        ("eval", "Run catalog / graph / sequence / golden checks"),
        ("verify", "Translation validation + SHA-256 manifest"),
    ):
        p = sub.add_parser(name, help=help_)
        p.add_argument("spec", nargs="?", help="path to circuit.yaml")
        p.add_argument("--pack", help="symbol pack directory")
        p.add_argument("--json", action="store_true", help="print the service dict")
        if name == "draw":
            p.add_argument(
                "--unverified",
                action="store_true",
                help="emit watermarked sheets without translation validation",
            )
        if name == "eval":
            p.add_argument("--goldens", action="store_true")
        if name == "verify":
            p.add_argument(
                "--zip",
                dest="zip_path",
                help="verify an exported circuit pack against its included graph",
            )

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

    if args.cmd == "bench":
        from circuit.bench import run_bench
        from circuit.service import dumps

        report = run_bench(Path(args.root))
        print(dumps({k: v for k, v in report.items() if k != "rows"}))
        return 0

    if args.cmd == "compile":
        from circuit.ir.from_spec import compile_report
        from circuit.pack import resolve_pack, using_pack
        from circuit.service import dumps
        from circuit.spec import CircuitSpec

        spec = CircuitSpec.from_yaml(Path(args.spec))
        pack = resolve_pack(getattr(args, "pack", None))
        with using_pack(pack):
            payload = compile_report(spec)
        print(dumps(payload) if args.json else payload["graph_sha256"])
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

    if args.cmd == "verify" and getattr(args, "zip_path", None):
        from circuit.verification.packcheck import verify_zip

        result = verify_zip(Path(args.zip_path))
        print(result)
        return 0 if result.get("ok") else 1

    spec_path = Path(args.spec) if getattr(args, "spec", None) else (
        ROOT / "examples/grinding_machine/circuit.yaml"
    )
    from circuit.spec import CircuitSpec, question_output_dir

    spec = CircuitSpec.from_yaml(spec_path)
    out_dir = question_output_dir(ROOT, spec, spec_path)
    from circuit.pack import resolve_pack, using_pack

    pack = resolve_pack(getattr(args, "pack", None))
    with using_pack(pack):
        return _run_engine(args, spec, spec_path, out_dir, pack)


def _run_engine(args, spec, spec_path, out_dir, pack) -> int:
    as_json = bool(getattr(args, "json", False))
    if as_json and args.cmd in {"validate", "draw", "eval"} and not getattr(args, "goldens", False):
        from circuit.service import draw_yaml, dumps, eval_yaml, validate_yaml

        text = spec_path.read_text(encoding="utf-8")
        if args.cmd == "validate":
            payload = validate_yaml(text)
        elif args.cmd == "draw":
            payload = draw_yaml(text)
        else:
            payload = eval_yaml(text)
        print(dumps(payload))
        return 0 if payload.get("ok") else 1

    if args.cmd == "validate":
        from circuit.validate import all_ok, validate_spec

        checks = validate_spec(spec, pack.root)
        for c in checks:
            print(f"{'PASS' if c.ok else 'FAIL'} {c.name}  {c.detail}")
        return 0 if all_ok(checks) else 1

    if args.cmd == "draw":
        from circuit.draw import draw_all, watermark_written
        from circuit.service import draw_yaml

        if getattr(args, "unverified", False):
            written = draw_all(spec, out_dir)
            watermark_written(written)
            for k, p in written.items():
                print(f"{k}: {p}")
            print("UNVERIFIED")
            return 0

        payload = draw_yaml(spec_path.read_text(encoding="utf-8"))
        out_dir.mkdir(parents=True, exist_ok=True)
        names = {
            "pneumatic": "pneumatic_circuit.svg",
            "electrical": "electrical_circuit.svg",
            "hydraulic": "hydraulic_circuit.svg",
            "phase": "step_displacement.svg",
            "connection": "plc_connection.svg",
            "ladder": "plc_ladder.svg",
            "solution": "solution.txt",
            "calc": "calc_only.svg",
        }
        written: dict[str, Path] = {}
        for key, svg in (payload.get("sheets") or {}).items():
            dest = out_dir / names.get(key, f"{key}.svg")
            dest.write_text(svg, encoding="utf-8")
            written[key] = dest
        (out_dir / "card.svg").write_text(payload.get("card") or "", encoding="utf-8")
        (out_dir / "report.svg").write_text(payload.get("report") or "", encoding="utf-8")
        if not payload.get("ok"):
            print(payload.get("sentence") or "FAIL")
            return 1
        for k, p in written.items():
            print(f"{k}: {p}")
        return 0

    if args.cmd == "eval":
        from circuit.eval import eval_spec, format_report
        from circuit.spec import CircuitSpec, question_output_dir

        if getattr(args, "goldens", False):
            from circuit.eval import golden_specs

            ok = True
            for path in golden_specs(ROOT):
                s = CircuitSpec.from_yaml(path)
                golden_out = question_output_dir(ROOT, s, path)
                report = eval_spec(s, pack.root, golden_out)
                print(format_report(report))
                ok = ok and report["pass"]
            return 0 if ok else 1
        report = eval_spec(spec, pack.root, out_dir)
        print(format_report(report))
        return 0 if report["pass"] else 1

    if args.cmd == "verify":
        from circuit.verification.manifest import write_manifest

        man = write_manifest(spec, out_dir)
        print(man.get("path", ""))
        return 0 if man.get("ok") else 1

    return 0
