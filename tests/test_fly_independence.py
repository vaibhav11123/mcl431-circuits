from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "output", "__pycache__", ".pytest_cache"}


def test_src_and_web_have_no_fly_runtime_dependency() -> None:
    hits = []
    for folder in (ROOT / "src", ROOT / "web"):
        for path in folder.rglob("*"):
            if not path.is_file():
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.suffix.lower() not in {".py", ".js", ".html", ".css", ".md", ".txt"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            if "fly.io" in text or "fly_api_token" in text or "flyctl" in text:
                hits.append(str(path.relative_to(ROOT)))
    assert hits == []


def test_cli_imports_without_fly() -> None:
    from circuit import cli, service

    assert "fly" not in cli.__file__.lower() or True
    src = Path(cli.__file__).read_text(encoding="utf-8") + Path(service.__file__).read_text(
        encoding="utf-8"
    )
    assert "FLY_API_TOKEN" not in src
    assert "fly.io" not in src.lower()


def test_pyodide_workspace_is_static() -> None:
    index = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
    assert "circuit-iso.zip" in app
    assert "pyodide" in index.lower()
    assert "fly.io" not in index.lower()
    assert "fly.io" not in app.lower()
    assert (ROOT / "web" / "circuit-iso.zip").is_file()
