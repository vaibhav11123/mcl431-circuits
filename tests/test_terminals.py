from circuit.terminals import bare, contact_actuated, contact_kind, contact_terminals


def test_start_is_pushbutton_13_14() -> None:
    assert contact_kind("START") == "pushbutton"
    assert contact_terminals("START") == ("13", "14")
    assert contact_actuated("START") is False


def test_s1_s3_same_as_start() -> None:
    for tag in ("S1", "S3"):
        assert contact_kind(tag) == contact_kind("START")
        assert contact_terminals(tag) == contact_terminals("START")
        assert contact_actuated(tag) == contact_actuated("START")


def test_k1_first_aux_11_14() -> None:
    assert contact_kind("K1") == "contact_no"
    assert contact_terminals("K1", 0) == ("11", "14")
    assert contact_terminals("K1") == ("11", "14")


def test_k1_second_aux_21_24() -> None:
    assert contact_kind("K1") == "contact_no"
    assert contact_terminals("K1", 1) == ("21", "24")
    assert contact_terminals("K1", 2) == ("21", "24")


def test_home_b1_is_nc_1_2_actuated() -> None:
    for tag in ("1B1", "2B1"):
        assert contact_kind(tag) == "contact_nc"
        assert contact_terminals(tag) == ("1", "2")
        assert contact_actuated(tag) is True


def test_extend_b2_13_14_not_actuated() -> None:
    for tag in ("1B2", "2B2"):
        assert contact_kind(tag) == "limit_switch"
        assert contact_terminals(tag) == ("13", "14")
        assert contact_actuated(tag) is False


def test_job_limit_13_14_not_actuated() -> None:
    assert contact_kind("JOB") == "limit_switch"
    assert contact_terminals("JOB") == ("13", "14")
    assert contact_actuated("JOB") is False


def test_t1_contact_delayed_7_8() -> None:
    assert contact_kind("T1") == "contact_no"
    assert contact_terminals("T1") == ("7", "8")
    assert contact_actuated("T1") is False


def test_bang_prefix_stripped() -> None:
    assert bare("!K4") == "K4"
    assert contact_kind("!K4") == "contact_no"
    assert contact_terminals("!K4", 0) == ("11", "14")


def test_y_tags_are_not_classified_as_home_sensors() -> None:
    assert contact_kind("1Y1") != "contact_nc"
    assert contact_actuated("1Y1") is False
