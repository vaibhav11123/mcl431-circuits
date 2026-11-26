from pathlib import Path

import pytest

from circuit.compile_sequence import apply_compile
from circuit.draw import draw_all
from circuit.ir.from_spec import from_spec
from circuit.pack import Pack, using_pack
from circuit.spec import CircuitSpec
from circuit.verification.artifact import seal
from circuit.verification.refine import verify_spec


ROOT = Path(__file__).resolve().parents[1]
ISO_PACK = Pack(
    root=ROOT / "src/circuit/packs/iso_sequence",
    atlas_path=ROOT / "src/circuit/packs/iso_sequence/atlas.yaml",
    stamp_dir=ROOT / "src/circuit/packs/iso_sequence/stamps",
    hooks_module="circuit.packs.iso_sequence",
)


def test_verified_draw_does_not_call_compile_paths(tmp_path: Path, monkeypatch) -> None:
    spec = CircuitSpec.from_yaml(ROOT / "examples/iso_sequence/circuit.yaml")
    with using_pack(ISO_PACK):
        compiled = apply_compile(spec)
        graph = from_spec(compiled)
        vr = verify_spec(compiled)
        sealed = seal(compiled, graph, vr)

        def boom(*_a, **_k):
            raise AssertionError("compile_paths during render")

        monkeypatch.setattr("circuit.compile_sequence.compile_paths", boom)
        written = draw_all(sealed.spec, tmp_path, verified=sealed)
    svg = written["electrical"].read_text()
    assert 'data-origin="spec:coil"' in svg
    assert "1Y1" in svg
