# Sequence Circuit workspace

Generate path: **Pyodide first**. `app.js` loads Pyodide 314, `micropip.install` pydantic + pyyaml, unpacks `circuit-iso.zip` (ISO-safe copy of `src/circuit`, no ingest/rasterize/pymupdf), and calls `draw_yaml` in the browser.

If WASM fails, this VM / local demo POSTs YAML to `python -m circuit.web_server` (`/api/draw` → `draw_yaml`). GitHub Pages still works as a YAML editor: paste, download, run the CLI.

Pyodide spike: `spike.html`. No Fly URL. No paid API.
