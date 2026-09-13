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
7. Reply with the SVG paths, `solution.txt`, and the eval report.

## Hard rules

- Eval is required. Shipping SVGs without a passing report is incomplete.
- No image generation.
- Electrical agent must not add hydraulic valves. Hydraulic agent must not rewrite L8 path numbers.
- Only the supervisor runs `draw`.
