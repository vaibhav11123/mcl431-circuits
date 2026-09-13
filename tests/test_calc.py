from circuit.calc import area_mm2, grinding_hc1_pressure_bar, l4_regen_example


def test_cap_area() -> None:
    assert abs(area_mm2(45) - 1590.431) < 0.01


def test_grinding_pressure_positive() -> None:
    assert grinding_hc1_pressure_bar() > 10


def test_l4_regen_speed_ratio_is_two() -> None:
    # Vext = Q/Ar, Vret = Q/(Ap-Ar); Ap=3 Ar => Vext/Vret = 2
    r = l4_regen_example()
    assert abs(r["speed_ratio"] - 2.0) < 1e-9
    assert abs(r["load_ratio"] - 0.5) < 1e-9
