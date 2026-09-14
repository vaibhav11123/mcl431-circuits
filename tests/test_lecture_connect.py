from circuit.lecture_connect import connect_recipes


def test_dac_4_3_a_is_cylinder_cap() -> None:
    recipes = connect_recipes()
    assert recipes["dac_4_3"]["A"] == "cylinder.cap"
    assert recipes["dac_4_3"]["B"] == "cylinder.rod"
    assert recipes["dac_4_3"]["P"] == "pump_rail"
    assert recipes["dac_4_3"]["T"] == "tank_rail"
