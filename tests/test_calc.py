from circuit.calc import area_mm2, grinding_hc1_pressure_bar, l4_regen_example, solution_lines_hilo_2017


def test_cap_area() -> None:
    assert abs(area_mm2(45) - 1590.431) < 0.01


def test_grinding_pressure_positive() -> None:
    assert grinding_hc1_pressure_bar() > 10


def test_l4_regen_speed_ratio_is_two() -> None:
    # Vext = Q/Ar, Vret = Q/(Ap-Ar); Ap=3 Ar => Vext/Vret = 2
    r = l4_regen_example()
    assert abs(r["speed_ratio"] - 2.0) < 1e-9
    assert abs(r["load_ratio"] - 0.5) < 1e-9


def test_hilo_2017_does_not_invent_bore() -> None:
    lines = "\n".join(solution_lines_hilo_2017())
    assert "7800" in lines
    assert "15 cm/s" in lines
    assert "not_given" in lines
    assert "50" not in lines
    assert "28" not in lines
