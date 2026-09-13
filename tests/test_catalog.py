from circuit.catalog import GLYPHS, glyph


def test_every_stamp_file_exists() -> None:
    for gid in GLYPHS:
        g = glyph(gid)
        assert g.path.is_file(), gid
