---
name: generate-circuit
description: Turn an MCL 431 exam question into lecture-locked hydraulic/electrical/PLC SVGs. Use when the user pastes a circuit question, PYQ, or asks to draw a hydraulic, pneumatic, relay, or PLC ladder.
---

# Generate circuit

## Do this every time

1. Read the question and `exams/index.yaml`.
   - **Index hit:** start from that transcribed folder (`facts.yaml`, `deliverables.yaml`). Do not run ingest.
   - **No index hit, and the user handed a local PDF or scan:** run `python -m circuit ingest <path>` first (needs `pip install -e ".[ingest]"`). The parser may read `exams/ingest/<stem>/document.md` and `draft.yaml` (or `lecture/ingest/` for notes). Copy identifiers, tables, quantities, and sequence tokens (`1A+`, including prose-inferred motions). Do not promote `domain_guess` to `meta.domain` unless the question text says the domain. Do not turn a figure note or bbox into an atlas id. Run `python -m circuit promote <ingest_dir>` for a `proposal/` checklist; promoting into `exams/transcribed/` or the atlas is still a human edit.
2. If domain is **not** PLC: read `lecture/atlas.yaml`. You may only use those symbol IDs.
   If domain **is** PLC: skip atlas glyphs; fill a `plc:` block (see below). Notes L11–L13 under `lecture/ingest/` are searchable reference only.
3. Launch **four parallel** Cursor Task subagents in one turn. They return YAML fragments only. They must not draw and must not invent atlas IDs.

### Non-PLC papers

| Subagent | Returns |
| --- | --- |
| Parser | actuators, numbers, sequence, domain, deliverable list, identifier style |
| Hydraulic / pneumatic | pattern IDs from the lecture catalog, nets, valve types |
| Electrical | numbered current paths, K/Y/B tags, contact tables (L8) |
| Calc | solution block using L4–L6 formulas, or `not_given` |

### PLC papers (`domain: plc`)

| Subagent | Returns |
| --- | --- |
| Parser | domain plc, deliverables (`plc_connection`, `plc_ladder`), identifiers |
| PLC-I/O | `plc.io` rows + `plc.field` boxes (addresses from paper or suitable Micrologix-style) |
| PLC-ladder | `plc.rungs` with kinds `contact`, `coil`, `mov`, `cmp`, `ctu`, `ton`, `res`, `ons`, `otl`, `otu` |
| Calc | analog counts via `plc_counts` / paper presets, or `not_given` |

4. Merge into `circuit.yaml`. Conflicts: question domain + atlas (or paper PLC addresses) win.
5. Run:

```bash
python -m circuit validate <spec.yaml>
python -m circuit draw <spec.yaml>
python -m circuit eval <spec.yaml>
```

6. If eval fails, launch **one** fixer with `eval.json` (max two rounds), then stop and report what the atlas is missing (or which `plc:` field is wrong).
7. Reply with the SVG paths under `output/<exam_id>/`, `solution.txt`, and the eval report. Draw never dumps every question into a shared `output/` root.

## Hard rules

- Eval is required. Shipping SVGs without a passing report is incomplete.
- No image generation.
- Electrical agent must not add hydraulic valves. Hydraulic agent must not rewrite L8 path numbers.
- PLC agents must not emit L8 coils or atlas hydraulic IDs.
- Only the supervisor runs `draw`.

## Visual marking checklist

Eval PASS is not handwriting. After draw, check the sheet as an exam marker would:

- **Terminals:** home nB1 is NC **1/2** with rest-closed arrow; K aux is **11/14** (second **21/24**); START/S1/S3 pushbutton **13/14**; T1 timed contact **7/8**. Never label home NC as 21/22.
- **Contact-element table** under each K and T1 coil (coil name, A1/A2, aux terms used).
- **L8:** coils at the bottom of numbered current paths; sheet drawn de-energized.
- **Hydraulic:** ISO hop (polyline, no filled dot) at P/T crossings; B1 uses `cylinder_da`, not the L10 air cylinder; RV1 setpoint on B1 is **15.72 bar** (2.5 kN is the relief setting, not a pressure switch).
- Hydraulic-only papers skip electrical/phase sheets; electro papers write both.
- **PLC:** `plc_connection.svg` + `plc_ladder.svg` from `plc:` IR (I/O table, connection, ladder with CMP/MOV/CTU/TON as needed). Not an L8 relay sheet. Quote YAML `sense: "NO"` / `"NC"` (bare `NO` becomes boolean false).
- Outputs go to `output/<exam_id>/`.
- **Strip-feed:** H1 lamp on a main path; start contacts S1/S3, not JOB.
- **Emboss:** PS≥4 bar holds 2A1; do not retract on 2B2.
- **Pneumatic air (notes p6, p14, p22):** 5/2 for air (4/2 is hydraulics). Port 1 = P supply, 2/4 = actuator, 3/5 = exhaust with open triangles and no continuing pipe. Cylinder over the valve; cap → 4, rod jog → 2. Solenoid boxes flush on the envelopes (no stem). Label contacts with the tag (`K5`), not `!K5`. FRL is on the supply path but has no atlas glyph — name it in the BOM, do not invent a stamp.
- Missing atlas crop (`dcv_5_3` etc.) → stop. Do not draw a generic ISO box.
