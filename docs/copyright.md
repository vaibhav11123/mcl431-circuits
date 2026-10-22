# Copyright

Code in this repo is **MIT** ([LICENSE](../LICENSE)). Lecture slides and exam papers belong to the course / IIT Delhi.

## What GitHub has

- Drawer code (`src/circuit/`)
- Lecture lockfiles: `lecture/atlas.yaml`, `lecture/diagrams.yaml`, cropped **stamps** under `lecture/crops/stamps/`
- PYQ transcriptions (`exams/transcribed/`) and `exams/index.yaml` — how the paper asks, not the scan
- Golden `circuit.yaml` files and the gallery PNGs we drew (`docs/images/`)

## What stays on your machine

Lecture decks and PYQ scans are **not in this repo** (gitignored on purpose). Do not add them.

- lecture decks (pdf)
- exam papers under `exams/pyqs/`
- slide and paper rasters (rebuild locally with `python -m circuit rasterize` if you have the files)
- Docling drafts under `exams/ingest/` and `lecture/ingest/` (rebuild with `python -m circuit ingest`; optional `promote` writes `proposal/` only — still local)

The stamps already in the repo are enough to draw. You do not need to publish course files to use the tool.

The 5/2 and 5/3 valve bodies are ISO 1219-1 symbols from Wikimedia Commons
([File:Symbol 5-2 ski selector valve.svg](https://commons.wikimedia.org/wiki/File:Symbol_5-2_ski_selector_valve.svg)
and
[File:Symbol 5-3 ski selector valve (mid-position closed).svg](https://commons.wikimedia.org/wiki/File:Symbol_5-3_ski_selector_valve_(mid-position_closed).svg),
MovGP0, [CC-BY-3.0](https://creativecommons.org/licenses/by/3.0/)). Operators are the lecture `solenoid_box` stamp.

## If you have your own copies

Put lecture PDFs in `lecture/` and papers in `exams/pyqs/` locally. They will not be committed. Do not open a PR that adds those files.
