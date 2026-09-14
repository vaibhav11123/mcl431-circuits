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

## Visual marking checklist

Eval PASS is not handwriting. Check the sheet as an exam marker would:

- **Terminals:** home nB1 is NC **1/2** with rest-closed arrow; K aux is **11/14** (second **21/24**); START/S1/S3 pushbutton **13/14**; T1 timed contact **7/8**. Never label home NC as 21/22.
- **Contact-element table** under each K and T1 coil (coil name, A1/A2, aux terms used).
- **L8:** coils at the bottom of numbered current paths; sheet drawn de-energized.
- **Hydraulic:** ISO hop (polyline, no filled dot) at P/T crossings; B1 uses `cylinder_da`, not the L10 air cylinder; RV1 setpoint on B1 is **15.72 bar** (2.5 kN is the relief setting, not a pressure switch).
- Hydraulic-only papers skip electrical/phase sheets; electro papers write both.
- Outputs go to `output/<exam_id>/`.
- **Strip-feed:** H1 lamp on a main path; start contacts S1/S3, not JOB.
- Missing atlas crop (`dcv_5_3` etc.) → stop. Do not draw a generic ISO box.
