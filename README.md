# MCL 431 circuit studio

Draw **hydraulic** and **electropneumatic** exam sheets the way IIT Delhi MCL 431 (CAM and Automation) teaches them: lecture symbols, de-energized valves, L8 current paths, L10 step-displacement.

You write a `circuit.yaml`. Python draws the SVGs and checks the spec. It does not invent extra valves, pumps, or meter-in/out unless the question asks for them.

## What you get

| File | What it is |
| --- | --- |
| `output/hydraulic_circuit.svg` / `.png` | Power unit + actuators + 4/3 valves (lecture glyphs) |
| `output/pneumatic_circuit.svg` / `.png` | L10 p5 two DAC + 5/2 (when the domain is pneumatic) |
| `output/electrical_circuit.svg` / `.png` | +24 V / 0 V, numbered paths, coils at the bottom |
| `output/step_displacement.svg` / `.png` | 0/1 traces per actuator (L10 method) |
| `output/solution.txt` | Sequence + lecture-form calculations |
| `output/eval.json` | Pass/fail checks |

Worked example: **2023 Self-Study Minor B1** (surface grinding — HC1 / HC2 / HM1, JOB, 30 s grind). Clamp pressure in `solution.txt` is **15.72 bar**.

## Install

Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Lecture **PDFs are not in this repo** (course copyright). Put your copies in `lecture/` if you want to re-crop symbols. The checked-in `lecture/crops/` stamps are enough to draw.

## Draw the grinding example

```bash
python -m circuit validate examples/grinding_machine/circuit.yaml
python -m circuit draw examples/grinding_machine/circuit.yaml
python -m circuit eval examples/grinding_machine/circuit.yaml
```

Open the SVGs under `output/`.

## What is tested

```bash
pytest -q
python -m circuit eval --goldens
```

**Covered (`pytest` + `eval --goldens`):**

| Exam | What eval requires | Must not do |
| --- | --- | --- |
| 2023 Self-Study B1 grinding | JOB, one pump, 30 s, 15.72 bar, L8 latch, no Y-as-contact | Extra FCV / second pump |
| 2017 Minor-1 hi-lo punch | P1+P2, UV, RV; bore `not_given` | Invented 50/28 |
| 2023 Minor-2 Q1 strip feed | Domain pneumatic, two 5/2, coils `1Y1 2Y2 1Y2 2Y1` | Hydraulic 4/3 on a 5/2 paper |
| 2018 hi-lo / 2019 meter / 2016 hoist / 2023 B2 / 2022 grind-given | `figure_given` calc cites `facts.yaml` | Draw a figure the paper already printed |
| L4 regen identity | \(A_p = 3 A_r \Rightarrow V_\mathrm{ext}/V_\mathrm{ret} = 2\) | Attach regen math to B1 or hi-lo |

Also: every stamp PNG exists; B1 SVG has HC1/HC2/HM1; this Mac writes PNG next to each SVG (`qlmanage`).

**Skipped:**

- PLC v2 Minor-2 Q2 (`pattern_hint: plc_v2_skip`)
- 2017 indexing drill — `dcv_5_3` crop is `null` (`examples/drill_2017/README.md`)
- Pixel-SSIM against a full lecture slide

A pretty SVG that fails `eval` is not done. A passing `eval` means the **spec is legal for that exam**, not that the sheet looks like handwriting.

## Solve another question

1. Read `exams/index.yaml` and the matching `exams/transcribed/<id>/`.
2. Only use symbol IDs from `lecture/atlas.yaml`.
3. Follow connection rules in `lecture/diagrams.yaml` (ports on the de-energized envelope, coils under contacts).
4. Write `circuit.yaml`, then `validate` → `draw` → `eval`.

Paper identifiers win (`HC1` vs `1A`). Hydraulic and electrical stay on **separate** sheets.

`AGENTS.md` is the same contract if you use an AI assistant to write the YAML.

## Repo layout

```
src/circuit/     # validate, draw, eval, catalog (stamps + port anchors)
lecture/         # atlas, diagrams, crops/stamps — not the original PDFs
exams/           # PYQ index + transcriptions — not the scanned papers
examples/        # drawing goldens + figure-given calc goldens
tests/           # pytest
```

## Course material

Lecture slides and exam scans belong to the course / IIT Delhi. This repo ships **code, YAML lockfiles, transcriptions, and cropped ISO glyphs** so classmates can reproduce drawings. Drop your own PDFs in `lecture/` and `exams/pyqs/` locally; they are gitignored on purpose.

## License

MIT for the code. Lecture and exam content remain with their owners.
