from pathlib import Path

from circuit.compile_sequence import apply_compile, bare, displacement_rows
from circuit.spec import CircuitSpec


def test_grinding_compiles_six_steps_and_timer() -> None:
    spec = CircuitSpec.from_yaml(
        Path(__file__).resolve().parents[1] / "examples/grinding_machine/circuit.yaml"
    )
    compiled = apply_compile(spec)
    coils = [p.coil for p in compiled.electrical.paths if p.coil]
    for name in ("K1", "K2", "K4", "K3", "1Y1", "3Y1", "2Y1", "T1_30s", "2Y2", "1Y2"):
        assert name in coils, name
    assert coils.count("K4") == 1
    assert coils.count("K3") == 1
    contacts = {bare(c) for p in compiled.electrical.paths for c in (p.contacts or [])}
    for name in ("START", "JOB", "K1", "1B2", "2B1", "2B2", "1B1", "K2", "K4", "K3"):
        assert name in contacts, name
    assert "3Y1" not in contacts
    assert any(p.coil == "K1" and "K1" in (p.contacts or []) for p in compiled.electrical.paths)
    kinds = [p.kind for p in compiled.electrical.paths]
    assert kinds == sorted(kinds, key=lambda k: 0 if k != "main" else 1)
    rows = displacement_rows(spec.sequence)
    assert len(rows) == 6


def test_grinding_hc2_waits_for_motor_and_home() -> None:
    spec = CircuitSpec.from_yaml(
        Path(__file__).resolve().parents[1] / "examples/grinding_machine/circuit.yaml"
    )
    paths = apply_compile(spec).electrical.paths
    feed_set = next(
        p for p in paths if p.coil == "K3" and "2B1" in (p.contacts or [])
    )
    assert "K2" in feed_set.contacts
    assert "!K4" in feed_set.contacts
    y1 = next(p for p in paths if p.coil == "1Y1")
    assert "K1" in y1.contacts
    assert "!K4" in y1.contacts
    assert "!1Y2" in y1.contacts
    y2 = next(p for p in paths if p.coil == "2Y1")
    assert "K1" not in y2.contacts
    assert "!2Y2" in y2.contacts
    retract = next(p for p in paths if p.coil == "2Y2")
    assert retract.contacts == ["K4", "!2Y1"]
    unclamp = next(p for p in paths if p.coil == "1Y2")
    assert "K4" in unclamp.contacts
    assert "2B1" in unclamp.contacts
    assert "!1Y1" in unclamp.contacts
    done = [p for p in paths if p.coil == "K4"]
    assert len(done) == 1
    assert done[0].contacts == ["T1"]


def test_indexing_drill_step_relays_and_km() -> None:
    spec = CircuitSpec.from_yaml(
        Path(__file__).resolve().parents[1] / "examples/drill_2017/circuit.yaml"
    )
    paths = apply_compile(spec).electrical.paths
    coils = [p.coil for p in paths if p.coil]
    for name in ("K1", "K2", "K13", "K14", "KM", "1Y1", "1Y2", "2Y1", "2Y2", "3Y1", "3Y2"):
        assert name in coils, name
    assert coils.count("3Y1") == 4
    assert coils.count("3Y2") == 4
    k1_set = next(p for p in paths if p.coil == "K1" and "START" in (p.contacts or []))
    for tag in ("START", "S0", "1B1", "2B1", "3B1"):
        assert tag in k1_set.contacts, tag
    k1_latch = next(p for p in paths if p.coil == "K1" and "K1" in (p.contacts or []))
    assert "S0" in k1_latch.contacts
    assert "!K14" in k1_latch.contacts
    km = next(p for p in paths if p.coil == "KM")
    assert "K1" in km.contacts
    assert "!K13" in km.contacts
    k2_hold = next(
        p for p in paths if p.coil == "K2" and "!K3" in (p.contacts or [])
    )
    assert k2_hold.contacts == ["K2", "!K3"]
    y1 = next(p for p in paths if p.coil == "1Y1")
    assert "K4" in y1.contacts
    assert "!1Y2" in y1.contacts
    no_y = [
        c
        for p in paths
        for c in (p.contacts or [])
        if not c.startswith("!") and "Y" in c
    ]
    assert no_y == []


def test_strip_feed_still_chains_on_end_sensors() -> None:
    spec = CircuitSpec.from_yaml(
        Path(__file__).resolve().parents[1] / "examples/strip_feed_2023/circuit.yaml"
    )
    coils = [p.coil for p in apply_compile(spec).electrical.paths if p.coil]
    for name in ("1Y1", "2Y2", "1Y2", "2Y1", "H1"):
        assert name in coils, name
    contacts = {bare(c) for p in apply_compile(spec).electrical.paths for c in (p.contacts or [])}
    assert "H1" not in contacts


def test_emboss_2016_waits_for_pressure_not_2b2() -> None:
    spec = CircuitSpec.from_yaml(
        Path(__file__).resolve().parents[1] / "examples/emboss_2016/circuit.yaml"
    )
    paths = apply_compile(spec).electrical.paths
    coils = [p.coil for p in paths if p.coil]
    for name in ("K1", "K3", "K4", "K5", "1Y1", "1Y2", "2Y1", "2Y2"):
        assert name in coils, name
    k1_set = next(p for p in paths if p.coil == "K1" and "S1" in (p.contacts or []))
    for tag in ("S1", "S0", "1B1", "2B1"):
        assert tag in k1_set.contacts, tag
    k4_set = next(p for p in paths if p.coil == "K4" and "PS" in (p.contacts or []))
    assert "K3" in k4_set.contacts
    retract = next(p for p in paths if p.coil == "2Y2")
    assert "K4" in retract.contacts
    assert "2B2" not in retract.contacts
    assert "!2Y1" in retract.contacts
    advance = next(p for p in paths if p.coil == "2Y1")
    assert "2B2" not in advance.contacts
    unclamp = next(p for p in paths if p.coil == "1Y2")
    assert "K5" in unclamp.contacts
    assert "2B1" not in unclamp.contacts
    rows = displacement_rows(spec.sequence)
    assert [r["action"] for r in rows] == ["1A1+", "2A1+", "PS", "2A1-", "1A1-"]
