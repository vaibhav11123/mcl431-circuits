# MCL 431 CAM and Automation — circuit drawings (IIT Delhi)

Write a YAML spec. Python draws hydraulic, electropneumatic, and PYQ sheets the way this IIT Delhi course teaches them — lecture symbols, de-energized valves, L8 paths, L10 sequences.

## Contents

- [Gallery](#gallery)
- [Start in 3 commands](#start-in-3-commands)
- [What papers](#what-papers)
- [Handbook](#handbook)
- [Copyright](#copyright)

## Gallery

2023 Self-Study B1 grinding (HC1 / HC2 / HM1):

![2023 B1 grinding hydraulic](docs/images/b1-hydraulic.png)

![2023 B1 grinding electrical](docs/images/b1-electrical.png)

![2023 B1 step-displacement](docs/images/b1-phase.png)

2023 Minor-2 Q1 strip feed (1A / 2A, 5/2):

![2023 Minor-2 Q1 strip-feed pneumatic](docs/images/strip-feed-pneumatic.png)

## Start in 3 commands

Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

```bash
python -m circuit validate examples/grinding_machine/circuit.yaml
python -m circuit draw examples/grinding_machine/circuit.yaml
python -m circuit eval examples/grinding_machine/circuit.yaml
```

Open the sheets under `output/<exam_id>/` after draw (B1 → `output/2023_selfstudy_b1/`). Each question gets its own folder.

## What papers

- **Sheets:** 2023 B1 grinding, 2017 hi-lo punch, 2023 Minor-2 strip feed, 2023 Minor-2 PLC conveyor, 2017 5/3 drill, 2016 emboss, L14 PLC set, 2018 air-jet (3Z = `dcv_3_2`), 2020 mill clamp (5 bar), 2022 two-hand stamp, 2023 four-hole drill, majors PLC (oven, sprinkler, lockout, preset counter, tank mix, orange juice, plywood stack, traffic / quiz conveyor)
- **Solution text** (figure given or numeric only): 2018 hi-lo, 2019 meter-in/out, 2016 hoist, 2023 B2 head loss, 2022 grind-given, 2019 vertical meter-out, 2020/2022 hoist with pipe loss, stepper/servo numbers, 2023 Part A, quiz regen
- **Not a sheet:** corporate-adaptation prose; CNC part programs until every figure coordinate is in `facts.yaml` (`not_given` otherwise)

Full gates: [docs/eval.md](docs/eval.md). Learnings log: [docs/pyq-solution-run-log.md](docs/pyq-solution-run-log.md).

## Handbook

- [Solve a question](docs/solve-a-question.md)
- [What eval checks](docs/eval.md)
- [Copyright](docs/copyright.md)

Paper identifiers win (`HC1` vs `1A`). Hydraulic and electrical stay on separate sheets.

## Copyright

Code is MIT. Lecture decks and exam scans are not in this repo. Details: [docs/copyright.md](docs/copyright.md).
