# Self-hosting (zero mandatory spend)

Fly.io is **SKIPPED_OPTIONAL**. Nothing in the mandatory product path calls Fly, a paid API, or a developer-owned cloud account.

## 1. CLI (no network)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m circuit draw examples/iso_sequence/circuit.yaml
python -m circuit verify examples/iso_sequence/circuit.yaml
python -m circuit bench benchmarks/sequencebench
python -m circuit bench --suite 300
python -m circuit bench --suite llm
```

## 2. Browser workspace (static hosting)

`web/` is a static site. `app.js` loads Pyodide 314 from jsDelivr and unpacks `circuit-iso.zip`. There is no Fly URL.

Serve it from any static host you already have:

```bash
python -m http.server 8000 --bind 127.0.0.1 --directory web
```

GitHub Pages: publish the `web/` folder. The compiler runs in the browser. If WASM fails, the page is still a YAML editor; download YAML and run the CLI.

Rebuild the zip after engine changes:

```bash
python scripts/sync_web_circuit.py
```

## 3. Local MCP (stdio — Cursor, Claude Desktop)

```bash
python -m circuit.mcp_server
```

Config: [plugin/mcp.stdio.json](../plugin/mcp.stdio.json). This is **not** directory-eligible.

## 4. Local MCP (HTTP on loopback)

```bash
pip install -e ".[mcp]"
python -m circuit.mcp_server --http --host 127.0.0.1 --port 8000
curl -s http://127.0.0.1:8000/health
```

Bind `0.0.0.0` only if you intend LAN access. Directory clients still need a public **HTTPS** origin.

## 5. Optional public HTTPS without Fly

A public ChatGPT/Claude directory listing needs `https://<your-host>/mcp` plus `/privacy`, `/terms`, `/support`, and (OpenAI) `/.well-known/openai-apps-challenge`.

Zero-spend options that use hardware or accounts you already have:

- Cloudflare Tunnel / Tailscale Funnel on a machine you already run
- Caddy or nginx with an existing certificate
- Docker: `docker build` then run `python -m circuit.mcp_server --http --host 0.0.0.0 --port 8080`

Do not treat a tunnel URL as a completed OpenAI/Anthropic listing. Copy [plugin/SUBMISSION.md](../plugin/SUBMISSION.md) after the origin is stable.

Static legal pages live in [deploy/static/](../deploy/static/).
