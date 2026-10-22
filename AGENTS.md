# MCL 431 circuit studio

Cursor-only. You interpret the question; `python -m circuit` draws.

## Commands

```bash
python -m circuit rasterize
python -m circuit ingest <local.pdf|jpeg>   # needs pip install -e ".[ingest]"
python -m circuit promote <exams|lecture>/ingest/<stem>  # proposal/ only; never edits locks
python -m circuit validate <spec.yaml>
python -m circuit draw <spec.yaml>
python -m circuit eval <spec.yaml>
python -m circuit eval --goldens
```

## Source of truth (in order)

1. `lecture/atlas.yaml`, `lecture/diagrams.yaml`, and crops — symbols, rest position, connections, L8 drawing law
2. `exams/index.yaml` and `exams/transcribed/` — how the paper asks, tags, deliverables
3. Golden specs in `examples/` and `lecture/goldens/`
4. The user question

Never invent a symbol ID. Never skip `eval`. Hydraulic and electrical are separate sheets.

## PLC notes vs problems (local)

- **Notes (L11–L13):** `lecture/MCL431_L11_PLC_Basics.pdf`, `…_L12_…`, `…_L13_…` (gitignored). Ingest → `lecture/ingest/` drafts only. Do **not** promote into the atlas.
- **Problems (L14):** `lecture/MCL431_L14_PLC_Problems.pdf`. Locked facts under `exams/transcribed/plc_l14_*` + index rows. Goldens under `examples/plc_l14_*` and `examples/plc_conveyor_2023`.
- PLC sheets use `domain: plc` and a `plc:` IR block (`io`, `field`, `scaling`, `rungs`). Rung kinds: `contact`, `coil`, `mov`, `cmp`, `ctu`, `ton`, `res`, `ons`, `otl`, `otu`. Draw writes `plc_connection.svg` + `plc_ladder.svg` — never L8 coils. No atlas PLC glyphs. Visual/answer gates: [docs/plc-visual-qa.md](docs/plc-visual-qa.md).

## Solve a question

Follow `.cursor/skills/generate-circuit/SKILL.md`. Fan out four subagents, merge YAML, then validate → draw → eval. Sheets land in `output/<exam_id>/`.

The later product build is [docs/ship-execution-plan.md](docs/ship-execution-plan.md). Do not start it unless the user asks to execute that plan.
