import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ISO_HASH = "a2db286f342329af9595cb8d933fc11ab65bdf194931b4571e3f60fb8a9c06f6"


def test_pyodide_spike_and_zip() -> None:
    spike = (ROOT / "web" / "spike.html").read_text(encoding="utf-8")
    assert "pyodide loaded" in spike
    assert "v314.0.2" in spike
    assert "draw_yaml" in spike
    assert "fly.io" not in spike.lower()
    zpath = ROOT / "web" / "circuit-iso.zip"
    assert zpath.is_file()
    names = zipfile.ZipFile(zpath).namelist()
    assert any(n.endswith("circuit/service.py") for n in names)
    assert not any("ingest" in n or n.endswith("rasterize.py") for n in names)


def test_iso_graph_hash_locked() -> None:
    from circuit.ir.from_spec import compile_report
    from circuit.pack import Pack, using_pack
    from circuit.spec import CircuitSpec

    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    pack = Pack(
        root=ROOT / "src/circuit/packs/iso_sequence",
        atlas_path=ROOT / "src/circuit/packs/iso_sequence/atlas.yaml",
        stamp_dir=ROOT / "src/circuit/packs/iso_sequence/stamps",
        hooks_module="circuit.packs.iso_sequence",
    )
    with using_pack(pack):
        assert compile_report(spec)["graph_sha256"] == ISO_HASH
