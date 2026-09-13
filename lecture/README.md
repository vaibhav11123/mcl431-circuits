Lecture PDFs are the symbol and method atlas.

- `*.pdf` — original slides (do not move)
- `pages/` — 200 dpi rasters from `python -m circuit rasterize`
- `crops/` — pixels cut from those pages (`python lecture/crop_glyphs.py`)
- `crops/stamps/` — trimmed glyphs the drawer pastes (`python lecture/prepare_stamps.py`)
- `atlas.yaml` — allowed symbol IDs
- `diagrams.yaml` — every lecture circuit: where ports go, when to use it
- `goldens/` — worked examples from the slides

Read `diagrams.yaml` before drawing. `src/circuit/catalog.py` stamps the cited PNG and returns port anchors. The drawer only draws wires. Do not invent a glyph.
