import asyncio
from pathlib import Path

import pytest

from circuit.mcp_server import _LOG, create_server, INSTRUCTIONS


ROOT = Path(__file__).resolve().parents[1]
ISO_YAML = (ROOT / "examples/iso_sequence/circuit.yaml").read_text()


def test_instructions_cap() -> None:
    assert len(INSTRUCTIONS) <= 512


def test_list_tools_annotations() -> None:
    mcp = create_server()
    tools = asyncio.run(mcp.list_tools())
    names = {t.name for t in tools}
    assert "draw_spec" in names
    assert "get_sheet" in names
    listing = next(t for t in tools if t.name == "list_symbols")
    assert listing.annotations and listing.annotations.readOnlyHint is True
    assert listing.title
    draw = next(t for t in tools if t.name == "draw_spec")
    assert draw.annotations.readOnlyHint is False
    assert draw.annotations.openWorldHint is False
    sheet = next(t for t in tools if t.name == "get_sheet")
    assert sheet.annotations.readOnlyHint is True


def test_draw_spec_iso_has_image() -> None:
    mcp = create_server()
    result = asyncio.run(mcp.call_tool("draw_spec", {"yaml": ISO_YAML}))
    blocks = result if isinstance(result, (list, tuple)) else getattr(result, "content", result)
    types = []
    for b in blocks:
        t = b.get("type") if isinstance(b, dict) else getattr(b, "type", None)
        types.append(t)
    assert "image" in types


def test_oversize_yaml_is_error() -> None:
    mcp = create_server()
    huge = "x: " + ("a" * 300_000)
    with pytest.raises(Exception):
        asyncio.run(mcp.call_tool("draw_spec", {"yaml": huge}))


def test_get_sheet_without_yaml_is_error() -> None:
    mcp = create_server()
    with pytest.raises(Exception) as exc:
        asyncio.run(mcp.call_tool("get_sheet", {}))
    assert "full spec YAML" in str(exc.value)


def test_log_omits_yaml_marker() -> None:
    _LOG.clear()
    mcp = create_server()
    marker = "MARKER-do-not-log"
    yaml_text = ISO_YAML.replace("ISO two-cylinder", marker)
    try:
        asyncio.run(mcp.call_tool("draw_spec", {"yaml": yaml_text}))
    except Exception:
        pass
    joined = "\n".join(_LOG)
    assert marker not in joined
