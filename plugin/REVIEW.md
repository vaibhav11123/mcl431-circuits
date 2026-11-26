# Review script

## Draw

### Draw 1 — ISO 5/2 two cylinder
Paste `examples/iso_sequence/circuit.yaml`. Expect a pneumatic PNG.

### Draw 2 — A+ B+ B- A-
Natural language sequence. Expect 5/2 assumption on the report.

### Draw 3 — PLC conveyor
`examples/plc_conveyor_2023/circuit.yaml`. Connection + ladder.

### Draw 4 — TIMER 3s
Insert a wait after B+. Timer coil on the electrical sheet.

### Draw 5 — get_sheet retry
If chat has no picture, call get_sheet with the same YAML.

## Refuse

### Refuse invented id
Valve type `magic_valve`. Sentence: That symbol is not in the pack.

### Refuse simulate
"Simulate the pressure." Sentence: No pressure physics. Open the sequence explorer.

### Refuse ingest PDF
Uploading a lecture PDF. Skill refuses ingest on the public pack.
