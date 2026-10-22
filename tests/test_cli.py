from circuit.cli import main


def test_no_args_prints_usage() -> None:
    assert main([]) == 0


def test_help_exits_zero() -> None:
    try:
        main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0


def test_ingest_help_exits_zero() -> None:
    try:
        main(["ingest", "--help"])
    except SystemExit as exc:
        assert exc.code == 0


def test_ingest_missing_file_exits_two_without_docling() -> None:
    """Without the ingest extra, any ingest path returns 2 before file work."""
    try:
        import docling  # noqa: F401
    except ImportError:
        assert main(["ingest", "/tmp/does-not-exist-circuit-ingest.pdf"]) == 2
        return
    # Docling present: missing file is a convert/path error (1), not 2.
    assert main(["ingest", "/tmp/does-not-exist-circuit-ingest.pdf"]) == 1


def test_ingest_does_not_import_docling_on_help() -> None:
    import sys

    sys.modules.pop("docling", None)
    try:
        main(["ingest", "--help"])
    except SystemExit:
        pass
    assert "docling" not in sys.modules


def test_promote_help_exits_zero() -> None:
    try:
        main(["promote", "--help"])
    except SystemExit as exc:
        assert exc.code == 0


def test_promote_missing_dir_exits_nonzero() -> None:
    assert main(["promote", "/tmp/circuit-ingest-promote-missing-xyz"]) == 1


def test_cli_import_does_not_load_docling() -> None:
    import sys

    sys.modules.pop("docling", None)
    import circuit.cli  # noqa: F401

    assert "docling" not in sys.modules
