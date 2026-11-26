import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from circuit.ir.from_spec import compile_report, from_spec, graph_sha256
from circuit.pack import Pack, using_pack
from circuit.spec import CircuitSpec
from circuit.verification.manifest import write_manifest


ROOT = Path(__file__).resolve().parents[1]
ISO = Pack(
    root=ROOT / "src/circuit/packs/iso_sequence",
    atlas_path=ROOT / "src/circuit/packs/iso_sequence/atlas.yaml",
    stamp_dir=ROOT / "src/circuit/packs/iso_sequence/stamps",
    hooks_module="circuit.packs.iso_sequence",
)


def test_cli_vs_inprocess_hash(tmp_path: Path) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    with using_pack(ISO):
        a = write_manifest(spec, tmp_path / "a")
        b = write_manifest(spec, tmp_path / "b")
        in_process = graph_sha256(from_spec(spec))
    assert a["sha256_spec"] == b["sha256_spec"]
    assert a["sha256_spec"] == hashlib.sha256(spec.to_yaml().encode()).hexdigest()
    assert a["graph_sha256"] == in_process
    assert a["graph_sha256"] == b["graph_sha256"]


def test_cli_compile_json_matches_inprocess() -> None:
    spec_path = ROOT / "examples/iso_sequence/circuit.yaml"
    spec = CircuitSpec.from_yaml(spec_path)
    with using_pack(ISO):
        want = compile_report(spec)["graph_sha256"]
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "circuit",
            "compile",
            str(spec_path),
            "--json",
            "--pack",
            str(ISO.root),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    got = json.loads(proc.stdout)["graph_sha256"]
    assert got == want


def test_graph_hash_stable_across_hashseed() -> None:
    spec_path = ROOT / "examples/iso_sequence/circuit.yaml"
    cmd = [
        sys.executable,
        "-m",
        "circuit",
        "compile",
        str(spec_path),
        "--json",
        "--pack",
        str(ISO.root),
    ]
    hashes = []
    for seed in ("0", "1"):
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = seed
        proc = subprocess.run(
            cmd, cwd=ROOT, capture_output=True, text=True, check=True, env=env
        )
        hashes.append(json.loads(proc.stdout)["graph_sha256"])
    assert hashes[0] == hashes[1]
