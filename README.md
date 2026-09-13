# MCL 431 circuit studio

Draw **hydraulic** and **electropneumatic** exam sheets the way IIT Delhi MCL 431 (CAM and Automation) teaches them: lecture symbols, de-energized valves, L8 current paths, L10 step-displacement.

You write a `circuit.yaml`. Python draws the SVGs and checks the spec. It does not invent extra valves, pumps, or meter-in/out unless the question asks for them.

## What you get

| File | What it is |
| --- | --- |
| `output/hydraulic_circuit.svg` | Power unit + actuators + 4/3 valves (lecture glyphs) |
| `output/electrical_circuit.svg` | +24 V / 0 V, numbered paths, coils at the bottom |
| `output/step_displacement.svg` | 0/1 traces per actuator (L10 method) |
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

**Covered today (10 unit tests + golden eval):**

- B1 spec loads (HC1 45/22.5 mm, HM1 400 rpm, 6-step sequence)
- Atlas lock: valve types exist, one pump, JOB sensor, no extra FCV
- Sequence compiles to coils `K_START, 1Y1, 3Y1, 2Y1, T1_30s, 2Y2, 1Y2`
- Clamp math: \(P = F / (0.1 A_p) = 15.72\) bar
- L4 regenerative identity: \(A_p = 3 A_r \Rightarrow V_\mathrm{ext}/V_\mathrm{ret} = 2\)
- Every stamp PNG the drawer uses is present
- 2017 hi-lo punch golden **validates** (pumps, PRV, coils)

**Not tested (do not treat as exam-ready):**

- Pixel-perfect match to a slide (no screenshot tests)
- The other transcribed PYQs — they are indexed and typed, not solved + eval’d
- Every number in every paper (pump \(Q\) is left `not_given` when the question omits it)
- Visual layout of every new question you add

A pretty SVG that fails `eval` is not done. A passing `eval` means the **spec** is legal, not that the drawing looks like your handwriting.

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
examples/        # B1 grinding + 2017 hi-lo punch
tests/           # pytest
```

## Course material

Lecture slides and exam scans belong to the course / IIT Delhi. This repo ships **code, YAML lockfiles, transcriptions, and cropped ISO glyphs** so classmates can reproduce drawings. Drop your own PDFs in `lecture/` and `exams/pyqs/` locally; they are gitignored on purpose.

## License

MIT for the code. Lecture and exam content remain with their owners.
