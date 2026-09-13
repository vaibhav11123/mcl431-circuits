from circuit.cli import main


def test_no_args_prints_usage() -> None:
    assert main([]) == 0


def test_help_exits_zero() -> None:
    try:
        main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0
