---
name: generate-circuit
description: Turn an MCL 431 exam question into lecture-locked hydraulic/electrical SVGs. Use when the user pastes a circuit question, PYQ, or asks to draw a hydraulic, pneumatic, or relay sequence.
---

# Generate circuit

## Do this every time

1. Read the question and `exams/index.yaml`. If a transcribed PYQ matches, start from that golden.
2. Read `lecture/atlas.yaml`. You may only use those symbol IDs.
3. Launch **four parallel** Cursor Task subagents in one turn. They return YAML fragments only. They must not draw and must not invent atlas IDs.

| Subagent | Returns |
| --- | --- |
| Parser | actuators, numbers, sequence, domain, deliverable list, identifier style |
| Hydraulic / pneumatic | pattern IDs from the lecture catalog, nets, valve types |
| Electrical | numbered current paths, K/Y/B tags, contact tables (L8) |
| Calc | solution block using L4–L6 formulas, or `not_given` |

4. Merge into `circuit.yaml`. Conflicts: question domain + atlas win.
5. Run:

```bash
python -m circuit validate <spec.yaml>
python -m circuit draw <spec.yaml>
python -m circuit eval <spec.yaml>
```

6. If eval fails, launch **one** fixer with `eval.json` (max two rounds), then stop and report what the atlas is missing.
7. Reply with the SVG paths under `output/<exam_id>/`, `solution.txt`, and the eval report. Draw never dumps every question into a shared `output/` root.

## Hard rules

- Eval is required. Shipping SVGs without a passing report is incomplete.
- No image generation.
- Electrical agent must not add hydraulic valves. Hydraulic agent must not rewrite L8 path numbers.
- Only the supervisor runs `draw`.

## Visual marking checklist

Eval PASS is not handwriting. After draw, check the sheet as an exam marker would:

- **Terminals:** home nB1 is NC **1/2** with rest-closed arrow; K aux is **11/14** (second **21/24**); START/S1/S3 pushbutton **13/14**; T1 timed contact **7/8**. Never label home NC as 21/22.
- **Contact-element table** under each K and T1 coil (coil name, A1/A2, aux terms used).
- **L8:** coils at the bottom of numbered current paths; sheet drawn de-energized.
- **Hydraulic:** ISO hop (polyline, no filled dot) at P/T crossings; B1 uses `cylinder_da`, not the L10 air cylinder; RV1 setpoint on B1 is **15.72 bar** (2.5 kN is the relief setting, not a pressure switch).
- Hydraulic-only papers skip electrical/phase sheets; electro papers write both.
- Outputs go to `output/<exam_id>/`.
- **Strip-feed:** H1 lamp on a main path; start contacts S1/S3, not JOB.
- Missing atlas crop (`dcv_5_3` etc.) → stop. Do not draw a generic ISO box.
