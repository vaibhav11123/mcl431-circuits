# Solve a question

You write a `circuit.yaml`. Python draws and checks. It does not invent extra valves, pumps, or meter-in/out unless the paper asks.

## 1. Read how the paper asks

Open [`exams/index.yaml`](../exams/index.yaml). If a transcribed PYQ matches, start from that folder under [`exams/transcribed/`](../exams/transcribed/) (`facts.yaml`, `deliverables.yaml`). Use the paper’s identifiers (`HC1` vs `1A`), not a default guess.

## 2. Lock symbols to the lecture atlas

Only use IDs in [`lecture/atlas.yaml`](../lecture/atlas.yaml). Ports and rest position are in [`lecture/diagrams.yaml`](../lecture/diagrams.yaml). If an atlas crop is missing, stop — do not substitute a generic box.

## 3. Write the spec

Copy a close golden from [`examples/`](../examples/) (B1 grinding, 2017 hi-lo, 2023 strip-feed). Preserve the stated sequence. Valves are drawn de-energized.

Hydraulic and electrical stay on **separate sheets**. Pneumatic papers use the L10 5/2 sheet, not a hydraulic 4/3.

## 4. Validate, draw, eval

```bash
python -m circuit validate path/to/circuit.yaml
python -m circuit draw path/to/circuit.yaml
python -m circuit eval path/to/circuit.yaml
```

Open the files under `output/<exam_id>/` (gitignored). Draw and eval write that folder only — they do not overwrite another question. A pretty SVG that fails eval is not done.

Worked start: [`examples/grinding_machine/circuit.yaml`](../examples/grinding_machine/circuit.yaml).

If you use an AI assistant to write YAML, give it [`AGENTS.md`](../AGENTS.md) — same atlas-first contract.
