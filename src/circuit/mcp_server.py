"""MCP server. YAML in, PNG out. Never log YAML. Never invent symbols."""

from __future__ import annotations

import argparse
import base64
import sys
import time
from collections import deque
from pathlib import Path

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
        title="List pack symbols",
        description=(
            "Return atlas symbol ids and ports from the active pack. "
            "Justifications: readOnlyHint=true because this does not emit sheets "
            "or write server state; destructiveHint=false because nothing stored "
            "is modified; openWorldHint=false because the pack is local."
        ),
        annotations=ToolAnnotations(
            title="List pack symbols",
            readOnlyHint=True,
            destructiveHint=False,
            openWorldHint=False,
        ),
    )
    def list_symbols() -> dict:
        _log("list_symbols ok=true")
        return list_symbols_fn()

    @mcp.tool(
        title="Validate circuit YAML",
        description=(
            "Run pack catalog checks on a YAML spec. "
            "Justifications: readOnlyHint=true because no sheet is stored; "
            "destructiveHint=false because the server has no durable circuit; "
            "openWorldHint=false because validation is local."
        ),
        annotations=ToolAnnotations(
            title="Validate circuit YAML",
            readOnlyHint=True,
            destructiveHint=False,
            openWorldHint=False,
        ),
    )
    def validate_spec(yaml: str) -> dict:
        if len(yaml.encode()) > MAX_YAML_BYTES:
            _log("validate_spec ok=false")
            raise ToolError(SENTENCE_TOO_LARGE)
        out = validate_yaml(yaml)
        _log(f"validate_spec ok={out.get('ok')}")
        return out

    @mcp.tool(
        title="Evaluate circuit YAML",
        description=(
            "Run eval checks on a YAML spec and return an English sentence. "
            "Justifications: readOnlyHint=true because no artifact is published; "
            "destructiveHint=false because nothing is stored; "
            "openWorldHint=false because eval is local."
        ),
        annotations=ToolAnnotations(
            title="Evaluate circuit YAML",
            readOnlyHint=True,
            destructiveHint=False,
            openWorldHint=False,
        ),
    )
    def eval_spec(yaml: str) -> dict:
        if len(yaml.encode()) > MAX_YAML_BYTES:
            _log("eval_spec ok=false")
            raise ToolError(SENTENCE_TOO_LARGE)
        out = eval_yaml(yaml)
        _log(f"eval_spec ok={out.get('ok')}")
        return out

    @mcp.tool(
        title="Draw verified circuit sheets",
        description=(
            "Compile YAML to sheets only if validate, eval, and translation "
            "validation PASS. Example legal YAML: a two-cylinder 5/2 sequence "
            "A+ B+ B- A- with valves typed dcv_5_2_double_solenoid. "
            "Justifications: readOnlyHint=false because this produces a new "
            "artifact for the caller; destructiveHint=false because the server "
            "does not overwrite stored circuits; openWorldHint=false because "
            "draw is local and does not call the public internet."
        ),
        annotations=ToolAnnotations(
            title="Draw verified circuit sheets",
            readOnlyHint=False,
            destructiveHint=False,
            openWorldHint=False,
        ),
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
        title="Get one sheet PNG",
        description=(
            "Redraw one named sheet from the full YAML. This server does not "
            "store previous draws. Justifications: readOnlyHint=true because "
            "nothing is stored; destructiveHint=false because no durable state "
            "is modified; openWorldHint=false because render is local."
        ),
        annotations=ToolAnnotations(
            title="Get one sheet PNG",
            readOnlyHint=True,
            destructiveHint=False,
            openWorldHint=False,
        ),
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

    def _static_page(name: str, fallback: str) -> str:
        path = Path(__file__).resolve().parents[2] / "deploy" / "static" / name
        if path.is_file():
            return path.read_text(encoding="utf-8")
        return fallback

    @mcp.custom_route("/privacy", methods=["GET"])
    async def privacy(request: Request):
        return HTMLResponse(
            _static_page(
                "privacy.html",
                "<html><body><h1>Privacy</h1><p>No accounts. YAML is not stored.</p></body></html>",
            )
        )

    @mcp.custom_route("/terms", methods=["GET"])
    async def terms(request: Request):
        return HTMLResponse(
            _static_page(
                "terms.html",
                "<html><body><h1>Terms</h1><p>Logical verification only. Not a safety certificate.</p></body></html>",
            )
        )

    @mcp.custom_route("/support", methods=["GET"])
    async def support(request: Request):
        return HTMLResponse(
            _static_page(
                "support.html",
                "<html><body><h1>Support</h1><p>Open a GitHub issue. No accounts.</p></body></html>",
            )
        )

    @mcp.custom_route("/.well-known/openai-apps-challenge", methods=["GET"])
    async def openai_apps_challenge(request: Request):
        from starlette.responses import PlainTextResponse

        token = _static_page("openai-apps-challenge.txt", "REPLACE_TOKEN").strip()
        return PlainTextResponse(token)

    return mcp


mcp = None


def get_mcp():
    global mcp
    if mcp is None:
        mcp = create_server()
    return mcp


def http_transport_security(
    *,
    public_host: str | None = None,
    disable_dns_rebind: bool | None = None,
):
    """Build FastMCP DNS-rebinding settings for tunnel / workers.dev Host headers.

    MCP only matches exact Host values (or ``host:*`` port wildcards), not
    ``*.loca.lt``. Pass ``CIRCUIT_MCP_PUBLIC_HOST=hostname`` or
    ``CIRCUIT_MCP_DISABLE_DNS_REBIND=1``.
    """
    import os

    from mcp.server.transport_security import TransportSecuritySettings

    allowed_hosts = [
        "127.0.0.1",
        "127.0.0.1:*",
        "localhost",
        "localhost:*",
        "[::1]",
        "[::1]:*",
    ]
    allowed_origins = [
        "http://127.0.0.1",
        "http://127.0.0.1:*",
        "http://localhost",
        "http://localhost:*",
        "http://[::1]",
        "http://[::1]:*",
    ]
    if public_host is None:
        public_host = os.environ.get("CIRCUIT_MCP_PUBLIC_HOST", "").strip()
    if public_host:
        public = (
            public_host.removeprefix("https://")
            .removeprefix("http://")
            .split("/")[0]
        )
        allowed_hosts.extend([public, f"{public}:*"])
        allowed_origins.extend([f"https://{public}", f"https://{public}:*"])
    if disable_dns_rebind is None:
        disable_dns_rebind = os.environ.get("CIRCUIT_MCP_DISABLE_DNS_REBIND", "").strip() in {
            "1",
            "true",
            "yes",
        }
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=not disable_dns_rebind,
        allowed_hosts=allowed_hosts,
        allowed_origins=allowed_origins,
    )


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
        server.settings.transport_security = http_transport_security()
        server.run(transport="streamable-http")
        return 0
    server.run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
