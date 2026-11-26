"""MCP server. YAML in, PNG out. Never log YAML. Never invent symbols."""

from __future__ import annotations

import argparse
import base64
import sys
import time
from collections import deque

INSTRUCTIONS = (
    "YAML specs only. Use ids from the symbols resource. Never invent a valve "
    "or sensor. Never generate an image yourself — call draw_spec then get_sheet. "
    "Assume 5/2 double solenoid if the valve is unnamed and say so on the report. "
    "Refuse FluidSIM .ct, pressure simulation, and cascade beyond 3 cylinders "
    "(offer the 5/2 electropneumatic equivalent). Retry draw at most twice. "
    "If chat has no picture, call get_sheet with the same YAML."
)
assert len(INSTRUCTIONS) <= 512

_LOG: list[str] = []
_DRAWS: deque[float] = deque()
_MAX_DRAWS_PER_HOUR = 30


def _log(msg: str) -> None:
    _LOG.append(msg)
    print(msg, file=sys.stderr)


def _rate_ok() -> bool:
    now = time.time()
    while _DRAWS and now - _DRAWS[0] > 3600:
        _DRAWS.popleft()
    if len(_DRAWS) >= _MAX_DRAWS_PER_HOUR:
        return False
    _DRAWS.append(now)
    return True


def create_server():
    from mcp.server.fastmcp import FastMCP
    from mcp.types import Annotations, ImageContent, TextContent, ToolAnnotations
    from mcp.server.fastmcp.exceptions import ToolError
    from starlette.requests import Request
    from starlette.responses import JSONResponse, HTMLResponse

    from circuit.service import (
        SENTENCE_TOO_LARGE,
        draw_yaml,
        eval_yaml,
        get_sheet as fetch_sheet,
        list_symbols as list_symbols_fn,
        validate_yaml,
        MAX_YAML_BYTES,
    )

    mcp = FastMCP("sequence-circuit", instructions=INSTRUCTIONS)

    def _preview_image(yaml_text: str, name: str = "pneumatic"):
        png = fetch_sheet(yaml_text, name)
        if not png:
            png = fetch_sheet(yaml_text, "card")
        if not png:
            return None
        return ImageContent(
            type="image",
            data=base64.b64encode(png).decode("ascii"),
            mimeType="image/png",
            annotations=Annotations(audience=["user"]),
        )

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False),
    )
    def list_symbols() -> dict:
        _log("list_symbols ok=true")
        return list_symbols_fn()

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False),
    )
    def validate_spec(yaml: str) -> dict:
        if len(yaml.encode()) > MAX_YAML_BYTES:
            _log("validate_spec ok=false")
            raise ToolError(SENTENCE_TOO_LARGE)
        out = validate_yaml(yaml)
        _log(f"validate_spec ok={out.get('ok')}")
        return out

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False),
    )
    def eval_spec(yaml: str) -> dict:
        if len(yaml.encode()) > MAX_YAML_BYTES:
            _log("eval_spec ok=false")
            raise ToolError(SENTENCE_TOO_LARGE)
        out = eval_yaml(yaml)
        _log(f"eval_spec ok={out.get('ok')}")
        return out

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False),
    )
    def draw_spec(yaml: str):
        if len(yaml.encode()) > MAX_YAML_BYTES:
            _log("draw_spec ok=false")
            raise ToolError(SENTENCE_TOO_LARGE)
        if not _rate_ok():
            raise ToolError("draw rate limit")
        t0 = time.time()
        out = draw_yaml(yaml)
        if time.time() - t0 > 30:
            raise ToolError("draw timed out")
        _log(f"draw_spec ok={out.get('ok')}")
        sentence = out.get("sentence") or ""
        content = [TextContent(type="text", text=sentence)]
        img = _preview_image(yaml, "pneumatic") or _preview_image(yaml, "card")
        if img is not None:
            content.append(img)
        names = list((out.get("sheets") or {}).keys())
        content.append(TextContent(type="text", text="sheets: " + ",".join(names)))
        return content

    @mcp.tool(
        name="get_sheet",
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False),
    )
    def get_sheet(yaml: str = "", name: str = "pneumatic"):
        if not yaml.strip():
            _log("get_sheet ok=false")
            raise ToolError("Pass the full spec YAML; this server does not store sheets.")
        if len(yaml.encode()) > MAX_YAML_BYTES:
            raise ToolError(SENTENCE_TOO_LARGE)
        img = _preview_image(yaml, name)
        if img is None:
            raise ToolError("No sheet for that name.")
        _log("get_sheet ok=true")
        return [img]

    @mcp.resource("symbols://iso")
    def symbols_iso() -> str:
        import json
        from pathlib import Path

        from circuit.pack import Pack, using_pack

        root = Path(__file__).resolve().parent / "packs" / "iso_sequence"
        pack = Pack(
            root=root,
            atlas_path=root / "atlas.yaml",
            stamp_dir=root / "stamps",
            hooks_module="circuit.packs.iso_sequence",
        )
        with using_pack(pack):
            return json.dumps(list_symbols_fn())

    @mcp.custom_route("/health", methods=["GET"])
    async def health(request: Request):
        return JSONResponse({"ok": True})

    @mcp.custom_route("/privacy", methods=["GET"])
    async def privacy(request: Request):
        return HTMLResponse("<html><body><h1>Privacy</h1><p>No accounts. YAML is not stored.</p></body></html>")

    return mcp


mcp = None


def get_mcp():
    global mcp
    if mcp is None:
        mcp = create_server()
    return mcp


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="circuit.mcp_server")
    parser.add_argument("--http", action="store_true")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="127.0.0.1")
    args, _unknown = parser.parse_known_args(argv)
    server = get_mcp()
    if args.http:
        server.settings.host = args.host
        server.settings.port = args.port
        server.run(transport="streamable-http")
        return 0
    server.run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
