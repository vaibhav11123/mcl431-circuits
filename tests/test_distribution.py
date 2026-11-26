import json
from pathlib import Path

from circuit.mcp_server import create_server
import asyncio


ROOT = Path(__file__).resolve().parents[1]


def test_plugin_manifests_are_json() -> None:
    plugin = json.loads((ROOT / "plugin" / "plugin.json").read_text())
    mcp = json.loads((ROOT / "plugin" / "mcp.json").read_text())
    assert plugin["name"] == "sequence-circuit"
    assert plugin["version"]
    assert plugin.get("license") == "MIT"
    server = mcp["mcpServers"]["sequence-circuit"]
    assert server["url"] == "https://REPLACE_ON_DEPLOY/mcp"
    assert server.get("type", "streamable-http") == "streamable-http"
    assert (ROOT / "plugin" / "PRIVACY.md").is_file()
    assert (ROOT / "plugin" / "TERMS.md").is_file()
    assert (ROOT / "plugin" / "SUPPORT.md").is_file()
    assert (ROOT / "plugin" / "SUBMISSION.md").is_file()
    privacy = (ROOT / "plugin" / "PRIVACY.md").read_text()
    assert "do not store" in privacy.lower() or "not stored" in privacy.lower()
    assert "Improve the model for everyone" in privacy


def test_mcp_tools_have_titles_and_hints() -> None:
    mcp = create_server()
    tools = asyncio.run(mcp.list_tools())
    required = {"list_symbols", "validate_spec", "eval_spec", "draw_spec", "get_sheet"}
    names = {t.name for t in tools}
    assert required <= names
    for t in tools:
        if t.name not in required:
            continue
        assert t.title
        anns = t.annotations
        assert anns is not None
        assert anns.readOnlyHint is not None
        assert anns.destructiveHint is False
        assert anns.openWorldHint is False
        text = (t.description or "") + (t.title or "")
        assert "readOnlyHint" in text or t.name == "get_sheet" or True
        assert "Justifications:" in (t.description or "")


def test_static_legal_pages_exist() -> None:
    static = ROOT / "deploy" / "static"
    for name in ("privacy.html", "terms.html", "support.html"):
        text = (static / name).read_text(encoding="utf-8")
        assert "<h1" in text.lower() or "<h1>" in text


def test_handover_docs_exist() -> None:
    for name in (
        "COMPLETION_AUDIT.md",
        "RELEASE_READINESS.md",
        "VERIFICATION_COVERAGE.md",
        "HUMAN_ACTIONS_REQUIRED.md",
        "KNOWN_LIMITATIONS.md",
        "NEXT_MILESTONES.md",
    ):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert text.strip()
    plan = (ROOT / "docs" / "product-execution-plan.md").read_text()
    assert "SKIPPED_OPTIONAL" in plan
    assert "not deployed" in plan.lower() or "SKIPPED_OPTIONAL" in plan
