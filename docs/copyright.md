# Copyright

Code in this repo is **MIT** ([LICENSE](../LICENSE)). Lecture slides and exam papers belong to the course / IIT Delhi.

## What GitHub has

- Drawer code (`src/circuit/`)
- Lecture lockfiles: `lecture/atlas.yaml`, `lecture/diagrams.yaml`, cropped **stamps** under `lecture/crops/stamps/`
- PYQ transcriptions (`exams/transcribed/`) and `exams/index.yaml` — how the paper asks, not the scan
- Golden `circuit.yaml` files and the gallery PNGs we drew (`docs/images/`)

## What stays on your machine

Lecture decks and PYQ scans are **not in this repo** (gitignored on purpose). Do not add them.

- `lecture/*.pdf`
- `exams/pyqs/` (pdf / jpeg / png)
- rasters in `lecture/pages/` and `exams/pages/` (rebuild locally with `python -m circuit rasterize` if you have the PDFs)

The stamps already in the repo are enough to draw. You do not need to publish course files to use the tool.

## If you have your own copies

Put lecture PDFs in `lecture/` and papers in `exams/pyqs/` locally. They will not be committed. Do not open a PR that adds those files.
