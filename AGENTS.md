# MCL 431 circuit studio

Cursor-only. You interpret the question; `python -m circuit` draws.

## Commands

```bash
python -m circuit rasterize
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

## Solve a question

Follow `.cursor/skills/generate-circuit/SKILL.md`. Fan out four subagents (parser, hydraulic, electrical, calc), merge YAML, then validate → draw → eval. Sheets land in `output/<exam_id>/`.
