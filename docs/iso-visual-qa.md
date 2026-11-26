# ISO visual QA

Score the PNG, do not trust pytest alone.

| Sheet | Command | Pass |
| --- | --- | --- |
| ISO pneumatic | `output/iso_sequence/pneumatic_circuit.png` — cylinder over valve, cap→4, rod jog→2, exhaust 3/5, rest envelope right | pass |
| ISO electrical | coils at bottom rail, numbered paths | pass |
| ISO phase | 0/1 traces | pass |
| Card | sequence + English sentence + safety footer | pass |
| Report | PASS/FAIL rows, assumptions, not certified | pass |
| ISO hydraulic | lecture pack still draws PRV/tank; ISO hydraulic vectors via `draw_glyph` | pass |
| Workspace | `http://127.0.0.1:8088/` Generate → SVG | pass |
| Fail card | closed_center nowhere for the oil | pass |
